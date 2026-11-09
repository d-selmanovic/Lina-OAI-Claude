"""Provjera iz onoga što je kandidat rekao, bez čekanja da model pozove alat."""

from __future__ import annotations

import re
import unicodedata

from .datumi import parse_datum
from .kontekst import Stanica

_SKOLA = ("skol", "gimnaz", "fakultet", "univerzitet", "akademij")
_KRATKO = {
    "da",
    "ne",
    "imam",
    "nemam",
    "moze",
    "aha",
    "dobro",
    "ok",
    "u redu",
    "jesam",
    "nisam",
    "tako je",
}
# (riječ u govoru, riječ koja mora postojati u već upisanim poslovima)
_TVRDNJE = (
    ("masin", "masin"),
    ("bager", "bager"),
    ("rovokop", "rovokop"),
    ("buldoz", "buldoz"),
    ("utovariv", "utovariv"),
    ("kamion", "kamion"),
    ("optik", "optik"),
)
_ORDINAL = {
    "deset": 10,
    "desete": 10,
    "jedanaest": 11,
    "jedanaeste": 11,
    "dvanaest": 12,
    "dvanaeste": 12,
    "trinaest": 13,
    "trinaeste": 13,
    "cetrnaest": 14,
    "cetrnaeste": 14,
    "petnaest": 15,
    "petnaeste": 15,
    "sesnaest": 16,
    "sesnaeste": 16,
    "sedamnaest": 17,
    "sedamnaeste": 17,
    "osamnaest": 18,
    "osamnaeste": 18,
    "devetnaest": 19,
    "devetnaeste": 19,
    "dvadeset": 20,
    "dvadesete": 20,
    "dvadeset jedan": 21,
    "dvadeset prve": 21,
    "dvadeset dva": 22,
    "dvadeset druge": 22,
    "dvadeset tri": 23,
    "dvadeset trece": 23,
    "dvadeset cetiri": 24,
    "dvadeset cetvrte": 24,
    "dvadeset pet": 25,
    "dvadeset pete": 25,
    "dvadeset sest": 26,
    "dvadeset seste": 26,
}


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()


def izgleda_kao_skola(naziv: str) -> bool:
    f = fold(naziv)
    return any(w in f for w in _SKOLA)


def godine_iz_teksta(tekst: str) -> list[int]:
    f = fold(tekst)
    nasao = [int(x) for x in re.findall(r"\b(?:19|20)\d{2}\b", f)]
    if "dvije hiljade" in f or "dve hiljade" in f:
        for rijec, n in sorted(_ORDINAL.items(), key=lambda kv: -len(kv[0])):
            if rijec in f:
                nasao.append(2000 + n)
                break
    return sorted(set(nasao))


def _kratko(tekst: str) -> bool:
    return fold(tekst).strip(" .!?") in _KRATKO


def pitanje_skola(tekst: str, prethodno: str) -> str:
    if _kratko(tekst):
        return ""
    if "skol" not in fold(prethodno) and "skol" not in fold(tekst):
        return ""
    if izgleda_kao_skola(tekst):
        return ""
    ime = " ".join(tekst.split())
    if len(fold(ime)) < 4:
        return ""
    return (
        f"Samo da provjerim — „{ime}“ je škola u tom gradu? "
        "Ako nije, reci pravi naziv."
    )


def pitanje_preklapanje(tekst: str, stanice: list[Stanica]) -> str:
    godine = godine_iz_teksta(tekst)
    if not godine:
        return ""
    nova = Stanica(
        "novi",
        "novi",
        parse_datum(str(min(godine)), kraj=False),
        parse_datum(str(max(godine)), kraj=True),
    )
    from datetime import date

    from .plausibilitaet import provjeri

    for n in provjeri([*stanice, nova], [], None, [], date(2026, 11, 9)):
        if n.pravilo == "L1":
            return n.tekst + " Je li bilo paralelno, ili je godina pogrešna?"
    if len(godine) == 1:
        y = godine[0]
        for s in stanice:
            if s.od and s.do and s.od.datum.year < y < s.do.datum.year:
                return (
                    f"Godina {y} je unutar posla „{s.kratko()}“. "
                    "Je li to isti posao, ili drugi u isto vrijeme?"
                )
    return ""


def pitanje_tvrdnja(tekst: str, stanice: list[Stanica], poznato: list[str]) -> str:
    f = fold(tekst)
    blob = fold(" ".join(poznato + [s.pozicija + " " + s.poslodavac for s in stanice]))
    for rijec, u_listi in _TVRDNJE:
        if rijec in f and u_listi not in blob:
            return (
                "U prijavi toga nema. Jesi to radio negdje što nisi naveo? "
                "Reci firmu i godine. Ne smiju se preklapati s poslovima koji već pišu."
            )
    return ""


def obavezno_pitanje(
    tekst: str,
    prethodno: str,
    stanice: list[Stanica],
    poznato: list[str],
    pitano: set[str],
) -> str:
    for kljuc, q in (
        ("GOVOR:preklop", pitanje_preklapanje(tekst, stanice)),
        ("GOVOR:skola", pitanje_skola(tekst, prethodno)),
        ("GOVOR:tvrdnja", pitanje_tvrdnja(tekst, stanice, poznato)),
    ):
        if q and kljuc not in pitano:
            pitano.add(kljuc)
            return q
    return ""
