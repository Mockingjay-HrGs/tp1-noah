from kata_parking.parking import calculer_tarif


def test_stationnement_une_minute_est_gratuit():
    assert calculer_tarif(1) == 0

def test_stationnement_trente_minutes_est_gratuit():
    assert calculer_tarif(30) == 0

def test_stationnement_trente_et_une_minutes_coute_un_euro_cinquante():
    assert calculer_tarif(31) == 1.50

def test_stationnement_soixante_minutes_coute_un_euro_cinquante():
    assert calculer_tarif(60) == 1.50

def test_stationnement_soixante_et_une_minutes_coute_trois_euros():
    assert calculer_tarif(61) == 3

def test_stationnement_cent_vingt_minutes_coute_quatre_euros_cinquante():
    assert calculer_tarif(120) == 4.50

def test_stationnement_huit_heures_est_plafonne_a_dix_huit_euros():
    assert calculer_tarif(8 * 60) == 18

def test_stationnement_vingt_cinq_heures_coute_trente_six_euros():
    assert calculer_tarif(25 * 60) == 36

def test_stationnement_exactement_vingt_quatre_heures_coute_dix_huit_euros():
    assert calculer_tarif(24 * 60) == 18

def test_stationnement_vingt_quatre_heures_et_une_minute_coute_trente_six_euros():
    assert calculer_tarif(24 * 60 + 1) == 36