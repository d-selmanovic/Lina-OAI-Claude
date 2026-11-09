"""Govorne provjere: škola, preklapanje, tvrdnja van liste."""

from lina.datumi import parse_datum
from lina.govor import obavezno_pitanje
from lina.kontekst import Stanica


def st(od, do, poz="Prodavac", firma="JYSK"):
    return Stanica(poz, firma, parse_datum(od, kraj=False), parse_datum(do, kraj=True))


def test_lazna_skola_kad_je_pitala():
    q = obavezno_pitanje(
        "Ciganska mahala",
        "U koju školu si išao?",
        [],
        [],
        set(),
    )
    assert "škola" in q
    assert "Ciganska mahala" in q


def test_prava_skola_ne_pita():
    q = obavezno_pitanje(
        "Elektrotehnička srednja škola",
        "U koju školu si išao?",
        [],
        [],
        set(),
    )
    assert q == ""


def test_preklapanje_sa_starim_poslom():
    q = obavezno_pitanje(
        "Radio sam od 2016 do 2018 u drugoj firmi",
        "Reci posao.",
        [st("2014", "2020", poz="Mjerio vodu", firma="Vodovod")],
        [],
        set(),
    )
    assert "preklapaju" in q
    assert "Vodovod" in q


def test_granicna_godina_nije_preklapanje():
    q = obavezno_pitanje(
        "Od 2021 do 2023",
        "",
        [st("2014", "2020")],
        [],
        set(),
    )
    assert q == ""


def test_masine_nisu_u_prijavi():
    q = obavezno_pitanje(
        "Radio sam na mašinama",
        "Koja pozicija?",
        [st("2015", "2017")],
        ["Prodavac, JYSK"],
        set(),
    )
    assert "nisi naveo" in q


def test_prodavac_je_u_prijavi():
    q = obavezno_pitanje(
        "Radio sam kao prodavac",
        "",
        [st("2015", "2017", poz="Prodavac")],
        [],
        set(),
    )
    assert q == ""
