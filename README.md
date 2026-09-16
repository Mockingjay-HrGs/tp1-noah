# TP1 : rendre modifiable un code que personne n'ose toucher

Durée 5 heures. Travail individuel. Ce qui est rendu et noté, c'est un dépôt git.

Tout ce dont tu as besoin techniquement est dans le support de cours du jour 1,
`jour1/cours-jour1.md`. Garde-le ouvert à côté. Ici, on te donne des objectifs et
des critères d'acceptation, pas la marche à suivre.

---

## Le contexte qu'on te donne

Tu arrives dans une PME qui gère trois entrepôts de matériel de chantier.

Le module `legacy/inventaire.py` calcule la valeur du stock, les alertes de
réapprovisionnement et le rapport mensuel que la direction reçoit tous les 5 du mois.
Il tourne en production depuis 2019. Il a été écrit par Kevin, qui est parti en 2022.

Ce matin, la responsable logistique t'annonce trois choses.

Elle ne fait plus confiance aux alertes, parce que deux ruptures de stock sont passées
au travers le mois dernier.

La direction veut ajouter une tarification de stationnement pour les camions de
livraison, et veut que ce nouveau module, lui, soit fiable dès le premier jour.

Et ton responsable technique a dit, textuellement : « de toute façon ce fichier est
foutu, on va tout réécrire ».

Ta mission de la journée est de démontrer qu'il a tort, chiffres à l'appui.

---

## Ce qu'on attend de toi à la fin de la séance

Un dépôt git dont l'historique prouve que tu as travaillé en petits pas.

Un fichier `RAPPORT-QUALITE.md` qui contient des mesures avant et après, pas des adjectifs.

Un module neuf, développé intégralement en TDD, avec ses tests.

Le module `inventaire.py` couvert par des tests et refactorisé, à comportement identique
sauf pour les bugs que tu auras explicitement documentés et corrigés.

Un garde-fou automatique qui empêche ton dépôt de se dégrader, et la preuve qu'il bloque.

---

## Les règles du jeu

**Règle 1.** Tu crées ton propre dépôt git. Tu ne travailles jamais sans avoir fait
`git init` et un premier commit.

**Règle 2.** Les messages de commit suivent exactement cette convention, préfixe en
minuscules suivi de deux points :

| Préfixe | Quand | Contenu autorisé dans ce commit |
|---|---|---|
| `red:` | tu viens d'écrire un test qui échoue | du code de test uniquement |
| `green:` | le test passe | du code de production, le minimum |
| `refactor:` | tu améliores la structure, tests verts avant et après | du code de production uniquement |
| `test:` | tu ajoutes un test qui passe du premier coup sur du code existant | du code de test uniquement |
| `fix:` | tu corriges un bug déjà prouvé par un test rouge | du code de production |
| `chore:` | outillage, configuration, documentation | tout le reste |

**Règle 3.** Un commit `green:` doit toujours être précédé d'un commit `red:`. Sans
exception, sur le module développé en TDD.

**Règle 4.** Un commit `red:` doit réellement être rouge. On vérifiera en rejouant
ton historique. Un commit `red:` dont la suite de tests passe au vert vaut zéro pour
le cycle concerné.

**Règle 5.** Tu ne modifies jamais un test pour le faire passer. Si un test te gêne,
c'est qu'il décrit un comportement, et c'est le comportement qu'il faut discuter.

**Règle 6.** Tu ne mélanges jamais un changement de comportement et un refactoring
dans le même commit.

**Règle 7.** Tu commites au minimum toutes les 10 minutes. Si tu n'as rien à commiter
au bout de 10 minutes, c'est que ton pas est trop grand. Reviens en arrière.

---

## Ce que tu dois savoir avant de commencer

Ces éléments sont tous détaillés dans le support du jour 1. Si l'un d'eux ne te dit
rien, va le relire maintenant plutôt qu'à la troisième mission.

Le cycle rouge, vert, refactor et les trois lois.

Les techniques pour passer au vert : faire semblant, l'implémentation évidente, la triangulation.

La structure d'un test en trois blocs et les conventions de nommage des tests.

Les commandes pytest : `-q`, `-x`, `-k`, `--lf`, `--cov`, `--cov-branch`, `--cov-report=term-missing`.

`pytest.raises` et `pytest.mark.parametrize`.

La lecture des sorties de `radon cc`, `radon mi`, `pylint`, `ruff`, `vulture`, `xenon`.

Les cinq propriétés FIRST et la raison pour laquelle un test unitaire ne touche jamais
à l'horloge système.

---

# Mission 0 : monter ton atelier

**Durée indicative : 20 minutes.**

Tu dois arriver à un état où une seule commande te dit si ton projet va bien.

Ce qui doit être vrai à la fin de cette mission.

Un dossier de travail à toi, nommé `tp1-tonnom`, qui est un dépôt git initialisé.

Un environnement virtuel Python actif et un fichier `requirements-dev.txt` qui liste
les outils. Le support de cours contient la liste exacte des outils attendus.

Une copie de `legacy/inventaire.py` et `legacy/exemple_utilisation.py` dans un sous-dossier
`inventaire/` de ton dépôt. Tu travailles sur ta copie, jamais sur l'original.

Un fichier `.gitignore` qui exclut au minimum `.venv/`, `__pycache__/`, `.pytest_cache/`,
`htmlcov/` et `.coverage`. Un dépôt qui contient l'environnement virtuel perd des points.

Un premier commit `chore:` qui contient tout ça.

**Critère d'acceptation.** `git log --oneline` affiche au moins un commit, `pytest --version`
et `radon --version` répondent, et `git status` est propre.

---

# Mission 1 : l'état des lieux chiffré

**Durée indicative : 45 minutes.**

Ton responsable technique veut tout réécrire. Tu vas lui répondre avec un diagnostic,
pas avec une opinion.

Interdiction absolue pendant cette mission : tu ne corriges rien, tu ne renommes rien,
tu ne réorganises rien. Tu mesures et tu décris.

## Ce que tu produis

Un fichier `RAPPORT-QUALITE.md` à la racine de ton dépôt, structuré en trois parties.

**Partie 1, le tableau de bord initial.** Une ligne par fonction du module, avec sa
complexité cyclomatique et son rang. Puis une ligne de synthèse pour le fichier entier
avec le nombre de lignes de code réelles, la complexité moyenne, l'indice de maintenabilité,
le score pylint, le nombre de problèmes remontés par ruff, et la couverture de tests actuelle.

Pour chaque chiffre, indique la commande exacte qui l'a produit. Un chiffre sans sa
commande n'est pas un chiffre, c'est une affirmation.

**Partie 2, le catalogue des odeurs.** Au minimum douze problèmes distincts, chacun avec
son numéro de ligne, le nom de l'odeur ou du défaut, et une phrase expliquant la
conséquence concrète pour quelqu'un qui devrait modifier ce fichier demain.

Les odeurs que tu cherches ont été listées en cours. Certaines sont détectées par les
outils, d'autres non. Celles que les outils ne voient pas valent plus cher dans la notation.

Au moins trois de tes douze entrées doivent concerner un problème qu'aucun outil n'a
signalé.

**Partie 3, l'argumentaire.** Une demi-page maximum. Tu réponds à la question
« faut-il tout réécrire ». Tu t'appuies sur tes chiffres et sur au moins un exemple
historique vu en cours. Tu proposes un ordre d'intervention en justifiant par où
tu commences et pourquoi.

## Le piège de cette mission

Le score pylint de ce fichier est plutôt flatteur. L'indice de maintenabilité aussi.
Si ton rapport se contente de ces deux chiffres, il conclura que tout va bien, et il
aura tort. Trouve les indicateurs qui, eux, disent la vérité, et explique dans ton
argumentaire pourquoi les deux premiers t'ont menti.

**Critère d'acceptation.** Un commit `chore: rapport d'audit initial` contenant
`RAPPORT-QUALITE.md`. Le code de `inventaire.py` est strictement inchangé à ce stade,
vérifiable par `git diff`.

---

# Mission 2 : le module neuf, en TDD strict

**Durée indicative : 95 minutes.**

C'est la mission qui pèse le plus lourd dans la note. Ce n'est pas le code final qui
est évalué, c'est ton historique git.

Tu développes un tarificateur pour le parking des camions de livraison, dans
`kata_parking/parking.py`, avec ses tests dans `kata_parking/test_parking.py`.

## La méthode imposée

Tu traites les exigences dans l'ordre, une par une. Tu ne lis pas l'exigence suivante
avant d'avoir terminé la précédente.

Pour chaque exigence, tu produis au minimum une paire de commits `red:` puis `green:`,
et tu ajoutes un commit `refactor:` chaque fois que le code le mérite.

Tu ne crées aucun fichier de production avant que le premier test n'existe et n'échoue.

Le nom de chacun de tes tests doit décrire un comportement métier. Quelqu'un qui lit
uniquement la liste de tes noms de tests doit pouvoir reconstituer le cahier des charges.

## Les exigences, à traiter dans cet ordre

**E1.** Un stationnement de 30 minutes ou moins est gratuit.

**E2.** Au-delà de 30 minutes, chaque demi-heure commencée est facturée 1,50 euro.
Les 30 premières minutes restent gratuites.

**E3.** Le montant est plafonné à 18 euros par tranche de 24 heures commencée.

**E4.** Un camion abonné paie 60 % du montant calculé, plafond compris.

**E5.** Un camion électrique branché sur une borne bénéficie de 60 minutes gratuites
au lieu de 30. L'avantage se cumule avec l'abonnement.

**E6.** Une durée négative, ou une heure de sortie antérieure à l'heure d'entrée,
lève une erreur dont le message explique le problème.

**E7.** Au-delà de 72 heures, le véhicule est déclaré en fourrière et le montant est
un forfait de 250 euros. Ni le plafond journalier, ni la remise abonné, ni l'avantage
électrique ne s'appliquent dans ce cas.

**E8.** La responsable veut connaître le montant dû par un camion encore stationné,
à l'instant présent. Tu ajoutes cette possibilité. Contrainte non négociable : tes
tests doivent rester reproductibles dans dix ans, un samedi comme un lundi. Le support
de cours explique la technique.

## Quelques valeurs de référence

Cette liste n'est pas exhaustive et c'est volontaire. Les valeurs limites qui manquent,
c'est à toi de les trouver, et ce sont elles qui rapportent des points.

| Situation | Montant attendu |
|---|---|
| 30 minutes | 0,00 |
| 31 minutes | 1,50 |
| 60 minutes | 1,50 |
| 61 minutes | 3,00 |
| 120 minutes | 4,50 |
| 8 heures | 18,00 |
| 25 heures | 36,00 |
| 31 minutes, abonné | 0,90 |
| 60 minutes, électrique | 0,00 |
| 61 minutes, électrique et abonné | 0,90 |
| 72 heures exactement | 54,00 |
| 72 heures et 1 minute | 250,00 |

Attention à la ligne des 72 heures exactement. Relis E7 avant de coder.

## Ce qui est vérifié à la fin de la mission

Toutes les exigences de E1 à E8 sont couvertes par au moins un test.

Ton historique contient au moins 8 paires `red:` puis `green:` sur ce module. En pratique,
un travail correct en produit entre 12 et 20.

Chaque commit `red:` ne contient que du code de test. On le vérifie avec `git show --stat`.

Chaque commit `red:` fait bien échouer la suite. On le vérifie en rejouant ton historique.

Aucune fonction de `parking.py` ne dépasse le rang A au sens de radon.

La couverture de branches de `parking.py` est d'au moins 95 %.

Aucun test ne contient de `if`, de boucle, ou d'appel à l'horloge système.

---

# Mission 3 : poser le filet avant de toucher au patient

**Durée indicative : 65 minutes.**

Tu reviens sur `inventaire/inventaire.py`. Règle non négociable de cette mission :
aucune ligne de code de production n'est modifiée tant qu'un test ne décrit pas le
comportement actuel de la partie concernée.

## Première partie, le filet

Tu écris des tests qui décrivent ce que le code fait **aujourd'hui**, y compris quand
ce qu'il fait est faux.

Oui, tu vas écrire des tests qui figent un comportement que tu sais incorrect. C'est
volontaire. Ces tests ne sont pas là pour dire si le code est juste, ils sont là pour
t'alerter si tu changes quelque chose sans le vouloir pendant le refactoring.

Chaque fois que tu remarques un écart entre ce que le code fait et ce que les règles
métier ci-dessous décrivent, tu ne corriges pas. Tu ajoutes une ligne dans une section
`Écarts constatés` de ton `RAPPORT-QUALITE.md`, avec le numéro de ligne, ce que le code
fait, et ce que la règle dit.

Ces tests-là se commitent avec le préfixe `test:`.

## Les règles métier officielles du module

Elles sont extraites du cahier des charges de 2019. Le code est censé les respecter.

**M1.** La valeur du stock est la somme des quantités multipliées par les prix unitaires
hors taxe, arrondie au centime.

**M2.** Un article est en alerte lorsque sa quantité est inférieure ou égale à son seuil.
Un article dont la quantité est exactement au seuil est en alerte.

**M3.** Un mouvement de sortie dont la quantité dépasse le stock disponible est refusé,
et le stock reste inchangé.

**M4.** Un mouvement dont la quantité est nulle ou négative est refusé.

**M5.** Le coût de réapprovisionnement d'un article en alerte correspond à la quantité
nécessaire pour remonter à trois fois le seuil, multipliée par le prix unitaire. Une
remise de 10 % s'applique à partir de 100 unités commandées, 100 incluses.

**M6.** Le classement par valeur trie les articles par valeur de stock décroissante.

**M7.** La rotation renvoie le nombre de jours de stock restant, arrondi à l'entier
inférieur, à partir des ventes des 30 derniers jours. Si aucune vente n'a eu lieu,
la fonction lève une erreur explicite plutôt que de renvoyer une valeur.

**M8.** Le rapport mensuel ne modifie aucune donnée et ne dépend d'aucune ressource
extérieure au moment où il calcule.

## Deuxième partie, la chirurgie

Une fois le filet en place, tu refactorises. Petits pas, tests verts après chaque pas,
un commit `refactor:` par pas.

Ce que tu dois avoir obtenu à la fin.

Aucune fonction du module au-dessus du rang B au sens de radon, et la fonction la plus
complexe descendue d'au moins deux rangs par rapport à ta mesure initiale.

Aucune fonction avec plus de 4 paramètres.

Aucun nombre magique dans le code métier.

Aucun `print` dans le code de calcul.

Aucun argument par défaut mutable.

Aucun attrape-tout d'exception.

Le code mort supprimé, dans un commit séparé et identifiable.

Des noms de fonctions et de variables compréhensibles sans commentaire.

## Ce qui est vérifié

Les tests écrits en première partie sont toujours verts à la fin, à l'exception de ceux
que tu auras explicitement modifiés en mission 5, avec justification.

`git log` montre une succession de petits commits `refactor:`, pas un commit géant
intitulé `refactor: tout`.

Les métriques après, relevées dans `RAPPORT-QUALITE.md` avec les mêmes commandes qu'en
mission 1.

**Critère d'acceptation supplémentaire.** `python3 exemple_utilisation.py` doit toujours
fonctionner à la fin. Si tu as changé les signatures, tu adaptes ce fichier dans un
commit dédié et tu l'expliques.

---

# Mission 4 : rendre la régression impossible

**Durée indicative : 30 minutes.**

Tout ce que tu viens de faire sera annulé dans trois mois si rien ne l'empêche. Tu
installes le mécanisme qui l'empêche.

## Ce que tu mets en place

Une configuration `pyproject.toml` qui fixe les seuils de ton équipe : longueur de ligne,
complexité maximale, nombre maximal d'arguments, couverture minimale.

Un fichier `.pre-commit-config.yaml` qui accroche au minimum le formatage, le lint, les
tests, et une barrière de complexité, et qui est réellement installé par `pre-commit install`.

Un script `verifier.sh` à la racine, exécutable, qui lance toute la chaîne et renvoie
un code de sortie non nul dès qu'un contrôle échoue.

Le support du jour 1 contient un exemple de chacun de ces trois fichiers. Tu as le droit
de t'en inspirer, à condition d'adapter les seuils à ton projet et d'être capable
d'expliquer chaque ligne à l'oral.

## La preuve

Un fichier `preuve-garde-fou.txt` à la racine, qui contient la sortie complète du terminal
lors d'une tentative de commit volontairement fautive.

Tu casses une ligne, tu tentes de commiter, tu copies la sortie, tu remets la ligne
en état, et tu commites la preuve.

Ce fichier doit montrer un contrôle en échec et l'absence de commit créé.

**Critère d'acceptation.** `./verifier.sh` renvoie 0 sur ton dépôt final, et
`echo $?` le confirme.

---

# Mission 5 : prouver le bug avant de le corriger

**Durée indicative : 25 minutes.**

Tu reprends ta section `Écarts constatés` de la mission 3.

Tu en choisis au minimum deux. Pour chacun, dans cet ordre strict, sans raccourci.

Tu écris un test qui exprime la règle métier officielle. Il échoue, puisque le code est
faux. Tu commites en `red:`.

Tu corriges le code de production, le minimum nécessaire. Tu commites en `fix:`.

Tu vérifies que le test de caractérisation écrit en mission 3, celui qui figeait le
comportement faux, est maintenant rouge. Tu le mets à jour pour qu'il décrive le
comportement correct, et tu commites ce changement avec un message qui explique
pourquoi tu modifies un test.

C'est le seul moment du TP où tu as le droit de modifier un test existant, et c'est
parce que le comportement attendu a officiellement changé.

## Ce que tu documentes

Dans `RAPPORT-QUALITE.md`, une section finale avec, pour chaque bug corrigé : la règle
métier violée, la ligne d'origine, l'empreinte du commit `red:` qui le prouve, l'empreinte
du commit `fix:` qui le corrige, et une phrase sur la conséquence métier réelle. Pour
au moins un des bugs, cette conséquence doit être chiffrable en euros ou en ruptures de stock.

## Un indice, et un seul

Deux des écarts se trouvent dans des comparaisons. Un troisième se voit uniquement si tu
appelles deux fois la même fonction de suite et que tu observes le résultat du deuxième appel.

---

# Comment ton rendu sera vérifié

On ne lira pas seulement ton code final. On rejouera ton historique.

```bash
git log --oneline
git log --format="%h %s" --reverse
```

On compte les paires `red:` puis `green:`, et on vérifie l'ordre.

```bash
git show --stat <commit_red>
```

On vérifie qu'un commit `red:` ne contient aucun fichier de production.

Et surtout, on tire au hasard trois de tes commits `red:` et on relance la suite de tests
à cet état exact. Elle doit être rouge. Si elle est verte, le commit ment.

Un script fait tout cela automatiquement, il est fourni avec le sujet. Lance-le sur ton
propre dépôt avant de rendre, tu verras passer les mêmes contrôles que nous.

```bash
cd /chemin/vers/tp1
./outils/verifier-historique.sh /chemin/vers/ton/depot 3
```

Le dernier argument est le nombre de commits `red:` tirés au hasard et rejoués.

Un squelette de `RAPPORT-QUALITE.md` est fourni dans `modeles/`. Tu le copies à la racine
de ton dépôt et tu le remplis. Les sections sont imposées, le contenu est à toi.

---

# Le barème

| Ce qui est évalué | Points |
|---|---|
| Hygiène du dépôt : `.gitignore`, pas de fichiers parasites, commits atomiques, messages conformes | 1 |
| Mission 1 : tableau de bord chiffré avec ses commandes | 1,5 |
| Mission 1 : catalogue de douze odeurs dont trois invisibles aux outils | 1 |
| Mission 1 : argumentaire contre la réécriture, appuyé sur les chiffres | 0,5 |
| Mission 2 : exigences E1 à E8 couvertes par des tests pertinents | 2 |
| Mission 2 : historique `red` puis `green` conforme et rejouable | 3 |
| Mission 2 : qualité des noms de tests et des valeurs limites choisies | 1 |
| Mission 2 : complexité et couverture de branches du module neuf | 1 |
| Mission 3 : filet de tests sur au moins six fonctions avant toute modification | 2 |
| Mission 3 : refactoring en petits pas, comportement préservé | 2 |
| Mission 3 : métriques après, mesurées et commentées | 1 |
| Mission 4 : garde-fou fonctionnel et preuve du blocage | 2 |
| Mission 5 : deux bugs prouvés par un test rouge avant correction | 2 |
| **Total** | **20** |

Pénalités.

Un commit `green:` sans `red:` correspondant sur le module en TDD : moins 0,5 par
occurrence, dans la limite de 3 points.

Un commit `red:` qui passe au vert quand on le rejoue : moins 1 par occurrence.

Le dossier `.venv` versionné : moins 1.

Un fichier `RAPPORT-QUALITE.md` qui contient des adjectifs à la place des chiffres :
moins 2.

---

# Si tu bloques

**Tu ne sais pas par quel test commencer en mission 2.** Prends la situation la plus
simple possible, celle où il ne se passe presque rien. Ici, c'est un camion qui reste
une minute.

**Ton test ne veut pas échouer alors qu'il devrait.** Lis le message de pytest en entier.
Neuf fois sur dix, le fichier de test n'est pas ramassé, ou l'assertion compare deux
choses toujours égales.

**Tu es au rouge depuis vingt minutes.** Ton pas est trop grand. `git stash`, reviens au
dernier vert, et redécoupe.

**Tu ne sais pas quoi tester dans `inventaire.py`.** Appelle la fonction avec le jeu de
données de `exemple_utilisation.py`, regarde ce qu'elle renvoie, et écris un test qui
affirme exactement ça. Tu ne juges pas, tu enregistres.

**Le refactoring casse tout.** C'est l'information que tu cherchais. Annule le dernier
pas, fais-en un plus petit.

**Tu as fini en avance.** Trois pistes : monte la couverture de branches de `inventaire.py`
au-dessus de 90 %, remplace les dictionnaires d'articles par un type dédié sans casser
un seul test, ou ajoute une exigence E9 de ton invention au kata parking et traite-la en TDD.
