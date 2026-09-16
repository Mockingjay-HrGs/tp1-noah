from inventaire.legacy.inventaire import val, alerte, mouv

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