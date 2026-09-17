"""Calculs de stock et orchestration des mouvements, rapports et exports.

Les écarts métier caractérisés restent présents jusqu’à la mission 5.
"""

import datetime
import json
import math
import random
from dataclasses import dataclass

PERIODE_VENTES_JOURS = 30
SEUIL_RUPTURE_IMMINENTE_JOURS = 7
SEUIL_SURVEILLANCE_JOURS = 30

TAUX_TVA = 0.2
MULTIPLICATEUR_STOCK_CIBLE = 3
TAUX_REMISE_REAPPROVISIONNEMENT = 0.1
SEUIL_REMISE_QUANTITE = 100
PRECISION_MONETAIRE = 2
IDENTIFIANT_EXPORT_MIN = 1
IDENTIFIANT_EXPORT_MAX = 9999
CHEMIN_HISTORIQUE_PAR_DEFAUT = "/tmp/inv.json"
JOURNAL_MOUVEMENTS_PARTAGE = []
HISTORIQUE_EXPORT_PARTAGE = []
JOURNAL = []
DERNIER = 0


def calculer_valeur_stock(articles):
    """Additionner les valeurs des stocks positifs et arrondir au centime."""
    valeur_totale = 0
    for article in articles:
        if article["q"] > 0:
            valeur_totale = valeur_totale + article["q"] * article["pu"]
        else:
            valeur_totale = valeur_totale + 0
    return round(valeur_totale, PRECISION_MONETAIRE)


def lister_references_en_alerte(articles):
    """Lister les références strictement sous leur seuil, comme le code initial."""
    references_en_alerte = []
    for article in articles:
        if article["q"] < article["seuil"]:
            references_en_alerte.append(article["ref"])
    return references_en_alerte


@dataclass(frozen=True)
class OptionsMouvement:
    """Regrouper le type de mouvement, le forçage et l’affichage."""

    type_mouvement: str = "out"
    forcer: bool = False
    afficher_messages: bool = True


@dataclass(frozen=True)
class OptionsRapport:
    """Regrouper les filtres du rapport et ses options de sortie."""

    categorie: str | None = None
    quantite_minimale: int | None = None
    exporter: bool = False
    afficher_messages: bool = True


def appliquer_variation_stock(article, quantite, type_mouvement, force):
    """Modifier le stock et renvoyer une erreur éventuelle, sans affichage."""
    if quantite <= 0:
        return "quantite invalide : " + str(quantite)

    if type_mouvement == "out":
        article["q"] = article["q"] - quantite
        if article["q"] < 0 and force == False:
            return "stock insuffisant pour " + article["ref"]
    elif type_mouvement == "in":
        article["q"] = article["q"] + quantite
    else:
        return "type de mouvement inconnu : " + str(type_mouvement)

    return None


def enregistrer_mouvement(article, quantite, journal=None, options=None):
    """Appliquer le mouvement, afficher les erreurs et journaliser les succès."""
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
    journal.append(
        {
            "id": DERNIER,
            "ref": article["ref"],
            "q": quantite,
            "t": options.type_mouvement,
        }
    )
    JOURNAL.append(
        {
            "id": DERNIER,
            "ref": article["ref"],
            "q": quantite,
            "t": options.type_mouvement,
        }
    )
    return True


def calculer_cout_reapprovisionnement(article):
    """Chiffrer la commande vers le stock cible avec la remise actuelle."""
    if article["q"] < article["seuil"]:
        quantite_a_commander = (
            article["seuil"] * MULTIPLICATEUR_STOCK_CIBLE - article["q"]
        )
        montant = quantite_a_commander * article["pu"]
        if quantite_a_commander > SEUIL_REMISE_QUANTITE:
            montant = montant - montant * TAUX_REMISE_REAPPROVISIONNEMENT
        return round(montant, PRECISION_MONETAIRE)
    return 0


def classer_par_valeur_stock(articles):
    """Créer un classement décroissant stable sans modifier la liste reçue."""
    return sorted(
        articles,
        key=lambda article: article["q"] * article["pu"],
        reverse=True,
    )


def calculer_jours_stock_restants(article, ventes_mensuelles):
    """Calculer la rotation, en conservant le retour historique à zéro en erreur."""
    try:
        return math.floor(article["q"] / (ventes_mensuelles / PERIODE_VENTES_JOURS))
    except (ZeroDivisionError, KeyError, TypeError, ValueError, OverflowError):
        return 0


def calculer_valeurs_par_categorie(articles):
    """Additionner les valeurs par catégorie, puis arrondir chaque total."""
    valeurs_par_categorie = {}

    for article in articles:
        categorie = article["cat"]
        if categorie not in ("outil", "consommable", "piece"):
            categorie = "autre"

        valeur_stock = article["q"] * article["pu"]
        valeurs_par_categorie[categorie] = (
            valeurs_par_categorie.get(categorie, 0) + valeur_stock
        )

    for categorie, valeur in valeurs_par_categorie.items():
        valeurs_par_categorie[categorie] = round(valeur, PRECISION_MONETAIRE)

    return valeurs_par_categorie


def message_rotation(article, ventes):
    """Déterminer le message de rotation sans effectuer d’affichage."""
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
    if jours_restants < SEUIL_SURVEILLANCE_JOURS:
        return "a surveiller " + reference
    return None


def respecte_filtres(article, categorie, quantite_minimale):
    """Vérifier les filtres de catégorie et de quantité minimale."""
    if categorie is not None and article["cat"] != categorie:
        return False
    if quantite_minimale is not None and article["q"] < quantite_minimale:
        return False
    return True


def motif_exclusion_article(article):
    """Renvoyer la raison d’exclusion, ou None si l’article est comptabilisable."""
    if article["q"] > 0:
        if article["pu"] > 0:
            return None
        return "prix invalide " + article["ref"]
    return "stock vide " + article["ref"]


def messages_article(article, ventes):
    """Préparer les messages d’alerte et de rotation dans leur ordre historique."""
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
    """Calculer les totaux et messages sans horloge, affichage ni accès aux fichiers."""
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
        "valeur": round(valeur_totale, PRECISION_MONETAIRE),
        "nb": nombre_articles,
        "alertes": references_en_alerte,
        "ttc": round(valeur_totale * (1 + TAUX_TVA), PRECISION_MONETAIRE),
    }
    return resultat, messages


def generer_rapport(articles, ventes=None, date_rapport=None, options=None):
    """Orchestrer la date, le calcul pur, les affichages et l’export optionnel."""
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
        exporter_rapport_json(resultat)
    return resultat


def exporter_rapport_json(resultat):
    """Écrire un rapport dans le fichier temporaire numéroté habituel."""
    identifiant = random.randint(IDENTIFIANT_EXPORT_MIN, IDENTIFIANT_EXPORT_MAX)
    chemin = "/tmp/rapport_" + str(identifiant) + ".json"
    with open(chemin, "w", encoding="utf-8") as fichier:
        fichier.write(json.dumps(resultat))


def exporter_historique_json(
    resultat, chemin=CHEMIN_HISTORIQUE_PAR_DEFAUT, historique=None
):
    """Ajouter le résultat à l’historique fourni ou partagé, puis l’exporter."""
    if historique is None:
        historique = HISTORIQUE_EXPORT_PARTAGE

    historique.append(resultat)
    with open(chemin, "w", encoding="utf-8") as fichier:
        fichier.write(json.dumps(historique))
    return historique
