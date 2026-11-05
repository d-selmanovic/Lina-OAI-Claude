#!/usr/bin/env bash
# lk-audit.sh – READ-ONLY Bestandsaufnahme (LiveKit + Claude Code + Projekt). Ändert nichts, maskiert Keys.
# Nutzung: bash tools/lk-audit.sh [PROJEKTORDNER]
set -u
export HOMEBREW_NO_AUTO_UPDATE=1
PROJ="${1:-}"
hr()   { printf '\n=== %s ===\n' "$1"; }
have() { command -v "$1" >/dev/null 2>&1; }
mask() { sed -E 's/(API[A-Za-z0-9]{6})[A-Za-z0-9]+/\1…[masked]/g; s/[A-Za-z0-9+\/]{32,}={0,2}/[masked]/g'; }

hr "Tools"
for t in brew lk uv python3 git claude; do have "$t" && printf '%-8s %s\n' "$t" "$(command -v "$t")" || printf '%-8s FEHLT\n' "$t"; done
hr "LiveKit CLI"
have lk && { lk --version 2>&1 | head -1; lk project list 2>&1 | mask | head -20; }
hr "livekit-agents auf PyPI"
curl -fsS --max-time 10 https://pypi.org/pypi/livekit-agents/json 2>/dev/null | python3 -c 'import sys,json; print(json.load(sys.stdin)["info"]["version"])' 2>/dev/null || echo "PyPI nicht erreichbar"
hr "Claude Code"
if have claude; then
  claude --version 2>&1 | head -1
  claude plugin details livekit 2>&1 | grep -E "Source|Skills \(|MCP servers" || echo "Plugin livekit fehlt"
  claude mcp list 2>/dev/null | grep -i livekit || echo "kein livekit-MCP"
  ls -d ~/.claude/skills/*livekit* ~/.agents/skills/*livekit* 2>/dev/null || echo "keine doppelten LiveKit-Skills (gut)"
fi
if [ -n "$PROJ" ] && cd "$PROJ" 2>/dev/null; then
  hr "Projekt: $(pwd)"
  for f in AGENTS.md CLAUDE.md CLAUDE.local.md .claude/settings.json .claude/rules .claude/agents docs/airtable.md docs/knowledge pyproject.toml src/agent.py scenarios.yaml .env.local; do
    [ -e "$f" ] && printf '%-26s vorhanden\n' "$f" || printf '%-26s –\n' "$f"; done
  echo "-- CLAUDE.md importiert AGENTS.md?"; grep -q '^@AGENTS.md' CLAUDE.md 2>/dev/null && echo ja || echo NEIN
  echo "-- Rules:"; ls .claude/rules 2>/dev/null
  echo "-- agent_name:"; grep -n 'agent_name' src/agent.py 2>/dev/null
  echo "-- LIVEKIT_URL:"; grep '^LIVEKIT_URL' .env.local 2>/dev/null || echo "keine .env.local"
  echo "-- Variablennamen .env.local (ohne Werte):"; [ -f .env.local ] && sed -nE 's/^([A-Z0-9_]+)=.*/\1/p' .env.local
  echo "-- livekit-Pakete:"; have uv && [ -d .venv ] && uv pip list 2>/dev/null | grep -i livekit
  echo "-- Git:"; git status --short 2>/dev/null | head -20
fi
hr "Fertig – nichts wurde verändert"
