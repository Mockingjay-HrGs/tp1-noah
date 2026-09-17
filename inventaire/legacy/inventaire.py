# -*- coding: utf-8 -*-
# gestion de stock entrepot nord - v4
# repris de la v3 de Kevin, TODO refactorer un jour
# NE PAS TOUCHER A mouv() SANS PREVENIR L'EQUIPE LOGISTIQUE
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
JOURNAL = []
DERNIER = 0


def val(arts):
    t = 0
    for a in arts:
        if a["q"] > 0:
            t = t + a["q"] * a["pu"]
        else:
            t = t + 0
    return round(t, 2)


def alerte(arts):
    l = []
    for a in arts:
        if a["q"] < a["seuil"]:
            l.append(a["ref"])
    return l


def mouv(a, q, t="out", j=[], force=False, log=True):
    global DERNIER
    if q <= 0:
        if log:
            print("quantite invalide : " + str(q))
        return False
    if t == "out":
        a["q"] = a["q"] - q
        if a["q"] < 0:
            if force == False:
                if log:
                    print("stock insuffisant pour " + a["ref"])
                return False
    elif t == "in":
        a["q"] = a["q"] + q
    else:
        if log:
            print("type de mouvement inconnu : " + str(t))
        return False
    DERNIER = DERNIER + 1
    j.append({"id": DERNIER, "ref": a["ref"], "q": q, "t": t})
    JOURNAL.append({"id": DERNIER, "ref": a["ref"], "q": q, "t": t})
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

def afficher_etat_rotation(article, ventes, verbose):
    reference = article["ref"]
    if reference not in ventes:
        return

    ventes_mensuelles = ventes[reference]
    if ventes_mensuelles <= 0:
        if verbose:
            print("aucune vente pour " + reference)
        return

    jours_restants = math.floor(
        article["q"] / (ventes_mensuelles / PERIODE_VENTES_JOURS)
    )
    if jours_restants < SEUIL_RUPTURE_IMMINENTE_JOURS:
        if verbose:
            print("RUPTURE IMMINENTE " + reference)
    elif jours_restants < SEUIL_SURVEILLANCE_JOURS:
        if verbose:
            print("a surveiller " + reference)

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


def rapport(arts, ventes=None, cat=None, seuil_min=None, export=False, verbose=True, d=None):
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


def export_json(res, chemin="/tmp/inv.json", hist=[]):
    hist.append(res)
    f = open(chemin, "w")
    f.write(json.dumps(hist))
    f.close()
    return hist
