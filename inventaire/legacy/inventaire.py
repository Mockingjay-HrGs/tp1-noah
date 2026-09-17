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

TVA = 0.2
MULTIPLICATEUR_STOCK_CIBLE = 3
TAUX_REMISE_REAPPROVISIONNEMENT = 0.1
SEUIL_REMISE_QUANTITE = 100
JOURNAL_MOUVEMENTS_PARTAGE = []
HISTORIQUE_EXPORT_PARTAGE = []
JOURNAL = []
DERNIER = 0


def val(arts):
    valeur_totale = 0
    for article in arts:
        if article["q"] > 0:
            valeur_totale = valeur_totale + article["q"] * article["pu"]
        else:
            valeur_totale = valeur_totale + 0
    return round(valeur_totale, 2)


def alerte(arts):
    references_en_alerte = []
    for article in arts:
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


def mouv(article, quantite, j=None, options=None):
    global DERNIER

    if options is None:
        options = OptionsMouvement()
    if j is None:
        j = JOURNAL_MOUVEMENTS_PARTAGE

    erreur = appliquer_variation_stock(
        article, quantite, options.type_mouvement, options.forcer
    )
    if erreur is not None:
        if options.afficher_messages:
            print(erreur)
        return False

    DERNIER = DERNIER + 1
    j.append({
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


def cout(article):
    if article["q"] < article["seuil"]:
        quantite_a_commander = (
                article["seuil"] * MULTIPLICATEUR_STOCK_CIBLE - article["q"]
        )
        montant = quantite_a_commander * article["pu"]
        if quantite_a_commander > SEUIL_REMISE_QUANTITE:
            montant = montant - montant * TAUX_REMISE_REAPPROVISIONNEMENT
        return round(montant, 2)
    return 0


def classer(articles):
    return sorted(
        articles,
        key=lambda article: article["q"] * article["pu"],
        reverse=True,
    )


def rot(a, v):
    try:
        return math.floor(a["q"] / (v / PERIODE_VENTES_JOURS))
    except (ZeroDivisionError, KeyError, TypeError, ValueError, OverflowError):
        return 0


def par_cat(articles):
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


def afficher_etat_rotation(article, ventes, verbose):
    message = message_rotation(article, ventes)
    if verbose and message is not None:
        print(message)

def respecte_filtres(article, categorie, seuil_min):
    if categorie is not None:
        if article["cat"] != categorie:
            return False
    if seuil_min is not None:
        if article["q"] < seuil_min:
            return False
    return True

def article_comptabilisable(article, verbose):
    if article["q"] > 0:
        if article["pu"] > 0:
            return True
        if verbose:
            print("prix invalide " + article["ref"])
    else:
        if verbose:
            print("stock vide " + article["ref"])
    return False


def rapport(arts, ventes=None, d=None, options=None):
    if options is None:
        options = OptionsRapport()
    cat = options.categorie
    seuil_min = options.quantite_minimale
    export = options.exporter
    verbose = options.afficher_messages

    if d is None:
        d = datetime.datetime.now()
    res = {}
    res["date"] = str(d)
    tot = 0
    nb = 0
    liste_alerte = []

    for a in arts:
        if not respecte_filtres(a, cat, seuil_min):
            continue
        if not article_comptabilisable(a, verbose):
            continue

        tot = tot + a["q"] * a["pu"]
        nb = nb + 1
        if a["q"] < a["seuil"]:
            liste_alerte.append(a["ref"])
            if verbose:
                print("ALERTE " + a["ref"] + " : " + str(a["q"]) + " restants")
        if ventes is not None:
            afficher_etat_rotation(a, ventes, verbose)

    res["valeur"] = round(tot, 2)
    res["nb"] = nb
    res["alertes"] = liste_alerte
    res["ttc"] = round(tot * (1 + TVA), 2)
    if export:
        f = open("/tmp/rapport_" + str(random.randint(1, 9999)) + ".json", "w")
        f.write(json.dumps(res))
        f.close()
    return res


def export_json(res, chemin="/tmp/inv.json", hist=None):
    if hist is None:
        hist = HISTORIQUE_EXPORT_PARTAGE

    hist.append(res)
    with open(chemin, "w") as fichier:
        fichier.write(json.dumps(hist))
    return hist
