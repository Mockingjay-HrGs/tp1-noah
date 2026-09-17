import inventaire.legacy.inventaire as module_inventaire
import pytest
from inventaire.legacy.inventaire import val, alerte, mouv, cout, classer, rot, rapport, par_cat, export_json
from datetime import datetime
from copy import deepcopy
from unittest.mock import patch
import json

def test_valeur_stock_additionne_quantites_multipliees_par_prix():
    articles = [
        {"q": 3, "pu": 10},
        {"q": 2, "pu": 4.50},
    ]

    assert val(articles) == 39

def test_valeur_stock_est_arrondie_au_centime():
    articles = [
        {"q": 3, "pu": 1.234},
    ]

    assert val(articles) == 3.70

def test_article_sous_le_seuil_est_en_alerte():
    articles = [
        {"ref": "MARTEAU", "q": 2, "seuil": 5},
    ]

    assert alerte(articles) == ["MARTEAU"]

def test_article_exactement_au_seuil_ne_declenche_actuellement_pas_alerte():
    articles = [
        {"ref": "MARTEAU", "q": 5, "seuil": 5},
    ]

    assert alerte(articles) == []

def test_sortie_superieure_au_stock_est_refusee_mais_rend_actuellement_le_stock_negatif():
    article = {"ref": "MARTEAU", "q": 2}

    resultat = mouv(article, 3, j=[], log=False)

    assert resultat is False
    assert article["q"] == -1

def test_mouvement_de_quantite_nulle_est_refuse_et_conserve_le_stock():
    article = {"ref": "MARTEAU", "q": 5}

    resultat = mouv(article, 0, j=[], log=False)

    assert resultat is False
    assert article["q"] == 5

def test_mouvement_de_quantite_negative_est_refuse_et_conserve_le_stock():
    article = {"ref": "MARTEAU", "q": 5}

    resultat = mouv(article, -1, j=[], log=False)

    assert resultat is False
    assert article["q"] == 5

def test_cout_reapprovisionnement_permet_de_remonter_a_trois_fois_le_seuil():
    article = {"q": 2, "seuil": 5, "pu": 10}

    assert cout(article) == 130

def test_cout_pour_cent_unites_commandees_ne_beneficie_actuellement_pas_de_remise():
    article = {"q": 20, "seuil": 40, "pu": 10}

    assert cout(article) == 1000

def test_cout_pour_cent_une_unites_commandees_applique_dix_pour_cent_de_remise():
    article = {"q": 19, "seuil": 40, "pu": 10}

    assert cout(article) == 909

def test_classement_trie_les_articles_par_valeur_de_stock_decroissante():
    marteau = {"ref": "MARTEAU", "q": 2, "pu": 10}
    perceuse = {"ref": "PERCEUSE", "q": 1, "pu": 50}
    vis = {"ref": "VIS", "q": 100, "pu": 0.05}

    resultat = classer([marteau, vis, perceuse])

    assert resultat == [perceuse, marteau, vis]

def test_rotation_arrondit_les_jours_de_stock_a_entier_inferieur():
    article = {"q": 5}

    assert rot(article, 12) == 12

def test_rotation_sans_vente_renvoie_actuellement_zero():
    article = {"q": 5}

    assert rot(article, 0) == 0

def test_rapport_calcule_la_valeur_ht_ttc_et_le_nombre_articles():
    articles = [
        {"ref": "MARTEAU", "q": 3, "pu": 10, "seuil": 2, "cat": "outil"},
    ]

    resultat = rapport(
        articles,
        d=datetime(2026, 9, 16, 10, 0),
        verbose=False,
    )

    assert resultat == {
        "date": "2026-09-16 10:00:00",
        "valeur": 30,
        "nb": 1,
        "alertes": [],
        "ttc": 36,
    }

def test_rapport_ne_modifie_pas_les_articles_ni_les_ventes():
    articles = [
        {"ref": "MARTEAU", "q": 3, "pu": 10, "seuil": 5, "cat": "outil"},
    ]
    ventes = {"MARTEAU": 12}
    articles_avant = deepcopy(articles)
    ventes_avant = deepcopy(ventes)

    rapport(
        articles,
        ventes=ventes,
        d=datetime(2026, 9, 16, 10, 0),
        verbose=False,
    )

    assert articles == articles_avant
    assert ventes == ventes_avant

def test_rapport_sans_date_utilise_actuellement_horloge_systeme():
    date_fixe = datetime(2026, 9, 16, 10, 0)

    with patch("inventaire.legacy.inventaire.datetime.datetime") as horloge:
        horloge.now.return_value = date_fixe

        resultat = rapport([], verbose=False)

        horloge.now.assert_called_once_with()

    assert resultat["date"] == "2026-09-16 10:00:00"

def test_rapport_filtre_les_articles_par_categorie():
    articles = [
        {"ref": "MARTEAU", "q": 3, "pu": 10, "seuil": 2, "cat": "outil"},
        {"ref": "VIS", "q": 100, "pu": 0.50, "seuil": 20, "cat": "consommable"},
    ]

    resultat = rapport(
        articles,
        cat="outil",
        d=datetime(2026, 9, 16, 10, 0),
        verbose=False,
    )

    assert resultat == {
        "date": "2026-09-16 10:00:00",
        "valeur": 30,
        "nb": 1,
        "alertes": [],
        "ttc": 36,
    }

def test_rapport_conserve_les_articles_dont_la_quantite_atteint_le_minimum():
    articles = [
        {"ref": "MARTEAU", "q": 5, "pu": 10, "seuil": 2, "cat": "outil"},
        {"ref": "PINCE", "q": 4, "pu": 20, "seuil": 2, "cat": "outil"},
    ]

    resultat = rapport(
        articles,
        seuil_min=5,
        d=datetime(2026, 9, 16, 10, 0),
        verbose=False,
    )

    assert resultat == {
        "date": "2026-09-16 10:00:00",
        "valeur": 50,
        "nb": 1,
        "alertes": [],
        "ttc": 60,
    }

def test_rapport_signale_un_article_sous_son_seuil():
    articles = [
        {"ref": "MARTEAU", "q": 2, "pu": 10, "seuil": 5, "cat": "outil"},
    ]

    resultat = rapport(
        articles,
        d=datetime(2026, 9, 16, 10, 0),
        verbose=False,
    )

    assert resultat["alertes"] == ["MARTEAU"]

def test_rapport_ne_signale_actuellement_pas_un_article_au_stock_nul():
    articles = [
        {"ref": "MARTEAU", "q": 0, "pu": 10, "seuil": 5, "cat": "outil"},
    ]

    resultat = rapport(
        articles,
        d=datetime(2026, 9, 16, 10, 0),
        verbose=False,
    )

    assert resultat["alertes"] == []
    assert resultat["nb"] == 0
    assert resultat["valeur"] == 0

def test_valeur_par_categorie_additionne_les_articles_de_meme_categorie():
    articles = [
        {"cat": "outil", "q": 2, "pu": 10},
        {"cat": "outil", "q": 1, "pu": 30},
        {"cat": "consommable", "q": 100, "pu": 0.50},
    ]

    assert par_cat(articles) == {
        "outil": 50,
        "consommable": 50,
    }

def test_categories_inconnues_sont_regroupees_dans_autre():
    articles = [
        {"cat": "equipement", "q": 2, "pu": 15},
        {"cat": "protection", "q": 3, "pu": 10},
    ]

    assert par_cat(articles) == {"autre": 60}

def test_valeur_categorie_piece_additionne_les_valeurs_de_stock():
    articles = [
        {"cat": "piece", "q": 2, "pu": 12},
        {"cat": "piece", "q": 3, "pu": 5},
    ]

    assert par_cat(articles) == {"piece": 39}

def test_valeur_categorie_consommable_additionne_les_valeurs_de_stock():
    articles = [
        {"cat": "consommable", "q": 100, "pu": 0.50},
        {"cat": "consommable", "q": 20, "pu": 2},
    ]

    assert par_cat(articles) == {"consommable": 90}

def test_sortie_acceptee_diminue_le_stock_et_enregistre_le_mouvement(monkeypatch):
    monkeypatch.setattr(module_inventaire, "DERNIER", 0)
    monkeypatch.setattr(module_inventaire, "JOURNAL", [])
    article = {"ref": "MARTEAU", "q": 5}
    journal = []

    resultat = mouv(article, 2, j=journal, log=False)

    mouvement = {"id": 1, "ref": "MARTEAU", "q": 2, "t": "out"}
    assert resultat is True
    assert article["q"] == 3
    assert journal == [mouvement]
    assert module_inventaire.JOURNAL == [mouvement]
    assert module_inventaire.DERNIER == 1

def test_entree_acceptee_augmente_le_stock_et_enregistre_le_mouvement(monkeypatch):
    monkeypatch.setattr(module_inventaire, "DERNIER", 0)
    monkeypatch.setattr(module_inventaire, "JOURNAL", [])
    article = {"ref": "MARTEAU", "q": 5}
    journal = []

    resultat = mouv(article, 3, t="in", j=journal, log=False)

    mouvement = {"id": 1, "ref": "MARTEAU", "q": 3, "t": "in"}
    assert resultat is True
    assert article["q"] == 8
    assert journal == [mouvement]
    assert module_inventaire.JOURNAL == [mouvement]
    assert module_inventaire.DERNIER == 1

def test_type_mouvement_inconnu_est_refuse_sans_modifier_stock_ni_journaux(monkeypatch):
    monkeypatch.setattr(module_inventaire, "DERNIER", 0)
    monkeypatch.setattr(module_inventaire, "JOURNAL", [])
    article = {"ref": "MARTEAU", "q": 5}
    journal = []

    resultat = mouv(article, 2, t="inconnu", j=journal, log=False)

    assert resultat is False
    assert article["q"] == 5
    assert journal == []
    assert module_inventaire.JOURNAL == []
    assert module_inventaire.DERNIER == 0

def test_sortie_forcee_accepte_un_stock_negatif_et_journalise_le_mouvement(monkeypatch):
    monkeypatch.setattr(module_inventaire, "DERNIER", 0)
    monkeypatch.setattr(module_inventaire, "JOURNAL", [])
    article = {"ref": "MARTEAU", "q": 2}
    journal = []

    resultat = mouv(article, 3, j=journal, force=True, log=False)

    mouvement = {"id": 1, "ref": "MARTEAU", "q": 3, "t": "out"}
    assert resultat is True
    assert article["q"] == -1
    assert journal == [mouvement]
    assert module_inventaire.JOURNAL == [mouvement]

def test_rapport_affiche_une_alerte_et_une_rupture_imminente(capsys):
    articles = [
        {"ref": "MARTEAU", "q": 2, "pu": 10, "seuil": 5, "cat": "outil"},
    ]

    rapport(
        articles,
        ventes={"MARTEAU": 30},
        d=datetime(2026, 9, 16, 10, 0),
    )

    assert capsys.readouterr().out == (
        "ALERTE MARTEAU : 2 restants\n"
        "RUPTURE IMMINENTE MARTEAU\n"
    )

@pytest.mark.parametrize(
    "ventes_mensuelles, message_attendu",
    [
        (10, "a surveiller MARTEAU\n"),
        (2, ""),
        (0, "aucune vente pour MARTEAU\n"),
    ],
)
def test_messages_du_rapport_selon_les_ventes(
        ventes_mensuelles, message_attendu, capsys
):
    articles = [
        {"ref": "MARTEAU", "q": 5, "pu": 10, "seuil": 2, "cat": "outil"},
    ]

    rapport(
        articles,
        ventes={"MARTEAU": ventes_mensuelles},
        d=datetime(2026, 9, 16, 10, 0),
    )

    assert capsys.readouterr().out == message_attendu

@pytest.mark.parametrize(
    "quantite, prix, message_attendu",
    [
        (0, 10, "stock vide MARTEAU\n"),
        (-1, 10, "stock vide MARTEAU\n"),
        (5, 0, "prix invalide MARTEAU\n"),
        (5, -1, "prix invalide MARTEAU\n"),
    ],
)
def test_rapport_exclut_les_stocks_et_prix_non_positifs(
        quantite, prix, message_attendu, capsys
):
    articles = [
        {
            "ref": "MARTEAU",
            "q": quantite,
            "pu": prix,
            "seuil": 2,
            "cat": "outil",
        },
    ]

    resultat = rapport(
        articles,
        d=datetime(2026, 9, 16, 10, 0),
    )

    assert resultat["valeur"] == 0
    assert resultat["ttc"] == 0
    assert resultat["nb"] == 0
    assert resultat["alertes"] == []
    assert capsys.readouterr().out == message_attendu

def test_classement_conserve_ordre_des_egalites_et_liste_origine():
    marteau = {"ref": "MARTEAU", "q": 2, "pu": 10}
    pince = {"ref": "PINCE", "q": 1, "pu": 20}
    perceuse = {"ref": "PERCEUSE", "q": 1, "pu": 50}
    articles = [marteau, pince, perceuse]

    resultat = classer(articles)

    assert resultat == [perceuse, marteau, pince]
    assert articles == [marteau, pince, perceuse]
    assert resultat is not articles

@pytest.mark.parametrize(
    "article, ventes",
    [
        ({}, 10),
        ({"q": 5}, None),
    ],
)
def test_rotation_renvoie_actuellement_zero_pour_des_donnees_invalides(
        article, ventes
):
    assert rot(article, ventes) == 0

def test_export_json_ajoute_le_resultat_a_historique_et_ecrit_le_fichier(tmp_path):
    historique = [{"valeur": 10}]
    resultat = {"valeur": 20}
    chemin = tmp_path / "inventaire.json"

    historique_retourne = export_json(
        resultat, chemin=chemin, hist=historique
    )

    attendu = [{"valeur": 10}, {"valeur": 20}]
    assert historique == attendu
    assert historique_retourne is historique
    assert json.loads(chemin.read_text()) == attendu

def test_exports_sans_historique_partagent_actuellement_la_meme_liste(tmp_path):
    premier_resultat = {"valeur": 10}
    second_resultat = {"valeur": 20}

    premier_historique = export_json(
        premier_resultat, chemin=tmp_path / "premier.json"
    )
    taille_initiale = len(premier_historique) - 1

    try:
        second_historique = export_json(
            second_resultat, chemin=tmp_path / "second.json"
        )

        assert second_historique is premier_historique
        assert second_historique[-2:] == [
            premier_resultat,
            second_resultat,
        ]
        assert json.loads(
            (tmp_path / "second.json").read_text()
        ) == second_historique
    finally:
        del premier_historique[taille_initiale:]