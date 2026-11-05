"""Datumsangaben des Kandidaten parsen. Ungefähre Angaben (nur Jahr) werden markiert."""

from __future__ import annotations

import calendar
import re
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Datum:
    datum: date
    approx: bool  # True, wenn Tag (und evtl. Monat) nicht genannt wurden


def parse_datum(v: str | None, *, kraj: bool) -> Datum | None:
    """Akzeptiert YYYY, YYYY-MM, YYYY-MM-DD, DD.MM.YYYY, MM.YYYY.

    `kraj=True` füllt fehlende Teile zum Ende des Zeitraums auf (31.12. bzw. Monatsende),
    sonst zum Anfang (01.01. bzw. Monatsanfang).
    """
    if v is None:
        return None
    s = str(v).strip().rstrip(".")
    try:
        if m := re.fullmatch(r"(\d{4})", s):
            y = int(m.group(1))
            return Datum(date(y, 12, 31) if kraj else date(y, 1, 1), True)
        if m := re.fullmatch(r"(\d{4})-(\d{1,2})", s) or re.fullmatch(
            r"(\d{1,2})\.(\d{4})", s
        ):
            a, b = int(m.group(1)), int(m.group(2))
            y, mo = (a, b) if a > 31 else (b, a)
            d = calendar.monthrange(y, mo)[1] if kraj else 1
            return Datum(date(y, mo, d), True)
        if m := re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", s):
            return Datum(date(int(m.group(1)), int(m.group(2)), int(m.group(3))), False)
        if m := re.fullmatch(r"(\d{1,2})\.\s?(\d{1,2})\.\s?(\d{4})", s):
            return Datum(date(int(m.group(3)), int(m.group(2)), int(m.group(1))), False)
    except ValueError:
        return None
    return None
