"""Emission des factures d'abonnement."""

from dataclasses import dataclass
from datetime import date, datetime

from facturation.abonnements import Abonnement
from facturation.passerelles import ClientSMTP
from facturation.tarifs import montant_hors_taxe, montant_toutes_taxes

PREFIXE_DE_NUMERO = "FA"


@dataclass
class Facture:
    numero: str
    client: str
    emise_le: date
    montant_ht: float
    montant_ttc: float


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
        facture = Facture(
            numero=self.numeroter(emise_le),
            client=abonnement.client,
            emise_le=emise_le,
            montant_ht=montant_hors_taxe(abonnement, code_promo, premiere_facture),
            montant_ttc=montant_toutes_taxes(abonnement, code_promo, premiere_facture),
        )
        corps = "\n".join(
            [
                f"Facture {facture.numero}",
                f"Client        : {facture.client}",
                f"Emise le      : {facture.emise_le.isoformat()}",
                f"Formule       : {abonnement.formule}, {abonnement.nombre_de_postes} postes",
                f"Montant HT    : {facture.montant_ht:.2f}",
                f"Montant TTC   : {facture.montant_ttc:.2f}",
            ]
        )
        self.passerelle.envoyer_courriel(adresse, f"Votre facture {facture.numero}", corps)
        return facture
