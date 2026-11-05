"""Aktuelles Datum und Uhrzeit in Europe/Sarajevo (Sommerzeit automatisch).

`LINA_NOW` (ISO, z. B. 2026-11-05T10:00) fixiert die Uhr für Tests und Simulationen.
"""

from __future__ import annotations

import os
from datetime import datetime
from zoneinfo import ZoneInfo

from .config import TIMEZONE

TZ = ZoneInfo(TIMEZONE)

DANI = ("ponedjeljak", "utorak", "srijeda", "četvrtak", "petak", "subota", "nedjelja")
MJESECI = (
    "januar",
    "februar",
    "mart",
    "april",
    "maj",
    "juni",
    "juli",
    "august",
    "septembar",
    "oktobar",
    "novembar",
    "decembar",
)


def sada() -> datetime:
    fiks = os.getenv("LINA_NOW")
    if fiks:
        dt = datetime.fromisoformat(fiks)
        return dt.replace(tzinfo=TZ) if dt.tzinfo is None else dt.astimezone(TZ)
    return datetime.now(TZ)


def opis(dt: datetime | None = None) -> str:
    """Z. B. 'četvrtak, 5. novembar 2026, 21:30 (Europe/Sarajevo)'."""
    dt = dt or sada()
    return f"{DANI[dt.weekday()]}, {dt.day}. {MJESECI[dt.month - 1]} {dt.year}, {dt:%H:%M} ({TIMEZONE})"


def parse_termin(v: str) -> datetime | None:
    """ISO-Datum mit Uhrzeit in Europe/Sarajevo, z. B. 2026-11-06T15:00."""
    try:
        dt = datetime.fromisoformat(v.strip())
    except ValueError:
        return None
    return dt.replace(tzinfo=TZ) if dt.tzinfo is None else dt.astimezone(TZ)
