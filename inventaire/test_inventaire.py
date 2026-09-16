from inventaire.legacy.inventaire import val


def test_valeur_stock_additionne_quantites_multipliees_par_prix():
    articles = [
        {"q": 3, "pu": 10},
        {"q": 2, "pu": 4.50},
    ]

    assert val(articles) == 39