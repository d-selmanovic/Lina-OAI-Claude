"""Lina-Agent: Tools für Anruf 1 (Datenerfassung). Die Logik liegt in den reinen Modulen;
hier wird nur verdrahtet. Tools ändern nur den Gesprächszustand – geschrieben wird erst in
`zavrsi_razgovor` bzw. beim Sitzungsende (einmalig).
"""

from __future__ import annotations

import logging
from typing import Literal

from livekit.agents import Agent, RunContext, function_tool

from . import werte
from .airtable import Store, sacuvaj
from .datumi import parse_datum
from .kontekst import Skola, Stanica
from .plausibilitaet import provjeri
from .stanje import Ishod, Stanje
from .zeit import opis, parse_termin

logger = logging.getLogger("lina.agent")

Polje = Literal[
    "status_boravka",
    "radna_dozvola",
    "vozacka",
    "drzavljanstvo",
    "bracno_stanje",
    "njemacki",
    "engleski",
    "djeca",
    "broj_djece",
    "dob_djece",
    "email",
    "datum_rodjenja",
    "mjesto_rodjenja",
    "adresa",
    "vjestine",
]
PoljeRada = Literal[
    "pozicija", "poslodavac", "od", "do", "aktuelno", "grad", "drzava", "opis"
]
PoljeSkole = Literal["skola", "adresa_skole", "od", "do", "smjer", "stepen"]
Stepen = Literal[
    "",
    "Osnovna škola",
    "Srednja – 3 godine (KV)",
    "Srednja – 4 godine",
    "Viša/Fakultet",
    "Kurs/obuka",
]


def _datum(v: str | None, *, kraj: bool):
    if v is None or not str(v).strip():
        return None, None
    d = parse_datum(v, kraj=kraj)
    return (
        (d, None) if d else (None, f"Neispravan datum '{v}'. Koristi YYYY ili YYYY-MM.")
    )


class LinaAgent(Agent):
    def __init__(
        self,
        *,
        instructions: str,
        stanje: Stanje,
        store: Store,
        tools: list | None = None,
    ) -> None:
        super().__init__(instructions=instructions, tools=tools or [])
        self.stanje = stanje
        self.store = store

    # ---------- einzelne Angaben ----------

    @function_tool
    async def sacuvaj_podatak(
        self, context: RunContext, polje: Polje, vrijednost: str
    ) -> str:
        """Speichert eine einzelne Angabe des Kandidaten, sobald er sie genannt hat.

        Erlaubte Werte:
        status_boravka: 'BiH' | 'EU – <država>' | 'Drugo – <država>'
        radna_dozvola: 'Nema' | 'Da – EU' | 'Da – Njemačka' | 'Da – <država>'
        vozacka: Kategorien kommagetrennt aus AM,A1,A2,A,B,BE,C1,C1E,C,CE,D1,D1E,D,DE,F,G,M oder 'Nema'
        drzavljanstvo: BiH, Srbija, Hrvatska, Crna Gora, Sjeverna Makedonija, Kosovo, Albanija, Slovenija (kommagetrennt) oder 'Drugo – <država>'
        bracno_stanje: Neoženjen/Neudata | Oženjen/Udata | Vanbračna zajednica | Razveden/Razvedena | Udovac/Udovica
        njemacki, engleski: Nema | Osnove (A1–A2) | Srednje (B1–B2) | Napredno (C1–C2)
        djeca: Da | Ne;  broj_djece: Zahl;  dob_djece: Zahlen kommagetrennt, z. B. '4, 9'
        datum_rodjenja: YYYY-MM-DD;  email: vollständige Adresse;  mjesto_rodjenja, adresa, vjestine: Text

        Args:
            polje: Welche Angabe.
            vrijednost: Der Wert, auf die erlaubten Werte abgebildet.
        """
        w, greska = werte.normalisiere(polje, vrijednost)
        if greska:
            return f"Nije sačuvano: {greska} Pitaj kandidata kratko još jednom."
        self.stanje.podaci[polje] = w  # type: ignore[assignment]
        return f"Sačuvano: {polje} = {w}."

    # ---------- Berufserfahrung (mehrfach) ----------

    @function_tool
    async def dodaj_radno_mjesto(
        self,
        context: RunContext,
        pozicija: str,
        poslodavac: str,
        od: str,
        do: str = "",
        aktuelno: bool = False,
        grad: str = "",
        drzava: str = "",
        opis: str = "",
    ) -> str:
        """Fügt EINE Berufsstation hinzu (eine pro Aufruf), nachdem der Kandidat sie bestätigt hat.

        Args:
            pozicija: Tätigkeit, z. B. 'Zidar'.
            poslodavac: Firma.
            od: Beginn als YYYY oder YYYY-MM.
            do: Ende als YYYY oder YYYY-MM; leer, wenn aktuell.
            aktuelno: True, wenn er dort noch arbeitet.
            grad: Stadt.
            drzava: Land.
            opis: Kurze Beschreibung der Tätigkeit (optional).
        """
        d_od, e1 = _datum(od, kraj=False)
        d_do, e2 = _datum(do, kraj=True)
        if e1 or e2:
            return f"Nije sačuvano: {e1 or e2}"
        self.stanje.nove_stanice.append(
            Stanica(
                (pozicija or "").strip(),
                (poslodavac or "").strip(),
                d_od,
                d_do,
                bool(aktuelno),
                (grad or "").strip(),
                (drzava or "").strip(),
                (opis or "").strip(),
                izvor="lina",
            )
        )
        n = len(self.stanje.nove_stanice)
        return f"Sačuvano kao radno mjesto broj {n}. Pozovi provjeri_podatke."

    @function_tool
    async def ispravi_radno_mjesto(
        self, context: RunContext, redni_broj: int, polje: PoljeRada, vrijednost: str
    ) -> str:
        """Korrigiert eine von Lina erfasste Berufsstation.

        Args:
            redni_broj: Nummer aus dodaj_radno_mjesto (1, 2, ...).
            polje: Welches Feld.
            vrijednost: Neuer Wert (Datum als YYYY oder YYYY-MM, aktuelno als 'da'/'ne').
        """
        if not 1 <= redni_broj <= len(self.stanje.nove_stanice):
            return "Nepostojeći redni broj."
        s = self.stanje.nove_stanice[redni_broj - 1]
        if polje in ("od", "do"):
            d, e = _datum(vrijednost, kraj=polje == "do")
            if e:
                return f"Nije ispravljeno: {e}"
            setattr(s, polje, d)
        elif polje == "aktuelno":
            s.aktuelno = vrijednost.strip().lower() in ("da", "true", "1")
        else:
            setattr(s, polje, vrijednost.strip())
        self.stanje.pitani_nalazi = {
            k for k in self.stanje.pitani_nalazi if f"r{redni_broj}" not in k
        }
        return "Ispravljeno. Pozovi provjeri_podatke."

    # ---------- Ausbildung (mehrfach) ----------

    @function_tool
    async def dodaj_skolu(
        self,
        context: RunContext,
        skola: str,
        adresa_skole: str = "",
        od: str = "",
        do: str = "",
        smjer: str = "",
        stepen: Stepen = "",
    ) -> str:
        """Fügt EINE Schule bzw. Ausbildung hinzu (eine pro Aufruf), nachdem der Kandidat sie bestätigt hat.

        Args:
            skola: Name der Schule.
            adresa_skole: Ort, Land.
            od: Beginn als YYYY oder YYYY-MM.
            do: Ende als YYYY oder YYYY-MM.
            smjer: Fachrichtung bzw. Beruf, z. B. 'Zidar'.
            stepen: Abschlussstufe.
        """
        d_od, e1 = _datum(od, kraj=False)
        d_do, e2 = _datum(do, kraj=True)
        if e1 or e2:
            return f"Nije sačuvano: {e1 or e2}"
        self.stanje.nove_skole.append(
            Skola(
                (skola or "").strip(),
                (adresa_skole or "").strip(),
                d_od,
                d_do,
                (smjer or "").strip(),
                stepen or "",
                izvor="lina",
            )
        )
        return f"Sačuvano kao škola broj {len(self.stanje.nove_skole)}. Pozovi provjeri_podatke."

    @function_tool
    async def ispravi_skolu(
        self, context: RunContext, redni_broj: int, polje: PoljeSkole, vrijednost: str
    ) -> str:
        """Korrigiert eine von Lina erfasste Schule.

        Args:
            redni_broj: Nummer aus dodaj_skolu (1, 2, ...).
            polje: Welches Feld.
            vrijednost: Neuer Wert.
        """
        if not 1 <= redni_broj <= len(self.stanje.nove_skole):
            return "Nepostojeći redni broj."
        s = self.stanje.nove_skole[redni_broj - 1]
        if polje in ("od", "do"):
            d, e = _datum(vrijednost, kraj=polje == "do")
            if e:
                return f"Nije ispravljeno: {e}"
            setattr(s, polje, d)
        elif polje == "adresa_skole":
            s.adresa = vrijednost.strip()
        else:
            setattr(s, polje, vrijednost.strip())
        self.stanje.pitani_nalazi = {
            k for k in self.stanje.pitani_nalazi if f"s{redni_broj}" not in k
        }
        return "Ispravljeno. Pozovi provjeri_podatke."

    # ---------- Plausibilität ----------

    @function_tool
    async def provjeri_podatke(self, context: RunContext) -> str:
        """Prüft alle bisherigen Angaben auf Logikfehler (Überschneidungen, Ende vor Beginn,
        Arbeit vor 15 usw.). Liefert nur neue Auffälligkeiten; jede wird nur einmal gemeldet."""
        st = self.stanje
        dr = st.kontekst.datum_rodjenja
        if "datum_rodjenja" in st.podaci:
            dr = parse_datum(st.podaci["datum_rodjenja"], kraj=False) or dr
        nalazi = provjeri(
            st.sve_stanice, st.sve_skole, dr, st.dob_djece(), st.sada().date()
        )
        nove = [n for n in nalazi if n.kljuc not in st.pitani_nalazi]
        st.pitani_nalazi.update(n.kljuc for n in nove)
        if not nove:
            return "Sve je logično. Nastavi."
        return "Pitaj jednom, ljubazno, redom:\n" + "\n".join(
            f"[{n.kljuc}] {n.tekst}" for n in nove
        )

    @function_tool
    async def zabiljezi_objasnjenje(
        self, context: RunContext, kljuc: str, objasnjenje: str
    ) -> str:
        """Speichert die Erklärung des Kandidaten zu einer Auffälligkeit aus provjeri_podatke.

        Args:
            kljuc: Der Schlüssel in eckigen Klammern, z. B. 'L1:r1-r2'.
            objasnjenje: Was der Kandidat gesagt hat, kurz.
        """
        self.stanje.napomene_provjere[kljuc] = (objasnjenje or "").strip()
        return "Zabilježeno. Ne pitaj ponovo."

    # ---------- Zeit, Rückruf, Ende ----------

    @function_tool
    async def trenutno_vrijeme(self, context: RunContext) -> str:
        """Aktuelles Datum, Wochentag und Uhrzeit in Europe/Sarajevo."""
        dt = self.stanje.sada()
        return f"{opis(dt)}; ISO {dt.isoformat(timespec='minutes')}"

    @function_tool
    async def zakazi_povratni_poziv(
        self, context: RunContext, datum_vrijeme: str, napomena: str = ""
    ) -> str:
        """Speichert einen Rückruftermin als absolutes Datum mit Uhrzeit.

        Args:
            datum_vrijeme: ISO in Europe/Sarajevo, z. B. 2026-11-06T15:00.
            napomena: Kurzer Hinweis, z. B. 'nakon posla'.
        """
        dt = parse_termin(datum_vrijeme)
        if dt is None:
            return "Neispravan termin. Koristi YYYY-MM-DDTHH:MM."
        if dt <= self.stanje.sada():
            return "Termin je u prošlosti. Pitaj ponovo."
        self.stanje.povratni_poziv = dt
        self.stanje.povratni_poziv_napomena = (napomena or "").strip()
        return f"Termin sačuvan: {opis(dt)}. Ponovi ga kandidatu."

    @function_tool
    async def zavrsi_razgovor(
        self, context: RunContext, ishod: Ishod, sazetak: str
    ) -> str:
        """Beendet die Datenerfassung und speichert alles in Airtable. Danach end_call aufrufen.

        Args:
            ishod: Ergebnis des Gesprächs.
            sazetak: Ein Satz Zusammenfassung auf Bosnisch.
        """
        self.stanje.ishod = ishod
        self.stanje.sazetak = (sazetak or "").strip()
        try:
            await sacuvaj(self.store, self.stanje)
        except Exception:
            logger.exception(
                "Speichern fehlgeschlagen für %s", self.stanje.kontekst.record_id
            )
            return "Spremanje nije uspjelo, ali se ljubazno oprosti od kandidata. Kolege će provjeriti."
        return "Sačuvano. Zahvali se, ljubazno se oprosti i pozovi end_call."
