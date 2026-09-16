from inventaire.legacy.inventaire import val, alerte, mouv, cout

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