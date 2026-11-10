"""Handoff Pozdrav → Lina → Kraj ohne doppelte Tool-Namen (Regression: Stille nach Handoff)."""

import asyncio
from datetime import datetime

from livekit.agents import function_tool, llm

from lina.agent_lina import PozdravAgent
from lina.airtable import FakeStore, Paket
from lina.kontekst import izracunaj
from lina.stanje import Stanje
from lina.zeit import TZ


@function_tool
async def end_call() -> str:
    """Test-Ersatz für EndCallTool."""
    return "ok"


def _namen(agent) -> list[str]:
    return [t.info.name for t in llm.ToolContext(agent.tools).flatten()]


def test_handoff_kette_ohne_doppelte_tools():
    k = izracunaj("recT", {"fldQCU77iYMy8gFS8": "BiH"}, [], [], [])
    st = Stanje(k, fiksno_vrijeme=datetime(2026, 11, 5, 10, 0, tzinfo=TZ))
    store = FakeStore(Paket({}, [], [], []))
    pozdrav = PozdravAgent(
        stanje=st, store=store, kontekst=k, vrijeme="sri 10:00", tools=[end_call]
    )
    lina, _ = asyncio.run(pozdrav.nastavi_prikupljanje(None))
    kraj, _ = asyncio.run(lina.predji_na_kraj(None))
    for a in (pozdrav, lina, kraj):
        namen = _namen(a)
        assert len(namen) == len(set(namen)), namen
        assert "end_call" in namen
