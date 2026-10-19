"""Séance 4 — Récursion, folds et structures de données persistantes.

- Une liste chaînée immuable (« Cons list ») : ajouter en tête PARTAGE la queue
  au lieu de la copier (partage structurel) -> immutabilité bon marché.
- `fold_left` / `fold_right` : les deux schémas de récursion fondamentaux sur les listes.
- Python n'optimise pas la récursion terminale (pas de TCO) : on contourne avec un
  trampoline — ce que font aussi les bibliothèques d'effets (cf. séance 9).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import assert_never

from nimbus.s03_algebraic_types import Outlier, Missing, Measurement, Valid

# ---------------------------------------------------------------------------
# LinkedList persistante (fournie)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Empty:
    pass


@dataclass(frozen=True)
class Cons[A]:
    head: A
    queue: LinkedList[A]


type LinkedList[A] = Empty | Cons[A]

EMPTY = Empty()


def from_iterable[A](it: Iterable[A]) -> LinkedList[A]:
    """Fourni : construit une LinkedList à partir d'un itérable (en conservant l'ordre)."""
    result: LinkedList[A] = EMPTY
    for x in reversed(list(it)):
        result = Cons(x, result)
    return result


def to_python_list[A](l: LinkedList[A]) -> list[A]:
    """Fourni : conversion inverse (itérative)."""
    out: list[A] = []
    while isinstance(l, Cons):
        out.append(l.head)
        l = l.queue
    return out


# ---------------------------------------------------------------------------
# Exercices
# ---------------------------------------------------------------------------


def length[A](l: LinkedList[A]) -> int:
    """Exercice 4.1 — longueur, en RÉCURSIF avec `match` (pas de boucle)."""
    raise NotImplementedError("S04 — à compléter")


def fold_left[A, B](l: LinkedList[A], initial: B, f: Callable[[B, A], B]) -> B:
    """Exercice 4.2 — fold gauche : f(f(f(initial, a0), a1), a2).

    Sa forme récursive est TERMINALE, donc on a le droit de l'écrire avec une
    boucle `while` : c'est exactement ce qu'un compilateur avec TCO produirait.
    """
    raise NotImplementedError("S04 — à compléter")


def fold_right[A, B](l: LinkedList[A], initial: B, f: Callable[[A, B], B]) -> B:
    """Exercice 4.3 — fold droit : f(a0, f(a1, f(a2, initial))). En récursif."""
    raise NotImplementedError("S04 — à compléter")


def reverse[A](l: LinkedList[A]) -> LinkedList[A]:
    """Exercice 4.4 — inverser une liste avec fold_left (une ligne)."""
    raise NotImplementedError("S04 — à compléter")


def map_list[A, B](l: LinkedList[A], f: Callable[[A], B]) -> LinkedList[B]:
    """Exercice 4.5 — map avec fold_right (une ligne)."""
    raise NotImplementedError("S04 — à compléter")


def scan_left[A, B](xs: Iterable[A], initial: B, f: Callable[[B, A], B]) -> list[B]:
    """Exercice 4.6 — comme fold_left mais renvoie TOUS les accumulateurs intermédiaires.

    scan_left([1, 2, 3], 0, add) == [0, 1, 3, 6]
    """
    raise NotImplementedError("S04 — à compléter")


def fill_gaps(ms: Iterable[Measurement]) -> list[float | None]:
    """Exercice 4.7 — imputation « dernière valeur connue » (forward fill) via scan_left.

    [Valid(1), Missing(), Outlier(..), Valid(4)] -> [1.0, 1.0, 1.0, 4.0]
    Avant la première valeur valide : None.
    """
    raise NotImplementedError("S04 — à compléter")


# ---------------------------------------------------------------------------
# Trampoline : récursion sans exploser la pile
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Done[A]:
    value: A


@dataclass(frozen=True)
class Bounce[A]:
    then: Callable[[], Trampoline[A]]


type Trampoline[A] = Done[A] | Bounce[A]


def run_trampoline[A](t: Trampoline[A]) -> A:
    """Exercice 4.8 — déroule les rebonds dans une boucle jusqu'à obtenir Done."""
    raise NotImplementedError("S04 — à compléter")


def sum_trampoline(l: LinkedList[float]) -> float:
    """Exercice 4.9 — somme « récursive » qui ne dépasse pas la pile sur 100 000 éléments.

    Écrire une fonction auxiliaire récursive qui renvoie Bounce(lambda: aux(queue, acc + tete))
    au lieu de s'appeler directement.
    """
    raise NotImplementedError("S04 — à compléter")
