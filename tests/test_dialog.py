"""Dialog-Protokoll und Langfuse-Anreicherung (ohne Netzwerk, In-Memory-Exporter)."""

import json
import time
from dataclasses import dataclass

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from lina.dialog import (
    LF_IN,
    LF_OUT,
    LF_TRACE_OUT,
    DialogProtokoll,
    LangfuseDialogProzessor,
    maskiraj,
)


@dataclass
class Msg:
    role: str
    text_content: str | None
    id: str
    created_at: float
    interrupted: bool = False


def _setup(inhalte=True):
    exp = InMemorySpanExporter()
    tp = TracerProvider()
    proz = LangfuseDialogProzessor(inhalte=inhalte)
    tp.add_span_processor(proz)
    tp.add_span_processor(SimpleSpanProcessor(exp))
    p = DialogProtokoll()
    proz.binde(p, {"record_id": "recX"})
    return tp.get_tracer("t"), p, exp


def _attrs(exp, name):
    return [dict(s.attributes) for s in exp.get_finished_spans() if s.name == name]


def test_maskierung():
    assert maskiraj("zovi me na +387 63 558 550 molim") == "zovi me na [telefon] molim"
    assert maskiraj("063/558-550") == "[telefon]"
    assert maskiraj("broj je 063 558 550.") == "broj je [telefon]."
    assert maskiraj("Termin 05.11.2026 u 10") == "Termin 05.11.2026 u 10"
    assert maskiraj("od 2018-2021 u firmi") == "od 2018-2021 u firmi"
    assert maskiraj("rođen 05.11.1990") == "rođen 05.11.1990"
    assert maskiraj("key sk-lf-abcdef123456 ok") == "key [secret] ok"
    assert "patAbc" not in maskiraj("patAbcdefghij1234.0123456789abcdef0123456789")


def test_reihenfolge_dedupe_und_spaete_transkripte():
    p = DialogProtokoll()
    t = 1000.0
    p.dodaj(Msg("assistant", "Zdravo, ovdje Lina.", "a1", t))
    # Kandidat beginnt bei t+3, finales Transkript kommt erst nach Linas nächster Antwort
    p.dodaj(Msg("assistant", "Odlično.", "a2", t + 6))
    p.dodaj(Msg("user", "Da, imam", "u1", t + 3))
    p.dodaj(Msg("user", "Da, imam vremena.", "u1", t + 3))  # Upsert, keine Dublette
    p.dodaj(Msg("user", "   ", "u2", t + 7))  # leeres Transkript ignorieren
    p.dodaj(Msg("system", "x", "s1", t))  # andere Rollen ignorieren
    v = p.verlauf()
    assert [(a.rolle, a.text) for a in v] == [
        ("lina", "Zdravo, ovdje Lina."),
        ("kandidat", "Da, imam vremena."),
        ("lina", "Odlično."),
    ]


def test_agent_turn_input_output_und_session_output():
    tr, p, exp = _setup()
    t0 = time.time() - 100  # Sprechbeginn liegt immer vor dem Ende des Turns
    with tr.start_as_current_span("agent_session") as root:
        with tr.start_as_current_span("agent_turn") as s:  # Begrüßung
            s.set_attribute("lk.pii.response.text", "Zdravo, imaš li par minuta?")
            p.dodaj(Msg("assistant", "Zdravo, imaš li par minuta?", "a1", t0))
        # Kandidat spricht zwei Sätze hintereinander
        p.dodaj(Msg("user", "Da.", "u1", t0 + 1))
        p.dodaj(Msg("user", "Imam vremena, zovi me na 063 558 550.", "u2", t0 + 1.5))
        with tr.start_as_current_span("agent_turn") as s:
            s.set_attribute("lk.pii.response.text", "Odlično. Gdje radiš?")
            s.set_attribute("lk.interrupted", True)
            p.dodaj(
                Msg("assistant", "Odlično. Gdje radiš?", "a2", t0 + 2, interrupted=True)
            )
        p.beendet = True
        p.abschluss = {"ishod": "prekinuto"}
        root.set_attribute("x", 1)

    turns = _attrs(exp, "agent_turn")
    assert len(turns) == 2
    gruss_in = json.loads(turns[0][LF_IN])
    assert gruss_in["kandidat"] is None and gruss_in["hinweis"]
    zweit_in = json.loads(turns[1][LF_IN])
    assert zweit_in["kandidat"] == "Da.\nImam vremena, zovi me na [telefon]."
    assert zweit_in["vorherige_lina_frage"] == "Zdravo, imaš li par minuta?"
    out = json.loads(turns[1][LF_OUT])
    assert out == {"lina": "Odlično. Gdje radiš?", "unterbrochen": True}

    sess = _attrs(exp, "agent_session")[0]
    gesamt = json.loads(sess[LF_OUT])
    assert sess[LF_TRACE_OUT] == sess[LF_OUT]
    assert [d["rolle"] for d in gesamt["dialog"]] == [
        "lina",
        "kandidat",
        "kandidat",
        "lina",
    ]
    assert [d["role"] for d in gesamt["dialog"]][:2] == ["assistant", "user"]
    assert gesamt["vollstaendig"] is True and gesamt["ishod"] == "prekinuto"
    assert "063" not in sess[LF_OUT]


def test_kandidat_nie_doppelt_zugeordnet():
    p = DialogProtokoll()
    p.dodaj(Msg("user", "Zidar.", "u1", 10.0))
    assert p.turn_input(20.0)["kandidat"] == "Zidar."
    assert p.turn_input(30.0)["kandidat"] is None


def test_ohne_inhalte_keine_ergaenzung():
    tr, p, exp = _setup(inhalte=False)
    p.dodaj(Msg("user", "Tajna", "u1", time.time()))
    with tr.start_as_current_span("agent_turn") as s:
        s.set_attribute("lk.pii.response.text", "x")
    a = _attrs(exp, "agent_turn")[0]
    assert LF_IN not in a and LF_OUT not in a


def test_fehler_in_anreicherung_stoert_nicht():
    tr, p, exp = _setup()
    p.turn_input = None  # erzwingt Ausnahme im Prozessor
    with tr.start_as_current_span("agent_turn"):
        pass
    assert len(_attrs(exp, "agent_turn")) == 1


def test_version_aus_pyproject():
    from lina.telemetrie import lina_version

    v = lina_version()
    assert v != "unbekannt" and v.count(".") == 2
