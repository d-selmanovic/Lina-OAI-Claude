# Lina testen

Reihenfolge: erst Unit-Tests, dann Debugger, dann Console, dann Simulationen.
**GPT-Live ist audio-only:** Debugger und Simulationen laufen im **Audio-Modus**.

## 0. Einmalig
In `.env.local` steht der Test-Kandidat (K-0196, kein echter Bewerber):
```text
LINA_TEST_RECORD_ID=rec17GODhyD0Lkgzp
```
Er gilt nur, wenn ein Job **ohne** Dispatch-Metadaten startet (lokale Tests). Echte Anrufe
übergeben `{"record_id": "rec..."}` als Metadaten.

## 1. Unit-Tests (kein Netz, keine Kosten)
```bash
uv run pytest
uv run ruff check src tests
```

## 2. Pre-Call-Fetch gegen Airtable (nur lesen)
```bash
uv run python -c "import asyncio, dotenv; dotenv.load_dotenv('.env.local'); \
from lina.airtable import AirtableStore; from lina.kontekst import izracunaj; \
p=asyncio.run(AirtableStore().ucitaj('rec17GODhyD0Lkgzp')); \
print(izracunaj('rec17GODhyD0Lkgzp',p.kandidat,p.dopune,p.radno_iskustvo,p.obrazovanje).nedostaje)"
```
Erwartet: Liste der fehlenden Angaben, **ohne** `drzavljanstvo` (bei K-0196 eingetragen).

## 3. Agent-Debugger (Audio)
```bash
lk agent debugger start src/agent.py --audio
lk agent debugger say "Halo?"
lk agent debugger say "Da, imam vremena."
lk agent debugger say "Radim kao zidar u firmi Hidrogradnja od dvije hiljade osamnaeste."
lk agent debugger stop --chat-history
```
Achte auf: bosnische Antworten, eine Frage pro Turn, Tool-Calls (`sacuvaj_podatak`,
`dodaj_radno_mjesto`, `provjeri_podatke`). Nach Codeänderungen: `lk agent debugger restart`.

**Achtung:** Endet das Gespräch mit `zavrsi_razgovor` oder bricht ab, schreibt Lina einen
neuen Eintrag in `Dopune` (und ggf. `Radno iskustvo` / `Obrazovanje`) – verknüpft mit dem
Test-Kandidaten K-0196. Diese Testeinträge danach in Airtable löschen oder auf „Odbačeno“ setzen.

## 4. Mit Lina sprechen (Mikrofon, Browser)
```bash
lk agent dev
```
Den ausgegebenen Agent-Console-Link öffnen und sprechen.

## 5. Simulationen (kosten Inferenz)
```bash
lk agent simulate audio --scenarios scenarios.yaml
lk agent simulate audio --scenarios scenarios-guardrails.yaml
lk agent simulate list
```
Simulationen nutzen **keinen** Airtable-Zugriff: Kandidaten kommen aus `userdata`
(`src/lina/simulacija.py`), der Endzustand wird in `on_simulation_end` geprüft.
