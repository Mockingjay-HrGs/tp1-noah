# Rapport de conception — Noah

Date : 18 septembre 2026. Départ : `e40136c` (`depart-tp2`).

## 1. Les cinq violations (lignes de depart-tp2)

| Principe | Fichier et ligne | Symptôme observable | Conséquence concrète |
|---|---|---|---|
| SRP | facturation/facture.py:33–59 | `emettre` calcule les montants, compose six lignes de texte et appelle SMTP. | Changer la présentation du courriel oblige à rouvrir la méthode qui numérote et calcule les factures. |
| OCP | facturation/tarifs.py:24–53 | Trois fonctions sélectionnent prix, palier et promotion avec des `if`. | Chaque nouvelle formule, remise ou promotion modifie une fonction déjà testée. |
| LSP | facturation/abonnements.py:47–55 | `AbonnementAnnuel.resilier` lève systématiquement une exception, même pour une date après le début. | Un client acceptant un `Abonnement` ne peut pas résilier un annuel selon le contrat du parent. |
| ISP | facturation/passerelles.py:6–25, 39–43 | Six méthodes abstraites imposées à SMTP ; SMS et push lèvent `NotImplementedError`. | Un fournisseur de courriel doit implémenter des opérations inutiles, et un client peut appeler une opération non supportée. |
| DIP | facturation/facture.py:4, 7, 27, 40 | Import de `ClientSMTP`, construction directe et lecture de `datetime.now()`. | Tester le destinataire exige de capturer stdout ; tester une facture de 2019 exige de modifier l'horloge ou de patcher une dépendance. |

## 2. Coût des demandes avant

| Demande | Fichiers à rouvrir | Fonctions à modifier | Tests existants à rejouer |
|---|---|---|---|
| D1 découverte | 1 : tarifs.py | prix_par_poste | 14 cas : 4 catalogue, 3 montants, 4 promotions, 3 émission ; suite complète 25 |
| D2 RENTREE | 1 : tarifs.py | appliquer_code_promo | 10 cas : 3 montants, 4 promotions, 3 émission ; suite complète 25 |
| D3 200 postes | 1 : tarifs.py | taux_de_remise_volume | 16 cas : 6 paliers, 3 montants, 4 promotions, 3 émission ; suite complète 25 |

## 3. Dépendances initiales

Commande : `rg -n '^(from |import )' facturation -g '*.py' -g '!test_*.py'`.

| Module | Imports | Inversion nécessaire |
|---|---|---|
| abonnements | dataclasses, datetime.date | non : données et dates explicites |
| tarifs | abonnements | non : métier vers métier |
| facture | dataclasses, datetime.date/datetime, abonnements, passerelles, tarifs | oui : passerelles.ClientSMTP et horloge globale |
| passerelles | abc | non : infrastructure |
| __init__ | aucun | non |

## Contraintes contradictoires et choix de réalisation

Le test initial à 500 postes impose 20 %, alors que D3 impose 30 %. La configuration
historique restera accessible aux fonctions d'origine ; l'assemblage applicatif utilisera
une configuration indépendante qui recevra les extensions. Les tests ne seront ni
supprimés ni neutralisés : les deux configurations auront des tests explicites.

La mission 5 exige de modifier la hiérarchie, mais le gel après mission 4 interdit ces
modifications. La preuve rouge puis la correction LSP seront donc faites avant
`ouverture-terminee`, sans introduire D1, D2 ou D3 avant cette étiquette. Ce décalage est
explicite : l'ordre strict des missions 4 et 5 et le gel absolu ne peuvent être satisfaits
simultanément. Le support `jour2/cours-jour2.md` n'est pas présent dans les fichiers fournis.
