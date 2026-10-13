"""Séance 7 La programmation fonctionnelle au cœur du ML moderne : JAX.

JAX exige des fonctions PURES. En échange, il offre des TRANSFORMATIONS DE FONCTIONS
(des fonctions d'ordre supérieur !) :
    jax.grad(f)  -> la fonction gradient de f        (différentiation automatique)
    jax.vmap(f)  -> f vectorisée sur un lot           (plus de boucles sur les exemples)
    jax.jit(f)   -> f compilée par XLA                (vitesse, y compris sur CPU de laptop)
    jax.lax.scan -> une boucle exprimée comme un fold (séance 4 !)

Les paramètres sont immuables : un pas d'optimisation est une fonction
    (paramètres, données) -> nouveaux paramètres
exactement comme l'état dans `optax` ou `flax`.

Avant JAX, on construit une mini différentiation automatique avec les nombres duaux
pour démystifier `grad`.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date
from itertools import groupby
from typing import NamedTuple

import jax
import jax.numpy as jnp

from nimbus.s03_types_algebriques import ReleveMesure, Valide, est_complet, mesures

# ---------------------------------------------------------------------------
# Partie A — différentiation automatique « à la main » : nombres duaux
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Dual:
    """a + b·ε avec ε² = 0.  Si on évalue f(x + 1·ε), on obtient f(x) + f'(x)·ε."""

    val: float
    eps: float = 0.0

    @staticmethod
    def _lift(x: Dual | float) -> Dual:
        return x if isinstance(x, Dual) else Dual(float(x), 0.0)

    def __add__(self, autre: Dual | float) -> Dual:
        """Exercice 7.1a"""
        raise NotImplementedError("S07 — à compléter")

    def __mul__(self, autre: Dual | float) -> Dual:
        """Exercice 7.1b — (a + bε)(c + dε) = ac + (ad + bc)ε"""
        raise NotImplementedError("S07 — à compléter")

    def __sub__(self, autre: Dual | float) -> Dual:
        return self + Dual._lift(autre) * -1.0

    def __pow__(self, n: int) -> Dual:
        resultat = Dual(1.0)
        for _ in range(n):
            resultat = resultat * self
        return resultat

    __radd__ = __add__
    __rmul__ = __mul__


def exp_dual(x: Dual) -> Dual:
    """Exercice 7.1c exp(a + bε) = exp(a) + b·exp(a)·ε"""
    raise NotImplementedError("S07 — à compléter")


def derivee(f: Callable[[Dual], Dual]) -> Callable[[float], float]:
    """Exercice 7.1d fonction d'ordre supérieur : renvoie la fonction dérivée de f."""
    raise NotImplementedError("S07 — à compléter")


# ---------------------------------------------------------------------------
# Partie B jeu de données « va-t-il pleuvoir demain ? »
# ---------------------------------------------------------------------------

SEUIL_PLUIE_MM = 0.2


def _veille_et_lendemain(r1: ReleveMesure, r2: ReleveMesure) -> bool:
    return (date.fromisoformat(r2.date) - date.fromisoformat(r1.date)).days == 1


def construire_jeu(releves: Sequence[ReleveMesure]) -> tuple[list[tuple[float, ...]], list[float]]:
    """Exercice 7.2 exemples (x_t, y_{t+1}), station par station.

    - trier par (station, date) puis grouper par station (itertools.groupby)
    - pour chaque couple de relevés CONSÉCUTIFS (zip(rs, rs[1:])) dont les dates
      se suivent (`_veille_et_lendemain`), que r_t est complet (`est_complet`)
      et que la pluie de r_{t+1} est Valide :
        x = valeurs des 5 mesures de r_t, y = 1.0 si pluie(t+1) > SEUIL_PLUIE_MM sinon 0.0
    """
    raise NotImplementedError("S07 — à compléter")


class Normalisation(NamedTuple):
    moyenne: jax.Array
    ecart_type: jax.Array


def standardiser(X: jax.Array) -> tuple[jax.Array, Normalisation]:
    """Exercice 7.3 — centre-réduit chaque colonne ; renvoie aussi les paramètres utilisés.

    (Remplacer un écart-type nul par 1.0 pour éviter la division par zéro : `jnp.where`.)
    """
    raise NotImplementedError("S07 — à compléter")


# ---------------------------------------------------------------------------
# Partie C — régression logistique purement fonctionnelle
# ---------------------------------------------------------------------------


class Params(NamedTuple):
    """Un NamedTuple est un « pytree » : JAX sait le parcourir (grad, tree_map...)."""

    w: jax.Array
    b: jax.Array


def init_params(n_variables: int) -> Params:
    return Params(jnp.zeros(n_variables), jnp.array(0.0))


def predire_un(params: Params, x: jax.Array) -> jax.Array:
    """Exercice 7.4 — probabilité de pluie pour UN exemple x (vecteur) : sigmoïde(w·x + b)."""
    raise NotImplementedError("S07 — à compléter")


def predire_lot(params: Params, X: jax.Array) -> jax.Array:
    """Exercice 7.5 — vectoriser `predire_un` sur toutes les lignes de X avec `jax.vmap`.

    Indice : in_axes=(None, 0) — on ne vectorise pas sur les paramètres.
    """
    raise NotImplementedError("S07 — à compléter")


def perte(params: Params, X: jax.Array, y: jax.Array) -> jax.Array:
    """Exercice 7.6 — entropie croisée binaire moyenne (clipper p dans [1e-7, 1 - 1e-7])."""
    raise NotImplementedError("S07 — à compléter")


def pas_gradient(params: Params, X: jax.Array, y: jax.Array, lr: float) -> Params:
    """Exercice 7.7 — un pas de descente de gradient, SANS muter params.

    g = jax.grad(perte)(params, X, y) a la même structure que params (un Params !).
    `jax.tree_util.tree_map(lambda p, g: ..., params, g)` applique la mise à jour feuille à feuille.
    """
    raise NotImplementedError("S07 — à compléter")


def entrainer(params: Params, X: jax.Array, y: jax.Array, lr: float = 0.5, n_iter: int = 300) -> tuple[Params, jax.Array]:
    """Exercice 7.8 — boucle d'entraînement exprimée comme un FOLD avec `jax.lax.scan`.

    scan(etape, etat_initial, xs=None, length=n_iter) où
        etape(params, _) -> (nouveaux_params, perte_courante)
    Renvoie (params finaux, historique des pertes).
    Bonus : décorer une fonction interne avec @jax.jit et mesurer le gain.
    """
    raise NotImplementedError("S07 — à compléter")


def exactitude(params: Params, X: jax.Array, y: jax.Array) -> float:
    """Exercice 7.9 — proportion de prédictions correctes au seuil 0.5."""
    raise NotImplementedError("S07 — à compléter")
