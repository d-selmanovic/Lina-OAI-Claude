"""Einstieg: Lina – Outbound-Recruiting-Agent (Anruf 1: Datenerfassung).

Ablauf: Kandidat bestimmen → Pre-Call-Fetch aus Airtable (vor dem Sessionstart) →
Instruktionen mit Kontext bauen → GPT-Live-Session → am Ende einmalig zurückschreiben.

Kandidat: Dispatch-Metadaten `{"record_id": "rec..."}`. Nur zum lokalen Testen ohne Metadaten
gilt `LINA_TEST_RECORD_ID` (Test-Kandidat K-0196).
"""

import asyncio
import json
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from livekit.agents import (
    AMD,
    AgentServer,
    AgentSession,
    CloseEvent,
    ConversationItemAddedEvent,
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
from lina.dialog import DialogProtokoll
from lina.kontekst import izracunaj
from lina.simulacija import paket_iz_userdata, razlike
from lina.stanje import Stanje
from lina.telemetrie import setup_langfuse, umgebung
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
    # GPT-Live delegiert asynchron: Die Simulation endet oft mit Linas Abschiedssatz, bevor das
    # Backend die letzten Angaben gespeichert hat. Kurz warten, bis der Abschluss gemeldet ist.
    for _ in range(20):
        if stanje.ishod is not None:
            break
        await asyncio.sleep(0.5)
    await asyncio.sleep(1.0)
    if fehler := razlike(stanje, expected):
        sim.fail(reason="; ".join(fehler))


def _tekst_iz_historije(history) -> str:
    items = getattr(history, "items", None)
    if items is None and isinstance(history, list):
        items = history
    linije = []
    for item in items or []:
        role = getattr(item, "role", None)
        if role not in ("user", "assistant"):
            continue
        tekst = getattr(item, "text_content", None)
        if not tekst:
            sadrzaj = getattr(item, "content", "")
            if isinstance(sadrzaj, list):
                tekst = " ".join(str(c) for c in sadrzaj if isinstance(c, str))
            else:
                tekst = str(sadrzaj or "")
        tekst = (tekst or "").strip()
        if not tekst:
            continue
        linije.append(("Kandidat: " if role == "user" else "Lina: ") + tekst)
    return "\n".join(linije)


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
    langfuse = setup_langfuse(
        metadata={"langfuse.session.id": ctx.room.name, "lina.record_id": record_id}
    )
    trace_provider, dialog_prozessor = (
        langfuse if langfuse is not None else (None, None)
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
    stanje.polja = dict(paket.kandidat)
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

    # Gesprächsverlauf beider Seiten für Langfuse (Kandidat + Lina), siehe lina/dialog.py
    protokoll = DialogProtokoll()
    if dialog_prozessor is not None:
        dialog_prozessor.binde(
            protokoll,
            {
                "record_id": record_id,
                "umgebung": umgebung(),
                "anzahl_fehlender_angaben": len(kontekst.nedostaje),
            },
        )

    @session.on("conversation_item_added")
    def _dialog_item(ev: ConversationItemAddedEvent) -> None:
        protokoll.dodaj(ev.item)

    @session.on("close")
    def _dialog_kraj(ev: CloseEvent) -> None:
        # läuft vor dem Ende des agent_session-Spans, der den ganzen Dialog bekommt
        protokoll.abschluss = {
            "ishod": stanje.ishod or stanje.ishod_bez_kraja(),
            "sazetak": stanje.sazetak,
            "razlog_kraja": str(getattr(ev, "reason", "") or ""),
        }
        protokoll.beendet = True

    async def spremi_na_kraju() -> None:
        if stanje.sacuvano:
            return
        stanje.transkript = _tekst_iz_historije(session.history)
        if not stanje.sazetak and stanje.transkript:
            stanje.sazetak = stanje.transkript.replace("\n", " ")[:240]
        stanje.ishod = stanje.ishod or stanje.ishod_bez_kraja()
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
        # Default-STT von AMD (cartesia/ink-whisper) gibt es in der EU-Region nicht;
        # ohne Transkript endet AMD immer mit UNCERTAIN. Nova-3 hat EU-Endpunkt und Bosnisch.
        async with AMD(
            session,
            stt=os.getenv("LINA_AMD_STT", "deepgram/nova-3:bs"),
            ivr_detection=False,
        ) as detector:
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
