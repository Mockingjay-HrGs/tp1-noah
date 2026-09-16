from kata_parking.parking import calculer_tarif


def test_stationnement_une_minute_est_gratuit():
    assert calculer_tarif(1) == 0