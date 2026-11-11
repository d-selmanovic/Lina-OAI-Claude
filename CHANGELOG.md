# Changelog – Lina

Versionsnummer: `pyproject.toml` (Hauptversion.Funktion.Korrektur). Ablauf: `docs/DEPLOY.md`.
„LiveKit-Version“ = ID aus `lk agent status` (für `lk agent rollback`).

## Merge dev → main – in Arbeit (Branch `merge-dev`)
- Aus dev übernommen: Langfuse-Dialog beider Seiten (`src/lina/dialog.py`), Version und
  Environment in Langfuse, Simulationen nur manuell, Wartezeit am Simulationsende,
  `testanruf*.json` ignoriert (zusätzlich bleibt `allowlist-testanruf.json`), DEPLOY-Ablauf,
  Szenarien-Anpassungen und `scenarios-neu.yaml`.
- Nicht übernommen: `prompts.py` aus 0.2.2 (main ist neuer), Version und `uv.lock` aus dev.
  Die Prompt-Regeln aus 0.2.2 (Scherz, Beleidigungen, Rückruf mit Wochentag, „schon in der
  Bewerbung“, E-Mail-Bestätigung) kommen erst mit dem Lina-3-Prompt.
- Korrektur: Langfuse-Abschluss nutzt `stanje.ishod or stanje.ishod_bez_kraja()`, wie beim Speichern.

## 1.0.0 – production, 10.11.2026 (Commit `af8cfbb`, Git-Tag `lina-v2.0-prod`, LiveKit-Version `5b6DoCZ8oQ7X`)
- Stand von main vor Lina 3: AMD mit EU-fähigem STT, Handoffs Pozdrav → Lina → Kraj ohne
  doppelte Tools, Status nach dem Anruf aus den Fakten, Gesprächsende ohne Abschluss über
  `ishod_bez_kraja()`. Einzelheiten in `git log 44cbd65..af8cfbb`.

## 0.2.2 – dev, nur teilweise nach main übernommen
- Stimmen-Prompt nach OpenAI-Leitfaden „Prompting GPT-Live“: Delegation policy mit
  `<|SpawnThinking|>` und `Backend tools:`, Backchannel policy, Interruption policy;
  nicht raten beim Warten, Bestätigung erst nach Backend-Ergebnis.
- Ablauf-Schritte nur für fehlende Angaben; „schon in der Bewerbung“ sofort akzeptieren.
- E-Mail buchstabiert zurücklesen und bestätigen lassen, erst dann speichern.
- Scherz/Unglaubwürdiges: einmal mit Humor ernst nachfragen; Backend speichert keine Scherze
  und keine beleidigenden Begriffe.
- Smalltalk kurz und menschlich; weniger gleichförmige Bestätigungen.
- Rückruf: Wochentag, Datum, Uhrzeit vom Backend; Widerspruch erst klären.
- Simulation: Endprüfung wartet auf den Gesprächsabschluss (asynchrone Delegation).
- Szenarien: Erwartungen präzisiert, Opt-out-Persona Kroatisch (Simulator lehnte „bos“ ab),
  neu `scenarios-neu.yaml` (Scherzantwort, E-Mail, Smalltalk).

## 0.2.1 – dev (Commit `de4dc06`)
- Versionsnummer in Langfuse (`langfuse.release`, `lina.version`).
- GitHub-Simulationen nur noch manuell (keine automatischen Kosten bei Push auf main).
- `testanruf*.json` von Git ausgeschlossen.

## 0.2.0 – staging, 06.11.2026 (Git-Tag `v0.2.0`, Commit `4fa39a8`)
- Langfuse: Gespräch beider Seiten (Kandidat + Lina) pro `agent_turn` und als ganzer Dialog
  am `agent_session`-Span; Telefonnummern/Secrets maskiert; Environment production/staging/lokal.
- Status: auf staging, Abnahme offen (Testanruf staging hatte Rauschen, Ursache offen).

## 0.1.0 – production, 05./06.11.2026 (Commit `44cbd65`, LiveKit-Version `iV8VZbkKehaz`)
- Erste Cloud-Version: Anruf 1 (Datenerfassung), Airtable, Langfuse (nur Linas Seite),
  Stimme/Emotionen, Telefonie über FusionPBX → TG400. Vorherige LiveKit-Version: `HFgDwp9SRJ9w`
  (gleicher Code).
