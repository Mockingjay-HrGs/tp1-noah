"""Point d'entrée : branche les détails techniques sur les ports du métier."""

from datetime import datetime
from functools import partial

from facturation import extensions as extensions
from facturation.facture import EmetteurDeFactures as ServiceDeFacturation
from facturation.facture import calculer_facture
from facturation.passerelles import ClientSMTP
from facturation.presentation import corps_de_facture
from facturation.registre import tarification


def aujourd_hui():
    return datetime.now().date()


def EmetteurDeFactures():  # noqa: N802 - compatibilité du constructeur public
    return ServiceDeFacturation(
        ClientSMTP(),
        aujourd_hui,
        corps_de_facture,
        partial(calculer_facture, tarification=tarification),
    )
