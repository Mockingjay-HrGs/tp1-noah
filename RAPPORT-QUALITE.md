# Rapport qualité, module inventaire

Nom :
Date :
Empreinte du commit de départ :

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

Rempli pendant la mission 3, sans rien corriger.

| Règle | Ligne | Ce que le code fait | Ce que la règle dit |
|---|---|---|---|
|M2|32|À quantité égale au seuil, aucune alerte : comparaison stricte `<`.|L'article doit être en alerte lorsque sa quantité est inférieure ou égale au seuil.|

---

## 5. Tableau de bord après refactoring

Mêmes mesures, mêmes commandes qu'en partie 1.

| Mesure | Avant | Après | Écart |
|---|---|---|---|
|  |  |  |  |

Ce que ce delta prouve, en trois phrases maximum :

---

## 6. Bugs prouvés puis corrigés

| Règle violée | Ligne d'origine | Commit red | Commit fix | Conséquence métier |
|---|---|---|---|---|
|  |  |  |  |  |

Pour au moins un de ces bugs, la conséquence est chiffrée en euros ou en ruptures de stock.
