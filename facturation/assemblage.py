"""Point d'entrée : branche les détails techniques sur les ports du métier."""

from datetime import datetime

from facturation.facture import EmetteurDeFactures as ServiceDeFacturation
from facturation.passerelles import ClientSMTP
from facturation.presentation import corps_de_facture


def aujourd_hui():
    return datetime.now().date()


def EmetteurDeFactures():  # noqa: N802 - compatibilité du constructeur public
    return ServiceDeFacturation(ClientSMTP(), aujourd_hui, corps_de_facture)
