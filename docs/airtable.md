# Airtable: Schema, Pflichtunterlagen, Pre-Call-Fetch

Stand: 05.11.2026. Schema per Airtable-Connector ausgelesen (nur Struktur, keine Datensätze).
**[Startwert]** = meine Annahme für den ersten Entwurf, von Denis noch zu bestätigen bzw. anzupassen.

## Base
- **GIG Casting**, `appz3VFomHaWhuILV` (Interface „Recruiter dashboard“ `pagYwUjTjMwr86Ll7`)
- Haupttabelle **`Prijave (test)`**, `tbl7WHRtBkRX7tGxt`: ein Datensatz pro Bewerber. Trotz „(test)“ im Namen ist das faktisch die Arbeitstabelle mit **echten Bewerberdaten**: tägliche Excel-Importe, davor jeweils Backup-Tabellen.
- Weitere Tabellen: `Dopune` (`tblzvtVFXZHFgk8mq`), `Termini i zadaci` (`tblMTxAh92crqggAY`), `Radno iskustvo`, `Obrazovanje`, `Casting ocjene`, `BACKUP …` (nicht anfassen)

**Im Code immer Field-IDs verwenden, nicht Namen.** Namen können sich ändern.

## Lesen (Pre-Call-Fetch) aus `Prijave (test)`

### Identifikation und Anrede
| Zweck | Feld | ID |
|---|---|---|
| Vorname (Anrede) | `Ime` | `fldlWTDSvVwiOZDmM` |
| Kandidaten-Code | `Šifra kandidata` | `fldFtCLmRLempwjls` |
| Vorwahl | `Pozivni broj` | `fldHiAvs5PSf1mIVY` |
| Telefonnummer | `Broj telefona` | `fldydnGFUIkAGolln` |
| Status | `Status kandidata` (singleSelect) | `fldio94d9MyPTN6ZI` |

### Unterlagen (nur für Anruf 2, später; in Anruf 1 nur als Kontext lesen) [Startwert]
Eine Unterlage gilt als **vorhanden**, wenn das Dateifeld **nicht leer** ist **oder** die Option in `Dokumenti` (`fldk4qbnRt5gBcd8U`) gesetzt ist. [Startwert: `Dok. obrada` wird vorerst ignoriert]

| Unterlage | Dateifeld (ID) | Option in `Dokumenti` | Pflicht? |
|---|---|---|---|
| Diplom/Zeugnis | `Svjedočanstva` (`fldvyFpU2ucXmtaXi`) | DIPLOMA oder SVJEDOČANSTVO 1–4 | ja [Startwert] |
| Pass (Fotoseite) | `Pasoš` (`fldLJQ2VYmf4j7JtO`) | SLIKA PASOŠA | ja [Startwert] |
| Foto für CV | `Foto` (`fldfquHbXCqyobesM`) | FOTOGRAFIJA ZA CV | ja [Startwert] |
| Lebenslauf | `Životopis` (`fldN7DFMEC9ETZaFc`) | – | nein [Startwert] |
| Führerschein (Datei) | `Vozačka dozvola (prilog)` (`fldthIhgrw3T3ChPF`) | – | nein [Startwert] |

### Anruf 1: Angaben für die Eignungsprüfung [Startwert]

**Grundregel: Ein Feld wird nur abgefragt, wenn es (a) als „abfragen“ markiert ist UND (b) leer ist.** Vorhandenes wird nie erneut abgefragt.

**„Leer“ heißt** [Startwert]: leer oder nur Leerzeichen, „-“ oder „?“. Alles andere zählt als vorhanden.

**Vorhanden ist ein Wert auch, wenn er schon in `Dopune` wartet:** Der Fetch lädt zusätzlich die verknüpften `Dopune`-Einträge (Link-Feld `Dopune` `fldK7uywuxbPhzjGH`), deren `Status pregleda` **nicht** „Odbačeno“ ist. Ist das entsprechende Feld dort gefüllt, gilt es als vorhanden. Damit fragt Lina auch bei einem zweiten Anruf nichts doppelt ab.

**Im Gespräch:** Was der Kandidat schon beantwortet hat, auch ungefragt, wird nicht noch einmal gefragt.

Felder, in dieser Reihenfolge:

| Angabe | Feld in `Prijave (test)` (ID) |
|---|---|
| Schule bzw. Beruf | `Tačan naziv škole, grad, država` (`fldczOviQFhemuJ9u`), `Tačan naziv struke ` (`fldV8JGvCxQ1cHHku`) |
| Diplom vorhanden? (nur ja/nein, **nicht** anfordern) | `Da li je diploma dostupna?` (`fldVslRckQwEOMxhb`) |
| Berufserfahrung | `RADNO MJESTO` (`fld1qJ6uYZ7HKsXuU`), `KOMPANIJA` (`fldeiamQZD6JaQE2r`), `Radno iskustvo – Od/Do` (`fld89KIp3njkrB6aT`/`fldJMsJXNZgMJ3q0f`) |
| Aufenthaltsstatus | `Status boravka` (`flducCUvS6Rny8wi4`) |
| Arbeitserlaubnis | `Radna dozvola` (`fldwC9YtkIbvWmNqF`) |
| Führerschein | `Vozačka dozvola` (`fldWFnqeYiukLviK9`) |
| Deutschkenntnisse (Selbsteinschätzung) | `Poznavanje njemačkog jezika` (`fldjoM8wtCi3IOm4E`) |

- Die Formel `Lični podaci – nedostaje` (`fldkpncNkxR0efZv4`) zeigt zusätzlich leere Personendaten. Adresse, Geburtsdaten und Familienstand fragt Lina in Anruf 1 **nicht** ab [Startwert].
- Die tatsächlichen Anforderungen (wer ist geeignet) sind **offen** und gehören in `docs/knowledge/job-angebot.md`.

### Weg zum Nachreichen
- `Kratki link za dopunu` (`fldMh2dBsJXf3PMA2`): persönlicher Upload-Link
- `Poslan link za dopunu` (`fldzh5zVs29i3SWO7`, Da/Ne): wurde er schon per WhatsApp gesendet?
- Wird erst in **Anruf 2** genutzt. Lina sendet selbst nichts, das läuft über die bestehende Automation.

### Wen Lina anruft
**Statusfrei.** Ein manueller oder n8n-Trigger übergibt eine Liste von Record-IDs, je ID ein Dispatch. Status-Filter kommen später.

## Neue Felder (vorgeschlagen, noch NICHT angelegt, wartet auf Freigabe)
| Tabelle | Feld | Typ |
|---|---|---|
| Prijave (test) und Dopune | `Djeca` | Auswahl Da / Ne |
| Prijave (test) und Dopune | `Broj djece` | Zahl |
| Prijave (test) und Dopune | `Dob djece` | Text (z. B. „4, 9“) |
| Prijave (test) und Dopune | `Njemački – nivo` | Auswahl Nema / Osnove (A1–A2) / Srednje (B1–B2) / Napredno (C1–C2). Neu angelegt, das bestehende Freitextfeld bleibt unverändert |
| Prijave (test) und Dopune | `Engleski – nivo` | Auswahl wie oben |
| Radno iskustvo | `Izvor podatka` | Auswahl Lina (nije provjereno) / Forma / Recruiter |
| Radno iskustvo | `Napomena provjere` | Langtext (Hinweise aus `provjeri_podatke`) |
| Obrazovanje | `Izvor podatka` | Auswahl wie oben |
| Obrazovanje | `Smjer / zanimanje` | Text |

## Mehrfache Erfahrung und Ausbildung (Option B, entschieden)
- Lina legt pro Station **einen neuen Datensatz** an: in `Radno iskustvo` (`tblbRG7v8pTRqVTqH`, Felder `Pozicija`, `Poslodavac`, `Od`, `Do`, `Aktuelno`, `Grad`, `Država`, `Opis`, Link `Kandidat veza` `fldZQZunKe7uh3Crr`) bzw. in `Obrazovanje` (`tblyAQ6ud95RW76Ym`, Felder `Škola`, `Adresa škole`, `Od`, `Do`, Link `Kandidat` `fldkiFDfqWQCmF0RQ`).
- Jeder Datensatz bekommt `Izvor podatka` = „Lina (nije provjereno)“. Das Team prüft über diesen Filter.
- **„Leer“** bedeutet für diese Bereiche: Es gibt noch keinen verknüpften Datensatz. Gibt es schon Einträge, liest Lina sie vor und fragt nur: „Je li to sve, ili ima još nešto?“
- Bestehende Datensätze überschreibt Lina nie.

## Schreiben (nach dem Gespräch) [Startwert]

Lina schreibt **nicht direkt** in `Prijave (test)`. **Personendaten** gehen nach `Dopune` (Prüfung durchs Team), **Erfahrung und Ausbildung** als neue, markierte Datensätze in `Radno iskustvo` bzw. `Obrazovanje` (siehe oben).

1. **Neuer Datensatz in `Dopune`** (`tblzvtVFXZHFgk8mq`):
   - `Kandidat` (`fldDZ1Ik9Xq7vm0f3`) → Link auf genau den geladenen Record
   - `Šifra kandidata` (`fldmOjzIemaOoizeT`)
   - `Status pregleda` (`fldLmjPcpFyO6O1Ro`) = **Novo**
   - am Telefon erhobene Angaben in die gleichnamigen `Dopune`-Felder, z. B. `Status boravka` (`fldxKNjPUZnC5uUyO`), `Radna dozvola` (`fldhrlSRrRjSKmKwV`), `Vozačka dozvola` (`fldoeHwM4FaEwjvzQ`), `Tačan naziv škole, grad, država` (`fld6GOMBwJf0CZlK7`), `Tačan naziv struke` (`fld6WimSC758MC85L`), `Da li je diploma dostupna?` (`fldpiOA7rUjsNE2St`), `Radno iskustvo 1 – …`
   - Gesprächsergebnis und Zusammenfassung in `Opis iskustva ili obrazovanja` (`fldejrE05pgkiVOY1`). [Startwert: Ein eigenes Feld „Ergebnis Lina-Anruf“ wäre sauberer und ist anzulegen]
2. **Bei Rückrufwunsch:** neuer Datensatz in `Termini i zadaci` (`tblMTxAh92crqggAY`): `Name`, `Datum i vrijeme termina`, `Kandidat` (Link), `Status` = Todo

Gesprächsergebnisse: `erreicht` · `rückruf` · `kein_interesse` · `opt_out` · `nicht_erreicht` · `falsche_person`

## Pre-Call-Fetch-Vertrag
1. Der Trigger (manuell oder n8n) übergibt pro Kandidat `record_id` als Dispatch-Metadaten.
2. Der Entrypoint lädt den Record **vor** `session.start` (Timeout, Fehler → kein Gespräch).
3. Der Code berechnet daraus:
   ```text
   ime: <Ime>
   nedostaje_podaci: [status_boravka, radna_dozvola, ...]   # Anruf 1
   nedostaje_dokumenti: [...]                              # erst Anruf 2
   ```
4. Nur diese Zusammenfassung geht in die Instruktionen.
5. Nach dem Gespräch schreibt das Tool in `Dopune` bzw. `Termini i zadaci`, nie direkt in `Prijave (test)`.

## Offen
- Alle [Startwert]-Punkte bestätigen
- Test-Datensatz in `Prijave (test)` anlegen (z. B. Name mit „test“, die Formel `Test oznaka (po imenu)` markiert ihn), Entwicklung nur damit
- Airtable-Token: Scopes `data.records:read`, `data.records:write`, `schema.bases:read`, **nur** Base `appz3VFomHaWhuILV`
