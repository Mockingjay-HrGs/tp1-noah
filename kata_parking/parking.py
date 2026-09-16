from math import ceil


def calculer_tarif(minutes):
    if minutes <= 30:
        return 0
    demi_heures_payantes = ceil((minutes - 30) / 30)
    tranches_journalieres = ceil(minutes / (24 * 60))
    plafond = tranches_journalieres * 18
    return min(demi_heures_payantes * 1.50, plafond)