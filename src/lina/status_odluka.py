"""Ein Status nach dem Anruf. Das Modell meldet Fakten, der Code setzt den Namen.

Nur schreiben, wenn die Karte noch in der Anruf-Schlange ist (leer, New Lead,
NE JAVLJA SE). Spätere Stapel bleiben unangetastet.
"""

from __future__ import annotations

from typing import Any

from .config import P
from .kontekst import _tekst, prazno

_PISATI = {"", "New Lead", "NE JAVLJA SE"}
_DIPLOMA = {
    "DIPLOMA",
    "SVJEDOČANSTVO 1",
    "SVJEDOČANSTVO 2",
    "SVJEDOČANSTVO 3",
    "SVJEDOČANSTVO 4",
}


def normalizuj(v: str | None) -> str:
    v = (v or "").strip().lower()
    return v if v in ("da", "ne", "nepoznato") else "nepoznato"


def odluka(
    *,
    javio_se: bool,
    zainteresiran: str,
    negativan_komentar: str,
    iskustvo_u_poslu: str,
    licni_popunjeni: bool,
    diploma: bool,
    pasos: bool,
    foto: bool,
    trenutni_status: str | None,
) -> str | None:
    trenutni = (trenutni_status or "").strip()
    if trenutni not in _PISATI:
        return None
    if not javio_se:
        novi = "NE JAVLJA SE"
    elif (
        negativan_komentar == "da"
        and zainteresiran == "ne"
        and iskustvo_u_poslu == "ne"
    ):
        novi = "Odustao"
    elif zainteresiran != "da":
        return None
    elif diploma and pasos and foto:
        novi = "Pre-casting"
    elif diploma or pasos or foto or licni_popunjeni:
        novi = "Zeleni / obrada"
    else:
        novi = "Zainteresiran"
    if novi == trenutni:
        return None
    return novi


def _oznake(polja: dict[str, Any]) -> set[str]:
    v = polja.get(P.DOKUMENTI) or []
    if isinstance(v, str):
        return {v}
    return {str(x) for x in v}


def dokumenti(polja: dict[str, Any]) -> tuple[bool, bool, bool]:
    oz = _oznake(polja)
    diploma = (not prazno(polja.get(P.SVJEDOCANSTVA))) or bool(oz & _DIPLOMA)
    pasos = (not prazno(polja.get(P.PASOS))) or "SLIKA PASOŠA" in oz
    foto = (not prazno(polja.get(P.FOTO))) or "FOTOGRAFIJA ZA CV" in oz
    return diploma, pasos, foto


def _ima(polja: dict[str, Any], podaci: dict[str, str], key: str, *fids: str) -> bool:
    if key and not prazno(podaci.get(key)):
        return True
    return any(not prazno(polja.get(fid)) for fid in fids)


def licni_popunjeni(polja: dict[str, Any], podaci: dict[str, str]) -> bool:
    """Lični podaci da, ohne Status boravka und Radna dozvola (die fragt sie nicht)."""
    return all(
        (
            _ima(polja, podaci, "", P.IME_PREZIME),
            _ima(polja, podaci, "", P.POZIVNI),
            _ima(polja, podaci, "", P.TELEFON),
            _ima(polja, podaci, "email", P.EMAIL),
            _ima(polja, podaci, "adresa", P.ADRESA, P.ULICA),
            _ima(polja, podaci, "datum_rodjenja", P.DATUM_RODJENJA_TXT, P.DATUM_RODJENJA_DATE),
            _ima(polja, podaci, "mjesto_rodjenja", P.MJESTO_RODJENJA),
            _ima(polja, podaci, "drzavljanstvo", P.DRZAVLJANSTVO),
            _ima(polja, podaci, "vozacka", P.VOZACKA),
            _ima(polja, podaci, "bracno_stanje", P.BRACNO_STANJE),
        )
    )


def trenutni_status(polja: dict[str, Any]) -> str:
    return _tekst(polja.get(P.STATUS_KANDIDATA))
