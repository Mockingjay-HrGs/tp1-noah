from math import ceil


def calculer_tarif(minutes):
    if minutes <= 30:
        return 0
    demi_heures_payantes = ceil((minutes - 30) / 30)
    return min(demi_heures_payantes * 1.50, 18)