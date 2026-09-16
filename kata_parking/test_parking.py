from kata_parking.parking import calculer_tarif, calculer_tarif_entre
import pytest
from datetime import datetime


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

def test_stationnement_trente_et_une_minutes_abonne_coute_quatre_vingt_dix_centimes():
    assert calculer_tarif(31, abonne=True) == 0.90

def test_stationnement_huit_heures_abonne_coute_dix_euros_quatre_vingts():
    assert calculer_tarif(8 * 60, abonne=True) == 10.80

def test_stationnement_soixante_minutes_electrique_branche_est_gratuit():
    assert calculer_tarif(60, electrique_branche=True) == 0

def test_stationnement_soixante_et_une_minutes_electrique_branche_abonne_coute_quatre_vingt_dix_centimes():
    assert calculer_tarif(61, abonne=True, electrique_branche=True) == 0.90

def test_stationnement_duree_negative_leve_une_erreur_explicite():
    with pytest.raises(ValueError, match="La durée ne peut pas être négative"):
        calculer_tarif(-1)

def test_sortie_avant_entree_leve_une_erreur_explicite():
    entree = datetime(2026, 9, 16, 10, 0)
    sortie = datetime(2026, 9, 16, 9, 0)

    with pytest.raises(ValueError, match="La sortie ne peut pas précéder l'entrée"):
        calculer_tarif_entre(entree, sortie)

def test_stationnement_entre_deux_dates_espacees_de_trente_et_une_minutes_coute_un_euro_cinquante():
    entree = datetime(2026, 9, 16, 10, 0)
    sortie = datetime(2026, 9, 16, 10, 31)

    assert calculer_tarif_entre(entree, sortie) == 1.50

def test_stationnement_depassant_soixante_douze_heures_coute_deux_cent_cinquante_euros():
    assert calculer_tarif(72 * 60 + 1) == 250
