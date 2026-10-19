"""Séance 1 — Pureté, transparence référentielle, immutabilité.

Idée clé : une fonction pure ne dépend que de ses arguments et ne fait rien
d'autre que renvoyer un résultat. On peut donc remplacer tout appel par sa
valeur (transparence référentielle) : c'est ce qui rend le code testable,
parallélisable et différentiable (cf. JAX en séance 7).

Les blocs entre « >>> SOLUTION » et « <<< SOLUTION » sont retirés dans la
version étudiante.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace

# ---------------------------------------------------------------------------
# Contre-exemple (fourni) : le style impératif que l'on va remplacer.
# Repérez les trois effets de bord de cette fonction.
# ---------------------------------------------------------------------------

_LOG: list[str] = []


def clean_imperative(temperatures: list[float]) -> float:
    """NE PAS IMITER. Modifie son argument, écrit dans un état global, imprime."""
    i = 0
    while i < len(temperatures):
        if temperatures[i] > 60:
            del temperatures[i]          # 1. mutation de l'argument
        else:
            i += 1
    _LOG.append("nettoyage")         # 2. écriture dans un état global
    print("moyenne calculée")            # 3. entrée/sortie
    return sum(temperatures) / len(temperatures)


# ---------------------------------------------------------------------------
# Exercices
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Reading:
    """Un relevé immuable. `frozen=True` interdit toute affectation après création."""

    date: str
    station: str
    temperature_c: float
    humidity_pct: float


def celsius_to_fahrenheit(c: float) -> float:
    """Exercice 1.1 — échauffement : F = C × 9/5 + 32."""
    raise NotImplementedError("S01 — à compléter")


def filter_plausible(temperatures: Sequence[float], threshold: float = 60.0) -> tuple[float, ...]:
    """Exercice 1.2 — version pure de la boucle de `clean_imperative`.

    Ne modifie pas l'entrée ; renvoie un tuple (immuable) des valeurs <= seuil.
    """
    raise NotImplementedError("S01 — à compléter")


def average(vals: Sequence[float]) -> float | None:
    """Exercice 1.3 — moyenne, ou None si la séquence est vide (pas d'exception !)."""
    raise NotImplementedError("S01 — à compléter")


def normalize(vals: Sequence[float]) -> tuple[float, ...]:
    """Exercice 1.4 — normalisation min-max dans [0, 1].

    Si toutes les valeurs sont égales, renvoyer des 0.0. Séquence vide -> tuple vide.
    """
    raise NotImplementedError("S01 — à compléter")


def correct_temperature(r: Reading, delta: float) -> Reading:
    """Exercice 1.5 — renvoie un NOUVEAU relevé dont la température est décalée de delta.

    Indice : `dataclasses.replace`.
    """
    raise NotImplementedError("S01 — à compléter")


def append(history: tuple[Reading, ...], r: Reading) -> tuple[Reading, ...]:
    """Exercice 1.6 — ajoute un relevé à un historique sans le modifier."""
    raise NotImplementedError("S01 — à compléter")


def clean_pure(temperatures: Sequence[float]) -> tuple[float | None, tuple[str, ...]]:
    """Exercice 1.7 — réécriture pure de `clean_imperative`.

    Au lieu d'écrire dans un journal global, on RENVOIE les messages de journal
    avec le résultat : (moyenne des plausibles, ("nettoyage",)).
    C'est le germe de la monade Writer — et de l'idée « l'effet devient une valeur ».
    """
    raise NotImplementedError("S01 — à compléter")


# ===========================================================================
# PARTIE B — Refactoring d'un script hérité (≈ 30 min)
# ===========================================================================
# Lisez `nimbus/s01_legacy.py`. Il produit un rapport par station en s'appuyant
# sur trois variables globales, des mutations et des `print`. Réécrivez-le en
# fonctions pures. Contrainte : `report(text)` doit renvoyer EXACTEMENT le
# texte que le script hérité affiche (un `\n` à la fin de chaque ligne).

TEMPERATURE_BOUNDS = (-40.0, 50.0)


def parse_temperatures(text: str) -> tuple[tuple[tuple[str, float], ...], int]:
    """Exercice 1.8 — ((station, température), ...) des lignes valides + nombre de rejets.

    Mêmes règles que le script hérité : 7 colonnes, température convertible en float,
    comprise dans TEMPERATURE_BOUNDS (bornes incluses). L'en-tête est ignoré.
    """
    raise NotImplementedError("S01 — à compléter")


def group_by_station(pairs: Sequence[tuple[str, float]]) -> Mapping[str, tuple[float, ...]]:
    """Exercice 1.9 — températures TRIÉES par station : {"BREST": (2.5, 3.1, ...), ...}."""
    raise NotImplementedError("S01 — à compléter")


def station_line(station: str, temperatures: Sequence[float]) -> str:
    """Exercice 1.10 — une ligne du rapport, au format exact du script hérité.

    `temperatures` est supposée triée et non vide. Médiane = élément d'indice len // 2.
    """
    raise NotImplementedError("S01 — à compléter")


def report(text: str) -> str:
    """Exercice 1.11 — le rapport complet, par composition des trois fonctions précédentes."""
    raise NotImplementedError("S01 — à compléter")


# ===========================================================================
# PARTIE C — Le hasard, purement (≈ 25 min)
# ===========================================================================
# `random.random()` est impur : deux appels identiques donnent deux résultats.
# Solution fonctionnelle : l'état du générateur devient une VALEUR qu'on passe
# en argument et qu'on renvoie mise à jour. C'est exactement le modèle de JAX :
#     key, sous_cle = jax.random.split(key); x = jax.random.normal(sous_cle)

_A = 6364136223846793005
_C = 1442695040888963407
_MASK = (1 << 64) - 1


def advance(state: int) -> int:
    """Fourni : un pas de générateur congruentiel linéaire 64 bits."""
    return (_A * state + _C) & _MASK


def rand(state: int) -> tuple[float, int]:
    """Exercice 1.12 — (flottant uniforme dans [0, 1), nouvel état).

    Calculer e2 = advance(state) puis renvoyer ((e2 >> 11) / 2**53, e2).
    """
    raise NotImplementedError("S01 — à compléter")


def rand_n(state: int, n: int) -> tuple[tuple[float, ...], int]:
    """Exercice 1.13 — n tirages successifs : on « fait passer » l'état de tirage en tirage."""
    raise NotImplementedError("S01 — à compléter")


def shuffle[T](xs: Sequence[T], state: int) -> tuple[tuple[T, ...], int]:
    """Exercice 1.14 — permutation aléatoire (Fisher-Yates) SANS modifier xs.

    Pour i de len-1 à 1 : tirer u = rand(state), j = int(u * (i + 1)), échanger i et j
    dans une COPIE locale. Renvoyer (tuple mélangé, état final).
    """
    raise NotImplementedError("S01 — à compléter")


def split_state(state: int) -> tuple[int, int]:
    """Exercice 1.15 — deux états indépendants à partir d'un seul (comme jax.random.split).

    Proposition : e1 = advance(state) ; e2 = advance(e1) XOR 0x9E3779B97F4A7C15.
    Pourquoi ne faut-il JAMAIS réutiliser `state` après l'avoir séparé ?
    """
    raise NotImplementedError("S01 — à compléter")


def train_test_split[T](xs: Sequence[T], part_test: float, state: int) -> tuple[tuple[T, ...], tuple[T, ...], int]:
    """Exercice 1.16 — découpage train/test reproductible : (apprentissage, test, nouvel état).

    Mélanger, puis les round(len * part_test) premiers éléments forment le test.
    Même graine => même découpage, sur toutes les machines : c'est ça, la reproductibilité.
    """
    raise NotImplementedError("S01 — à compléter")
