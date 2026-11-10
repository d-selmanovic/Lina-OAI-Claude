"""Gesprächszustand: was Lina im Gespräch erfasst. Wird erst am Ende geschrieben."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from .kontekst import Kontekst, Skola, Stanica

Ishod = Literal[
    "zavrseno",  # Datenerfassung abgeschlossen
    "djelimicno",  # ein Teil erfasst, Kandidat musste weg
    "povratni_poziv",  # Rückruf vereinbart
    "nije_zainteresiran",
    "ne_zovite_vise",  # Opt-out
    "pogresna_osoba",
    "prekinuto",  # Verbindung abgebrochen / kein ordentliches Ende
]


@dataclass
class Stanje:
    kontekst: Kontekst
    podaci: dict[str, str] = field(default_factory=dict)
    nove_stanice: list[Stanica] = field(default_factory=list)
    nove_skole: list[Skola] = field(default_factory=list)
    napomene_provjere: dict[str, str] = field(
        default_factory=dict
    )  # kljuc -> odgovor kandidata
    pitani_nalazi: set[str] = field(default_factory=set)
    povratni_poziv: datetime | None = None
    povratni_poziv_napomena: str = ""
    ishod: Ishod | None = None
    sazetak: str = ""
    transkript: str = ""
    polja: dict = field(default_factory=dict)
    zainteresiran: str = "nepoznato"
    negativan_komentar: str = "nepoznato"
    iskustvo_u_poslu: str = "nepoznato"
    sacuvano: bool = False
    zapisane_tabele: set[str] = field(
        default_factory=set
    )  # für Wiederholung ohne Duplikate
    sprema_u_toku: bool = False
    fiksno_vrijeme: datetime | None = None  # nur Simulation: Uhr fixieren

    def sada(self) -> datetime:
        from .zeit import sada

        return self.fiksno_vrijeme or sada()

    @property
    def sve_stanice(self) -> list[Stanica]:
        return [*self.kontekst.stanice, *self.nove_stanice]

    @property
    def sve_skole(self) -> list[Skola]:
        return [*self.kontekst.skole, *self.nove_skole]

    def ishod_bez_kraja(self) -> Ishod:
        """Ishod, wenn das Gespräch ohne zavrsi_razgovor endet (Leitung weg, Auflegen).

        Ein Rückruftermin oder schon gespeicherte Angaben sind kein Abbruch:
        sonst ruft der Dispatcher den Kandidaten erneut an und fragt alles noch einmal.
        """
        if self.povratni_poziv is not None:
            return "povratni_poziv"
        if self.podaci or self.nove_stanice or self.nove_skole:
            return "djelimicno"
        return "prekinuto"

    def dob_djece(self) -> list[int]:
        return [
            int(x)
            for x in self.podaci.get("dob_djece", "").split(",")
            if x.strip().isdigit()
        ]
