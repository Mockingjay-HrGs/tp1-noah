"""Le même contrat est exécuté sur chaque type qui revendique Abonnement."""

from datetime import date

import pytest

from facturation import abonnements
from facturation.abonnements import Abonnement, AbonnementAnnuel, ResiliationImpossible

TYPES_D_ABONNEMENT = [
    classe
    for classe in vars(abonnements).values()
    if isinstance(classe, type) and issubclass(classe, Abonnement)
]


@pytest.fixture(params=TYPES_D_ABONNEMENT, ids=lambda classe: classe.__name__)
def contrat(request):
    return request.param("Client", "pro", 3, date(2026, 1, 1))


@pytest.mark.parametrize("fin", [date(2026, 1, 1), date(2026, 7, 1), date(2027, 1, 1)])
def test_toute_date_depuis_le_debut_est_acceptee_et_enregistree(contrat, fin):
    assert contrat.resilier(fin) == fin
    assert contrat.fin == fin
    assert not contrat.est_actif(fin)


def test_date_avant_debut_leve_value_error_sans_mutation(contrat):
    with pytest.raises(ValueError, match="preceder"):
        contrat.resilier(date(2025, 12, 31))
    assert contrat.fin is None


def test_intervalle_actif_debut_inclus_fin_exclue(contrat):
    assert not contrat.est_actif(date(2025, 12, 31))
    assert contrat.est_actif(date(2026, 1, 1))
    contrat.resilier(date(2026, 7, 1))
    assert contrat.est_actif(date(2026, 6, 30))
    assert not contrat.est_actif(date(2026, 7, 1))


def test_annuel_preserve_engagement_et_accepte_le_terme():
    annuel = AbonnementAnnuel("Client", "pro", 3, date(2026, 1, 1))
    with pytest.raises(ResiliationImpossible):
        annuel.resilier(date(2026, 12, 31))
    assert annuel.fin is None
    assert annuel.est_actif(date(2026, 12, 31))
    assert annuel.resilier(date(2027, 1, 1)) == date(2027, 1, 1)
    assert annuel.fin == date(2027, 1, 1)
    assert not annuel.est_actif(date(2027, 1, 1))


def test_annuel_bissextile_se_termine_le_28_fevrier():
    annuel = AbonnementAnnuel("Client", "pro", 3, date(2024, 2, 29))
    with pytest.raises(ResiliationImpossible):
        annuel.resilier(date(2025, 2, 27))
    assert annuel.resilier(date(2025, 2, 28)) == date(2025, 2, 28)
