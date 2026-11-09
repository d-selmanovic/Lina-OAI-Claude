"""Provjera škole i ulice. None = mreža pala, ne pitaj. False = nema pogotka, pitaj jednom."""

from __future__ import annotations

import json
import re
import unicodedata
import urllib.parse
import urllib.request

_UA = "JobStep-Lina/1.0 (plausibilnost adrese)"
_CACHE: dict[str, list | None] = {}
_STOP = {
    "skola",
    "osnovna",
    "srednja",
    "gimnazija",
    "fakultet",
    "ulica",
    "ul",
    "bb",
    "br",
    "broj",
    "bih",
    "bosna",
    "hercegovina",
    "bosne",
    "i",
}
_LAZNO = re.compile(
    r"(?i)\b(test+|asdf+|qwerty+|xxx+|abcd+|lazn\w*|izmišljen\w*|izmisljen\w*"
    r"|nepostojeć\w*|nepostojec\w*)\b"
)


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()


def ocigledno_lazno(tekst: str) -> bool:
    return bool(_LAZNO.search(_fold(tekst)))


def tokeni(tekst: str, *jos_stop: str) -> list[str]:
    stop = _STOP | {_fold(x) for x in jos_stop if x}
    out = []
    for raw in re.findall(r"[a-z0-9]{4,}", _fold(tekst)):
        if raw in stop or raw.isdigit():
            continue
        out.append(raw)
    return out


def rastavi_adresu(tekst: str) -> tuple[str, str]:
    """Ulica i grad. Grad je dio iza zareza, ako ga ima."""
    s = (tekst or "").strip()
    if "," in s:
        ulica, grad = s.rsplit(",", 1)
        return ulica.strip(), grad.strip()
    return s, ""


def _upit(params: dict) -> list | None:
    key = urllib.parse.urlencode(sorted(params.items()))
    if key in _CACHE:
        return _CACHE[key]
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {**params, "format": "json", "addressdetails": 1, "limit": 3, "countrycodes": "ba"}
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=4) as r:
            data = json.loads(r.read().decode())
    except Exception:
        _CACHE[key] = None
        return None
    _CACHE[key] = data if isinstance(data, list) else []
    return _CACHE[key]


def _ima_tokene(data: list, treba: list[str], polja: tuple[str, ...]) -> bool:
    if not treba:
        return False
    for d in data:
        addr = d.get("address") or {}
        blob = " ".join(_fold(str(d.get(p) or addr.get(p) or "")) for p in polja)
        blob += " " + _fold(d.get("display_name") or "")
        if all(t in blob for t in treba):
            return True
    return False


def skola_u_gradu(naziv: str, grad: str = "") -> bool | None:
    """True = naziv nađen. False = nema. None = mreža. Previše općenito = True (ne optužuj)."""
    if ocigledno_lazno(naziv) or ocigledno_lazno(grad):
        return False
    treba = tokeni(naziv, grad)
    if not treba:
        return True
    data = _upit({"q": f"{naziv} {grad}".strip()})
    if data is None:
        return None
    return _ima_tokene(data, treba, ("name", "road"))


def ulica_u_gradu(adresa: str) -> bool | None:
    """True = ulica u tom gradu. False = nema. None = mreža. Samo grad, bez ulice = True."""
    if ocigledno_lazno(adresa):
        return False
    ulica, grad = rastavi_adresu(adresa)
    ulica = re.sub(r"\b\d+\w?\b", " ", ulica)
    ulica = re.sub(r"(?i)\b(ulica|ul\.?|bb)\b", " ", ulica)
    ulica = " ".join(ulica.split())
    treba = tokeni(ulica, grad)
    if not treba or not grad:
        return True
    data = _upit(
        {
            "street": ulica,
            "city": grad,
            "country": "Bosnia and Herzegovina",
        }
    )
    if data is None:
        return None
    return _ima_tokene(data, treba, ("road", "pedestrian", "residential", "name"))
