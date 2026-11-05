"""Tools direkt aufrufen (ohne LiveKit-Session, ohne Netzwerk)."""

import asyncio
from datetime import datetime

from lina.agent_lina import LinaAgent
from lina.airtable import FakeStore, Paket
from lina.config import T_DOPUNE, T_RADNO_ISKUSTVO
from lina.kontekst import izracunaj
from lina.stanje import Stanje
from lina.zeit import TZ


def _agent():
    k = izracunaj("recT", {"fldQCU77iYMy8gFS8": "BiH"}, [], [], [])
    st = Stanje(k, fiksno_vrijeme=datetime(2026, 11, 5, 10, 0, tzinfo=TZ))
    store = FakeStore(Paket({}, [], [], []))
    return LinaAgent(instructions="x", stanje=st, store=store), st, store


def run(c):
    return asyncio.run(c)


def test_ablauf_mit_ueberschneidung_und_speichern():
    a, _st, store = _agent()
    assert "Sačuvano" in run(a.sacuvaj_podatak(None, "vozacka", "b, ce"))
    assert "Nije sačuvano" in run(a.sacuvaj_podatak(None, "vozacka", "kamion"))
    run(a.dodaj_radno_mjesto(None, "Zidar", "A", "2010", "2015"))
    run(a.dodaj_radno_mjesto(None, "Zidar", "B", "2013", "2017", grad=None))
    r1 = run(a.provjeri_podatke(None))
    assert "L1:r1-r2" in r1
    r2 = run(a.provjeri_podatke(None))
    assert "logično" in r2  # dieselbe Auffälligkeit nicht nochmal
    run(a.zabiljezi_objasnjenje(None, "L1:r1-r2", "paralelno, vikendom"))
    assert "Sačuvano" in run(a.zavrsi_razgovor(None, "zavrseno", "Sve prikupljeno."))
    assert len(store.geschrieben[T_RADNO_ISKUSTVO]) == 2
    assert "paralelno" in store.geschrieben[T_DOPUNE][0]["fldejrE05pgkiVOY1"]


def test_korrektur_erlaubt_neue_rueckfrage():
    a, _st, _ = _agent()
    run(a.dodaj_radno_mjesto(None, "Zidar", "A", "2018", "2015"))
    assert "L2" in run(a.provjeri_podatke(None))
    run(a.ispravi_radno_mjesto(None, 1, "do", "2021"))
    assert "logično" in run(a.provjeri_podatke(None))


def test_rueckruf_nicht_in_vergangenheit():
    a, st, _ = _agent()
    assert "prošlosti" in run(a.zakazi_povratni_poziv(None, "2026-11-04T10:00"))
    assert "sačuvan" in run(a.zakazi_povratni_poziv(None, "2026-11-06T15:00", None))
    assert st.povratni_poziv.isoformat() == "2026-11-06T15:00:00+01:00"


def test_uhrzeit_sarajevo():
    a, _, _ = _agent()
    assert "četvrtak, 5. novembar 2026, 10:00" in run(a.trenutno_vrijeme(None))


def test_endzustand_pruefung():
    from lina.simulacija import razlike

    a, st, _ = _agent()
    run(a.sacuvaj_podatak(None, "status_boravka", "BiH"))
    assert (
        razlike(
            st, {"sacuvano": ["status_boravka"], "nije_sacuvano": ["drzavljanstvo"]}
        )
        == []
    )
    assert razlike(st, {"sacuvano": ["engleski"]})  # fehlt → Fehler
    run(a.sacuvaj_podatak(None, "drzavljanstvo", "BiH"))
    assert razlike(st, {"nije_sacuvano": ["drzavljanstvo"]})  # doppelt erfasst → Fehler


def test_langfuse_ohne_keys_aus(monkeypatch):
    from lina.telemetrie import setup_langfuse

    for k in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_BASE_URL"):
        monkeypatch.delenv(k, raising=False)
    assert setup_langfuse() is None


def test_langfuse_mit_keys_ohne_inhalte(monkeypatch):
    from lina import telemetrie

    gesehen = {}
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-lf-test")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-lf-test")
    monkeypatch.setenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
    monkeypatch.delenv("LANGFUSE_INHALTE", raising=False)
    import livekit.agents.telemetry as t

    monkeypatch.setattr(t, "set_tracer_provider", lambda p, **kw: gesehen.update(kw))
    assert telemetrie.setup_langfuse({"x": "y"}) is not None
    assert gesehen["allow_pii"] is False
