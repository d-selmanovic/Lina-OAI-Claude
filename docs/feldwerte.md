# Feste Werte (Auswahl statt Freitext)

**Prinzip:** Linas Schreib-Tools akzeptieren nur Werte aus diesen Listen (Enum im Tool-Schema). In Airtable landen sie als einheitlicher Text bzw. in neuen Auswahlfeldern.
**Bestehende Airtable-Felder werden NICHT umgebaut** (Typwechsel nur später, nach Backup, Test an einer Kopie und Freigabe), weil Formeln, die Maske, die Excel-Importe und die Dopune-Form davon abhängen.

Freitext bleibt nur, wo eine Liste nicht sinnvoll ist: Firmenname, Position, Schulname, Ort, Fähigkeiten.

| Feld | Erlaubte Werte |
|---|---|
| Status boravka | `BiH` · `EU – <država>` · `Drugo – <država>` |
| Radna dozvola | `Nema` · `Da – EU` · `Da – Njemačka` · `Da – <druga država>` |
| Vozačka dozvola | Kategorien kommagetrennt aus `AM, A1, A2, A, B, BE, C1, C1E, C, CE, D1, D1E, D, DE, F, G, M` · oder `Nema` |
| Državljanstvo | eine oder mehrere aus `BiH, Srbija, Hrvatska, Crna Gora, Sjeverna Makedonija, Kosovo, Albanija, Slovenija` · sonst `Drugo – <država>` |
| Bračno stanje | `Neoženjen/Neudata` · `Oženjen/Udata` · `Vanbračna zajednica` · `Razveden/Razvedena` · `Udovac/Udovica` |
| Djeca (neu) | `Da` · `Ne` |
| Broj djece (neu) | ganze Zahl ≥ 1 (nur wenn Djeca = Da) |
| Dob djece (neu) | Zahlen kommagetrennt, z. B. `4, 9` |
| Njemački – nivo / Engleski – nivo (neu) | `Nema` · `Osnove (A1–A2)` · `Srednje (B1–B2)` · `Napredno (C1–C2)` |
| Da li je diploma dostupna? | `Da` · `Ne` |
| Stepen obrazovanja (neu, Obrazovanje) | `Osnovna škola` · `Srednja – 3 godine (KV)` · `Srednja – 4 godine` · `Viša/Fakultet` · `Kurs/obuka` |
| Država (Radno iskustvo) | Liste wie Državljanstvo plus `Njemačka, Austrija, Švicarska` · sonst `Drugo – <država>` |
| Aktuelno (Radno iskustvo) | Checkbox |
| Izvor podatka (neu) | `Lina (nije provjereno)` · `Forma` · `Recruiter` |

Datumsangaben: `Od`/`Do` als Datum. Ist nur das Jahr bekannt, gilt der 01.01. bzw. 31.12. des Jahres, mit dem Vermerk `approx` in `Napomena provjere`.
