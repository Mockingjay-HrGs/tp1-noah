#!/usr/bin/env bash
# Verifie qu'un depot du TP2 a bien ete etendu sans etre modifie.
#
# Usage : ./verifier-ocp.sh [chemin_du_depot]
#
# Le script s'appuie sur deux etiquettes git que le sujet demande de poser :
#   depart-tp2          le code tel qu'il etait au debut de la journee
#   ouverture-terminee  apres la preparation des points de variation,
#                       avant l'implementation des trois nouvelles regles
#
# Ce qu'il controle entre ouverture-terminee et HEAD :
#   1. aucune ligne supprimee dans un fichier metier existant
#   2. aucun fichier de test existant modifie
#   3. les ajouts dans un fichier existant se limitent a des imports
#   4. des fichiers neufs et des tests neufs existent bien
#   5. la suite de tests est verte
#
# Le meme script est utilise pour la correction. Lance-le avant de rendre.

set -uo pipefail

DEPOT="${1:-.}"
TAG_DEPART="depart-tp2"
TAG_OUVERTURE="ouverture-terminee"

if ! git -C "$DEPOT" rev-parse --git-dir >/dev/null 2>&1; then
  echo "ERREUR : $DEPOT n'est pas un depot git."
  exit 2
fi
DEPOT="$(cd "$DEPOT" && pwd)"

ROUGE=$'\033[31m'; VERT=$'\033[32m'; JAUNE=$'\033[33m'; GRAS=$'\033[1m'; FIN=$'\033[0m'
ok()   { echo "${VERT}  ok${FIN}    $1"; }
ko()   { echo "${ROUGE}  ko${FIN}    $1"; }
warn() { echo "${JAUNE}  note${FIN}  $1"; }
titre(){ echo ""; echo "${GRAS}$1${FIN}"; }

PROBLEMES=0
incr() { PROBLEMES=$((PROBLEMES + 1)); }

g() { git -C "$DEPOT" "$@"; }

# ---------------------------------------------------------------------------
titre "1. Les etiquettes"

for tag in "$TAG_DEPART" "$TAG_OUVERTURE"; do
  if g rev-parse -q --verify "refs/tags/$tag" >/dev/null; then
    ok "$tag posee sur $(g rev-parse --short "$tag")"
  else
    ko "$tag manquante, le sujet demande de la poser"
    incr
  fi
done
if [ "$PROBLEMES" -gt 0 ]; then
  echo ""
  echo "${ROUGE}  Sans les deux etiquettes, la mission 3 ne peut pas etre evaluee.${FIN}"
  exit 1
fi

if g merge-base --is-ancestor "$TAG_DEPART" "$TAG_OUVERTURE" 2>/dev/null; then
  ok "depart-tp2 precede bien ouverture-terminee"
else
  ko "depart-tp2 ne precede pas ouverture-terminee"
  incr
fi
if g merge-base --is-ancestor "$TAG_OUVERTURE" HEAD 2>/dev/null; then
  ok "ouverture-terminee precede bien le dernier commit"
else
  ko "ouverture-terminee ne precede pas HEAD"
  incr
fi

NB_OUV=$(g rev-list --count "$TAG_DEPART..$TAG_OUVERTURE")
NB_EXT=$(g rev-list --count "$TAG_OUVERTURE..HEAD")
echo "  $NB_OUV commits pour ouvrir, $NB_EXT commits pour etendre"
[ "$NB_EXT" -eq 0 ] && { ko "aucun commit apres l'ouverture, rien n'a ete ajoute"; incr; }

# ---------------------------------------------------------------------------
titre "2. Ce qui a change depuis l'ouverture"

existait_avant() { g cat-file -e "$TAG_OUVERTURE:$1" 2>/dev/null; }

est_fichier_d_assemblage() {
  case "$(basename "$1")" in
    __init__.py|conftest.py) return 0 ;;
  esac
  case "$1" in
    *registre*|*regles/__init__*|*assemblage*) return 0 ;;
  esac
  return 1
}

est_un_test() {
  case "$(basename "$1")" in
    test_*.py|conftest.py) return 0 ;;
  esac
  case "$1" in
    */tests/*|tests/*) return 0 ;;
  esac
  return 1
}

NEUFS=0
SUPPRESSIONS=0
TESTS_TOUCHES=0
AJOUTS_NON_IMPORT=0

while IFS=$'\t' read -r ajoutees supprimees chemin; do
  [ -z "${chemin:-}" ] && continue
  case "$chemin" in *.py) ;; *) continue ;; esac

  if ! existait_avant "$chemin"; then
    NEUFS=$((NEUFS + 1))
    continue
  fi

  if [ "$supprimees" != "0" ] && [ "$supprimees" != "-" ]; then
    ko "$chemin : $supprimees ligne(s) supprimee(s) dans un fichier existant"
    SUPPRESSIONS=$((SUPPRESSIONS + supprimees))
    continue
  fi

  if est_un_test "$chemin"; then
    ko "$chemin : un fichier de test existant a ete modifie"
    TESTS_TOUCHES=$((TESTS_TOUCHES + 1))
    continue
  fi

  if [ "$ajoutees" != "0" ] && [ "$ajoutees" != "-" ]; then
    NON_IMPORT=$(g diff --no-renames "$TAG_OUVERTURE..HEAD" -- "$chemin" \
      | grep '^+' | grep -v '^+++' | sed 's/^+//' \
      | grep -vE '^[[:space:]]*(from |import |#|$)' | wc -l)
    if [ "$NON_IMPORT" -eq 0 ] && est_fichier_d_assemblage "$chemin"; then
      warn "$chemin : $ajoutees ligne(s) d'import ajoutee(s), tolere"
    elif [ "$NON_IMPORT" -eq 0 ]; then
      warn "$chemin : $ajoutees ligne(s) d'import ajoutee(s) hors fichier d'assemblage"
    else
      ko "$chemin : $NON_IMPORT ligne(s) de code ajoutee(s) dans un fichier existant"
      AJOUTS_NON_IMPORT=$((AJOUTS_NON_IMPORT + NON_IMPORT))
    fi
  fi
done < <(g diff --numstat --no-renames "$TAG_OUVERTURE..HEAD")

[ "$SUPPRESSIONS" -eq 0 ] && ok "aucune ligne supprimee dans un fichier existant" || incr
[ "$TESTS_TOUCHES" -eq 0 ] && ok "aucun fichier de test existant modifie" || incr
[ "$AJOUTS_NON_IMPORT" -eq 0 ] && ok "aucun ajout de code dans un fichier existant" || incr

if [ "$NEUFS" -gt 0 ]; then
  ok "$NEUFS fichier(s) Python neuf(s) depuis l'ouverture"
  g diff --name-only --diff-filter=A --no-renames "$TAG_OUVERTURE..HEAD" -- '*.py' | sed 's/^/        /'
else
  ko "aucun fichier neuf, les regles n'ont pas ete ajoutees en extension"
  incr
fi

# ---------------------------------------------------------------------------
titre "3. Les tests neufs"

NEUFS_TESTS=$(g diff --name-only --diff-filter=A --no-renames "$TAG_OUVERTURE..HEAD" -- '*.py' \
  | while read -r f; do est_un_test "$f" && echo "$f"; done | wc -l)
NB_NOUVEAUX_CAS=$(g diff "$TAG_OUVERTURE..HEAD" -- '*.py' \
  | grep -cE '^\+[[:space:]]*def test_' || true)

echo "  $NEUFS_TESTS fichier(s) de test neuf(s), $NB_NOUVEAUX_CAS cas de test ajoute(s)"
if [ "$NB_NOUVEAUX_CAS" -ge 3 ]; then
  ok "les nouvelles regles sont couvertes par des tests neufs"
else
  ko "seulement $NB_NOUVEAUX_CAS test(s) ajoute(s) pour trois regles"
  incr
fi

# ---------------------------------------------------------------------------
titre "4. Evolution de la suite de tests"

compter_tests() {
  local ref="$1" cible tmp sortie
  tmp="$(mktemp -d)"
  cible="$tmp/arbre"
  if ! g worktree add --detach -q "$cible" "$ref" 2>/dev/null; then
    echo "?"; rm -rf "$tmp"; return
  fi
  local brut
  brut="$(cd "$cible" && python3 -m pytest --collect-only -q 2>/dev/null)"
  sortie="$(echo "$brut" | grep -oE '[0-9]+ (test|tests) collected' | grep -oE '^[0-9]+')"
  if [ -z "$sortie" ]; then
    sortie="$(echo "$brut" | grep -cE '::')"
    [ "$sortie" = "0" ] && sortie=""
  fi
  echo "${sortie:-?}"
  g worktree remove --force "$cible" >/dev/null 2>&1
  rm -rf "$tmp"
}

if command -v python3 >/dev/null 2>&1; then
  T_DEPART="$(compter_tests "$TAG_DEPART")"
  T_OUV="$(compter_tests "$TAG_OUVERTURE")"
  T_HEAD="$(compter_tests HEAD)"
  echo "  depart-tp2 : ${T_DEPART:-?} tests"
  echo "  ouverture  : ${T_OUV:-?} tests"
  echo "  HEAD       : ${T_HEAD:-?} tests"
  if [[ "${T_OUV:-}" =~ ^[0-9]+$ && "${T_HEAD:-}" =~ ^[0-9]+$ ]]; then
    if [ "$T_HEAD" -gt "$T_OUV" ]; then
      ok "la suite a grossi de $((T_HEAD - T_OUV)) tests pendant l'extension"
    else
      ko "la suite n'a pas grossi pendant l'extension"
      incr
    fi
  fi
else
  warn "python3 introuvable, comptage ignore"
fi

# ---------------------------------------------------------------------------
titre "5. La suite est-elle verte"

SORTIE="$(cd "$DEPOT" && python3 -m pytest -q 2>&1)"; CODE=$?
RESUME="$(echo "$SORTIE" | grep -iE "passed|failed|error|interrupted" | tail -1)"
if [ "$CODE" -ne 0 ]; then
  ko "la suite n'est pas verte : $RESUME"
  incr
else
  ok "suite verte : $RESUME"
fi

# ---------------------------------------------------------------------------
titre "6. Livrables"

for f in RAPPORT-CONCEPTION.md; do
  if g ls-files --error-unmatch "$f" >/dev/null 2>&1; then
    ok "$f present"
  else
    ko "$f manquant"
    incr
  fi
done

g worktree prune >/dev/null 2>&1

titre "Bilan"
if [ "$PROBLEMES" -eq 0 ]; then
  echo "${VERT}  Extension conforme. Rien n'a ete modifie, tout a ete ajoute.${FIN}"
  exit 0
fi
echo "${ROUGE}  $PROBLEMES point(s) a corriger avant de rendre.${FIN}"
exit 1
