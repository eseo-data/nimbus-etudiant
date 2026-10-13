"""Séance 2 — Fonctions d'ordre supérieur, composition, curryfication, paresse.

Une fonction est une valeur : on peut la passer, la renvoyer, la combiner.
`map`, `filter` et `reduce` remplacent la plupart des boucles ; les générateurs
apportent l'évaluation paresseuse (on ne calcule que ce qu'on consomme).
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable, Iterator
from typing import Any

from nimbus.donnees import EN_TETE

type Fn = Callable[[Any], Any]


def compose(*fonctions: Fn) -> Fn:
    """Exercice 2.1 — composition mathématique, de droite à gauche.

    compose(f, g, h)(x) == f(g(h(x))) ; compose() est l'identité.
    """
    raise NotImplementedError("S02 — à compléter")


def pipe(valeur: Any, *fonctions: Fn) -> Any:
    """Exercice 2.2 — application de gauche à droite : pipe(x, h, g, f) == f(g(h(x)))."""
    raise NotImplementedError("S02 — à compléter")


def curry2[A, B, C](f: Callable[[A, B], C]) -> Callable[[A], Callable[[B], C]]:
    """Exercice 2.3 — curryfication : curry2(f)(a)(b) == f(a, b)."""
    raise NotImplementedError("S02 — à compléter")


def mon_map[A, B](f: Callable[[A], B], it: Iterable[A]) -> Iterator[B]:
    """Exercice 2.4 — `map` paresseux, écrit avec `yield` (sans utiliser map)."""
    raise NotImplementedError("S02 — à compléter")


def mon_filter[A](predicat: Callable[[A], bool], it: Iterable[A]) -> Iterator[A]:
    """Exercice 2.5 — `filter` paresseux, écrit avec `yield`."""
    raise NotImplementedError("S02 — à compléter")


def mon_reduce[A, B](f: Callable[[B, A], B], it: Iterable[A], initial: B) -> B:
    """Exercice 2.6 — `reduce` (fold gauche) : f(f(f(initial, x0), x1), x2)..."""
    raise NotImplementedError("S02 — à compléter")


def prendre[A](n: int, it: Iterable[A]) -> list[A]:
    """Exercice 2.7 — les n premiers éléments ; doit fonctionner sur un itérable INFINI."""
    raise NotImplementedError("S02 — à compléter")


def fenetres[A](it: Iterable[A], taille: int) -> Iterator[tuple[A, ...]]:
    """Exercice 2.8 — fenêtres glissantes paresseuses.

    fenetres([1, 2, 3, 4], 2) -> (1, 2), (2, 3), (3, 4)
    Indice : `collections.deque(maxlen=taille)`.
    """
    raise NotImplementedError("S02 — à compléter")


def moyenne_mobile(valeurs: Iterable[float], taille: int) -> Iterator[float]:
    """Exercice 2.9 — moyenne mobile = composition de `fenetres` et `mon_map`."""
    raise NotImplementedError("S02 — à compléter")


def memoiser[A, B](f: Callable[[A], B]) -> Callable[[A], B]:
    """Exercice 2.10 — fermeture (closure) qui met en cache les résultats de f.

    N'est légitime QUE parce que f est pure : pourquoi ?
    """
    raise NotImplementedError("S02 — à compléter")


# ---------------------------------------------------------------------------
# Application au fil rouge : découper le CSV brut en dictionnaires, paresseusement
# ---------------------------------------------------------------------------

COLONNES: tuple[str, ...] = tuple(EN_TETE.split(","))


def lignes_non_vides(texte: str) -> Iterator[str]:
    """Fourni."""
    return (l for l in texte.splitlines() if l.strip())


def decouper_csv(texte: str) -> Iterator[list[str]]:
    """Exercice 2.11 — ignore l'en-tête et renvoie chaque ligne découpée sur ','.

    À écrire comme un pipeline : lignes_non_vides -> sauter la 1re -> split.
    Indice : `itertools.islice`.
    """
    raise NotImplementedError("S02 — à compléter")
