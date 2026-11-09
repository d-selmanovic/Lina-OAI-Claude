"""Tests für das Zurückschreiben (ohne Netzwerk)."""

import asyncio
from datetime import datetime

from lina.airtable import FakeStore, Paket, napravi_zapise, sacuvaj
from lina.config import (
    OB,
    RI,
    T_DOPUNE,
    T_OBRAZOVANJE,
    T_PRIJAVE,
    T_RADNO_ISKUSTVO,
    T_TERMINI,
    TZ,
    D,
)
from lina.datumi import parse_datum
from lina.kontekst import Skola, Stanica, izracunaj
from lina.stanje import Stanje
from lina.zeit import TZ as ZONE


def _stanje():
    k = izracunaj(
        "recTEST",
        {"fldFtCLmRLempwjls": "K-0196", "fldlWTDSvVwiOZDmM": "Test"},
        [],
        [],
        [],
    )
    s = Stanje(k)
    s.podaci.update(
        {
            "status_boravka": "BiH",
            "njemacki": "Osnove (A1–A2)",
            "djeca": "Da",
            "broj_djece": "2",
        }
    )
    s.nove_stanice.append(
        Stanica(
            "Zidar",
            "Hidro",
            parse_datum("2018", kraj=False),
            parse_datum("2021", kraj=True),
        )
    )
    s.nove_skole.append(
        Skola(
            "MSŠ Bihać",
            "Bihać",
            parse_datum("2005", kraj=False),
            parse_datum("2008", kraj=True),
            smjer="Zidar",
        )
    )
    s.povratni_poziv = datetime(2026, 11, 6, 15, 0, tzinfo=ZONE)
    s.ishod = "povratni_poziv"
    return s


def test_nie_in_prijave_schreiben():
    assert T_PRIJAVE not in {t for t, r in napravi_zapise(_stanje()).items() if r}


def test_dopune_inhalt():
    dop = napravi_zapise(_stanje())[T_DOPUNE][0]
    assert dop[D.KANDIDAT] == ["recTEST"]
    assert dop[D.STATUS_PREGLEDA] == "Novo"
    assert dop[D.SIFRA] == "K-0196"
    assert dop[D.STATUS_BORAVKA] == "BiH"
    assert "Njemački – nivo" in dop[D.OPIS] and "Broj djece: 2" in dop[D.OPIS]
    assert "smjer Zidar" in dop[D.OPIS]


def test_stationen_und_schulen_als_eigene_datensaetze():
    z = napravi_zapise(_stanje())
    ri = z[T_RADNO_ISKUSTVO][0]
    assert (
        ri[RI.KANDIDAT] == ["recTEST"]
        and ri[RI.OD] == "2018-01-01"
        and ri[RI.DO] == "2021-12-31"
    )
    assert "približan" in ri[RI.OPIS]
    assert z[T_OBRAZOVANJE][0][OB.SKOLA] == "MSŠ Bihać"


def test_rueckruf_mit_zeitzone():
    t = napravi_zapise(_stanje())[T_TERMINI][0]
    assert t[TZ.DATUM] == "2026-11-06T15:00:00+01:00"
    assert t[TZ.STATUS] == "Todo"


def test_prazan_poziv_ipak_ima_log():
    from lina.config import PZ, T_POZIVI

    k = izracunaj("recPRAZAN", {"fldFtCLmRLempwjls": "K-0001"}, [], [], [])
    s = Stanje(k)
    z = napravi_zapise(s)
    assert z[T_POZIVI][0][PZ.ISHOD] == "prekinuto"
    assert z[T_POZIVI][0][PZ.KANDIDAT] == ["recPRAZAN"]
    assert z[T_DOPUNE] == []
    assert T_PRIJAVE not in z or not z.get(T_PRIJAVE)


def test_nur_einmal_speichern():
    store = FakeStore(Paket({}, [], [], []))
    s = _stanje()
    asyncio.run(sacuvaj(store, s))
    asyncio.run(sacuvaj(store, s))
    assert len(store.geschrieben[T_DOPUNE]) == 1
