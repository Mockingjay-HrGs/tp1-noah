from kata_parking.parking import calculer_tarif


def test_stationnement_une_minute_est_gratuit():
    assert calculer_tarif(1) == 0

def test_stationnement_trente_minutes_est_gratuit():
    assert calculer_tarif(30) == 0

def test_stationnement_trente_et_une_minutes_coute_un_euro_cinquante():
    assert calculer_tarif(31) == 1.50

def test_stationnement_soixante_minutes_coute_un_euro_cinquante():
    assert calculer_tarif(60) == 1.50