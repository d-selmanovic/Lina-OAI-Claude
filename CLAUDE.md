@AGENTS.md

# Projekt: Lina – Outbound-Recruiting-Agent (Job-Step)

## Ziel und Prozess
Zweistufiger Outbound-Prozess:
1. **Anruf 1 (aktueller Bau): Datenabfrage.** Lina ruft Bewerber an, bedankt sich für die Bewerbung und fragt **nur die fehlenden, für die Eignung relevanten Angaben** ab. **Sie fordert in diesem Anruf keine Unterlagen an.** Fragen zu Job-Step und zum Jobangebot beantwortet sie aus der Wissensbasis.
2. **Eignungsprüfung:** passiert außerhalb des Gesprächs (Team bzw. Code). Lina entscheidet nicht über die Eignung und kündigt sie nicht an.
3. **Anruf 2 (später): Unterlagen anfordern**, nur bei geeigneten Kandidaten.
- **Auslöser:** statusfrei. Manueller Start oder per n8n mit einer **Liste von Record-IDs**, ein Dispatch pro Kandidat. Status-Logik kommt später.
- Später folgt ein eigener Agent für Inbound auf derselben Basis.

## Fixe Vorgaben
- **Sprache: ausschließlich Bosnisch (ijekavski), Anrede „ti“.** Kein Deutsch, kein Englisch im Gespräch. Kandidaten sitzen in BiH.
- **Stack:** LiveKit Agents (Python) und LiveKit Cloud-Projekt `lina-oai`, Agent-Name `livekit-oai-gig-casting`.
- **Modell:** OpenAI GPT-Live 1. Regeln dazu in `.claude/rules/gpt-live.md`.
- **Datenquelle:** ausschließlich Airtable. Regeln in `.claude/rules/airtable.md`, Schema in `docs/airtable.md`.

## Architektur-Leitplanken
- **Pre-Call-Fetch im Code, nicht im Modell:** Vor dem Gesprächsstart lädt der Entrypoint den Kandidaten-Datensatz aus Airtable und berechnet daraus `vorhanden` und `fehlt`. Nur diese Zusammenfassung geht an die Instruktionen, keine Rohdaten.
- **Das Modell interpretiert, der Code entscheidet:** Zustand, Freigaben und Airtable-Schreibzugriffe liegen im Code bzw. in Tools.
- **Zurückschreiben** nur über ein Tool, nur Felder mit Inhalt, und mit Gesprächsergebnis (erreicht, Rückruf, kein Interesse, Opt-out).
- **So wenige Handoffs wie möglich.** Bei GPT-Live startet ein Handoff eine neue Session.
- **Wissen** (Job-Step, Jobangebot) liegt in `docs/knowledge/` und wird von dort in die Instruktionen geladen, nicht im Code dupliziert.

## Arbeitsregeln
- LiveKit entwickelt sich schnell: APIs, CLI-Flags, Modelle und Preise immer zuerst prüfen (Skill `reading-livekit-docs` bzw. `lk docs`), nie aus dem Gedächtnis antworten.
- Belegte Fakten, Schlussfolgerungen und Annahmen trennen. Unsicherheit benennen.
- Verhaltensänderung → zuerst ein Szenario in `scenarios.yaml`, dann bauen, dann `lk agent debugger`.
- **Kein Deploy, kein Rollback, keine Änderung an Cloud- oder Airtable-Daten ohne meine ausdrückliche Bestätigung.** Bei mehrstufigen Änderungen erst den Plan zeigen und auf „bestätige“ warten.
- Gegen Airtable nur mit **Test-Datensätzen** entwickeln, bis ich die Produktivtabelle freigebe.

## Datenschutz und Secrets
- Kandidatendaten sind personenbezogen: keine Namen, Telefonnummern oder Dokumentinhalte in Logs. Nur Record-IDs loggen.
- Keys nur in `.env.local` (gitignored). Nie in Code, Commits oder Chat.

## Projektdokumente
- `docs/knowledge/jobstep.md`, `docs/knowledge/job-angebot.md`: Wissensbasis (Entwurf, wird überarbeitet)
- `docs/airtable.md`: Felder, Pflichtunterlagen, Pre-Call-Fetch-Vertrag
- `docs/voice-prompting.md`: Prompt-Prinzipien
- `docs/legacy-lina-v2.md`: Was aus dem Gemini-Projekt übernommen wird
- `docs/adr/`: Architekturentscheidungen
- `docs/BACKLOG.md`: offene Entscheidungen und Aufgaben
