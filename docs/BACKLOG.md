# Backlog – Lina Outbound

## Offene Entscheidungen
- [ ] **ADR 0001:** GPT-Live über LiveKit Inference (Vorschlag) oder OpenAI-Plugin
- [ ] **Airtable-Schema:** echte Felder auslesen, Pflichtunterlagen und „vorhanden“-Felder festlegen (`docs/airtable.md`)
- [ ] **Jobbeschreibung** neu und genauer fassen (`docs/knowledge/job-angebot.md`)
- [ ] **Job-Step-Wissen** füllen (`docs/knowledge/jobstep.md`)
- [ ] **KI-Hinweis:** Gleich zu Beginn sagen, dass Lina digital ist, oder nur auf Nachfrage wie in v2? Rechtlich prüfen (EU AI Act Art. 50, Datenschutz BiH), Ergebnis als ADR
- [ ] **Aufzeichnung:** ja oder nein, Einwilligungsformulierung
- [ ] **Eignungskriterien** festlegen (wer geht in Anruf 2?)
- [ ] **Anruf 2 (Unterlagen):** später, eigener Ablauf, nutzt `Kratki link za dopunu`
- [ ] **Trigger:** n8n-Workflow oder manuelles Skript, das eine Liste von Record-IDs dispatcht
- [ ] **Status-Logik:** später
- [ ] **Telefonie:** SIP-Provider und Outbound-Trunk für BiH-Nummern
- [ ] **Anrufzeiten** und Wiederholversuche

## Entschieden (05.11.2026)
- Mehrfache Erfahrung und Ausbildung: Option B (direkt in `Radno iskustvo` / `Obrazovanje`)
- Vorerst NICHT: berechnete Berufsjahre, Markierung „nije provjereno“
- Alle Plausibilitätsregeln L1–L10 inklusive Lücken-Regel
- Keine Sprach-Kontrollfrage
- Zeitzone `Europe/Sarajevo`

## Aufgaben (Reihenfolge)
0. [ ] Neue Airtable-Felder anlegen (Liste in `docs/airtable.md`), **nach Freigabe**
1. [ ] Airtable-Schema über den Connector auslesen → `docs/airtable.md` aktualisieren
2. [x] Szenarien: `scenarios.yaml` (7, mit Endzustand) und `scenarios-guardrails.yaml` (6)
3. [x] Pre-Call-Fetch, Write-Tools, `provjeri_podatke`, `trenutno_vrijeme` – Fetch gegen K-0196 getestet (nur lesend), Schreiben nur mit Fake-Store getestet
4. [x] Erster Entwurf der Instruktionen (Voice bosnisch, Backend englisch), GPT-Live per Inference
5. [ ] Test mit `lk agent debugger --audio` und `lk agent dev` (Console) – siehe `docs/TESTEN.md`
5a. [ ] Erster echter Schreibtest gegen Airtable (K-0196), danach Testeinträge aufräumen
6. [ ] Feinschliff Persona, Wissen und Einwände
7. [ ] SIP-Outbound
8. [ ] Später: Inbound-Agent
