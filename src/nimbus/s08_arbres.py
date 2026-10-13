"""Séance 8 — Un arbre de décision est un type algébrique récursif.

    Arbre = Feuille(proba, n) | Noeud(variable, seuil, gauche, droite)

Tout ce qu'on fait sur un arbre (prédire, compter, afficher, élaguer) est soit un
parcours récursif guidé par `match`, soit un `fold_arbre` (catamorphisme) : on
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

NOMS_VARIABLES = ("temperature_c", "humidite_pct", "pression_hpa", "vent_kmh", "pluie_mm")


@dataclass(frozen=True)
class Feuille:
    proba_pluie: float
    n: int


@dataclass(frozen=True)
class Noeud:
    variable: int
    seuil: float
    gauche: Arbre   # x[variable] <= seuil
    droite: Arbre   # x[variable] >  seuil


type Arbre = Feuille | Noeud


def predire(arbre: Arbre, x: Sequence[float]) -> float:
    """Exercice 8.1 — descend dans l'arbre jusqu'à une feuille ; renvoie sa proba."""
    raise NotImplementedError("S08 — à compléter")


def fold_arbre[R](
    arbre: Arbre,
    f_feuille: Callable[[float, int], R],
    f_noeud: Callable[[int, float, R, R], R],
) -> R:
    """Exercice 8.2 — catamorphisme : remplace Feuille par f_feuille et Noeud par f_noeud."""
    raise NotImplementedError("S08 — à compléter")


def profondeur(arbre: Arbre) -> int:
    """Exercice 8.3 — via fold_arbre (une feuille seule a une profondeur 0)."""
    raise NotImplementedError("S08 — à compléter")


def nb_feuilles(arbre: Arbre) -> int:
    """Exercice 8.4 — via fold_arbre."""
    raise NotImplementedError("S08 — à compléter")


def afficher(arbre: Arbre) -> str:
    """Fourni (récursion explicite, pour comparer avec fold_arbre)."""

    def aux(a: Arbre, indent: str) -> list[str]:
        match a:
            case Feuille(p, n):
                return [f"{indent}→ P(pluie)={p:.2f}  (n={n})"]
            case Noeud(var, seuil, g, d):
                nom = NOMS_VARIABLES[var] if var < len(NOMS_VARIABLES) else f"x{var}"
                return (
                    [f"{indent}si {nom} <= {seuil:.1f} :"] + aux(g, indent + "  ")
                    + [f"{indent}sinon :"] + aux(d, indent + "  ")
                )
            case _:
                assert_never(a)

    return "\n".join(aux(arbre, ""))


# ---------------------------------------------------------------------------
# Apprentissage (algorithme glouton CART simplifié, 100 % pur)
# ---------------------------------------------------------------------------


def gini(ys: Sequence[float]) -> float:
    """Exercice 8.5 — impureté de Gini d'un ensemble d'étiquettes 0/1 : 2·p·(1-p). Vide -> 0."""
    raise NotImplementedError("S08 — à compléter")


def seuils_candidats(valeurs: Sequence[float], n: int = 12) -> list[float]:
    """Fourni : quelques quantiles distincts (rapide sur laptop, pas besoin de tous les seuils)."""
    vs = sorted(set(valeurs))
    if len(vs) <= 1:
        return []
    pas = max(1, len(vs) // (n + 1))
    return sorted(set(vs[i] for i in range(pas, len(vs) - 1, pas)))


def meilleure_coupe(X: Sequence[Sequence[float]], y: Sequence[float]) -> tuple[int, float, float] | None:
    """Exercice 8.6 — (variable, seuil, gini_pondéré) minimisant l'impureté pondérée des deux côtés.

    gini_pondéré = (|G|·gini(G) + |D|·gini(D)) / |total|. Ignorer les coupes laissant un côté vide.
    None si aucune coupe possible.
    """
    raise NotImplementedError("S08 — à compléter")


def construire(
    X: Sequence[Sequence[float]], y: Sequence[float], profondeur_max: int = 3, min_echantillons: int = 20
) -> Arbre:
    """Exercice 8.7 — construction récursive.

    Feuille(moyenne de y, len(y)) si : profondeur_max == 0, ou len(y) < min_echantillons,
    ou y pur (gini == 0), ou pas de coupe, ou la coupe n'améliore pas gini(y).
    Sinon Noeud(var, seuil, construire(gauche, ...), construire(droite, ...)).
    """
    raise NotImplementedError("S08 — à compléter")


def elaguer(arbre: Arbre) -> Arbre:
    """Exercice 8.8 — fusionne tout Noeud dont les deux enfants sont des feuilles
    prédisant la MÊME classe (proba > 0.5 des deux côtés, ou <= 0.5 des deux côtés).
    La feuille fusionnée a pour proba la moyenne pondérée par n. Via fold_arbre."""
    raise NotImplementedError("S08 — à compléter")
