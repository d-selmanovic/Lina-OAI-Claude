"""Lina 3: Versionsumschaltung, Schutzregeln im Prompt v3, Alter 45 (L1), Kinder (L2), Wissen (L6)."""

import asyncio
from datetime import datetime

import pytest

from lina import prompts, prompts_v2, verzija
from lina.agent_lina import LinaAgent
from lina.airtable import FakeStore, Paket, napravi_zapise
from lina.config import PZ, T_POZIVI
from lina.kontekst import izracunaj
from lina.stanje import Stanje
from lina.werte import dob_djece
from lina.zeit import TZ

DATUM_RODJENJA_TXT = "fld6qFZGy2q1yfcnw"


@pytest.fixture
def v3(monkeypatch):
    monkeypatch.setenv("LINA_PROMPT", "v3")


@pytest.fixture
def v2(monkeypatch):
    monkeypatch.delenv("LINA_PROMPT", raising=False)


def _agent(kandidat=None):
    k = izracunaj("recT", kandidat or {"fldQCU77iYMy8gFS8": "BiH"}, [], [], [])
    st = Stanje(k, fiksno_vrijeme=datetime(2026, 11, 11, 10, 0, tzinfo=TZ))
    store = FakeStore(Paket({}, [], [], []))
    return LinaAgent(instructions="x", stanje=st, store=store), st


def run(c):
    return asyncio.run(c)


# ---------- Versionen ----------


def test_standard_ist_v2(v2):
    assert prompts.aktivna_verzija() == "2.0.0"
    k = _agent()[1].kontekst
    assert prompts.voice(k, "x") == prompts_v2.voice(k, "x")
    assert prompts.backend(k, "x") == prompts_v2.backend(k, "x")


def test_v3_umschaltbar(v3):
    assert prompts.aktivna_verzija() == verzija.V3 == prompts.PROMPT_VERZIJA
    k = _agent()[1].kontekst
    assert prompts.voice(k, "x") != prompts_v2.voice(k, "x")


def test_v2_wissen_bleibt_eingefroren(v2):
    k = _agent()[1].kontekst
    for t in (prompts.voice(k, "x"), prompts.backend(k, "x")):
        assert "sedamnaestog i osamnaestog novembra" not in t  # jobstep.md nur in v3
        assert "vozi kamion s prikolicom" in t


# ---------- Schutzregeln v3 (wörtlich) ----------


def test_v3_schutzregeln(v3):
    k = _agent()[1].kontekst
    sve = [
        prompts.voice(k, "x"),
        prompts.voice_pozdrav(k, "x"),
        prompts.voice_kraj(k, "x"),
    ]
    for t in sve:
        assert "Nikad se ne opraštaj" in t
        assert "nikad ne reci da si čovjek" in t
        assert "<|SpawnThinking|>" in t
        assert "Nikad ne izmišljaj rezultat" in t
    for t in sve[:2]:
        assert "samo JEDNO pitanje" in t
        assert "bez SSML" in t
        assert "Ma, danas pričamo o tebi." in t
    b = prompts.backend(k, "x")
    assert "ne_zovite_vise" in b
    assert "never invent facts" in b


def test_v3_persona_ohne_digital_und_ohne_erfundenes(v3):
    k = _agent()[1].kontekst
    ko_si = prompts.voice(k, "x").split("# Jezik")[0]
    assert "digitaln" not in ko_si
    assert "Krajina" not in ko_si
    assert "Nikad ne žrtvuj tačnost" in ko_si


def test_v3_regeln_aus_dev(v3):
    t = prompts.VOICE
    assert "Takav odgovor ne predaješ pozadini" in t  # Scherz
    assert "Uvredljive ili pogrdne riječi nikad ne ponavljaš" in t
    assert "dan u sedmici, datum i sat" in t
    assert "već poslao ili napisao u prijavi" in t
    assert "Tek kad kandidat potvrdi, predaj ga pozadini" in t
    b = prompts.BACKEND
    assert "only after the voice model reports that the candidate confirmed" in b
    assert "weekday, date and time" in b


def test_v3_e3_bis_e6(v3):
    t = prompts.VOICE
    assert "četrdeset pet ili više godina" in t
    assert "Jesu li još mali" in t and "ne spominji platu" in t
    assert "Može i okvirno" in t
    assert "posao se ipak bilježi" in t
    assert "Pay: gross first; net only if" in prompts.BACKEND


def test_v3_wissen_in_allen_phasen(v3):
    """L6: auch die Abschlussphase hat das Wissen; jobstep.md wird geladen."""
    k = _agent()[1].kontekst
    for t in (
        prompts.voice(k, "x"),
        prompts.voice_pozdrav(k, "x"),
        prompts.voice_kraj(k, "x"),
        prompts.backend(k, "x"),
    ):
        assert "sedamnaestog i osamnaestog novembra" in t
        assert "Plaća firma, ne kandidat" in t
        assert "radi s ekipom na gradilištu" in t
        assert "Neto samo ako pita baš za neto" in t


# ---------- L1: Alter 45 ----------


def test_45_tool_hinweis_nur_v3(v3):
    a, _st = _agent()
    r = run(a.sacuvaj_podatak(None, "datum_rodjenja", "1979-05-01"))
    assert "KRAJ" in r and "zavrsi_razgovor (nije_zainteresiran)" in r
    a, _st = _agent()
    r = run(a.sacuvaj_podatak(None, "datum_rodjenja", "1990-05-01"))
    assert "KRAJ" not in r


def test_45_kein_hinweis_in_v2(v2):
    a, _st = _agent()
    assert "KRAJ" not in run(a.sacuvaj_podatak(None, "datum_rodjenja", "1979-05-01"))


def test_45_grenze_genau(v3):
    a, st = _agent()
    run(a.sacuvaj_podatak(None, "datum_rodjenja", "1981-11-11"))  # heute 45
    assert st.dob_iznad_granice()
    a, st = _agent()
    run(a.sacuvaj_podatak(None, "datum_rodjenja", "1981-11-12"))  # morgen 45
    assert not st.dob_iznad_granice()


def test_45_vermerk_im_sazetak(v3):
    a, st = _agent()
    run(a.sacuvaj_podatak(None, "datum_rodjenja", "1975-01-01"))
    st.ishod = "nije_zainteresiran"
    st.sazetak = "Kandidat ima 51 godinu."
    poziv = napravi_zapise(st)[T_POZIVI][0]
    assert poziv[PZ.SAZETAK].startswith("Dob 45+ – ne ispunjava uslov. ")
    assert poziv[PZ.ISHOD] == "nije_zainteresiran"


def test_45_kein_vermerk_bei_anderem_ishod(v3):
    a, st = _agent()
    run(a.sacuvaj_podatak(None, "datum_rodjenja", "1975-01-01"))
    st.ishod = "povratni_poziv"
    st.sazetak = "Rückruf."
    assert napravi_zapise(st)[T_POZIVI][0][PZ.SAZETAK] == "Rückruf."


def test_45_aus_kontekst(v3):
    k = izracunaj("recT", {DATUM_RODJENJA_TXT: "01.01.1975"}, [], [], [])
    if k.datum_rodjenja is None:
        pytest.skip("Geburtsdatum-Feld im Kontext anders abgebildet")
    assert "četrdeset pet ili više" in k.za_instrukcije()


# ---------- L2: Kinder ----------


@pytest.mark.parametrize(
    ("ein", "aus"),
    [
        ("mala", "mala"),
        ("mali", "mala"),
        ("veći", "veća"),
        ("Mala i veća", "mala i veća"),
        ("4, 9", "4, 9"),
    ],
)
def test_dob_djece_text_oder_zahl(ein, aus):
    assert dob_djece(ein) == (aus, None)


def test_dob_djece_unsinn_abgelehnt():
    w, greska = dob_djece("ne znam")
    assert w is None and "mala" in greska


def test_dob_djece_text_ueberspringt_l9():
    a, st = _agent()
    assert "Sačuvano" in run(a.sacuvaj_podatak(None, "dob_djece", "mala"))
    assert st.dob_djece() == []  # L9 prüft nur Zahlen


# ---------- E6: Station ohne Jahr ----------


def test_station_ohne_jahr_wird_gespeichert():
    a, st = _agent()
    r = run(a.dodaj_radno_mjesto(None, "Vozač", "Prevoz d.o.o.", ""))
    assert "Nije sačuvano" not in r
    assert len(st.nove_stanice) == 1
