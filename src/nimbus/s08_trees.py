"""Séance 8 — Un arbre de décision est un type algébrique récursif.

    Tree = Leaf(proba, n) | Node(variable, threshold, left, right)

Tout ce qu'on fait sur un arbre (prédire, compter, afficher, élaguer) est soit un
parcours récursif guidé par `match`, soit un `fold_tree` (catamorphisme) : on
remplace chaque constructeur par une fonction. C'est la généralisation du
fold_right de la séance 4 à n'importe quel type récursif.

Contrairement à scikit-learn, notre modèle est une VALEUR immuable et
inspectable : on peut l'afficher, le comparer avec ==, le sérialiser, le
transformer par une fonction pure.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import assert_never

VARIABLE_NAMES = ("temperature_c", "humidity_pct", "pressure_hpa", "wind_kmh", "rain_mm")


@dataclass(frozen=True)
class Leaf:
    rain_probability: float
    n: int


@dataclass(frozen=True)
class Node:
    variable: int
    threshold: float
    left: Tree   # x[variable] <= seuil
    right: Tree   # x[variable] >  seuil


type Tree = Leaf | Node


def predict(tree: Tree, x: Sequence[float]) -> float:
    """Exercice 8.1 — descend dans l'arbre jusqu'à une feuille ; renvoie sa proba."""
    raise NotImplementedError("S08 — à compléter")


def fold_tree[R](
    tree: Tree,
    f_leaf: Callable[[float, int], R],
    f_node: Callable[[int, float, R, R], R],
) -> R:
    """Exercice 8.2 — catamorphisme : remplace Leaf par f_leaf et Node par f_node."""
    raise NotImplementedError("S08 — à compléter")


def depth(tree: Tree) -> int:
    """Exercice 8.3 — via fold_tree (une feuille seule a une profondeur 0)."""
    raise NotImplementedError("S08 — à compléter")


def n_leaves(tree: Tree) -> int:
    """Exercice 8.4 — via fold_tree."""
    raise NotImplementedError("S08 — à compléter")


def display(tree: Tree) -> str:
    """Fourni (récursion explicite, pour comparer avec fold_tree)."""

    def aux(a: Tree, indent: str) -> list[str]:
        match a:
            case Leaf(p, n):
                return [f"{indent}→ P(pluie)={p:.2f}  (n={n})"]
            case Node(var, threshold, g, d):
                name = VARIABLE_NAMES[var] if var < len(VARIABLE_NAMES) else f"x{var}"
                return (
                    [f"{indent}si {name} <= {threshold:.1f} :"] + aux(g, indent + "  ")
                    + [f"{indent}sinon :"] + aux(d, indent + "  ")
                )
            case _:
                assert_never(a)

    return "\n".join(aux(tree, ""))


# ---------------------------------------------------------------------------
# Apprentissage (algorithme glouton CART simplifié, 100 % pur)
# ---------------------------------------------------------------------------


def gini(ys: Sequence[float]) -> float:
    """Exercice 8.5 — impureté de Gini d'un ensemble d'étiquettes 0/1 : 2·p·(1-p). Empty -> 0."""
    raise NotImplementedError("S08 — à compléter")


def candidate_thresholds(vals: Sequence[float], n: int = 12) -> list[float]:
    """Fourni : quelques quantiles distincts (rapide sur laptop, pas besoin de tous les seuils)."""
    vs = sorted(set(vals))
    if len(vs) <= 1:
        return []
    stride = max(1, len(vs) // (n + 1))
    return sorted(set(vs[i] for i in range(stride, len(vs) - 1, stride)))


def best_split(X: Sequence[Sequence[float]], y: Sequence[float]) -> tuple[int, float, float] | None:
    """Exercice 8.6 — (variable, threshold, weighted_gini) minimisant l'impureté pondérée des deux côtés.

    gini_pondéré = (|G|·gini(G) + |D|·gini(D)) / |total|. Ignorer les coupes laissant un côté vide.
    None si aucune coupe possible.
    """
    raise NotImplementedError("S08 — à compléter")


def build(
    X: Sequence[Sequence[float]], y: Sequence[float], max_depth: int = 3, min_samples: int = 20
) -> Tree:
    """Exercice 8.7 — construction récursive.

    Leaf(moyenne de y, len(y)) si : max_depth == 0, ou len(y) < min_samples,
    ou y pur (gini == 0), ou pas de coupe, ou la coupe n'améliore pas gini(y).
    Sinon Node(var, threshold, build(left, ...), build(right, ...)).
    """
    raise NotImplementedError("S08 — à compléter")


def prune(tree: Tree) -> Tree:
    """Exercice 8.8 — fusionne tout Node dont les deux enfants sont des feuilles
    prédisant la MÊME classe (proba > 0.5 des deux côtés, ou <= 0.5 des deux côtés).
    La feuille fusionnée a pour proba la moyenne pondérée par n. Via fold_tree."""
    raise NotImplementedError("S08 — à compléter")
