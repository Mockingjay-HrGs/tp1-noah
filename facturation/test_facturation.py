"""Suite de tests livree avec le code. Elle est verte, et elle a des trous."""

from datetime import date

import pytest

from facturation.abonnements import (
    FORMULE_ENTREPRISE,
    FORMULE_ESSENTIEL,
    FORMULE_PRO,
    Abonnement,
    AbonnementAnnuel,
    ResiliationImpossible,
)
from facturation.facture import EmetteurDeFactures
from facturation.tarifs import (
    CodePromoInconnu,
    FormuleInconnue,
    montant_hors_taxe,
    montant_toutes_taxes,
    prix_par_poste,
    taux_de_remise_volume,
)


def abonnement(**surcharges) -> Abonnement:
    valeurs = {
        "client": "Dupont SARL",
        "formule": FORMULE_PRO,
        "nombre_de_postes": 3,
        "debut": date(2026, 1, 1),
    }
    valeurs.update(surcharges)
    return Abonnement(**valeurs)


# --- le catalogue ---------------------------------------------------------


@pytest.mark.parametrize(
    "formule, attendu",
    [(FORMULE_ESSENTIEL, 9.0), (FORMULE_PRO, 19.0), (FORMULE_ENTREPRISE, 39.0)],
)
def test_chaque_formule_a_son_prix_par_poste(formule, attendu):
    assert prix_par_poste(formule) == attendu


def test_une_formule_inconnue_est_refusee():
    with pytest.raises(FormuleInconnue):
        prix_par_poste("platine")


# --- la remise volume -----------------------------------------------------


@pytest.mark.parametrize(
    "postes, attendu",
    [(1, 0.0), (9, 0.0), (10, 0.10), (49, 0.10), (50, 0.20), (500, 0.20)],
)
def test_la_remise_volume_suit_les_paliers(postes, attendu):
    assert taux_de_remise_volume(postes) == attendu


# --- le montant -----------------------------------------------------------


def test_le_montant_est_le_prix_par_poste_fois_le_nombre_de_postes():
    assert montant_hors_taxe(abonnement(nombre_de_postes=3)) == 57.0


def test_la_remise_volume_s_applique_au_montant():
    assert montant_hors_taxe(abonnement(nombre_de_postes=10)) == 171.0


def test_la_tva_de_vingt_pour_cent_s_ajoute():
    assert montant_toutes_taxes(abonnement(nombre_de_postes=3)) == 68.4


# --- les codes promo ------------------------------------------------------


def test_bienvenue_retire_cinq_euros_sur_la_premiere_facture():
    montant = montant_hors_taxe(abonnement(), code_promo="BIENVENUE", premiere_facture=True)
    assert montant == 52.0


def test_bienvenue_ne_fait_rien_sur_les_factures_suivantes():
    montant = montant_hors_taxe(abonnement(), code_promo="BIENVENUE", premiere_facture=False)
    assert montant == 57.0


def test_noel_retire_quinze_pour_cent():
    assert montant_hors_taxe(abonnement(), code_promo="NOEL") == 48.45


def test_un_code_promo_inconnu_est_refuse():
    with pytest.raises(CodePromoInconnu):
        montant_hors_taxe(abonnement(), code_promo="PAQUES")


# --- le cycle de vie ------------------------------------------------------


def test_un_abonnement_est_actif_apres_son_debut():
    assert abonnement().est_actif(date(2026, 6, 1)) is True


def test_un_abonnement_n_est_pas_actif_avant_son_debut():
    assert abonnement().est_actif(date(2025, 12, 31)) is False


def test_une_resiliation_enregistre_la_date_de_fin():
    contrat = abonnement()
    assert contrat.resilier(date(2026, 7, 1)) == date(2026, 7, 1)
    assert contrat.est_actif(date(2026, 8, 1)) is False


def test_une_resiliation_avant_le_debut_est_refusee():
    with pytest.raises(ValueError, match="preceder"):
        abonnement().resilier(date(2025, 1, 1))


def test_un_abonnement_annuel_refuse_toute_resiliation():
    annuel = AbonnementAnnuel(
        client="Martin SA", formule=FORMULE_PRO, nombre_de_postes=5, debut=date(2026, 1, 1)
    )
    with pytest.raises(ResiliationImpossible):
        annuel.resilier(date(2026, 7, 1))


# --- l'emission -----------------------------------------------------------


def test_le_numero_de_facture_est_incremente(capsys):
    emetteur = EmetteurDeFactures()
    premiere = emetteur.emettre(abonnement(), "compta@dupont.fr")
    seconde = emetteur.emettre(abonnement(), "compta@dupont.fr")
    capsys.readouterr()
    assert premiere.numero.endswith("-0001")
    assert seconde.numero.endswith("-0002")


def test_la_facture_porte_les_deux_montants(capsys):
    facture = EmetteurDeFactures().emettre(abonnement(nombre_de_postes=3), "compta@dupont.fr")
    capsys.readouterr()
    assert facture.montant_ht == 57.0
    assert facture.montant_ttc == 68.4


def test_la_facture_part_par_courriel(capsys):
    EmetteurDeFactures().emettre(abonnement(), "compta@dupont.fr")
    sortie = capsys.readouterr().out
    assert "compta@dupont.fr" in sortie
    assert "Montant TTC" in sortie
