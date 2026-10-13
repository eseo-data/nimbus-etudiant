"""Séance 6 Structures algébriques : semigroupes, monoïdes et leurs lois.

Un monoïde = (ensemble, élément neutre `vide`, opération `combiner` associative).
Lois :   combiner(vide, a) == a == combiner(a, vide)
         combiner(a, combiner(b, c)) == combiner(combiner(a, b), c)

Pourquoi c'est central en Data : l'ASSOCIATIVITÉ permet de découper les données
en morceaux, de les agréger en parallèle (ou sur plusieurs machines) puis de
recombiner — c'est le cœur de MapReduce, de Spark (`reduce`, `aggregate`) et
des agrégations streaming. Les lois se vérifient par tests de propriétés (Hypothesis).
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import reduce

from nimbus.s03_types_algebriques import ReleveMesure, Valide


@dataclass(frozen=True)
class Monoide[A]:
    vide: A
    combiner: Callable[[A, A], A]


# ---------------------------------------------------------------------------
# Instances simples
# ---------------------------------------------------------------------------

SOMME: Monoide[float] = Monoide(0.0, lambda a, b: a + b)
PRODUIT: Monoide[float] = Monoide(1.0, lambda a, b: a * b)

# Exercice 6.1 — complétez les deux instances ci-dessous (élément neutre !)
MAXIMUM: Monoide[float] = Monoide(0.0, lambda a, b: a)  # TODO 6.1
MINIMUM: Monoide[float] = Monoide(0.0, lambda a, b: a)  # TODO 6.1


def concat_tuples[A]() -> Monoide[tuple[A, ...]]:
    """Exercice 6.2 monoïde de la concaténation de tuples."""
    raise NotImplementedError("S06 — à compléter")


# ---------------------------------------------------------------------------
# Statistiques descriptives comme monoïde
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Stats:
    n: int
    somme: float
    somme_carres: float
    mini: float
    maxi: float

    @property
    def moyenne(self) -> float | None:
        return self.somme / self.n if self.n else None

    @property
    def variance(self) -> float | None:
        """Variance de population. (Numériquement naïve : voir l'algorithme de Welford/Chan en bonus.)"""
        if not self.n:
            return None
        m = self.somme / self.n
        return max(0.0, self.somme_carres / self.n - m * m)


def stats_de(x: float) -> Stats:
    """Exercice 6.3 les statistiques d'un seul point."""
    raise NotImplementedError("S06 — à compléter")


# Exercice 6.4 — le monoïde STATS (neutre + combinaison)
STATS: Monoide[Stats] = Monoide(Stats(0, 0.0, 0.0, 0.0, 0.0), lambda a, b: a)  # TODO 6.4


def fold_map[A, B](xs: Iterable[A], f: Callable[[A], B], m: Monoide[B]) -> B:
    """Exercice 6.5 transforme chaque élément puis réduit avec le monoïde."""
    raise NotImplementedError("S06 — à compléter")


def morceaux[A](xs: Sequence[A], n: int) -> list[Sequence[A]]:
    """Fourni : découpe xs en n morceaux contigus (certains peuvent être vides)."""
    taille = math.ceil(len(xs) / n) if xs else 0
    return [xs[i * taille:(i + 1) * taille] for i in range(n)] if taille else [xs]


def fold_map_parallele[A, B](xs: Sequence[A], f: Callable[[A], B], m: Monoide[B], n: int = 4) -> B:
    """Exercice 6.6 même résultat que fold_map, calculé par morceaux en parallèle.

    1. découper avec `morceaux`  2. fold_map de chaque morceau dans un ThreadPoolExecutor
    3. recombiner les résultats partiels avec le monoïde.
    Question : quelle loi garantit que le résultat ne dépend pas de n ?
    """
    raise NotImplementedError("S06 — à compléter")


def monoide_dict[K, V](m: Monoide[V]) -> Monoide[Mapping[K, V]]:
    """Exercice 6.7 combine deux dictionnaires clé par clé avec le monoïde des valeurs.

    {"a": 1} ⊕ {"a": 2, "b": 3} == {"a": 3, "b": 3}   (avec SOMME)
    """
    raise NotImplementedError("S06 — à compléter")


def stats_temperature_par_station(releves: Sequence[ReleveMesure]) -> Mapping[str, Stats]:
    """Exercice 6.8 fil rouge : statistiques de température (mesures valides uniquement)
    par station, en UNE passe `fold_map_parallele` avec `monoide_dict(STATS)`."""
    raise NotImplementedError("S06 — à compléter")
