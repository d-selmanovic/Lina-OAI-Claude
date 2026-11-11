"""Welche Lina-Version läuft: v2 (eingefroren, Standard) oder v3 (LINA_PROMPT=v3).

Eigenes Modul, damit prompts.py, kontekst.py und die Tools dieselbe Entscheidung lesen,
ohne sich gegenseitig zu importieren.
"""

from __future__ import annotations

import os

V2 = "2.0.0"
V3 = "3.0.0"


def aktivna_verzija() -> str:
    """Prompt-Version dieser Session: V3 bei LINA_PROMPT=v3, sonst V2."""
    return V3 if os.getenv("LINA_PROMPT", "v2").strip().lower() == "v3" else V2


def je_v3() -> bool:
    return aktivna_verzija() == V3


def granica_godina() -> int:
    """Ab diesem Alter endet das Gespräch: v3 ab 45 (Entscheidung E3), v2 ab 60."""
    return 45 if je_v3() else 60
