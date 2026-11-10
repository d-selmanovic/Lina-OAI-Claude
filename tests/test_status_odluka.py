"""Status nach dem Anruf: der Code entscheidet, nicht das Modell."""

from lina.status_odluka import odluka


def test_odustao_nur_wenn_alle_drei_explizit():
    assert (
        odluka(
            javio_se=True,
            zainteresiran="ne",
            negativan_komentar="da",
            iskustvo_u_poslu="ne",
            licni_popunjeni=False,
            diploma=False,
            pasos=False,
            foto=False,
            trenutni_status="",
        )
        == "Odustao"
    )


def test_eine_datei_ist_zeleni_nicht_precasting():
    assert (
        odluka(
            javio_se=True,
            zainteresiran="da",
            negativan_komentar="ne",
            iskustvo_u_poslu="da",
            licni_popunjeni=False,
            diploma=False,
            pasos=False,
            foto=True,
            trenutni_status="",
        )
        == "Zeleni / obrada"
    )


def test_alle_drei_dokumente_sind_precasting():
    assert (
        odluka(
            javio_se=True,
            zainteresiran="da",
            negativan_komentar="ne",
            iskustvo_u_poslu="nepoznato",
            licni_popunjeni=False,
            diploma=True,
            pasos=True,
            foto=True,
            trenutni_status="NE JAVLJA SE",
        )
        == "Pre-casting"
    )


def test_interessiert_ohne_daten_und_dateien_ist_zainteresiran():
    assert (
        odluka(
            javio_se=True,
            zainteresiran="da",
            negativan_komentar="ne",
            iskustvo_u_poslu="da",
            licni_popunjeni=False,
            diploma=False,
            pasos=False,
            foto=False,
            trenutni_status="New Lead",
        )
        == "Zainteresiran"
    )


def test_interessiert_mit_licnim_podacima_ist_zeleni():
    assert (
        odluka(
            javio_se=True,
            zainteresiran="da",
            negativan_komentar="ne",
            iskustvo_u_poslu="da",
            licni_popunjeni=True,
            diploma=False,
            pasos=False,
            foto=False,
            trenutni_status="",
        )
        == "Zeleni / obrada"
    )


def test_nicht_abgehoben_ist_ne_javlja_se():
    assert (
        odluka(
            javio_se=False,
            zainteresiran="nepoznato",
            negativan_komentar="nepoznato",
            iskustvo_u_poslu="nepoznato",
            licni_popunjeni=False,
            diploma=False,
            pasos=False,
            foto=False,
            trenutni_status="",
        )
        == "NE JAVLJA SE"
    )


def test_spaeteren_stapel_nicht_ueberschreiben():
    assert (
        odluka(
            javio_se=True,
            zainteresiran="da",
            negativan_komentar="ne",
            iskustvo_u_poslu="da",
            licni_popunjeni=True,
            diploma=True,
            pasos=True,
            foto=True,
            trenutni_status="Casting",
        )
        is None
    )


def test_odustao_faellt_weg_wenn_ein_fakt_unklar():
    assert (
        odluka(
            javio_se=True,
            zainteresiran="ne",
            negativan_komentar="nepoznato",
            iskustvo_u_poslu="ne",
            licni_popunjeni=False,
            diploma=False,
            pasos=False,
            foto=False,
            trenutni_status="",
        )
        is None
    )
