"""Unit-Tests für die Kernlogik (ohne Netzwerk, ohne LiveKit)."""

from datetime import date

from lina.config import DOPUNE_ODBACENO, RI, D, P
from lina.datumi import parse_datum
from lina.kontekst import Skola, Stanica, izracunaj, prazno
from lina.plausibilitaet import provjeri
from lina.werte import normalisiere

DANAS = date(2026, 11, 5)


def st(od, do, aktuelno=False, poz="Zidar", firma="X"):
    return Stanica(
        poz,
        firma,
        parse_datum(od, kraj=False),
        parse_datum(do, kraj=True) if do else None,
        aktuelno,
    )


def regeln(nalazi):
    return sorted({n.pravilo for n in nalazi})


# ---------- leer / nur wenn leer ----------


def test_prazno():
    for v in (None, "", "  ", "-", "?", [], {}):
        assert prazno(v)
    for v in ("BiH", "0", ["x"], 0, False):
        assert not prazno(v)


def test_nur_leere_felder_werden_gefragt():
    k = izracunaj(
        "rec1", {P.IME: "Amir", P.DRZAVLJANSTVO: "BiH", P.VOZACKA: "  "}, [], [], []
    )
    assert "drzavljanstvo" not in k.nedostaje
    assert "vozacka" in k.nedostaje  # nur Leerzeichen = leer


def test_offene_dopune_zaehlt_als_vorhanden():
    dop = [{D.STATUS_PREGLEDA: "Novo", D.STATUS_BORAVKA: "BiH"}]
    k = izracunaj("rec1", {}, dop, [], [])
    assert "status_boravka" not in k.nedostaje


def test_verworfene_dopune_zaehlt_nicht():
    dop = [{D.STATUS_PREGLEDA: DOPUNE_ODBACENO, D.RADNA_DOZVOLA: "Nema"}]
    k = izracunaj("rec1", {}, dop, [], [])
    assert "radna_dozvola" in k.nedostaje
    assert "status_boravka" not in k.nedostaje


def test_erfahrung_vorhanden_wird_nicht_erneut_gefragt():
    ri = [
        {
            RI.POZICIJA: "Zidar",
            RI.POSLODAVAC: "Hidro",
            RI.OD: "2018-04-01",
            RI.DO: "2021-10-31",
        }
    ]
    k = izracunaj("rec1", {}, [], ri, [])
    assert "radno_iskustvo" not in k.nedostaje
    assert "Zidar" in k.za_instrukcije()


def test_flaches_altfeld_zaehlt_als_vorhanden():
    k = izracunaj(
        "rec1", {P.RADNO_MJESTO: "Zidar", P.SKOLA_TXT: "MSŠ Bihać"}, [], [], []
    )
    assert "radno_iskustvo" not in k.nedostaje
    assert "obrazovanje" not in k.nedostaje


def test_alles_vorhanden_nichts_fehlt_text():
    k = izracunaj("rec1", {}, [], [], [])
    k.nedostaje = []
    assert "ništa" in k.za_instrukcije()


# ---------- Werte ----------


def test_werte():
    assert normalisiere("vozacka", "b, ce, C") == ("B, C, CE", None)
    assert normalisiere("vozacka", "kamion")[0] is None
    assert normalisiere("status_boravka", "eu - Njemačka") == ("EU – Njemačka", None)
    assert normalisiere("drzavljanstvo", "bih, hrvatska") == ("BiH, Hrvatska", None)
    assert normalisiere("njemacki", "osnove (a1–a2)") == ("Osnove (A1–A2)", None)
    assert normalisiere("datum_rodjenja", "1990-03-15") == ("15.03.1990", None)
    assert normalisiere("datum_rodjenja", "1990")[0] is None
    assert normalisiere("email", "Amir@Gmail.com") == ("amir@gmail.com", None)
    assert normalisiere("dob_djece", "4, 9") == ("4, 9", None)
    assert normalisiere("nepostojece", "x")[0] is None


def test_datum_parsing():
    assert parse_datum("2015", kraj=True).datum == date(2015, 12, 31)
    assert parse_datum("2015-02", kraj=True).datum == date(2015, 2, 28)
    assert parse_datum("15.03.1990", kraj=False).datum == date(1990, 3, 15)
    assert parse_datum("unsinn", kraj=False) is None


# ---------- Plausibilität ----------


def test_l1_ueberschneidung_beispiel_denis():
    n = provjeri(
        [st("2010", "2015"), st("2013", "2017", firma="Y")], [], None, [], DANAS
    )
    assert "L1" in regeln(n)


def test_l1_jahresgrenze_ist_kein_fehler():
    n = provjeri(
        [st("2010", "2015"), st("2015", "2017", firma="Y")], [], None, [], DANAS
    )
    assert "L1" not in regeln(n)


def test_l2_l3_l7():
    n = provjeri(
        [
            st("2018", "2015"),
            st("2025-01", "2027-06", firma="Y"),
            st("2020", "2022", aktuelno=True, firma="Z"),
        ],
        [],
        None,
        [],
        DANAS,
    )
    assert {"L2", "L3", "L7"} <= set(regeln(n))


def test_l4_l6_l9():
    rodjen = parse_datum("2000-01-01", kraj=False)
    n = provjeri([st("2012", "2016")], [], rodjen, [15], DANAS)
    assert {"L4", "L9"} <= set(regeln(n))
    n2 = provjeri([st("1990", "2026-10")], [], rodjen, [], DANAS)
    assert "L6" in regeln(n2)


def test_l5_l8_l10():
    sk = Skola(
        "MSŠ", "Bihać", parse_datum("2005", kraj=False), parse_datum("2009", kraj=True)
    )
    n = provjeri(
        [st("2006", "2010"), st("2013", "2016", firma="Y")], [sk], None, [], DANAS
    )
    assert {"L5", "L8"} <= set(regeln(n))
    rodjen = parse_datum("2000-01-01", kraj=False)
    sk2 = Skola(
        "OŠ", "Bihać", parse_datum("2003", kraj=False), parse_datum("2001", kraj=True)
    )
    assert "L10" in regeln(provjeri([], [sk2], rodjen, [], DANAS))


def test_sauberer_lebenslauf_ohne_befund():
    rodjen = parse_datum("1990-03-15", kraj=False)
    sk = Skola(
        "MSŠ", "Bihać", parse_datum("2005", kraj=False), parse_datum("2008", kraj=True)
    )
    n = provjeri(
        [st("2009", "2014"), st("2015", None, aktuelno=True, firma="Y")],
        [sk],
        rodjen,
        [4, 9],
        DANAS,
    )
    assert n == []


def test_schluessel_sind_stabil():
    a = provjeri(
        [st("2010", "2015"), st("2013", "2017", firma="Y")], [], None, [], DANAS
    )
    b = provjeri(
        [st("2010", "2015"), st("2013", "2017", firma="Y")], [], None, [], DANAS
    )
    assert [x.kljuc for x in a] == [x.kljuc for x in b]
