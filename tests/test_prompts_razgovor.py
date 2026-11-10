"""Vertrags-Tests für Voice-Instructions (Gesprächsführung, kein LiveKit)."""

from lina.prompts import BACKEND, VOICE, VOICE_POZDRAV


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
    assert "Ne govori ništa dok on" in VOICE_POZDRAV
    assert "Govorim li sa" in VOICE_POZDRAV
    assert "generate_reply" not in VOICE
    assert "generate_reply" not in VOICE_POZDRAV
    assert "nastavi_prikupljanje" in VOICE_POZDRAV


def test_voice_ablauf_skakanje_smalltalk():
    assert "Red na listi je orijentacija" in VOICE
    assert "Small talk smije usred razgovora" in VOICE
    assert "Ne poslije svakog posla" in VOICE
    assert "bez SSML" in VOICE
    assert "predji_na_kraj" in VOICE


def _sve_voice():
    from lina import prompts

    return (
        prompts.VOICE,
        prompts.VOICE_POZDRAV,
        prompts.VOICE_KRAJ,
    )


def test_gpt_live_politike_u_svakom_voice_promptu():
    for tpl in _sve_voice():
        assert "{zajednicko}" in tpl
        assert "{delegacija}" in tpl
    from lina.prompts import _DEL_KRAJ, _DEL_PODACI, _DEL_POZDRAV, _ZAJEDNICKO

    for naslov in ("Backchannel policy:", "Interruption policy:"):
        assert naslov in _ZAJEDNICKO
    for d in (_DEL_POZDRAV, _DEL_PODACI, _DEL_KRAJ):
        assert "Delegation policy:" in d
        assert "Backend tools:" in d
        assert "Generate <|SpawnThinking|> when:" in d
        assert "Do not generate <|SpawnThinking|> when:" in d


def test_halo_ispravke_iskrenost():
    from lina.prompts import _ZAJEDNICKO

    assert "Nikad ne ponavljaj pozdrav" in _ZAJEDNICKO
    assert "ponovi NOVU vrijednost" in _ZAJEDNICKO
    assert "ja sam Lina, digitalna asistentica" in _ZAJEDNICKO
    assert "nikad ne reci da si čovjek" in _ZAJEDNICKO
    assert "Ne pogađaj" in _ZAJEDNICKO


def test_njemacki_prvi_i_ponuda_prije_iskustva():
    assert "PRVO njemački" in VOICE
    assert "Ponuda (tačka 1–3) ide UVIJEK prije pitanja o radnom iskustvu" in VOICE


def test_pozdrav_bez_iskustva_i_kratko_ponavljanje():
    from lina import prompts

    t = prompts.VOICE_POZDRAV
    assert "Nikad u pozdravu ne pitaj za iskustvo" in t
    assert "odmah nastavi_prikupljanje" in t
    assert "ne ponavljaj cijeli pozdrav" in t


def test_jezici_odvojeno():
    from lina import prompts

    assert "Nikad „njemačkog ili engleskog“ u istom pitanju" in prompts.VOICE
