"""D2 : réduction inconditionnelle et ordre de calcul."""

from datetime import date

import pytest

from facturation.abonnements import Abonnement
from facturation.assemblage import EmetteurDeFactures
from facturation.registre import tarification
from facturation.tarifs import CodePromoInconnu
from facturation.test_emission import CourrielsEnMemoire


@pytest.mark.parametrize("premiere", [True, False])
def test_rentree_retire_dix_pour_cent_sur_toute_facture(premiere):
    assert tarification.appliquer_code_promo(100.0, "RENTREE", premiere) == 90.0


def test_rentree_apres_volume_et_avant_tva():
    emetteur = EmetteurDeFactures()
    emetteur.passerelle = CourrielsEnMemoire()
    facture = emetteur.emettre(
        Abonnement("Client", "pro", 10, date(2026, 1, 1)), "client@example.org", "RENTREE"
    )
    assert (facture.montant_ht, facture.montant_ttc) == (153.9, 184.68)


@pytest.mark.parametrize(
    "code,premiere,attendu",
    [
        (None, False, 100.0),
        ("BIENVENUE", True, 95.0),
        ("BIENVENUE", False, 100.0),
        ("NOEL", False, 85.0),
    ],
)
def test_promotions_historiques_preservees(code, premiere, attendu):
    assert tarification.appliquer_code_promo(100.0, code, premiere) == attendu


def test_code_inconnu_toujours_refuse():
    with pytest.raises(CodePromoInconnu):
        tarification.appliquer_code_promo(100.0, "PAQUES", False)


def test_bienvenue_ne_produit_pas_un_montant_negatif():
    assert tarification.appliquer_code_promo(4.0, "BIENVENUE", True) == 0.0
