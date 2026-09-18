"""Emission des factures d'abonnement."""

from dataclasses import dataclass
from datetime import date
from collections.abc import Callable
from typing import Protocol

from facturation.abonnements import Abonnement
from facturation.tarifs import TARIFICATION_ORIGINE

PREFIXE_DE_NUMERO = "FA"


@dataclass
class Facture:
    numero: str
    client: str
    emise_le: date
    montant_ht: float
    montant_ttc: float


def calculer_facture(  # noqa: PLR0913 - contexte explicite, configuration optionnelle
    abonnement, numero, emise_le, promotion=(None, False), *, tarification=TARIFICATION_ORIGINE
) -> Facture:
    code_promo, premiere_facture = promotion
    return Facture(
        numero=numero,
        client=abonnement.client,
        emise_le=emise_le,
        montant_ht=tarification.montant_hors_taxe(abonnement, code_promo, premiere_facture),
        montant_ttc=tarification.montant_toutes_taxes(abonnement, code_promo, premiere_facture),
    )


class EnvoiDeCourriel(Protocol):
    """Seul service de communication requis par le client facturation."""

    def envoyer_courriel(self, destinataire: str, sujet: str, corps: str) -> None: ...


class EmetteurDeFactures:
    """Coordonne le calcul et les ports injectés."""

    def __init__(
        self,
        passerelle: EnvoiDeCourriel,
        aujourd_hui: Callable[[], date],
        presenter: Callable[[Facture, Abonnement], str],
        calculer: Callable[..., Facture] = calculer_facture,
    ) -> None:
        self.compteur = 0
        self.passerelle = passerelle
        self.aujourd_hui = aujourd_hui
        self.presenter = presenter
        self.calculer = calculer

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
        emise_le = self.aujourd_hui()
        facture = self.calculer(
            abonnement, self.numeroter(emise_le), emise_le, (code_promo, premiere_facture)
        )
        corps = self.presenter(facture, abonnement)
        self.passerelle.envoyer_courriel(adresse, f"Votre facture {facture.numero}", corps)
        return facture
