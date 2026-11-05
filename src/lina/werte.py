"""Erlaubte Werte je Feld (Auswahl statt Freitext). Quelle: docs/feldwerte.md.

Jede `normalisiere_*`-Funktion gibt (wert, fehler) zurück: genau eines ist None.
Der Fehlertext geht an das Backend-Modell, damit es beim Kandidaten nachfragt.
"""

from __future__ import annotations

import re

from .datumi import parse_datum

DRZAVE = (
    "BiH",
    "Srbija",
    "Hrvatska",
    "Crna Gora",
    "Sjeverna Makedonija",
    "Kosovo",
    "Albanija",
    "Slovenija",
)
DRZAVE_RAD = (*DRZAVE, "Njemačka", "Austrija", "Švicarska")
VOZACKE = (
    "AM",
    "A1",
    "A2",
    "A",
    "B",
    "BE",
    "C1",
    "C1E",
    "C",
    "CE",
    "D1",
    "D1E",
    "D",
    "DE",
    "F",
    "G",
    "M",
)
BRACNO_STANJE = (
    "Neoženjen/Neudata",
    "Oženjen/Udata",
    "Vanbračna zajednica",
    "Razveden/Razvedena",
    "Udovac/Udovica",
)
JEZIK_NIVO = ("Nema", "Osnove (A1–A2)", "Srednje (B1–B2)", "Napredno (C1–C2)")
STEPEN_OBRAZOVANJA = (
    "Osnovna škola",
    "Srednja – 3 godine (KV)",
    "Srednja – 4 godine",
    "Viša/Fakultet",
    "Kurs/obuka",
)
DA_NE = ("Da", "Ne")

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
_DRUGO = re.compile(r"^Drugo\s*[–-]\s*(.+)$", re.IGNORECASE)

Rez = tuple[str | None, str | None]


def _iz_liste(v: str, dozvoljeno: tuple[str, ...]) -> str | None:
    for d in dozvoljeno:
        if v.strip().casefold() == d.casefold():
            return d
    return None


def _drugo(v: str) -> str | None:
    m = _DRUGO.match(v.strip())
    return f"Drugo – {m.group(1).strip()}" if m and m.group(1).strip() else None


def status_boravka(v: str) -> Rez:
    v = v.strip()
    if v.casefold() == "bih":
        return "BiH", None
    m = re.match(r"^EU\s*[–-]\s*(.+)$", v, re.IGNORECASE)
    if m and m.group(1).strip():
        return f"EU – {m.group(1).strip()}", None
    if d := _drugo(v):
        return d, None
    return None, "Dozvoljeno: 'BiH', 'EU – <država>' ili 'Drugo – <država>'."


def radna_dozvola(v: str) -> Rez:
    v = v.strip()
    if v.casefold() == "nema":
        return "Nema", None
    m = re.match(r"^Da\s*[–-]\s*(.+)$", v, re.IGNORECASE)
    if m and m.group(1).strip():
        return f"Da – {m.group(1).strip()}", None
    return None, "Dozvoljeno: 'Nema', 'Da – EU', 'Da – Njemačka' ili 'Da – <država>'."


def vozacka(v: str) -> Rez:
    if v.strip().casefold() == "nema":
        return "Nema", None
    kat = [k.strip().upper() for k in re.split(r"[,\s]+", v) if k.strip()]
    nepoznate = [k for k in kat if k not in VOZACKE]
    if not kat or nepoznate:
        return (
            None,
            f"Nepoznate kategorije {nepoznate}. Dozvoljeno: {', '.join(VOZACKE)} ili 'Nema'.",
        )
    return ", ".join(sorted(set(kat), key=VOZACKE.index)), None


def drzavljanstvo(v: str) -> Rez:
    if d := _drugo(v):
        return d, None
    dijelovi = [x.strip() for x in v.split(",") if x.strip()]
    rez = [_iz_liste(x, DRZAVE) for x in dijelovi]
    if not dijelovi or None in rez:
        return (
            None,
            f"Dozvoljeno: jedna ili više od {', '.join(DRZAVE)} (odvojeno zarezom) ili 'Drugo – <država>'.",
        )
    return ", ".join(r for r in rez if r), None


def enum(v: str, dozvoljeno: tuple[str, ...]) -> Rez:
    r = _iz_liste(v, dozvoljeno)
    return (r, None) if r else (None, f"Dozvoljeno: {' | '.join(dozvoljeno)}.")


def email(v: str) -> Rez:
    v = v.strip().lower()
    return (
        (v, None)
        if _EMAIL.match(v)
        else (
            None,
            "Neispravan e-mail. Zamoli kandidata da ga spelluje slovo po slovo.",
        )
    )


def datum_rodjenja(v: str) -> Rez:
    d = parse_datum(v, kraj=False)
    if d is None or d.approx:
        return None, "Treba tačan datum (dan, mjesec, godina), format YYYY-MM-DD."
    return d.datum.strftime("%d.%m.%Y"), None


def tekst(v: str) -> Rez:
    v = " ".join(v.split())
    return (v, None) if v else (None, "Vrijednost je prazna.")


def broj_djece(v: str) -> Rez:
    return (
        (v.strip(), None)
        if v.strip().isdigit() and int(v) >= 1
        else (None, "Broj djece mora biti cijeli broj ≥ 1.")
    )


def dob_djece(v: str) -> Rez:
    dob = [x.strip() for x in v.split(",") if x.strip()]
    if not dob or not all(x.isdigit() and int(x) < 60 for x in dob):
        return None, "Godine djece kao brojevi odvojeni zarezom, npr. '4, 9'."
    return ", ".join(dob), None


VALIDATORI = {
    "status_boravka": status_boravka,
    "radna_dozvola": radna_dozvola,
    "vozacka": vozacka,
    "drzavljanstvo": drzavljanstvo,
    "bracno_stanje": lambda v: enum(v, BRACNO_STANJE),
    "njemacki": lambda v: enum(v, JEZIK_NIVO),
    "engleski": lambda v: enum(v, JEZIK_NIVO),
    "djeca": lambda v: enum(v, DA_NE),
    "broj_djece": broj_djece,
    "dob_djece": dob_djece,
    "email": email,
    "datum_rodjenja": datum_rodjenja,
    "mjesto_rodjenja": tekst,
    "adresa": tekst,
    "vjestine": tekst,
}


def normalisiere(polje: str, vrijednost: str) -> Rez:
    fn = VALIDATORI.get(polje)
    if fn is None:
        return None, f"Nepoznato polje '{polje}'."
    return fn(vrijednost or "")
