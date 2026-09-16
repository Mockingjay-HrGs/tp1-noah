import inventaire.legacy.inventaire as module_inventaire
from inventaire.legacy.inventaire import val, alerte, mouv, cout, classer, rot, rapport, par_cat
from datetime import datetime
from copy import deepcopy
from unittest.mock import patch

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