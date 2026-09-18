"""D3 : bornes des paliers, ancienne configuration et application complète."""

from datetime import date

import pytest

from facturation.abonnements import Abonnement
from facturation.assemblage import EmetteurDeFactures
from facturation.registre import tarification
from facturation.tarifs import TARIFICATION_ORIGINE, Tarification
from facturation.test_emission import CourrielsEnMemoire


@pytest.mark.parametrize(
    "postes,taux",
    [
        (1, 0.0),
        (9, 0.0),
        (10, 0.10),
        (49, 0.10),
        (50, 0.20),
        (199, 0.20),
        (200, 0.30),
        (201, 0.30),
        (500, 0.30),
    ],
)
def test_volume_200_et_anciens_seuils_inclusifs(postes, taux):
    assert tarification.taux_de_remise_volume(postes) == taux


def test_configuration_historique_independante():
    assert TARIFICATION_ORIGINE.taux_de_remise_volume(500) == 0.20
    assert Tarification().taux_de_remise_volume(500) == 0.20
    assert tarification.taux_de_remise_volume(500) == 0.30


def test_les_trois_extensions_se_composent_dans_la_facture():
    emetteur = EmetteurDeFactures()
    emetteur.passerelle = CourrielsEnMemoire()
    facture = emetteur.emettre(
        Abonnement("Client", "decouverte", 200, date(2026, 1, 1)),
        "client@example.org",
        "RENTREE",
    )
    assert (facture.montant_ht, facture.montant_ttc) == (504.0, 604.8)
