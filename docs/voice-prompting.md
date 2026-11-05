# Voice-Prompting: Prinzipien und Checkliste

Grundlage: LiveKit Prompting Guide (`/agents/start/prompting`) und GPT-Live-Doku, Stand 05.11.2026. Dies ist eine eigene Zusammenfassung, für Details gilt das Original (über `reading-livekit-docs` abrufbar).

## 1. Prompt-Struktur
Klar getrennte Abschnitte: Identität, Gesprächsziel, Output-Regeln, Ablauf, Tools, Wissen, Einwände, Guardrails, Kandidatenkontext (aus dem Pre-Call-Fetch).
Bei GPT-Live gibt es zwei Sets: Voice-Modell (wie gesprochen wird) und Backend-Modell (was entschieden und welches Tool aufgerufen wird).

## 2. Output für Sprache
- Kurz: 1–2 Sätze, eine Frage pro Turn
- Klartext, kein Markdown
- Zahlen, Daten und Beträge auf Bosnisch ausschreiben
- Tool-Ergebnisse zusammenfassen, keine IDs vorlesen

## 3. Natürlichkeit
- Gesprochene Sprache modellieren: kurze Pausen, Spiegeln („Razumijem…“, „Odlično…“), Variation der Bestätigungen
- Ruhiger, warmer Ton. Persönlichkeit als beobachtbares Verhalten beschreiben, nicht als Adjektivliste
- Sprechmuster mehrfach im Prompt verankern, weil LLMs überwiegend auf geschriebenem Text trainiert sind

## 4. Architektur
- Kontext klein halten, so wenige Handoffs wie möglich (bei GPT-Live kosten sie eine neue Session)
- Das Modell interpretiert, der Code entscheidet. Airtable-Fetch und -Write passieren im Code bzw. in Tools
- Kandidatenkontext nur als berechnete Zusammenfassung, nicht als Rohdaten

## 5. Testen
1. Szenarien in `scenarios.yaml` schreiben, **bevor** das Verhalten gebaut wird
2. `lk agent debugger` nach jeder Änderung
3. Simulationen inklusive Endzustand prüfen (wurde der richtige Record korrekt gepatcht?)
4. Echte Sessions über Observability und Transkripte auswerten

Pflichtszenarien für Lina:
- Kandidat hat schon alles → Lina fragt nichts Vorhandenes ab
- Es fehlt nur der Pass → Lina nennt nur den Pass
- Kandidat hat keine Zeit → Rückruf wird vereinbart und gespeichert
- Opt-out → wird respektiert und gespeichert
- EU-Einreiseverbot → höflich beenden
- Frage nach Arbeitgebername → wird nicht genannt
- „Bist du ein Roboter?“ → ehrliche Antwort

## Checkliste
- [ ] Bosnisch-ijekavischer Output mit „ti“, keine deutschen oder englischen Füllwörter
- [ ] Kurz, eine Frage pro Turn
- [ ] Fragt nur, was laut Kontext fehlt
- [ ] Wissen nur aus `docs/knowledge/`
- [ ] Voice- und Backend-Instruktionen getrennt
- [ ] Pflichtaussagen per Szenario abgesichert
