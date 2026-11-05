# Airtable: Schema, Pflichtunterlagen, Pre-Call-Fetch

> **Status: ENTWURF.** Die Felder stammen aus Lina v2 (`/Users/Agents/Lina JSI Gemini`, Tabelle `Prijave (test)`) und sind **noch nicht gegen das echte Schema geprüft.** Nächster Schritt: Schema über den Airtable-Connector auslesen und diese Datei korrigieren.

## Base und Tabelle
- Base-ID: `AIRTABLE_BASE_ID` (in `.env.local`)
- Tabelle: `AIRTABLE_TABLE`, bisher `Prijave (test)`

## Bekannte Felder (aus Lina v2, ungeprüft)
| Feld | Bedeutung |
|---|---|
| `Telefon` | Telefonnummer, normalisiert (+387…) |
| `Tačan naziv škole, grad, država` | Schule, Ort, Land |
| `KOMPANIJA` | Bisherige Firma |
| `RADNO MJESTO` | Beruf bzw. Position |
| `Status boravka` | BiH oder EU |
| `Mjesto` | Wohnort |
| `Casting termin` | Casting-Termin |
| `Bilješka` | Notiz fürs HR-Team |

## Pflichtangaben und -unterlagen (zu bestätigen)
| Typ | Was | Feld in Airtable, das „vorhanden“ anzeigt |
|---|---|---|
| Unterlage | Diplom/Zeugnis | **offen** |
| Unterlage | Reisepass | **offen** |
| Unterlage | Foto für CV | **offen** |
| Angabe | Schule | `Tačan naziv škole, grad, država` |
| Angabe | Berufserfahrung | `KOMPANIJA` / `RADNO MJESTO` |
| Angabe | Aufenthaltsstatus | `Status boravka` |
| Angabe | Casting-Termin | `Casting termin` |

## Pre-Call-Fetch-Vertrag (Vorschlag)
1. Dispatch übergibt `record_id` (und Telefonnummer) als Job-Metadaten.
2. Der Entrypoint lädt den Record **vor** `session.start`, mit Timeout und Fehlerbehandlung.
3. Code berechnet:
   ```text
   vorhanden: [schule, status_boravka, ...]
   fehlt:     [pasos, diploma, ...]
   ime:       <Vorname>
   ```
4. Nur diese Zusammenfassung wird in die Instruktionen eingesetzt.
5. Am Ende patcht ein Tool genau diesen Record: neue Angaben plus Gesprächsergebnis.
