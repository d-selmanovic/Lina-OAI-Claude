"""Vertrags-Tests für Voice-Instructions (Gesprächsführung, kein LiveKit)."""

from lina.prompts import BACKEND, VOICE


def test_voice_keine_fragebogen_floskeln():
    assert "ne kao formular i ne kao spisak pitanja" in VOICE
    assert "Ne komentariši svaki odgovor" in VOICE
    for fraza in (
        "Hvala na odgovoru.",
        "Sljedeće pitanje je…",
        "Možete li mi reći…",
    ):
        assert fraza in VOICE


def test_voice_dopuna_je_orijentacija_ne_strop():
    assert "orijentacija, ne tvrdi strop" in VOICE
    assert "Već rečeno ne pitaj" in VOICE


def test_voice_nije_terapeut():
    assert "Nisi terapeut" in VOICE
    assert "ne glumiš oduševljenje" in VOICE


def test_voice_hrvatski_zabranjen():
    assert "tko→ko" in VOICE
    assert "tjedan→sedmica" in VOICE


def test_voice_jedno_pitanje():
    assert "samo JEDNO pitanje" in VOICE


def test_backend_samo_nedostajuce_polja():
    assert "Podaci koji NEDOSTAJU" in BACKEND
    assert "Never store or ask for a field" in BACKEND
    assert "sacuvaj_podatak" in BACKEND


def test_voice_cekaj_javljanje_pa_identitet():
    assert "Ne govori ništa dok on" in VOICE
    assert "Govorim li sa" in VOICE
    assert "generate_reply" not in VOICE


def test_voice_ablauf_skakanje_smalltalk():
    assert "Red na listi je orijentacija" in VOICE
    assert "Small talk smije usred razgovora" in VOICE
    assert "Ne poslije svakog posla" in VOICE
    assert "bez SSML" in VOICE
