"""Séance 9 — Effets fonctionnels : « un programme est une valeur » (à la ZIO).

Idée popularisée par John A. De Goes (ZIO, Scala) : au lieu d'EXÉCUTER des effets
de bord, on construit une DESCRIPTION du programme (une structure de données
immuable), puis un INTERPRÉTEUR l'exécute « au bout du monde » (dans `main`).

Conséquences :
- `retry`, `or_else`, `timeout`... deviennent de simples fonctions sur des valeurs ;
- le cœur métier reste pur, testable sans fichier ni réseau (on injecte de faux services) ;
- l'interpréteur peut être sûr vis-à-vis de la pile (pas de récursion Python).

Notre `Effect[A]` est une version minuscule de `ZIO[R, E, A]` : l'erreur est une
`Exception` et l'environnement R est passé explicitement (`Services`).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from nimbus.s05_errors import Err, Ok, Result

# ---------------------------------------------------------------------------
# Les primitives (fournies) : un petit langage dont les programmes sont des valeurs
# ---------------------------------------------------------------------------


class Effect[A]:
    """Classe de base. Les combinateurs ci-dessous sont à compléter."""

    def flat_map[B](self, f: Callable[[A], Effect[B]]) -> Effect[B]:
        return FlatMap(self, f)

    def fold[B](self, on_failure: Callable[[Exception], Effect[B]], on_success: Callable[[A], Effect[B]]) -> Effect[B]:
        return Fold(self, on_failure, on_success)

    # -- Exercices 9.1 à 9.6 : n'utiliser QUE flat_map, fold, success, failure -----

    def map[B](self, f: Callable[[A], B]) -> Effect[B]:
        """Exercice 9.1"""
        raise NotImplementedError("S09 — à compléter")

    def zip[B](self, other: Effect[B]) -> Effect[tuple[A, B]]:
        """Exercice 9.2 — exécute self puis autre, renvoie le couple des résultats."""
        raise NotImplementedError("S09 — à compléter")

    def tap(self, f: Callable[[A], Effect[Any]]) -> Effect[A]:
        """Exercice 9.3 — exécute l'effet f(a) pour son effet de bord, mais renvoie a."""
        raise NotImplementedError("S09 — à compléter")

    def catch_all(self, handler: Callable[[Exception], Effect[A]]) -> Effect[A]:
        """Exercice 9.4 — en cas d'échec, continue avec handler(error)."""
        raise NotImplementedError("S09 — à compléter")

    def or_else(self, alternative: Effect[A]) -> Effect[A]:
        """Exercice 9.5"""
        raise NotImplementedError("S09 — à compléter")

    def retry(self, n: int) -> Effect[A]:
        """Exercice 9.6 — réessaie jusqu'à n fois supplémentaires.

        Question clé : pourquoi ceci est-il IMPOSSIBLE avec une fonction Python
        ordinaire qui a déjà été appelée, mais trivial avec une description d'effet ?
        """
        raise NotImplementedError("S09 — à compléter")


@dataclass(frozen=True)
class Succeed[A](Effect[A]):
    value: A


@dataclass(frozen=True)
class Fail(Effect[Any]):
    error: Exception


@dataclass(frozen=True)
class Suspend[A](Effect[A]):
    """Encapsule un effet de bord SANS l'exécuter. Une exception levée devient un Fail (échec)."""

    thunk: Callable[[], A]


@dataclass(frozen=True)
class FlatMap[A, B](Effect[B]):
    effect: Effect[A]
    then: Callable[[A], Effect[B]]


@dataclass(frozen=True)
class Fold[A, B](Effect[B]):
    effect: Effect[A]
    on_failure: Callable[[Exception], Effect[B]]
    on_success: Callable[[A], Effect[B]]


def success[A](a: A) -> Effect[A]:
    return Succeed(a)


def failure(e: Exception) -> Effect[Any]:
    return Fail(e)


def suspend[A](thunk: Callable[[], A]) -> Effect[A]:
    return Suspend(thunk)


def for_each[A, B](xs: Iterable[A], f: Callable[[A], Effect[B]]) -> Effect[list[B]]:
    """Exercice 9.7 — `traverse` pour les effets : exécute f sur chaque élément, en séquence,
    et rassemble les résultats. Indice : partir de success([]) et enchaîner des flat_map."""
    raise NotImplementedError("S09 — à compléter")


# ---------------------------------------------------------------------------
# L'interpréteur : le SEUL endroit où les effets se produisent réellement
# ---------------------------------------------------------------------------


def execute[A](program: Effect[A]) -> Result[A, Exception]:
    """Exercice 9.8 — interpréteur itératif, sûr pour la pile.

    On maintient `current` (l'effet à évaluer) et une pile de continuations
    (des FlatMap et des Fold en attente).
      Succeed(v)    : dépiler jusqu'à trouver une continuation de succès
                      (FlatMap.then ou Fold.on_success) ; pile vide -> Ok(v)
      Fail(e)    : dépiler en IGNORANT les FlatMap jusqu'à un Fold -> on_failure(e) ;
                      pile vide -> Err(e)
      Suspend(t)  : exécuter t() ; résultat -> Succeed, exception -> Fail
      FlatMap/Fold  : empiler le nœud, continuer avec son `effect`
    """
    raise NotImplementedError("S09 — à compléter")


# ---------------------------------------------------------------------------
# Services (« environnement » R de ZIO) : injection de dépendances fonctionnelle
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Services:
    read: Callable[[str], str]
    save: Callable[[str, str], None]
    display: Callable[[str], None]


def read_file(s: Services, path: str) -> Effect[str]:
    """Exercice 9.9 — décrire (sans exécuter !) la lecture d'un fichier."""
    raise NotImplementedError("S09 — à compléter")


def write_file(s: Services, path: str, content: str) -> Effect[None]:
    """Exercice 9.10"""
    raise NotImplementedError("S09 — à compléter")


def display(s: Services, message: str) -> Effect[None]:
    """Exercice 9.11"""
    raise NotImplementedError("S09 — à compléter")
