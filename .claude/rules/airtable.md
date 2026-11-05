---
paths:
  - "src/**/*.py"
  - "docs/airtable.md"
---

# Airtable-Regeln

- Einzige Datenquelle. Schema und Pflichtunterlagen: `docs/airtable.md`. Feldnamen nie raten, sondern gegen das echte Schema prüfen.
- **Pre-Call-Fetch** im Entrypoint **vor** `session.start`, mit Timeout. Schlägt er fehl: nicht anrufen bzw. Gespräch abbrechen und Fehler loggen. Nicht blind alles abfragen.
- Das Modell bekommt nur die berechnete Zusammenfassung (`vorhanden`/`fehlt` plus Vorname), nie den ganzen Datensatz.
- Schreiben nur über ein Tool: Patch auf genau den geladenen Record (Record-ID aus dem Dispatch bzw. Fetch, nie vom Modell), nur nicht-leere Felder, nie bestehende Werte mit Leerwerten überschreiben.
- Token mit minimalen Scopes (`data.records:read`, `data.records:write`, `schema.bases:read`) und nur auf diese Base.
- Keine Kandidatendaten in Logs. Rate-Limits und Fehler behandeln.
