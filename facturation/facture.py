"""Emission des factures d'abonnement."""

from dataclasses import dataclass
from datetime import date, datetime

from facturation.abonnements import Abonnement
from facturation.passerelles import ClientSMTP
from facturation.presentation import corps_de_facture
from facturation.tarifs import montant_hors_taxe, montant_toutes_taxes

PREFIXE_DE_NUMERO = "FA"


@dataclass
class Facture:
    numero: str
    client: str
    emise_le: date
    montant_ht: float
    montant_ttc: float


def calculer_facture(abonnement, numero, emise_le, promotion=(None, False)) -> Facture:
    code_promo, premiere_facture = promotion
    return Facture(
        numero=numero,
        client=abonnement.client,
        emise_le=emise_le,
        montant_ht=montant_hors_taxe(abonnement, code_promo, premiere_facture),
        montant_ttc=montant_toutes_taxes(abonnement, code_promo, premiere_facture),
    )


class EmetteurDeFactures:
    """Calcule, met en forme et envoie les factures."""

    def __init__(self) -> None:
        self.compteur = 0
        self.passerelle = ClientSMTP()

    def numeroter(self, emise_le: date) -> str:
        self.compteur += 1
        return f"{PREFIXE_DE_NUMERO}-{emise_le.year}-{self.compteur:04d}"

    def emettre(
        self,
        abonnement: Abonnement,
        adresse: str,
        code_promo: str | None = None,
        premiere_facture: bool = False,
    ) -> Facture:
        emise_le = datetime.now().date()
        facture = calculer_facture(
            abonnement, self.numeroter(emise_le), emise_le, (code_promo, premiere_facture)
        )
        corps = corps_de_facture(facture, abonnement)
        self.passerelle.envoyer_courriel(adresse, f"Votre facture {facture.numero}", corps)
        return facture
