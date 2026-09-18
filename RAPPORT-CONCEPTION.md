# Rapport de conception — Noah

Date : 18 septembre 2026. Départ : `e40136c` (`depart-tp2`).
Ouverture : `7b49c8b` (`ouverture-terminee`).

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

## 4. Points de variation ouverts

| Variation | Technique | Justification |
|---|---|---|
| Prix | Dictionnaire formule → prix | Une donnée suffit ; aucune classe par formule. |
| Volume | Dictionnaire seuil → taux, sélection du plus grand seuil admissible | Les inscriptions n'ont pas besoin d'être triées ; aucun `if` par palier. |
| Promotion | Dictionnaire code → fonction | BIENVENUE dépend de la première facture, NOEL non : fonctions de même signature, sans hiérarchie artificielle. |

`Tarification` regroupe trois registres indépendants par instance. `registre.tarification`
est la configuration de l'application ; `TARIFICATION_ORIGINE` assure la compatibilité
explicite des fonctions historiques. Le calculateur est injecté avec `functools.partial`.

À la fin de l'ouverture : 41 tests verts, dont les 25 cas initiaux. Les tests initiaux
n'ont changé que d'import (`facture` → `assemblage`), conformément à la tolérance de la
mission 2. Aucun test n'est désactivé. Les trois règles nouvelles ne sont pas encore présentes.

Commandes de contrôle :

```bash
python3 -m pytest
python3 -m pytest --cov=facturation.facture --cov-branch --cov-fail-under=100
ruff check .
git diff depart-tp2 -- facturation/test_facturation.py
rg -n 'passerelles|datetime.now|presentation|print\(' facturation/{tarifs,facture,abonnements}.py
rg -n 'datetime.now' facturation -g '*.py'
```

La première recherche ne doit rien trouver ; la seconde doit désigner seulement
`assemblage.py`. Le protocole `EnvoiDeCourriel` est dans `facture.py`, chez son client :
le métier définit son besoin et les fournisseurs s'y adaptent. SMTP et le double mémoire
l'implémentent structurellement ; le double ne déclare qu'une méthode.

## 5. Coût des demandes après

| Demande | Fichiers existants rouverts / fonctions modifiées | Fichiers créés | Lignes initiales supprimées | Tests neufs / anciens rejoués |
|---|---|---|---|---|
| D1 découverte | assemblage.py : un import ; aucune fonction | extensions/decouverte.py, test_decouverte.py | 0 | 6 cas / les 25 initiaux |
| D2 RENTREE | aucun fichier présent au gel ; aucune fonction | extensions/rentree.py, test_rentree.py | 0 | 9 cas / les 25 initiaux |
| D3 200 postes | aucun fichier présent au gel ; aucune fonction | extensions/volume_200.py, test_volume_200.py | 0 | 11 cas / les 25 initiaux |

Un septième fichier neuf, `extensions/__init__.py`, assemble les trois inscriptions.
Les fonctions métier initiales ne changent plus. Les suites complètes passent après
chaque extension : 47, 56 puis 67 cas. Le test D3 intégré compose les trois règles :
200 × 4 × 0,70 × 0,90 = 504 € HT, puis 604,80 € TTC.

Sortie utile du vérificateur fourni, lancé avec
`PYTEST_ADDOPTS='-o addopts=' ./outils/verifier-ocp.sh .` :

```text
depart-tp2 : 25 tests
ouverture : 41 tests
HEAD : 67 tests
facturation/assemblage.py : 1 ligne d'import ajoutée, tolérée
aucune ligne supprimée dans un fichier existant
aucun fichier de test existant modifié
aucun ajout de code dans un fichier existant
7 fichiers Python neufs ; 3 fichiers de tests neufs ; 12 fonctions de test ajoutées
la suite a grossi de 26 tests pendant l'extension
suite verte : 67 passed
Extension conforme. Rien n'a été modifié, tout a été ajouté.
```

Le contrôle porte sur le diff depuis l'étiquette, pas sur le dépôt parent. Ruff et le
formatage sont verts. Couverture de `facture.py` : 100 % des instructions ; aucune
branche dans ce module, donc aucune branche manquante. Couverture globale : 94 %.
La complexité du code de production est au rang A (maximum 4).

## 6. La hiérarchie qui ment

Preuve rouge : commit `7c6df4f`, **7 échecs et 10 succès** dans la suite partagée et les
cas annuels. Cinq échecs proviennent du contrat commun, deux du terme annuel.
Correction : `e63451d`. La suite découvre automatiquement les classes du module qui
héritent d'`Abonnement` : initialement Abonnement, AbonnementAnnuel, AbonnementEssai ;
après correction Abonnement et AbonnementEssai. Le fichier de contrat n'a pas eu besoin
de changer sa sélection pour cacher un échec.

| Type | Contrat initial | Clause brisée | Correction |
|---|---|---|---|
| Abonnement | respecté | — | inchangé |
| AbonnementEssai | respecté | — | inchangé |
| AbonnementAnnuel | violé | exception nouvelle `ResiliationImpossible`, y compris là où le parent promet ValueError | ne prétend plus être un Abonnement ; contient un Abonnement et une fonction de validation d'engagement |

La résiliation avant douze mois reste interdite, sans mutation de la date de fin.
Au terme inclus et après, le cycle contenu accepte la résiliation. Le terme du
29 février est fixé au 28 février de l'année suivante, hypothèse explicite testée.
Cette correction change intentionnellement le refus systématique initial, comme le
demande la mission 5. Le test initial annuel reste vert et inchangé : il exerce juillet,
avant le terme, malgré son intitulé plus large. Aucun test livré n'a été modifié sur le fond.


## 7. Principe par principe, le coût de lecture

**S.** Le calcul produit une `Facture`, la présentation produit une chaîne, le fournisseur
achemine le message. Suivre le calcul et la mise en forme demande désormais deux fichiers
au lieu d'un, soit un fichier supplémentaire, mais chaque changement a son responsable.

**O.** Prix et paliers sont des données, les promotions des fonctions enregistrées.
Pour suivre une nouvelle règle jusqu'à son usage, le lecteur ouvre `tarifs`, `registre`
et le module d'extension : deux fichiers de plus que l'ancien module unique.

**L.** L'annuel compose un abonnement et une fonction qui vérifie l'engagement ; l'essai
reste un sous-type substituable. Aucun fichier supplémentaire à ouvrir pour suivre une
résiliation, mais une délégation et cinq propriétés d'accès sont le prix de la compatibilité.

**I.** Le protocole client exige seulement `envoyer_courriel`, implémenté par SMTP et par
le double mémoire ; les méthodes impossibles SMS/push ont disparu. Aucun fichier de plus
pour comprendre ce contrat, qui vit dans le module de facturation lui-même.

**D.** Horloge, fournisseur, calculateur configuré et présentation sont raccordés dans
`assemblage.py`. Un lecteur ouvre un fichier supplémentaire pour comprendre les choix
concrets ; le métier peut être exercé sans réseau ni horloge globale.

## 8. Le procès : le registre mutable et le chargement par import

J'ai introduit `registre.tarification`, rempli lorsque l'assemblage importe les extensions.
Ce choix rend chaque ajout très court et satisfait la limite d'une seule ligne d'import,
mais les effets des imports ne sont pas visibles dans le corps du constructeur.
Le lecteur doit ouvrir `assemblage.py`, `extensions/__init__.py`, le module de règle,
puis `registre.py` pour comprendre d'où vient une valeur ; le cache d'import Python
rend aussi la réinitialisation de cette configuration moins intuitive.

J'aurais pu construire une configuration explicite dans une fonction d'assemblage,
avec les trois prix/paliers/promotions réunis : moins de navigation, aucun état global
modifiable, au prix d'une modification de cette fonction à chaque extension. Pour une
application aussi petite, ce serait probablement mon choix hors contrainte du TP.
La coexistence d'une configuration historique et d'une configuration applicative ajoute
encore un risque de confusion : elle répond au test contradictoire à 500 postes, pas à
un besoin produit démontré. Si ce test pouvait être migré, je supprimerais cette double
entrée plutôt que d'en faire une architecture permanente.
