"""D2 : RENTREE retire dix pour cent, dès la première facture et ensuite."""

from facturation.registre import tarification


def rentree(montant: float, _premiere_facture: bool) -> float:
    return montant * 0.90


tarification.promotions["RENTREE"] = rentree
