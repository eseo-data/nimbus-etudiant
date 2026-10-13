"""Séance 1 — DÉFI ★★★ (facultatif, pour les plus curieux) : le vecteur persistant.

Question laissée ouverte en cours : « l'immutabilité, c'est bien, mais copier un
tuple d'un million d'éléments pour en changer UN, c'est ruineux ». Réponse des
langages fonctionnels (Clojure, Scala, Haskell...) : le VECTEUR PERSISTANT.

Idée (Phil Bagwell, Rich Hickey) : stocker les éléments dans les feuilles d'un
arbre où chaque nœud a jusqu'à 32 enfants. Pour modifier l'élément i, on ne
recopie QUE le chemin racine -> feuille (au plus ~4 nœuds pour un million
d'éléments) ; tout le reste est PARTAGÉ entre l'ancienne et la nouvelle version.
Les deux versions restent valides et immuables.

            racine (décalage = 5)
           /        |         \\
     [0..31]    [32..63]   [64..65]        <- feuilles : tuples de ≤ 32 valeurs

Pour trouver l'élément i : à chaque niveau, l'enfant à suivre est donné par
5 bits de i :   (i >> decalage) & 31,  puis decalage -= 5, jusqu'à la feuille
où l'on prend i & 31.

Représentation imposée (les tests en dépendent) :
- une feuille est un `tuple` de valeurs ; un nœud interne est un `tuple` de nœuds ;
- `decalage` = 5 × (hauteur - 1) : 0 quand la racine est elle-même une feuille ;
- aucun nœud vide ne doit subsister, et la racine n'a jamais un seul enfant
  si decalage > 0 (sauf transitoirement : voir `retirer_dernier`).

Difficulté : D1, D2, D5 ★★ ; D3, D4 ★★★ ; D6 ★★★★ (hors barème). Les tests vérifient le partage
structurel : une copie complète échoue, même si le résultat est juste.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from functools import reduce
from typing import Any

BITS = 5
LARGEUR = 1 << BITS      # 32
MASQUE = LARGEUR - 1     # 0b11111

type Noeud = tuple[Any, ...]


@dataclass(frozen=True)
class Vecteur[T]:
    taille: int
    decalage: int
    racine: Noeud

    def __len__(self) -> int:
        return self.taille

    def __iter__(self) -> Iterator[T]:
        return iter(vers_tuple(self))


VIDE: Vecteur[Any] = Vecteur(0, 0, ())


def profondeur(v: Vecteur[Any]) -> int:
    """Fourni : nombre de niveaux de l'arbre."""
    return v.decalage // BITS + 1


def obtenir[T](v: Vecteur[T], i: int) -> T:
    """D1 ★★ — l'élément d'indice i en O(log32 n). IndexError si i hors de [0, taille)."""
    raise NotImplementedError("S01 — à compléter")


def remplacer[T](v: Vecteur[T], i: int, x: T) -> Vecteur[T]:
    """D2 ★★ — nouvelle version où l'élément i vaut x ; seul le chemin est recopié."""
    raise NotImplementedError("S01 — à compléter")


def ajouter[T](v: Vecteur[T], x: T) -> Vecteur[T]:
    """D3 ★★★ — ajoute x à la fin.

    Trois cas : vecteur vide ; racine pleine (taille == 1 << (decalage + BITS)) : il
    faut une NOUVELLE racine, un niveau plus haut, dont le 2e enfant est un chemin neuf ;
    sinon : descendre en recopiant le chemin, et créer un chemin neuf là où l'enfant
    n'existe pas encore.
    """
    raise NotImplementedError("S01 — à compléter")


def retirer_dernier[T](v: Vecteur[T]) -> Vecteur[T]:
    """D4 ★★★ — supprime le dernier élément (IndexError si vide).

    Attention aux nœuds devenus vides (à supprimer) et à la racine qui n'a plus
    qu'un enfant (l'arbre doit perdre un niveau).
    """
    raise NotImplementedError("S01 — à compléter")


def vers_tuple[T](v: Vecteur[T]) -> tuple[T, ...]:
    """D5 ★★ — tous les éléments dans l'ordre (parcours de l'arbre, sans appeler obtenir n fois)."""
    raise NotImplementedError("S01 — à compléter")


def depuis[T](xs: Iterable[T]) -> Vecteur[T]:
    """Fourni : un fold d'`ajouter` (séance 4 !)."""
    return reduce(ajouter, xs, VIDE)


# ---------------------------------------------------------------------------
# D6 ★★★★ (hors barème) : `concatener(a, b)` en mieux que O(len(b)).
# Indice : chercher « RRB-tree » (Bagwell & Rompf, 2011). Aucun test fourni :
# écrivez les vôtres, avec Hypothesis, contre le modèle `tuple`.
# ---------------------------------------------------------------------------
