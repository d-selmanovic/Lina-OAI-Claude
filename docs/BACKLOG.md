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

## Aufgaben (Reihenfolge)
1. [ ] Airtable-Schema über den Connector auslesen → `docs/airtable.md` aktualisieren
2. [ ] Szenarien für die Pflichtfälle in `scenarios.yaml` (siehe `docs/voice-prompting.md`)
3. [ ] Pre-Call-Fetch (Anruf 1) und Write-Tool nach `Dopune`, mit Test-Record
4. [ ] Erster Entwurf der Instruktionen (Voice und Backend), GPT-Live per Inference
5. [ ] Test mit `lk agent debugger` und `lk agent console`
6. [ ] Feinschliff Persona, Wissen und Einwände
7. [ ] SIP-Outbound
8. [ ] Später: Inbound-Agent
