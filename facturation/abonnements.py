"""Les abonnements et leur cycle de vie."""

from dataclasses import dataclass
from datetime import date

FORMULE_ESSENTIEL = "essentiel"
FORMULE_PRO = "pro"
FORMULE_ENTREPRISE = "entreprise"


class ResiliationImpossible(RuntimeError):
    """La resiliation demandee n'est pas autorisee."""


@dataclass
class Abonnement:
    """Un abonnement mensuel.

    Contrat de `resilier` :
      - enregistre la date de fin demandee
      - renvoie la date de fin effective
      - toute date posterieure a la date de debut est acceptee
      - leve ValueError si la date demandee precede la date de debut
    """

    client: str
    formule: str
    nombre_de_postes: int
    debut: date
    fin: date | None = None

    def resilier(self, a_partir_de: date) -> date:
        if a_partir_de < self.debut:
            raise ValueError("une resiliation ne peut pas preceder le debut")
        self.fin = a_partir_de
        return self.fin

    def est_actif(self, le_jour: date) -> bool:
        if le_jour < self.debut:
            return False
        return self.fin is None or le_jour < self.fin


@dataclass
class AbonnementAnnuel(Abonnement):
    """Un abonnement engage sur douze mois."""

    def resilier(self, a_partir_de: date) -> date:
        raise ResiliationImpossible(
            f"{self.client} : engagement annuel, resiliation au {a_partir_de.isoformat()} "
            f"impossible avant le terme"
        )


@dataclass
class AbonnementEssai(Abonnement):
    """Un abonnement d'essai de trente jours, gratuit."""

    def est_gratuit(self) -> bool:
        return True
