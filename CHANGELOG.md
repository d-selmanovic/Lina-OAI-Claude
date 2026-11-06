# Changelog – Lina

Versionsnummer: `pyproject.toml` (Hauptversion.Funktion.Korrektur). Ablauf: `docs/DEPLOY.md`.
„LiveKit-Version“ = ID aus `lk agent status` (für `lk agent rollback`).

## 0.2.1 – in Arbeit (dev)
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
