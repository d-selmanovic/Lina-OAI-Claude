# ADR 0001: GPT-Live-Betrieb über LiveKit Inference

- **Status:** Vorschlag (wartet auf Bestätigung)
- **Datum:** 2026-11-05

## Kontext
Lina nutzt OpenAI GPT-Live 1. Laut LiveKit-Doku geht das auf zwei Wegen: über LiveKit Inference oder über das OpenAI-Plugin.

## Optionen
1. **LiveKit Inference:** `openai/gpt-live-1`. Kein eigener OpenAI-Key, Abrechnung über LiveKit Cloud, EU-Endpoint verfügbar, kein zusätzliches Paket.
2. **OpenAI-Plugin:** `livekit-agents[openai]` plus `OPENAI_API_KEY` mit Paid Tier. Eigene Abrechnung, OpenAI Hosted Tools verfügbar.

## Entscheidung (Vorschlag)
Option 1. Weniger Secrets und Pakete, EU-Endpoint, das reicht für den Entwurf. Wechsel zu 2 nur bei konkretem Bedarf, etwa Hosted Tools oder Kosten.

## Konsequenzen
- Kosten laufen über LiveKit Cloud (`get_pricing_info` prüfen)
- Für Option 2 später: Paket ergänzen, Key in `.env.local`

## Verifikation
Testanruf mit `lk agent console` und eine bosnische Antwort mit akzeptabler Latenz.
