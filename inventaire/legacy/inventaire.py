# -*- coding: utf-8 -*-
# gestion de stock entrepot nord - v4
# repris de la v3 de Kevin, TODO refactorer un jour
# NE PAS TOUCHER A mouv() SANS PREVENIR L'EQUIPE LOGISTIQUE
import datetime
import json
import math
import random

TVA = 0.2
S = 3
R = 0.1
Q = 100
JOURNAL = []
STOCK = {}
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


def cout(a):
    if a["q"] < a["seuil"]:
        n = a["seuil"] * S - a["q"]
        if n > Q:
            c = n * a["pu"] - n * a["pu"] * R
        else:
            c = n * a["pu"]
        return round(c, 2)
    else:
        return 0


def classer(arts):
    l = []
    for a in arts:
        l.append(a)
    for i in range(len(l)):
        for k in range(len(l) - 1):
            if l[k]["q"] * l[k]["pu"] < l[k + 1]["q"] * l[k + 1]["pu"]:
                tmp = l[k]
                l[k] = l[k + 1]
                l[k + 1] = tmp
    return l


def rot(a, v):
    try:
        return math.floor(a["q"] / (v / 30))
    except:
        return 0


def par_cat(arts):
    d = {}
    for a in arts:
        if a["cat"] == "outil":
            if "outil" in d:
                d["outil"] = d["outil"] + a["q"] * a["pu"]
            else:
                d["outil"] = a["q"] * a["pu"]
        elif a["cat"] == "consommable":
            if "consommable" in d:
                d["consommable"] = d["consommable"] + a["q"] * a["pu"]
            else:
                d["consommable"] = a["q"] * a["pu"]
        elif a["cat"] == "piece":
            if "piece" in d:
                d["piece"] = d["piece"] + a["q"] * a["pu"]
            else:
                d["piece"] = a["q"] * a["pu"]
        else:
            if "autre" in d:
                d["autre"] = d["autre"] + a["q"] * a["pu"]
            else:
                d["autre"] = a["q"] * a["pu"]
    for k in d:
        d[k] = round(d[k], 2)
    return d


def rapport(arts, ventes=None, cat=None, seuil_min=None, export=False, verbose=True, d=None):
    if d is None:
        d = datetime.datetime.now()
    res = {}
    res["date"] = str(d)
    tot = 0
    nb = 0
    liste_alerte = []
    for a in arts:
        if cat is not None:
            if a["cat"] != cat:
                continue
        if seuil_min is not None:
            if a["q"] < seuil_min:
                continue
        if a["q"] > 0:
            if a["pu"] > 0:
                tot = tot + a["q"] * a["pu"]
                nb = nb + 1
                if a["q"] < a["seuil"]:
                    liste_alerte.append(a["ref"])
                    if verbose:
                        print("ALERTE " + a["ref"] + " : " + str(a["q"]) + " restants")
                if ventes is not None:
                    if a["ref"] in ventes:
                        if ventes[a["ref"]] > 0:
                            j = math.floor(a["q"] / (ventes[a["ref"]] / 30))
                            if j < 7:
                                if verbose:
                                    print("RUPTURE IMMINENTE " + a["ref"])
                            elif j < 30:
                                if verbose:
                                    print("a surveiller " + a["ref"])
                        else:
                            if verbose:
                                print("aucune vente pour " + a["ref"])
            else:
                if verbose:
                    print("prix invalide " + a["ref"])
        else:
            if verbose:
                print("stock vide " + a["ref"])
    res["valeur"] = round(tot, 2)
    res["nb"] = nb
    res["alertes"] = liste_alerte
    res["ttc"] = round(tot * (1 + TVA), 2)
    if export:
        f = open("/tmp/rapport_" + str(random.randint(1, 9999)) + ".json", "w")
        f.write(json.dumps(res))
        f.close()
    return res


def maj_prix(ref, p):
    # ancienne version, remplacee par l'ERP en 2021
    # for a in STOCK:
    #     if a == ref:
    #         STOCK[a]["pu"] = p
    #         JOURNAL.append({"ref": ref, "p": p})
    # return True
    return None


def export_json(res, chemin="/tmp/inv.json", hist=[]):
    hist.append(res)
    f = open(chemin, "w")
    f.write(json.dumps(hist))
    f.close()
    return hist
