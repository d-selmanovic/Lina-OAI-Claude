"""Airtable-IDs und Fragenkatalog für Anruf 1.

Alle IDs stammen aus dem Schema der Base „GIG Casting“ (gelesen am 05.11.2026).
Im Code werden immer Field-IDs verwendet, nie Feldnamen. Siehe docs/airtable.md.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

TIMEZONE = "Europe/Sarajevo"

BASE_ID = os.getenv("AIRTABLE_BASE_ID", "appz3VFomHaWhuILV")
T_PRIJAVE = os.getenv("AIRTABLE_TABLE", "tbl7WHRtBkRX7tGxt")
T_DOPUNE = "tblzvtVFXZHFgk8mq"
T_RADNO_ISKUSTVO = "tblbRG7v8pTRqVTqH"
T_OBRAZOVANJE = "tblyAQ6ud95RW76Ym"
T_TERMINI = "tblMTxAh92crqggAY"
T_POZIVI = "tblXnTENm7kts7wwT"


class P:
    """Felder in `Prijave (test)`."""

    IME_PREZIME = "fldYKnT4AgUTYWRvG"
    IME = "fldlWTDSvVwiOZDmM"
    SIFRA = "fldFtCLmRLempwjls"
    POZIVNI = "fldHiAvs5PSf1mIVY"
    TELEFON = "fldydnGFUIkAGolln"
    STATUS_KANDIDATA = "fldio94d9MyPTN6ZI"
    DOKUMENTI = "fldk4qbnRt5gBcd8U"
    SVJEDOCANSTVA = "fldvyFpU2ucXmtaXi"
    PASOS = "fldLJQ2VYmf4j7JtO"
    FOTO = "fldfquHbXCqyobesM"
    LICNI_NEDOSTAJE = "fldkpncNkxR0efZv4"
    EMAIL = "fldp01HZxgHta8bwB"
    DATUM_RODJENJA_TXT = "fld6qFZGy2q1yfcnw"
    DATUM_RODJENJA_DATE = "fldmIHxbcAnWNeNi4"
    MJESTO_RODJENJA = "fldUkAy58bac8Pwnq"
    ADRESA = "fldmYZHIjf6r4DXua"
    ULICA = "fldOQYwJ6iJSgu4Xk"
    DRZAVLJANSTVO = "fldQCU77iYMy8gFS8"
    VOZACKA = "fldWFnqeYiukLviK9"
    STATUS_BORAVKA = "flducCUvS6Rny8wi4"
    RADNA_DOZVOLA = "fldwC9YtkIbvWmNqF"
    BRACNO_STANJE = "fldzjkTLkwg3UBMIu"
    VJESTINE = "fldfDNDkxydD1A7Vd"
    NJEMACKI_TXT = "fldjoM8wtCi3IOm4E"
    # Flache Altfelder (Excel-Import) – nur als „schon bekannt“ gelesen
    RADNO_MJESTO = "fld1qJ6uYZ7HKsXuU"
    KOMPANIJA = "fldeiamQZD6JaQE2r"
    RI_OD = "fld89KIp3njkrB6aT"
    RI_DO = "fldJMsJXNZgMJ3q0f"
    SKOLA_TXT = "fldczOviQFhemuJ9u"
    STRUKA_TXT = "fldV8JGvCxQ1cHHku"
    # Verknüpfungen
    L_RADNO_ISKUSTVO = "fldo5G5GN1fUDBL0L"
    L_OBRAZOVANJE = "fldfmH3wCy4G8MW6H"
    L_DOPUNE = "fldK7uywuxbPhzjGH"


class D:
    """Felder in `Dopune`."""

    SIFRA = "fldmOjzIemaOoizeT"
    KANDIDAT = "fldDZ1Ik9Xq7vm0f3"
    STATUS_PREGLEDA = "fldLmjPcpFyO6O1Ro"
    IME_PREZIME = "fldUM6wlglPiEmJyA"
    EMAIL = "fldeupT7JwNy8ptF8"
    DATUM_RODJENJA = "fldu9PeuryqF2fyYB"
    MJESTO_RODJENJA = "fldWq7AC3PDMsmwXj"
    ADRESA = "fldvmWSmbjk4FThA3"
    DRZAVLJANSTVO = "fldniTfnsKFYqFvzh"
    VOZACKA = "fldoeHwM4FaEwjvzQ"
    STATUS_BORAVKA = "fldxKNjPUZnC5uUyO"
    RADNA_DOZVOLA = "fldhrlSRrRjSKmKwV"
    BRACNO_STANJE = "fldPxRjuxvzUJZQ3x"
    VJESTINE = "fldnmlWmCl0ZnRLTg"
    OPIS = "fldejrE05pgkiVOY1"  # Langtext: Notizen von Lina (siehe docs/airtable.md)
    RI1_RADNO_MJESTO = "fldD65rvVT5Qn7RKY"
    SKOLA = "fld6GOMBwJf0CZlK7"


DOPUNE_ODBACENO = "Odbačeno"
DOPUNE_NOVO = "Novo"


class RI:
    """Felder in `Radno iskustvo`."""

    ISKUSTVO = "fldwlNb6f1clrXYif"
    POSLODAVAC = "fldfQs3YfasbRTAKg"
    POZICIJA = "fldYu8suwnxW6GHpL"
    OD = "fldMyV3yGH1hF5I4W"
    DO = "fldCOLGYk0xN7KkZq"
    AKTUELNO = "fld17ykYCTnxjThcl"
    GRAD = "fld4sIgNlpVfOg0HL"
    DRZAVA = "fldBBYN874H3UrW6C"
    OPIS = "fld6zQPRMp0Kkreqx"
    KANDIDAT = "fldZQZunKe7uh3Crr"


class OB:
    """Felder in `Obrazovanje`."""

    SKOLA = "fldCwehP7M1X1slOV"
    ADRESA_SKOLE = "fldDtFyWWvksX6SBs"
    OD = "fldHpNrqUfgU9IYU2"
    DO = "fldP9YwCVp537xF4w"
    KANDIDAT = "fldkiFDfqWQCmF0RQ"


class TZ:
    """Felder in `Termini i zadaci`."""

    NAME = "fldmDFr4wrmHeCeUf"
    NOTES = "fldTFWPPp6QzfVpcY"
    STATUS = "fldDwJ4reS4vPQuPk"
    DATUM = "flddFKVyAQSrGVWPw"
    KANDIDAT = "fldKD3UcAbSdArmra"


@dataclass(frozen=True)
class Pitanje:
    """Eine Angabe, die Lina abfragt – aber nur, wenn sie leer ist."""

    key: str
    label: str  # bosnisch, für die Instruktionen
    prijave: tuple[str, ...] = ()  # gefüllt in einem dieser Felder = vorhanden
    dopune: str | None = None  # gefüllt in offener Dopune = vorhanden; Schreibziel
    abfragen: bool = True


# Reihenfolge = Gesprächsreihenfolge. `abfragen=False` schaltet eine Frage ab.
# Djeca, Njemački/Engleski-Niveau haben noch kein eigenes Airtable-Feld
# (Vorschlag in docs/airtable.md); bis dahin landen sie in der Dopune-Notiz.
PITANJA: tuple[Pitanje, ...] = (
    Pitanje(
        "radno_iskustvo",
        "radno iskustvo (sva radna mjesta)",
        (P.L_RADNO_ISKUSTVO,),
        D.RI1_RADNO_MJESTO,
    ),
    Pitanje("obrazovanje", "školovanje (sve škole)", (P.L_OBRAZOVANJE,), D.SKOLA),
    Pitanje("njemacki", "znanje njemačkog jezika", (P.NJEMACKI_TXT,)),
    Pitanje("engleski", "znanje engleskog jezika"),
    Pitanje("vozacka", "vozačka dozvola (kategorije)", (P.VOZACKA,), D.VOZACKA),
    Pitanje("status_boravka", "status boravka", (P.STATUS_BORAVKA,), D.STATUS_BORAVKA, abfragen=False),
    Pitanje("radna_dozvola", "radna dozvola", (P.RADNA_DOZVOLA,), D.RADNA_DOZVOLA, abfragen=False),
    Pitanje("drzavljanstvo", "državljanstvo", (P.DRZAVLJANSTVO,), D.DRZAVLJANSTVO),
    Pitanje(
        "datum_rodjenja",
        "datum rođenja",
        (P.DATUM_RODJENJA_TXT, P.DATUM_RODJENJA_DATE),
        D.DATUM_RODJENJA,
    ),
    Pitanje(
        "mjesto_rodjenja", "mjesto rođenja", (P.MJESTO_RODJENJA,), D.MJESTO_RODJENJA
    ),
    Pitanje("adresa", "adresa stanovanja", (P.ADRESA, P.ULICA), D.ADRESA),
    Pitanje("bracno_stanje", "bračno stanje", (P.BRACNO_STANJE,), D.BRACNO_STANJE),
    Pitanje("djeca", "djeca (da/ne, koliko, koliko godina)"),
    Pitanje("email", "e-mail adresa", (P.EMAIL,), D.EMAIL),
    Pitanje("vjestine", "posebne vještine", (P.VJESTINE,), D.VJESTINE),
)

PITANJA_PO_KLJUCU = {p.key: p for p in PITANJA}


class PZ:
    """Felder in `Pozivi Lina`. IDs aus einem echten Datensatz gelesen."""

    OZNAKA = "fldPhgstZr2w0jWh0"
    DATUM = "fldnTzrg7Hr0JXbXX"
    SAZETAK = "fld2zR95HuXrH9n3U"
    ISHOD = "fld2x5xef6sTSqKxN"
    OKRUZENJE = "fldXBshsogj5bAmyg"
    KANDIDAT = "fldDpduprNvEcngxr"
    LINK = "fld1cRL36FOnMHXRT"
