# -*- coding: utf-8 -*-
# gestion de stock entrepot nord - v4
# repris de la v3 de Kevin, TODO refactorer un jour
# NE PAS TOUCHER A mouv() SANS PREVENIR L'EQUIPE LOGISTIQUE
from dataclasses import dataclass
import datetime
import json
import math
import random

PERIODE_VENTES_JOURS = 30
SEUIL_RUPTURE_IMMINENTE_JOURS = 7
SEUIL_SURVEILLANCE_JOURS = 30

TAUX_TVA = 0.2
MULTIPLICATEUR_STOCK_CIBLE = 3
TAUX_REMISE_REAPPROVISIONNEMENT = 0.1
SEUIL_REMISE_QUANTITE = 100
JOURNAL_MOUVEMENTS_PARTAGE = []
HISTORIQUE_EXPORT_PARTAGE = []
JOURNAL = []
DERNIER = 0


def calculer_valeur_stock(articles):
    valeur_totale = 0
    for article in articles:
        if article["q"] > 0:
            valeur_totale = valeur_totale + article["q"] * article["pu"]
        else:
            valeur_totale = valeur_totale + 0
    return round(valeur_totale, 2)


def lister_references_en_alerte(articles):
    references_en_alerte = []
    for article in articles:
        if article["q"] < article["seuil"]:
            references_en_alerte.append(article["ref"])
    return references_en_alerte

@dataclass(frozen=True)
class OptionsMouvement:
    type_mouvement: str = "out"
    forcer: bool = False
    afficher_messages: bool = True


@dataclass(frozen=True)
class OptionsRapport:
    categorie: str | None = None
    quantite_minimale: int | None = None
    exporter: bool = False
    afficher_messages: bool = True


def appliquer_variation_stock(article, quantite, type_mouvement, force):
    if quantite <= 0:
        return "quantite invalide : " + str(quantite)

    if type_mouvement == "out":
        article["q"] = article["q"] - quantite
        if article["q"] < 0:
            if force == False:
                return "stock insuffisant pour " + article["ref"]
    elif type_mouvement == "in":
        article["q"] = article["q"] + quantite
    else:
        return "type de mouvement inconnu : " + str(type_mouvement)

    return None


def enregistrer_mouvement(article, quantite, journal=None, options=None):
    global DERNIER

    if options is None:
        options = OptionsMouvement()
    if journal is None:
        journal = JOURNAL_MOUVEMENTS_PARTAGE

    erreur = appliquer_variation_stock(
        article, quantite, options.type_mouvement, options.forcer
    )
    if erreur is not None:
        if options.afficher_messages:
            print(erreur)
        return False

    DERNIER = DERNIER + 1
    journal.append({
        "id": DERNIER,
        "ref": article["ref"],
        "q": quantite,
        "t": options.type_mouvement,
    })
    JOURNAL.append({
        "id": DERNIER,
        "ref": article["ref"],
        "q": quantite,
        "t": options.type_mouvement,
    })
    return True


def calculer_cout_reapprovisionnement(article):
    if article["q"] < article["seuil"]:
        quantite_a_commander = (
                article["seuil"] * MULTIPLICATEUR_STOCK_CIBLE - article["q"]
        )
        montant = quantite_a_commander * article["pu"]
        if quantite_a_commander > SEUIL_REMISE_QUANTITE:
            montant = montant - montant * TAUX_REMISE_REAPPROVISIONNEMENT
        return round(montant, 2)
    return 0


def classer_par_valeur_stock(articles):
    return sorted(
        articles,
        key=lambda article: article["q"] * article["pu"],
        reverse=True,
    )


def calculer_jours_stock_restants(article, ventes_mensuelles):
    try:
        return math.floor(article["q"] / (ventes_mensuelles / PERIODE_VENTES_JOURS))
    except (ZeroDivisionError, KeyError, TypeError, ValueError, OverflowError):
        return 0


def calculer_valeurs_par_categorie(articles):
    valeurs_par_categorie = {}

    for article in articles:
        categorie = article["cat"]
        if categorie not in ("outil", "consommable", "piece"):
            categorie = "autre"

        valeur_stock = article["q"] * article["pu"]
        valeurs_par_categorie[categorie] = (
                valeurs_par_categorie.get(categorie, 0) + valeur_stock
        )

    for categorie in valeurs_par_categorie:
        valeurs_par_categorie[categorie] = round(
            valeurs_par_categorie[categorie], 2
        )

    return valeurs_par_categorie

def message_rotation(article, ventes):
    reference = article["ref"]
    if reference not in ventes:
        return None

    ventes_mensuelles = ventes[reference]
    if ventes_mensuelles <= 0:
        return "aucune vente pour " + reference

    jours_restants = math.floor(
        article["q"] / (ventes_mensuelles / PERIODE_VENTES_JOURS)
    )
    if jours_restants < SEUIL_RUPTURE_IMMINENTE_JOURS:
        return "RUPTURE IMMINENTE " + reference
    elif jours_restants < SEUIL_SURVEILLANCE_JOURS:
        return "a surveiller " + reference
    return None


def respecte_filtres(article, categorie, quantite_minimale):
    if categorie is not None:
        if article["cat"] != categorie:
            return False
    if quantite_minimale is not None:
        if article["q"] < quantite_minimale:
            return False
    return True

def motif_exclusion_article(article):
    if article["q"] > 0:
        if article["pu"] > 0:
            return None
        return "prix invalide " + article["ref"]
    return "stock vide " + article["ref"]


def messages_article(article, ventes):
    messages = []
    if article["q"] < article["seuil"]:
        messages.append(
            "ALERTE " + article["ref"] + " : " + str(article["q"]) + " restants"
        )
    if ventes is not None:
        message = message_rotation(article, ventes)
        if message is not None:
            messages.append(message)
    return messages


def calculer_rapport(articles, ventes, options):
    valeur_totale = 0
    nombre_articles = 0
    references_en_alerte = []
    messages = []

    for article in articles:
        if not respecte_filtres(article, options.categorie, options.quantite_minimale):
            continue
        motif = motif_exclusion_article(article)
        if motif is not None:
            messages.append(motif)
            continue

        valeur_totale = valeur_totale + article["q"] * article["pu"]
        nombre_articles = nombre_articles + 1
        if article["q"] < article["seuil"]:
            references_en_alerte.append(article["ref"])
        messages.extend(messages_article(article, ventes))

    resultat = {
        "valeur": round(valeur_totale, 2),
        "nb": nombre_articles,
        "alertes": references_en_alerte,
        "ttc": round(valeur_totale * (1 + TAUX_TVA), 2),
    }
    return resultat, messages


def generer_rapport(articles, ventes=None, date_rapport=None, options=None):
    if options is None:
        options = OptionsRapport()
    if date_rapport is None:
        date_rapport = datetime.datetime.now()

    resultat = {"date": str(date_rapport)}
    calcul, messages = calculer_rapport(articles, ventes, options)
    resultat.update(calcul)
    if options.afficher_messages:
        for message in messages:
            print(message)
    if options.exporter:
        fichier = open("/tmp/rapport_" + str(random.randint(1, 9999)) + ".json", "w")
        fichier.write(json.dumps(resultat))
        fichier.close()
    return resultat


def exporter_historique_json(resultat, chemin="/tmp/inv.json", historique=None):
    if historique is None:
        historique = HISTORIQUE_EXPORT_PARTAGE

    historique.append(resultat)
    with open(chemin, "w") as fichier:
        fichier.write(json.dumps(historique))
    return historique


# Compatibilité temporaire pendant la migration des appelants.
val = calculer_valeur_stock
alerte = lister_references_en_alerte
cout = calculer_cout_reapprovisionnement
classer = classer_par_valeur_stock
rot = calculer_jours_stock_restants
par_cat = calculer_valeurs_par_categorie


def mouv(article, quantite, j=None, options=None):
    return enregistrer_mouvement(article, quantite, journal=j, options=options)


def rapport(arts, ventes=None, d=None, options=None):
    return generer_rapport(arts, ventes=ventes, date_rapport=d, options=options)


def export_json(res, chemin="/tmp/inv.json", hist=None):
    return exporter_historique_json(res, chemin=chemin, historique=hist)
