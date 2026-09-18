"""Le métier se teste sans SMTP ni horloge globale."""

from datetime import date

from facturation.abonnements import Abonnement
from facturation.facture import EmetteurDeFactures, Facture, calculer_facture
from facturation.presentation import corps_de_facture


class CourrielsEnMemoire:
    messages = None

    def envoyer_courriel(self, destinataire, sujet, corps):
        self.messages = (destinataire, sujet, corps)


def contrat():
    return Abonnement("Dupont SARL", "pro", 3, date(2019, 1, 1))


def test_destinataire_et_sujet_sans_reseau():
    courriels = CourrielsEnMemoire()
    emetteur = EmetteurDeFactures(courriels, lambda: date(2019, 6, 1), corps_de_facture)
    facture = emetteur.emettre(contrat(), "compta@dupont.fr")
    assert courriels.messages == (
        "compta@dupont.fr",
        "Votre facture FA-2019-0001",
        corps_de_facture(facture, contrat()),
    )


def test_numero_et_date_portent_2019():
    emetteur = EmetteurDeFactures(CourrielsEnMemoire(), lambda: date(2019, 6, 1), corps_de_facture)
    premiere = emetteur.emettre(contrat(), "compta@dupont.fr")
    seconde = emetteur.emettre(contrat(), "compta@dupont.fr")
    assert (premiere.numero, seconde.numero) == ("FA-2019-0001", "FA-2019-0002")
    assert premiere.emise_le == date(2019, 6, 1)


def test_corps_exact_sans_envoi():
    facture = Facture("FA-2019-0001", "Dupont SARL", date(2019, 6, 1), 57.0, 68.4)
    assert corps_de_facture(facture, contrat()) == (
        "Facture FA-2019-0001\n"
        "Client        : Dupont SARL\n"
        "Emise le      : 2019-06-01\n"
        "Formule       : pro, 3 postes\n"
        "Montant HT    : 57.00\n"
        "Montant TTC   : 68.40"
    )


def test_calcul_independant_de_la_presentation():
    facture = calculer_facture(contrat(), "FA-2019-0001", date(2019, 6, 1))
    assert (facture.montant_ht, facture.montant_ttc) == (57.0, 68.4)
