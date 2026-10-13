"""Séance 9 — Effets fonctionnels : « un programme est une valeur » (à la ZIO).

Idée popularisée par John A. De Goes (ZIO, Scala) : au lieu d'EXÉCUTER des effets
de bord, on construit une DESCRIPTION du programme (une structure de données
immuable), puis un INTERPRÉTEUR l'exécute « au bout du monde » (dans `main`).

Conséquences :
- `retry`, `or_else`, `timeout`... deviennent de simples fonctions sur des valeurs ;
- le cœur métier reste pur, testable sans fichier ni réseau (on injecte de faux services) ;
- l'interpréteur peut être sûr vis-à-vis de la pile (pas de récursion Python).

Notre `Effet[A]` est une version minuscule de `ZIO[R, E, A]` : l'erreur est une
`Exception` et l'environnement R est passé explicitement (`Services`).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from nimbus.s05_erreurs import Err, Ok, Result

# ---------------------------------------------------------------------------
# Les primitives (fournies) : un petit langage dont les programmes sont des valeurs
# ---------------------------------------------------------------------------


class Effet[A]:
    """Classe de base. Les combinateurs ci-dessous sont à compléter."""

    def flat_map[B](self, f: Callable[[A], Effet[B]]) -> Effet[B]:
        return FlatMap(self, f)

    def fold[B](self, si_echec: Callable[[Exception], Effet[B]], si_succes: Callable[[A], Effet[B]]) -> Effet[B]:
        return Fold(self, si_echec, si_succes)

    # -- Exercices 9.1 à 9.6 : n'utiliser QUE flat_map, fold, succes, echec -----

    def map[B](self, f: Callable[[A], B]) -> Effet[B]:
        """Exercice 9.1"""
        raise NotImplementedError("S09 — à compléter")

    def zip[B](self, autre: Effet[B]) -> Effet[tuple[A, B]]:
        """Exercice 9.2 — exécute self puis autre, renvoie le couple des résultats."""
        raise NotImplementedError("S09 — à compléter")

    def tap(self, f: Callable[[A], Effet[Any]]) -> Effet[A]:
        """Exercice 9.3 — exécute l'effet f(a) pour son effet de bord, mais renvoie a."""
        raise NotImplementedError("S09 — à compléter")

    def catch_all(self, gestionnaire: Callable[[Exception], Effet[A]]) -> Effet[A]:
        """Exercice 9.4 — en cas d'échec, continue avec gestionnaire(erreur)."""
        raise NotImplementedError("S09 — à compléter")

    def or_else(self, alternative: Effet[A]) -> Effet[A]:
        """Exercice 9.5"""
        raise NotImplementedError("S09 — à compléter")

    def retry(self, n: int) -> Effet[A]:
        """Exercice 9.6 — réessaie jusqu'à n fois supplémentaires.

        Question clé : pourquoi ceci est-il IMPOSSIBLE avec une fonction Python
        ordinaire qui a déjà été appelée, mais trivial avec une description d'effet ?
        """
        raise NotImplementedError("S09 — à compléter")


@dataclass(frozen=True)
class Reussir[A](Effet[A]):
    valeur: A


@dataclass(frozen=True)
class Echouer(Effet[Any]):
    erreur: Exception


@dataclass(frozen=True)
class Suspendre[A](Effet[A]):
    """Encapsule un effet de bord SANS l'exécuter. Une exception levée devient un Echouer (échec)."""

    thunk: Callable[[], A]


@dataclass(frozen=True)
class FlatMap[A, B](Effet[B]):
    effet: Effet[A]
    suite: Callable[[A], Effet[B]]


@dataclass(frozen=True)
class Fold[A, B](Effet[B]):
    effet: Effet[A]
    si_echec: Callable[[Exception], Effet[B]]
    si_succes: Callable[[A], Effet[B]]


def succes[A](a: A) -> Effet[A]:
    return Reussir(a)


def echec(e: Exception) -> Effet[Any]:
    return Echouer(e)


def suspendre[A](thunk: Callable[[], A]) -> Effet[A]:
    return Suspendre(thunk)


def pour_chaque[A, B](xs: Iterable[A], f: Callable[[A], Effet[B]]) -> Effet[list[B]]:
    """Exercice 9.7 — `traverse` pour les effets : exécute f sur chaque élément, en séquence,
    et rassemble les résultats. Indice : partir de succes([]) et enchaîner des flat_map."""
    raise NotImplementedError("S09 — à compléter")


# ---------------------------------------------------------------------------
# L'interpréteur : le SEUL endroit où les effets se produisent réellement
# ---------------------------------------------------------------------------


def executer[A](programme: Effet[A]) -> Result[A, Exception]:
    """Exercice 9.8 — interpréteur itératif, sûr pour la pile.

    On maintient `courant` (l'effet à évaluer) et une pile de continuations
    (des FlatMap et des Fold en attente).
      Reussir(v)    : dépiler jusqu'à trouver une continuation de succès
                      (FlatMap.suite ou Fold.si_succes) ; pile vide -> Ok(v)
      Echouer(e)    : dépiler en IGNORANT les FlatMap jusqu'à un Fold -> si_echec(e) ;
                      pile vide -> Err(e)
      Suspendre(t)  : exécuter t() ; résultat -> Reussir, exception -> Echouer
      FlatMap/Fold  : empiler le nœud, continuer avec son `effet`
    """
    raise NotImplementedError("S09 — à compléter")


# ---------------------------------------------------------------------------
# Services (« environnement » R de ZIO) : injection de dépendances fonctionnelle
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Services:
    lire: Callable[[str], str]
    ecrire: Callable[[str, str], None]
    afficher: Callable[[str], None]


def lire_fichier(s: Services, chemin: str) -> Effet[str]:
    """Exercice 9.9 — décrire (sans exécuter !) la lecture d'un fichier."""
    raise NotImplementedError("S09 — à compléter")


def ecrire_fichier(s: Services, chemin: str, contenu: str) -> Effet[None]:
    """Exercice 9.10"""
    raise NotImplementedError("S09 — à compléter")


def afficher(s: Services, message: str) -> Effet[None]:
    """Exercice 9.11"""
    raise NotImplementedError("S09 — à compléter")
