"""Règles de tarification et configuration historique, sans dépendance technique."""

from collections.abc import Callable
from dataclasses import dataclass, field

from facturation.abonnements import (
    FORMULE_ENTREPRISE,
    FORMULE_ESSENTIEL,
    FORMULE_PRO,
    Abonnement,
)

TAUX_TVA = 0.20


class FormuleInconnue(ValueError):
    """La formule demandee n'existe pas au catalogue."""


class CodePromoInconnu(ValueError):
    """Le code promotionnel n'existe pas."""


def bienvenue(montant: float, premiere_facture: bool) -> float:
    return max(0.0, montant - 5.0) if premiere_facture else montant


def noel(montant: float, _premiere_facture: bool) -> float:
    return montant * 0.85


@dataclass
class Tarification:
    """Chaque configuration possède ses propres données et fonctions de promotion."""

    prix: dict[str, float] = field(
        default_factory=lambda: {
            FORMULE_ESSENTIEL: 9.0,
            FORMULE_PRO: 19.0,
            FORMULE_ENTREPRISE: 39.0,
        }
    )
    paliers: dict[int, float] = field(default_factory=lambda: {10: 0.10, 50: 0.20})
    promotions: dict[str, Callable[[float, bool], float]] = field(
        default_factory=lambda: {"BIENVENUE": bienvenue, "NOEL": noel}
    )

    def prix_par_poste(self, formule: str) -> float:
        try:
            return self.prix[formule]
        except KeyError:
            raise FormuleInconnue(formule) from None

    def taux_de_remise_volume(self, nombre_de_postes: int) -> float:
        seuil = max((seuil for seuil in self.paliers if seuil <= nombre_de_postes), default=0)
        return self.paliers.get(seuil, 0.0)

    def appliquer_code_promo(self, montant, code, premiere_facture):
        if code is None:
            return montant
        try:
            promotion = self.promotions[code]
        except KeyError:
            raise CodePromoInconnu(code) from None
        return promotion(montant, premiere_facture)

    def montant_hors_taxe(self, abonnement, code_promo=None, premiere_facture=False):
        base = self.prix_par_poste(abonnement.formule) * abonnement.nombre_de_postes
        apres_volume = base * (1 - self.taux_de_remise_volume(abonnement.nombre_de_postes))
        return round(self.appliquer_code_promo(apres_volume, code_promo, premiere_facture), 2)

    def montant_toutes_taxes(self, abonnement, code_promo=None, premiere_facture=False):
        return round(
            self.montant_hors_taxe(abonnement, code_promo, premiere_facture) * (1 + TAUX_TVA), 2
        )


TARIFICATION_ORIGINE = Tarification()


def prix_par_poste(formule: str) -> float:
    return TARIFICATION_ORIGINE.prix_par_poste(formule)


def taux_de_remise_volume(nombre_de_postes: int) -> float:
    return TARIFICATION_ORIGINE.taux_de_remise_volume(nombre_de_postes)


def appliquer_code_promo(montant: float, code: str | None, premiere_facture: bool) -> float:
    return TARIFICATION_ORIGINE.appliquer_code_promo(montant, code, premiere_facture)


def montant_hors_taxe(
    abonnement: Abonnement,
    code_promo: str | None = None,
    premiere_facture: bool = False,
) -> float:
    return TARIFICATION_ORIGINE.montant_hors_taxe(abonnement, code_promo, premiere_facture)


def montant_toutes_taxes(
    abonnement: Abonnement,
    code_promo: str | None = None,
    premiere_facture: bool = False,
) -> float:
    return TARIFICATION_ORIGINE.montant_toutes_taxes(abonnement, code_promo, premiere_facture)
