"""Vollständiger Gesprächsverlauf (Kandidat + Lina) für Langfuse.

Warum: Bei Realtime-Modellen (GPT-Live) schreibt LiveKit auf den `agent_turn`-Span nur Linas
Text (`lk.pii.response.text`), nicht die Aussage des Kandidaten. Die Kandidaten-Transkripte
liefert GPT-Live aber (`input_audio_transcription_completed`); LiveKit legt sie als
`conversation_item_added` (role=user) ab. Dieses Modul sammelt beide Seiten und ergänzt:

- jeden `agent_turn`: Input = Kandidatenaussage(n) seit dem letzten Turn, Output = Linas Antwort
- den Wurzel-Span `agent_session`: Output = ganzer Dialog (für Whole-Call-Evaluatoren)

Die Attribute werden in `on_end` gesetzt, BEVOR der Exporter den Span bekommt (Prozessor wird
vor dem BatchSpanProcessor registriert). Dasselbe Verfahren nutzt LiveKit selbst für die
PII-Filterung (Snapshot-Attribute neu binden).

Datenschutz: Inhalte nur mit LANGFUSE_INHALTE=1 und nie bei Projekt-Redaction. Telefonnummern
und Secrets werden in allen Text-Attributen des Langfuse-Exports maskiert (nicht bei LiveKit
Cloud; dafür gilt die Projekteinstellung).
"""

from __future__ import annotations

import json
import re
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from opentelemetry.sdk.trace import Event, ReadableSpan, Span, SpanProcessor

# LiveKit-Attributnamen (livekit.agents.telemetry.trace_types, 1.8.x)
ATTR_RESPONSE_TEXT = "lk.pii.response.text"
ATTR_INTERRUPTED = "lk.interrupted"
ATTR_SPEECH_ID = "lk.speech_id"
SPAN_AGENT_TURN = "agent_turn"
SPAN_SESSION = "agent_session"

LF_IN = "langfuse.observation.input"
LF_OUT = "langfuse.observation.output"
LF_TRACE_IN = "langfuse.trace.input"
LF_TRACE_OUT = "langfuse.trace.output"

ROLLE = {"user": "kandidat", "assistant": "lina"}

# --- Maskierung -----------------------------------------------------------------------------

# Telefonnummern: mit + / 00 oder führender 0, mind. 8 Ziffern. Keine Punkte als Trenner,
# damit Datumsangaben (05.11.2026) und Jahresbereiche (2018-2021) erhalten bleiben.
_TEL = re.compile(r"(?<!\w)(?<!\d\.)(?:\+|00|0)\d[\d \-/()]{5,}\d(?!\w)(?!\.\d)")
_SECRET = re.compile(
    r"\b(?:sk-lf-|pk-lf-|sk-)[A-Za-z0-9_\-]{8,}"
    r"|\bpat[A-Za-z0-9]{10,}\.[A-Za-z0-9]{20,}"
    r"|\bAPI[A-Za-z0-9]{10,}\b"
    r"|\b(?:Bearer|Basic)\s+[A-Za-z0-9+/=._\-]{16,}"
)


def _tel_ersetzen(m: re.Match[str]) -> str:
    ziffern = re.sub(r"\D", "", m.group(0))
    return "[telefon]" if len(ziffern) >= 8 else m.group(0)


def maskiraj(text: str) -> str:
    """Telefonnummern und Secrets aus Text entfernen. Gesprochene Zahlwörter erkennt das nicht."""
    if not text:
        return text
    text = _SECRET.sub("[secret]", text)
    return _TEL.sub(_tel_ersetzen, text)


def _maskiraj_vrijednost(v: Any) -> Any:
    if isinstance(v, str):
        return maskiraj(v)
    if isinstance(v, (list, tuple)):
        return type(v)(maskiraj(x) if isinstance(x, str) else x for x in v)
    return v


# --- Gesprächsverlauf -----------------------------------------------------------------------


@dataclass
class Aeusserung:
    nr: int
    rolle: str  # "kandidat" | "lina"
    text: str
    zeit: float  # Unix-Sekunden (Beginn der Äußerung, bei Kandidaten: Sprechbeginn)
    item_id: str
    unterbrochen: bool = False
    turn_zugeordnet: bool = False

    def als_dict(self) -> dict[str, Any]:
        return {
            "nr": self.nr,
            "rolle": self.rolle,
            "role": "user" if self.rolle == "kandidat" else "assistant",
            "text": self.text,
            "zeit": datetime.fromtimestamp(self.zeit, tz=timezone.utc).isoformat(),
            "unterbrochen": self.unterbrochen,
        }


class DialogProtokoll:
    """Thread-sicher; wird aus Session-Events gefüllt und vom Span-Prozessor gelesen."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._po_id: dict[str, Aeusserung] = {}
        self._zaehler = 0
        self.beendet = False
        self.abschluss: dict[str, Any] = {}

    # Eingang: ChatMessage aus `conversation_item_added`
    def dodaj(self, msg: Any) -> None:
        role = getattr(msg, "role", None)
        if role not in ROLLE:
            return
        text = (getattr(msg, "text_content", None) or "").strip()
        if not text:
            return  # leere/fehlende Transkripte nicht als Aussage zählen
        item_id = str(getattr(msg, "id", "") or f"ohne_id_{self._zaehler}")
        zeit = float(getattr(msg, "created_at", 0.0) or 0.0)
        unterbrochen = bool(getattr(msg, "interrupted", False))
        with self._lock:
            vorhanden = self._po_id.get(item_id)
            if (
                vorhanden is not None
            ):  # Upsert: späteres/finales Transkript ersetzt, keine Dublette
                vorhanden.text = text
                vorhanden.unterbrochen = vorhanden.unterbrochen or unterbrochen
                if zeit:
                    vorhanden.zeit = zeit
                return
            self._zaehler += 1
            self._po_id[item_id] = Aeusserung(
                nr=self._zaehler,
                rolle=ROLLE[role],
                text=text,
                zeit=zeit,
                item_id=item_id,
                unterbrochen=unterbrochen,
            )

    def verlauf(self) -> list[Aeusserung]:
        """Chronologisch nach Sprechbeginn; bei Gleichstand nach Eingang."""
        with self._lock:
            return sorted(self._po_id.values(), key=lambda a: (a.zeit, a.nr))

    def turn_input(self, bis: float) -> dict[str, Any]:
        """Kandidatenaussagen, die noch keinem Agent-Turn zugeordnet sind und vor `bis`
        begonnen haben (GPT-Live liefert finale Transkripte teils verspätet; die Zeit ist
        der Sprechbeginn). Werden dabei als zugeordnet markiert, also nie doppelt."""
        with self._lock:
            offen = sorted(
                (
                    a
                    for a in self._po_id.values()
                    if a.rolle == "kandidat" and not a.turn_zugeordnet and a.zeit <= bis
                ),
                key=lambda a: (a.zeit, a.nr),
            )
            for a in offen:
                a.turn_zugeordnet = True
            lina_davor = [
                a
                for a in self._po_id.values()
                if a.rolle == "lina" and a.zeit <= (offen[0].zeit if offen else bis)
            ]
        letzte_lina = (
            max(lina_davor, key=lambda a: (a.zeit, a.nr)).text if lina_davor else None
        )
        return {
            "kandidat": "\n".join(a.text for a in offen) if offen else None,
            "aeusserungen": [a.als_dict() for a in offen],
            "vorherige_lina_frage": letzte_lina,
            "hinweis": None
            if offen
            else "kein Kandidaten-Transkript vor diesem Turn (Begrüßung, Fortsetzung nach "
            "Tool-Aufruf oder fehlendes Transkript)",
        }

    def gesamt(self) -> dict[str, Any]:
        v = self.verlauf()
        return {
            "dialog": [a.als_dict() for a in v],
            "anzahl_kandidat": sum(a.rolle == "kandidat" for a in v),
            "anzahl_lina": sum(a.rolle == "lina" for a in v),
            "vollstaendig": self.beendet,
            **self.abschluss,
        }


def _json(o: Any) -> str:
    return json.dumps(o, ensure_ascii=False)


def _redaction_aktiv(attributes: Any) -> bool:
    try:
        from livekit.agents.telemetry.utils import redaction_enabled

        return bool(redaction_enabled(attributes))
    except Exception:  # API kann sich ändern: im Zweifel als aktiv behandeln
        return True


class LangfuseDialogProzessor(SpanProcessor):
    """Ergänzt agent_turn/agent_session um Input/Output und maskiert Text-Attribute.

    Muss VOR dem exportierenden BatchSpanProcessor registriert werden."""

    def __init__(self, *, inhalte: bool) -> None:
        self._inhalte = inhalte
        self.protokoll: DialogProtokoll | None = None
        self.session_input: dict[str, Any] = {}

    def binde(self, protokoll: DialogProtokoll, session_input: dict[str, Any]) -> None:
        self.protokoll = protokoll
        self.session_input = session_input

    def on_start(self, span: Span, parent_context: Any = None) -> None:
        pass

    def on_end(self, span: ReadableSpan) -> None:
        try:
            self._on_end(span)
        except Exception:  # Telemetrie darf das Gespräch nie stören
            import logging

            logging.getLogger("lina.dialog").exception(
                "Langfuse-Anreicherung fehlgeschlagen"
            )

    def _on_end(self, span: ReadableSpan) -> None:
        attrs = dict(span.attributes or {})
        if not self._inhalte or _redaction_aktiv(attrs):
            return  # keine Inhalte hinzufügen
        neu = {k: _maskiraj_vrijednost(v) for k, v in attrs.items()}
        p = self.protokoll

        if p is not None and span.name == SPAN_AGENT_TURN:
            ende = (span.end_time or 0) / 1e9
            neu[LF_IN] = _json(_maskiraj_dict(p.turn_input(ende)))
            neu[LF_OUT] = _json(
                {
                    "lina": maskiraj(str(attrs.get(ATTR_RESPONSE_TEXT, "") or ""))
                    or None,
                    "unterbrochen": bool(attrs.get(ATTR_INTERRUPTED, False)),
                }
            )
        elif p is not None and span.name == SPAN_SESSION:
            gesamt = _json(_maskiraj_dict(p.gesamt()))
            eingang = _json(self.session_input)
            neu[LF_IN] = eingang
            neu[LF_OUT] = gesamt
            neu[LF_TRACE_IN] = eingang
            neu[LF_TRACE_OUT] = gesamt

        span._attributes = neu  # wie LiveKits PII-Filter: Snapshot neu binden
        if span.events:
            span._events = tuple(
                Event(
                    e.name,
                    {
                        k: _maskiraj_vrijednost(v)
                        for k, v in (e.attributes or {}).items()
                    },
                    e.timestamp,
                )
                for e in span.events
            )

    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True


def _maskiraj_dict(o: Any) -> Any:
    if isinstance(o, dict):
        return {k: _maskiraj_dict(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_maskiraj_dict(v) for v in o]
    if isinstance(o, str):
        return maskiraj(o)
    return o
