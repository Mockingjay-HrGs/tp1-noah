"""Les abonnements et leur cycle de vie."""

from calendar import monthrange
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


def verifier_engagement_annuel(debut: date, demandee: date) -> None:
    """L'anniversaire du 29 février est le 28 février l'année suivante."""
    terme = date(
        debut.year + 1, debut.month, min(debut.day, monthrange(debut.year + 1, debut.month)[1])
    )
    if demandee < debut:
        raise ValueError("une resiliation ne peut pas preceder le debut")
    if demandee < terme:
        raise ResiliationImpossible("engagement annuel : resiliation impossible avant le terme")


class AbonnementAnnuel:
    """Compose un cycle mensuel et une règle d'engagement, sans promettre son contrat."""

    def __init__(self, client, formule, nombre_de_postes, debut, fin=None):  # noqa: PLR0913, PLR0917 - signature historique
        self.abonnement = Abonnement(client, formule, nombre_de_postes, debut, fin)
        self.verifier_resiliation = verifier_engagement_annuel

    @property
    def client(self):
        return self.abonnement.client

    @property
    def formule(self):
        return self.abonnement.formule

    @property
    def nombre_de_postes(self):
        return self.abonnement.nombre_de_postes

    @property
    def debut(self):
        return self.abonnement.debut

    @property
    def fin(self):
        return self.abonnement.fin

    def resilier(self, a_partir_de: date) -> date:
        self.verifier_resiliation(self.debut, a_partir_de)
        return self.abonnement.resilier(a_partir_de)

    def est_actif(self, le_jour: date) -> bool:
        return self.abonnement.est_actif(le_jour)


@dataclass
class AbonnementEssai(Abonnement):
    """Un abonnement d'essai de trente jours, gratuit."""

    def est_gratuit(self) -> bool:
        return True
