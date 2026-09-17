"""Exemple logistique adapté aux noms explicites de la mission 3.

Les données métier et les résultats attendus sont conservés.
Exécuter avec : python3 exemple_utilisation.py depuis ce dossier.
"""

from inventaire import (
    calculer_cout_reapprovisionnement,
    calculer_valeur_stock,
    calculer_valeurs_par_categorie,
    classer_par_valeur_stock,
    generer_rapport,
    lister_references_en_alerte,
)

ARTICLES = [
    {
        "ref": "VIS-M6",
        "lib": "Vis M6 acier",
        "q": 2,
        "pu": 0.15,
        "seuil": 20,
        "cat": "piece",
    },
    {
        "ref": "PERC-18",
        "lib": "Perceuse 18V",
        "q": 12,
        "pu": 89.90,
        "seuil": 3,
        "cat": "outil",
    },
    {
        "ref": "GANT-L",
        "lib": "Gants taille L",
        "q": 5,
        "pu": 4.20,
        "seuil": 5,
        "cat": "consommable",
    },
    {
        "ref": "HUILE-5",
        "lib": "Huile 5L",
        "q": 40,
        "pu": 12.50,
        "seuil": 10,
        "cat": "consommable",
    },
    {
        "ref": "CAB-3G",
        "lib": "Cable 3G2.5",
        "q": 0,
        "pu": 1.80,
        "seuil": 50,
        "cat": "autre",
    },
]

VENTES_30_JOURS = {
    "VIS-M6": 300,
    "PERC-18": 4,
    "GANT-L": 60,
    "HUILE-5": 15,
    "CAB-3G": 0,
}

if __name__ == "__main__":
    print("valeur du stock :", calculer_valeur_stock(ARTICLES))
    print("articles en alerte :", lister_references_en_alerte(ARTICLES))
    print("cout de reappro des gants :", calculer_cout_reapprovisionnement(ARTICLES[2]))
    print("valeur par categorie :", calculer_valeurs_par_categorie(ARTICLES))
    print(
        "classement :",
        [article["ref"] for article in classer_par_valeur_stock(ARTICLES)],
    )
    print("---")
    print(generer_rapport(ARTICLES, ventes=VENTES_30_JOURS))
