# Le code de départ du TP2

Une application de facturation d'abonnements logiciels, en service depuis trois ans.

## Ce qu'elle vaut aujourd'hui

| Mesure | Valeur |
|---|---|
| Tests | 25, tous verts |
| Complexité maximale | A |
| Complexité moyenne | A (1.70) |
| Problèmes ruff | 0 |
| Fonctions de plus de 20 lignes | 0 |
| Noms compréhensibles | oui |

Sur tous les critères du jour 1, ce code est irréprochable. C'est volontaire.
Le jour 2 commence exactement là où le jour 1 s'arrête.

## Le lancer

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pytest pytest-cov ruff radon xenon
pytest
```

## Les règles métier

Elles font foi. Quand le code s'en écarte, c'est le code qui a tort.

**R1.** Un abonnement porte un client, une formule, un nombre de postes et une date de
début. Il peut avoir une date de fin.

**R2.** Le prix mensuel par poste dépend de la formule : `essentiel` 9 euros,
`pro` 19 euros, `entreprise` 39 euros.

**R3.** Une remise sur le volume s'applique au montant : 10 % à partir de 10 postes,
20 % à partir de 50 postes. Les paliers sont inclusifs.

**R4.** Un code promotionnel s'applique après la remise sur le volume. `BIENVENUE`
retire 5 euros, mais seulement sur la première facture. `NOEL` retire 15 %. Un code
inconnu est refusé.

**R5.** La TVA de 20 % s'applique sur le montant remisé.

**R6.** Un abonnement est actif entre sa date de début incluse et sa date de fin exclue.

**R7.** Une résiliation enregistre la date de fin demandée et la renvoie. Une date
antérieure au début est refusée.

**R8.** Une facture porte un numéro de la forme `FA-<année>-<compteur sur 4 chiffres>`,
le nom du client, la date d'émission, le montant hors taxe et le montant toutes taxes.

**R9.** La facture est envoyée au client par courriel.

## Ce qui vous attend

Le sujet est dans `tp2/README.md`.

Une chose à savoir avant d'ouvrir le code : **il fonctionne**. Personne ne vous demande
de corriger un bug. On vous demande de le rendre modifiable, parce que trois demandes
d'évolution arrivent lundi et qu'en l'état, chacune oblige à rouvrir du code qui marche.
