from math import ceil


def calculer_tarif(minutes, abonne=False, electrique_branche=False):
    if minutes < 0:
        raise ValueError("La durée ne peut pas être négative")

    minutes_gratuites = 60 if electrique_branche else 30
    if minutes <= minutes_gratuites:
        return 0

    demi_heures_payantes = ceil((minutes - minutes_gratuites) / 30)
    tranches_journalieres = ceil(minutes / (24 * 60))
    plafond = tranches_journalieres * 18
    montant = min(demi_heures_payantes * 1.50, plafond)

    if abonne:
        montant = round(montant * 0.60, 2)

    return montant


def calculer_tarif_entre(entree, sortie):
    if sortie < entree:
        raise ValueError("La sortie ne peut pas précéder l'entrée")