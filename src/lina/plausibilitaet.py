"""Plausibilitätsprüfung L1–L10 (docs/plausibilitaet.md).

Reine Funktionen: Der Code prüft, das Modell fragt nur nach. Jede Auffälligkeit hat
einen stabilen Schlüssel, damit Lina pro Auffälligkeit genau einmal nachfragt.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .datumi import Datum
from .kontekst import Skola, Stanica

TOLERANZ_APPROX = (
    366  # Tage: Bei Jahresangaben sind Überschneidungen ≤ 1 Jahr unauffällig
)
TOLERANZ_GENAU = 31


@dataclass(frozen=True)
class Nalaz:
    pravilo: str
    kljuc: str  # stabil, für „nur einmal fragen“
    tekst: str  # bosnisch, wird dem Modell gegeben


def _dodaj_godine(d: date, godine: int) -> date:
    try:
        return d.replace(year=d.year + godine)
    except ValueError:  # 29.02.
        return d.replace(year=d.year + godine, day=28)


def _kraj(s: Stanica, danas: date) -> date | None:
    if s.aktuelno and s.do is None:
        return danas
    return s.do.datum if s.do else None


def _preklapanje(a0: date, a1: date, b0: date, b1: date) -> int:
    return max(0, (min(a1, b1) - max(a0, b0)).days)


def _approx(*ds: Datum | None) -> bool:
    return any(d is not None and d.approx for d in ds)


def provjeri(
    stanice: list[Stanica],
    skole: list[Skola],
    datum_rodjenja: Datum | None,
    dob_djece: list[int],
    danas: date,
) -> list[Nalaz]:
    n: list[Nalaz] = []
    rodjen = datum_rodjenja.datum if datum_rodjenja else None

    for i, s in enumerate(stanice, 1):
        ime = s.kratko()
        if s.od and s.do and s.do.datum < s.od.datum:
            n.append(
                Nalaz("L2", f"L2:r{i}", f"Kod posla '{ime}' je kraj prije početka.")
            )
        for d, naziv in ((s.od, "početak"), (s.do, "kraj")):
            if d and d.datum > danas and not (d.approx and d.datum.year == danas.year):
                n.append(
                    Nalaz(
                        "L3",
                        f"L3:r{i}:{naziv}",
                        f"Kod posla '{ime}' je {naziv} u budućnosti.",
                    )
                )
        if rodjen and s.od and s.od.datum < _dodaj_godine(rodjen, 15):
            n.append(
                Nalaz(
                    "L4", f"L4:r{i}", f"Posao '{ime}' počinje prije 15. godine života."
                )
            )
        if s.aktuelno and s.do and s.do.datum < danas:
            n.append(
                Nalaz(
                    "L7",
                    f"L7:r{i}",
                    f"Posao '{ime}' je označen kao aktuelan, a ima datum kraja.",
                )
            )

    # L1 Überschneidung von Jobs, L8 Lücken
    perioda = [
        (i, s, s.od.datum, _kraj(s, danas))
        for i, s in enumerate(stanice, 1)
        if s.od and _kraj(s, danas) and _kraj(s, danas) >= s.od.datum
    ]
    for a in range(len(perioda)):
        for b in range(a + 1, len(perioda)):
            i, s, a0, a1 = perioda[a]
            j, t, b0, b1 = perioda[b]
            tol = TOLERANZ_APPROX if _approx(s.od, s.do, t.od, t.do) else TOLERANZ_GENAU
            if _preklapanje(a0, a1, b0, b1) > tol:
                n.append(
                    Nalaz(
                        "L1",
                        f"L1:r{min(i, j)}-r{max(i, j)}",
                        f"Poslovi '{s.kratko()}' i '{t.kratko()}' se vremenski preklapaju.",
                    )
                )
    po_redu = sorted(perioda, key=lambda x: x[2])
    for (i, s, _a0, a1), (j, t, b0, _b1) in zip(po_redu, po_redu[1:]):
        tol = 365 + (TOLERANZ_APPROX if _approx(s.do, t.od) else 0)
        if (b0 - a1).days > tol:
            n.append(
                Nalaz(
                    "L8",
                    f"L8:r{i}-r{j}",
                    f"Između '{s.kratko()}' i '{t.kratko()}' je pauza duža od 12 mjeseci.",
                )
            )

    # L6 mehr Erfahrung als möglich (Vereinigung der Zeiträume)
    if rodjen and perioda:
        dani, kraj_do = 0, None
        for _i, _s, p0, p1 in po_redu:
            if kraj_do is None or p0 > kraj_do:
                dani += (p1 - p0).days
                kraj_do = p1
            elif p1 > kraj_do:
                dani += (p1 - kraj_do).days
                kraj_do = p1
        moguce = (danas - _dodaj_godine(rodjen, 15)).days
        if moguce >= 0 and dani > moguce + TOLERANZ_APPROX:
            n.append(
                Nalaz(
                    "L6",
                    "L6",
                    "Ukupno radno iskustvo je duže nego što je moguće prema godinama.",
                )
            )

    # L5 Schule und Job parallel, L10 Schule
    for k, sk in enumerate(skole, 1):
        if sk.od and sk.do and sk.do.datum < sk.od.datum:
            n.append(
                Nalaz(
                    "L10",
                    f"L10:s{k}:kraj",
                    f"Kod škole '{sk.kratko()}' je kraj prije početka.",
                )
            )
        if rodjen and sk.od and sk.od.datum < _dodaj_godine(rodjen, 6):
            n.append(
                Nalaz(
                    "L10",
                    f"L10:s{k}:dob",
                    f"Škola '{sk.kratko()}' počinje prije 6. godine života.",
                )
            )
        if not (sk.od and sk.do) or sk.do.datum < sk.od.datum:
            continue
        for i, s, p0, p1 in perioda:
            tol = TOLERANZ_APPROX if _approx(sk.od, sk.do, s.od, s.do) else 183
            if _preklapanje(sk.od.datum, sk.do.datum, p0, p1) > tol:
                n.append(
                    Nalaz(
                        "L5",
                        f"L5:s{k}-r{i}",
                        f"Škola '{sk.kratko()}' i posao '{s.kratko()}' su u isto vrijeme.",
                    )
                )

    # L9 Kinder
    if rodjen:
        godine = (danas - rodjen).days // 365
        for d in dob_djece:
            if d > godine - 15:
                n.append(
                    Nalaz(
                        "L9",
                        f"L9:{d}",
                        f"Dijete od {d} godina nije logično uz godine kandidata ({godine}).",
                    )
                )

    return n
