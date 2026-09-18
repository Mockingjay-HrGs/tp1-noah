"""D1 : prix, anciennes formules et intégration dans une facture."""

from datetime import date

import pytest

from facturation.abonnements import Abonnement
from facturation.assemblage import EmetteurDeFactures
from facturation.registre import tarification
from facturation.tarifs import FormuleInconnue
from facturation.test_emission import CourrielsEnMemoire


def test_decouverte_coute_quatre_euros_par_poste():
    assert tarification.prix_par_poste("decouverte") == 4.0


@pytest.mark.parametrize("formule,prix", [("essentiel", 9.0), ("pro", 19.0), ("entreprise", 39.0)])
def test_anciens_prix_preserves(formule, prix):
    assert tarification.prix_par_poste(formule) == prix


def test_formule_inconnue_toujours_refusee():
    with pytest.raises(FormuleInconnue):
        tarification.prix_par_poste("platine")


def test_facture_decouverte_utilise_le_catalogue_etendu():
    emetteur = EmetteurDeFactures()
    courriels = CourrielsEnMemoire()
    emetteur.passerelle = courriels
    facture = emetteur.emettre(
        Abonnement("Client", "decouverte", 3, date(2026, 1, 1)), "client@example.org"
    )
    assert (facture.montant_ht, facture.montant_ttc) == (12.0, 14.4)
    assert courriels.messages[0] == "client@example.org"
