"""Einstieg: Lina – Outbound-Recruiting-Agent (Anruf 1: Datenerfassung).

Ablauf: Kandidat bestimmen → Pre-Call-Fetch aus Airtable (vor dem Sessionstart) →
Instruktionen mit Kontext bauen → GPT-Live-Session → am Ende einmalig zurückschreiben.

Kandidat: Dispatch-Metadaten `{"record_id": "rec..."}`. Nur zum lokalen Testen ohne Metadaten
gilt `LINA_TEST_RECORD_ID` (Test-Kandidat K-0196).
"""

import json
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from livekit.agents import (
    AMD,
    AgentServer,
    AgentSession,
    JobContext,
    SimulationContext,
    cli,
    inference,
    room_io,
)
from livekit.agents.beta import EndCallTool
from livekit.plugins import ai_coustics

from lina import prompts
from lina.agent_lina import PozdravAgent
from lina.airtable import AirtableStore, FakeStore, Store, sacuvaj
from lina.kontekst import izracunaj
from lina.simulacija import paket_iz_userdata, razlike
from lina.stanje import Stanje
from lina.telemetrie import setup_langfuse
from lina.zeit import TZ, opis

logger = logging.getLogger("agent")

load_dotenv(".env.local")

AGENT_NAME = "livekit-oai-gig-casting"


def _record_id(ctx: JobContext) -> str | None:
    meta = (ctx.job.metadata or "").strip()
    if meta:
        try:
            rid = json.loads(meta).get("record_id")
        except (ValueError, AttributeError):
            rid = None
        if rid:
            return str(rid)
        logger.error("Dispatch-Metadaten ohne gültiges record_id")
        return None
    return os.getenv("LINA_TEST_RECORD_ID") or None


async def on_simulation_end(sim: SimulationContext) -> None:
    expected = sim.userdata().get("expected_state")
    if not expected:
        return
    session = sim.job_context.primary_session
    if session is None:
        sim.fail(reason="Session wurde nicht gestartet")
        return
    stanje: Stanje = session.userdata
    if fehler := razlike(stanje, expected):
        sim.fail(reason="; ".join(fehler))


server = AgentServer()


@server.rtc_session(agent_name=AGENT_NAME, on_simulation_end=on_simulation_end)
async def my_agent(ctx: JobContext):
    store: Store
    fiksno: datetime | None = None
    if sim := ctx.simulation_context():
        ud = sim.userdata()
        store = FakeStore(paket_iz_userdata(ud))
        record_id = "recSIMULACIJA00001"
        if ud.get("sada"):
            fiksno = datetime.fromisoformat(ud["sada"]).replace(tzinfo=TZ)
    else:
        record_id = _record_id(ctx)
        if not record_id:
            logger.error("Kein Kandidat (record_id) – Session wird nicht gestartet")
            ctx.shutdown(reason="no record_id")
            return
        store = AirtableStore()

    ctx.log_context_fields = {"room": ctx.room.name, "record_id": record_id}

    # Langfuse (optional): vor dem Sessionstart, damit alle Spans ankommen.
    trace_provider = setup_langfuse(
        metadata={"langfuse.session.id": ctx.room.name, "lina.record_id": record_id}
    )
    if trace_provider is not None:

        async def flush_trace() -> None:
            trace_provider.force_flush()

        ctx.add_shutdown_callback(flush_trace)

    # Pre-Call-Fetch: VOR dem Sessionstart. Ohne Kontext wird nicht telefoniert.
    try:
        paket = await store.ucitaj(record_id)
    except Exception:
        logger.exception("Pre-Call-Fetch fehlgeschlagen")
        ctx.shutdown(reason="pre-call fetch failed")
        return
    kontekst = izracunaj(
        record_id, paket.kandidat, paket.dopune, paket.radno_iskustvo, paket.obrazovanje
    )
    stanje = Stanje(kontekst, fiksno_vrijeme=fiksno)
    vrijeme = opis(stanje.sada())
    logger.info("Kontekst: %d Angaben fehlen", len(kontekst.nedostaje))

    session = AgentSession(
        llm=inference.DuplexModel(
            model="openai/gpt-live-1",
            voice=os.getenv("LINA_VOICE", "marin"),
            extra_kwargs={
                "responses_options": {
                    "model": os.getenv("LINA_BACKEND_MODEL", "gpt-5.6-luna"),
                    "instructions": prompts.backend(kontekst, vrijeme),
                },
            },
        ),
        # GPT-Live steuert Turns selbst; eine VAD ist nötig, damit Barge-in die Wiedergabe stoppt.
        vad=inference.VAD(model="silero"),
        userdata=stanje,
    )

    async def spremi_na_kraju() -> None:
        if stanje.sacuvano:
            return
        if stanje.ishod is None and not (
            stanje.podaci
            or stanje.nove_stanice
            or stanje.nove_skole
            or stanje.povratni_poziv
        ):
            # Nichts erfasst und kein Ergebnis: keinen leeren Dopune-Eintrag erzeugen.
            logger.info("Gespräch ohne erfasste Angaben beendet – nichts gespeichert")
            return
        stanje.ishod = stanje.ishod or "prekinuto"
        try:
            await sacuvaj(store, stanje)
        except Exception:
            logger.exception("Speichern beim Sitzungsende fehlgeschlagen")

    ctx.add_shutdown_callback(spremi_na_kraju)

    extra = [EndCallTool(end_instructions=None, ignore_on_enter=True)]
    agent = PozdravAgent(
        stanje=stanje,
        store=store,
        kontekst=kontekst,
        vrijeme=vrijeme,
        tools=extra,
    )

    await session.start(
        agent=agent,
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=ai_coustics.audio_enhancement(
                    model=ai_coustics.EnhancerModel.QUAIL_VF_S
                ),
            ),
        ),
    )
    await ctx.connect()
    # Nicht sofort reden: warten, bis der Angerufene sich meldet (Halo / Da?).
    if ctx.simulation_context():
        return
    try:
        async with AMD(session, ivr_detection=False) as detector:
            amd = await detector.execute()
        logger.info("AMD category=%s", amd.category)
        if amd.category == "machine-vm":
            handle = session.generate_reply(
                instructions=(
                    "Govori bosanski, kratko, bez tagova. Reci da je Lina iz Job-Stepa "
                    "zvala i da ćemo se javiti. Onda šuti."
                )
            )
            await handle.wait_for_playout()
            stanje.ishod = stanje.ishod or "prekinuto"
            ctx.shutdown(reason="voicemail")
            return
        if amd.category == "machine-unavailable":
            stanje.ishod = stanje.ishod or "prekinuto"
            ctx.shutdown(reason="mailbox unavailable")
            return
    except Exception:
        logger.exception("AMD fehlgeschlagen – weiter wie Mensch")


if __name__ == "__main__":
    cli.run_app(server)
