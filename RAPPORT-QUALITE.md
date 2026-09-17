# Rapport qualité, module inventaire

Nom :
Date : 17 septembre 2026 (mesures après refactoring)
Empreinte du commit de départ : `2a3b2edb5698c9b3f37c2c235a2ca863a7a8183d`

---

## 1. Tableau de bord initial

Mesures relevées avant toute modification.

### Complexité par fonction

| Fonction | Ligne | Complexité cyclomatique | Rang |
|---|---|---|---|
|rapport|122|22|D|
|par_cat|94|10|B|
|mouv|37|9|B|
|classer|74|5|A|
|val|19|3|A|
|alerte|29|3|A|
|cout|62|3|A|
|rot|87|2|A|
|maj_prix|175|1|A|
|export_json|185|1|A|

Commande utilisée :

```bash
radon cc inventaire/legacy/inventaire.py -s -a
```

### Synthèse du fichier

| Mesure | Valeur | Commande |
|---|---|---|
| Lignes de code réelles |159|radon raw inventaire/legacy/inventaire.py|
| Complexité moyenne |5,9 - rang B|radon cc inventaire/legacy/inventaire.py -s -a|
| Indice de maintenabilité |36,80 - rang A|radon mi inventaire/legacy/inventaire.py -s|
| Score pylint |7,76/10|pylint inventaire/legacy/inventaire.py|
| Problèmes ruff |14|ruff check inventaire/legacy/inventaire.py|
| Entrées vulture |14|vulture inventaire/legacy/inventaire.py|
| Couverture de branches |Non mesurée : aucun test découvert, aucune donnée collectée|pytest --cov=inventaire/legacy --cov-branch --cov-report=term-missing|
| Barrière xenon |Échec : fonction rapport de rang D, moyenne et module de rang B|xenon --max-absolute B --max-modules A --max-average A inventaire/legacy/inventaire.py|

---

## 2. Catalogue des odeurs

Douze entrées minimum. Trois au moins doivent être invisibles pour les outils.
La colonne conséquence décrit ce qui arrive à la personne qui devra modifier ce
fichier dans six mois.

| # | Ligne | Odeur ou défaut | Détecté par | Conséquence concrète |
|---|---|---|---|---|
| 1 | 37, 185 | Arguments par défaut mutables (`j=[]`, `hist=[]`) | pylint, ruff | La même liste est conservée entre les appels sans argument explicite : une modification peut faire apparaître des données provenant d'un appel précédent. |
| 2 | 38, 56–58 | État global partagé (`DERNIER`, `JOURNAL`) | pylint pour `global`, lecture manuelle pour `JOURNAL` | Comprendre ou tester un mouvement exige de connaître l'état laissé par les appels précédents. |
| 3 | 37, 122 | Trop de paramètres : 6 pour `mouv`, 7 pour `rapport` | pylint | Lors d'une modification des appels, les nombreux paramètres augmentent le risque d'inversion et compliquent la lecture. |
| 4 | 90–91 | Capture de toutes les exceptions sans distinction | pylint, ruff | Une clé absente ou une donnée invalide peut être masquée par un retour à zéro, ce qui complique le diagnostic. |
| 5 | 130–163 | Imbrication excessive des conditions | pylint, ruff pour certaines conditions imbriquées | Pour changer une branche, il faut reconstituer toutes les conditions qui permettent de l'atteindre. |
| 6 | 169–171, 187–189 | Gestion manuelle de la fermeture des fichiers | pylint, ruff | Si l'écriture lève une exception, l'appel à `close()` est sauté et la fermeture du fichier n'est pas garantie à cet endroit. |
| 7 | 169, 187 | Encodage des fichiers non explicite | pylint | Le format écrit dépend de l'encodage par défaut de l'environnement, ce qui complique la garantie d'un export identique entre machines. |
| 8 | 175–182 | Fonction `maj_prix` sans effet et ancienne implémentation commentée | pylint et vulture pour les paramètres inutilisés, lecture manuelle pour le corps | Son nom laisse attendre une mise à jour alors qu'elle renvoie seulement `None` : un développeur peut l'utiliser en croyant modifier un prix. |
| 9 | 97–116 | Duplication du calcul de valeur par catégorie | Lecture manuelle ; non signalé par les outils exécutés | Modifier la formule exige de modifier plusieurs branches, avec un risque d'en oublier une. |
| 10 | 89, 148–152 | Nombres métier sans nom explicite (`30`, `7`) | Lecture manuelle ; non signalé par les outils exécutés | Il faut deviner le rôle de chaque nombre avant de changer une période de ventes ou un seuil d'alerte. |
| 11 | 139–170 | Calcul, affichage et export mélangés dans `rapport` | Lecture manuelle ; non signalé par les outils exécutés | Modifier le calcul impose de tenir compte des affichages et des accès au disque, ce qui complique sa réutilisation et ses tests isolés. |
| 12 | 78–83 | Tri manuel avec deux boucles parcourues intégralement | Lecture manuelle ; non signalé par les outils exécutés (pylint signale seulement `i` inutilisé) | Le nombre de comparaisons croît de façon quadratique avec le nombre d'articles ; le développeur doit aussi maintenir lui-même la logique d'échange. |

Les mentions « non signalé » concernent les sorties des outils exécutés pendant cet
audit, avec leur configuration actuelle. Elles ne signifient pas qu'aucun outil ne
pourrait détecter ces problèmes avec une autre configuration.

---

## 3. Faut-il tout réécrire

Les mesures justifient une amélioration progressive du module, sans réécriture
complète. Sur 159 lignes de code et 10 fonctions, `rapport` concentre la plus forte
complexité : 22, rang D, contre une moyenne de 5,9, rang B. La barrière xenon échoue
sur les trois seuils choisis. Aucun test n'est découvert : nous n'avons donc pas
de filet automatique pour vérifier qu'une modification préserve les comportements.

Le score pylint de 7,76/10 et l'indice de maintenabilité de 36,80, classé A par
radon, ne suffisent pas à conclure que le module est facile à modifier. Pylint
vérifie des règles statiques, sans garantir la conformité aux règles métier.
L'indice de maintenabilité résume le fichier et masque les difficultés locales de
`rapport`. Les 14 problèmes ruff, les conditions imbriquées, l'état global et le
mélange des calculs avec les affichages et l'export complètent ce diagnostic.
Les 14 entrées vulture restent des suspicions, puisque seul ce fichier a été analysé.

Le cas Netscape présenté dans le support du jour 1 illustre le risque d'une
réécriture complète : le remplacement du moteur a retardé la livraison d'une
version compétitive. Repartir de zéro peut aussi faire perdre des comportements
accumulés dans le code existant (voir `jour1/cours-jour1.md`, sections « Netscape »
et « Joel Spolsky, 6 avril 2000 »).

Je commencerais par des tests de caractérisation des mouvements de stock, des
alertes et des calculs, puis du rapport, pour figer le comportement actuel et
documenter les écarts métier. Ensuite, je simplifierais `rapport` par petits pas,
en séparant calculs, affichages et export, puis je réduirais les duplications et
l'état partagé. Chaque étape serait vérifiée par les tests et les mêmes mesures.
Enfin, un garde-fou automatique limiterait les régressions ; les bugs documentés
seraient corrigés séparément, après avoir été prouvés par des tests en échec.

---

## 4. Écarts constatés entre le code et les règles métier

Observations de la mission 3, sans correction des règles métier. Les numéros de
ligne se rapportent au module initial du commit `2a3b2ed`, avant les extractions
et renommages. Les tests de caractérisation conservent les comportements observés.

| Règle | Ligne d'origine | Ce que le code fait | Ce que la règle dit |
|---|---|---|---|
| M1 | 22–25 | La valeur du stock ignore les quantités négatives ; un stock de −2 unités à 10 € ne retranche pas 20 € du total. | La valeur est la somme des quantités multipliées par les prix unitaires HT, arrondie au centime. Le cas d'un stock négatif est observable après une sortie excessive. |
| M2 | 32 | À quantité égale au seuil, aucune alerte : comparaison stricte `<`. | L'article doit être en alerte lorsque sa quantité est inférieure ou égale au seuil. |
| M3 | 45–50 | Une sortie de 3 unités sur un stock de 2 est refusée, mais le stock devient −1. | Une sortie excessive doit être refusée et le stock doit rester inchangé. |
| M3 | 46–50 | Avec `force=True`, cette sortie excessive est acceptée et journalisée. | M3 ne prévoit pas d'exception pour une sortie forcée. |
| M5 | 63–71 | À quantité égale au seuil, aucun réapprovisionnement n'est calculé : 0 € pour quantité 5, seuil 5, prix 10 €. | Selon M2 et M5, cet article est en alerte et doit remonter à 15 unités : 10 unités à commander, soit 100 €. |
| M5 | 65 | Pour exactement 100 unités commandées, aucune remise n'est appliquée. | La remise de 10 % s'applique dès 100 unités incluses : 900 € au lieu de 1 000 € dans le cas testé. |
| M7 | 88–91 | Sans vente, la division par zéro est interceptée et la fonction renvoie 0. Des données invalides produisent aussi 0. | En l'absence de ventes, la fonction doit lever une erreur explicite. |
| M8 | 123–124, 169–171 | Le rapport initial lit l'horloge sans date fournie et effectue un export quand demandé. | Le calcul du rapport ne doit dépendre d'aucune ressource extérieure. Ces opérations sont désormais dans `generer_rapport` et `exporter_rapport_json`, hors du calcul pur `calculer_rapport`. Le comportement des appels externes est conservé. |
| M2 | 138–143 | Le rapport exclut les articles de stock nul avant les alertes : stock 0 et seuil 5 ne déclenchent aucune alerte. | Tout article dont la quantité est inférieure ou égale au seuil doit être en alerte, y compris à stock nul. |

Observation technique complémentaire : deux exports sans historique explicite
réutilisent la même liste et le second fichier contient aussi le résultat du
premier. Le test de caractérisation le prouve. Les arguments par défaut mutables
ont été remplacés par `None`, mais les historiques partagés restent explicites
(`HISTORIQUE_EXPORT_PARTAGE`, `JOURNAL_MOUVEMENTS_PARTAGE`) pour ne pas corriger ce
comportement pendant le refactoring.

---

## 5. Tableau de bord après refactoring

Mesures du 17 septembre 2026 sur `inventaire/legacy/inventaire.py` après le commit
`376ef83`. Les commandes et périmètres de la partie 1 sont conservés. Les tests sont
lancés depuis la racine du dépôt, avec l'environnement virtuel actif.

| Mesure | Avant | Après | Écart |
|---|---|---|---|
| Lignes de code réelles (SLOC) | 159 | 212 | +53 : fonctions extraites, options et noms explicites |
| Complexité moyenne de tous les blocs radon | 5,9 — B | 3,33 — A | −2,57 ; 18 blocs après, dont 2 classes d'options |
| Plus forte complexité | `rapport` : 22 — D | `generer_rapport` et `appliquer_variation_stock` : 6 — B | −16 ; deux rangs gagnés pour le rapport |
| Nombre maximal de paramètres par fonction | 7 | 4 | −3 |
| Indice de maintenabilité | 36,80 — A | 28,41 — A | −8,39 ; cette mesure globale ne s'améliore pas |
| Score pylint | 7,76/10 | 9,88/10 | +2,12 |
| Problèmes ruff | 14 | 2 | −12 |
| Entrées vulture, module seul | 14 | 9 | −5 ; fonctions publiques appelées dans les tests ou l'exemple |
| Couverture de branches, module inventaire | Non mesurée | 100 % : 76/76 branches | Toutes les branches instrumentées sont exécutées |
| Couverture instructions + branches, module inventaire | Non mesurée | 100 % : 174/174 instructions, 76/76 branches | Aucun manque dans le module |
| Couverture instructions + branches, dossier `inventaire/legacy` | Non mesurée | 95 % | Inclut l'exemple, exécuté séparément hors couverture |
| Couverture de branches du dossier complet | Non mesurée | 97,44 % : 76/78 branches | Les 2 branches non couvertes appartiennent à l'exemple |
| Barrière xenon B / A / A | Échec | Réussite, code de sortie 0 | Fonction maximale B, module et moyenne A |
| Tests | Aucun test découvert lors de l'audit initial | 50 inventaire + 21 parking = 71 réussis | Tests de caractérisation et parking exécutés ensemble |

Ce que ce delta prouve, en trois phrases maximum :

La complexité maximale est passée de D (22) à B (6), tandis que les 50 tests
inventaire et les 21 tests parking passent. Le module inventaire est couvert à
100 % en instructions et branches, et les calculs sont séparés des affichages,
de l'horloge et des fichiers. Le fichier contient davantage de code et son indice
de maintenabilité baisse ; ces chiffres ne prouvent ni l'absence de bugs métier
ni une amélioration de chaque mesure.

### Commandes et périmètres

```bash
radon raw inventaire/legacy/inventaire.py
radon cc inventaire/legacy/inventaire.py -s -a
radon mi inventaire/legacy/inventaire.py -s
pylint inventaire/legacy/inventaire.py
ruff check inventaire/legacy/inventaire.py
vulture inventaire/legacy/inventaire.py
pytest --cov=inventaire/legacy --cov-branch --cov-report=term-missing
xenon --max-absolute B --max-modules A --max-average A inventaire/legacy/inventaire.py
```

Versions : Python 3.14.3, pytest 9.1.1, radon 6.0.1, xenon 0.9.3,
pylint 4.0.8, ruff 0.16.7, vulture 2.16. Seul le répertoire de cache de pylint a
été déplacé vers un dossier temporaire accessible (`PYLINTHOME`), sans changer
ses règles. La configuration ruff existante est conservée pour la comparaison ;
les garde-fous propres au projet seront installés en mission 4.

### Vérification des critères de la mission 3

- Toutes les fonctions ont quatre paramètres au maximum et un rang A ou B.
- Les nombres métier (période de ventes, seuils de rotation, stock cible, remise,
  TVA, précision monétaire) portent un nom explicite.
- `calculer_rapport` calcule les valeurs et prépare les messages sans `print`,
  horloge ni accès aux fichiers. Seuls les orchestrateurs `generer_rapport` et
  `enregistrer_mouvement` affichent ; les écritures sont dans les fonctions d'export.
- Aucun argument par défaut mutable et aucun `except:` général ne restent.
- `maj_prix` et `STOCK` ont été supprimés dans le commit dédié `b64693e`.
- Les fonctions publiques ont des noms explicites ; les clés historiques des
  données (`q`, `pu`, `ref`, etc.) restent identiques pour préserver leur format.
- Les assertions des tests existants conservent les mêmes attentes ; seuls les
  imports, noms et arguments d'appel ont été migrés.
- L'exemple est adapté dans le commit dédié `3957c8f` : imports et appels renommés,
  données métier inchangées. `python3 exemple_utilisation.py`, depuis
  `inventaire/legacy`, termine avec un code 0 et une valeur HT totale de 1 600,10 €.
- Une comparaison ponctuelle avec le module initial sur 720 rapports combinant
  quantités, prix, seuils, catégories et filtres donne les mêmes résultats et
  affichages. Elle complète les tests sans prouver tous les comportements possibles.

### Limites conservées et observations des outils

Pylint signale encore l'état global du compteur des mouvements et la comparaison
historique `force == False`, conservée pour ne pas changer sa sémantique. Ruff
signale une simplification possible du retour de `respecte_filtres` et la date
locale sans fuseau de l'orchestrateur ; ajouter un fuseau changerait le format
historique testé. Les neuf alertes vulture sur le module seul correspondent aux
fonctions publiques : une analyse incluant tests et exemple ne les signale plus
(elle signale en revanche des usages de mocks dans les tests).

L'état partagé des journaux reste présent : enlever un argument mutable n'élimine
pas ce couplage. Les messages du rapport sont désormais affichés après le calcul
complet ; en cas d'exception pendant ce calcul, aucun message partiel n'est affiché.
Le resserrement des exceptions de rotation laisse aussi remonter les erreurs
inattendues et les interruptions auparavant avalées par le `except:` général.
Les écarts métier de la section 4 attendent leurs tests `red:` et corrections
`fix:` en mission 5 ; ils ne sont pas masqués par les mesures de qualité.

---

## 6. Bugs prouvés puis corrigés

| Règle violée | Ligne d'origine | Commit red | Commit fix | Conséquence métier |
|---|---|---|---|---|
|  |  |  |  |  |

Pour au moins un de ces bugs, la conséquence est chiffrée en euros ou en ruptures de stock.
