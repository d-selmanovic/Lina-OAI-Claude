"""Gesprächsende ohne zavrsi_razgovor: Ergebnis aus dem Zustand ableiten."""

from datetime import datetime

from lina.kontekst import izracunaj
from lina.stanje import Stanje
from lina.zeit import TZ


def _st() -> Stanje:
    k = izracunaj("recT", {"fldQCU77iYMy8gFS8": "BiH"}, [], [], [])
    return Stanje(k, fiksno_vrijeme=datetime(2026, 11, 10, 15, 0, tzinfo=TZ))


def test_ohne_daten_prekinuto():
    assert _st().ishod_bez_kraja() == "prekinuto"


def test_mit_daten_djelimicno():
    st = _st()
    st.podaci["broj_djece"] = "3"
    assert st.ishod_bez_kraja() == "djelimicno"


def test_rueckruf_hat_vorrang():
    st = _st()
    st.podaci["broj_djece"] = "3"
    st.povratni_poziv = datetime(2026, 11, 10, 19, 0, tzinfo=TZ)
    assert st.ishod_bez_kraja() == "povratni_poziv"
