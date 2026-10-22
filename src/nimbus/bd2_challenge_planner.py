"""BD2 — DÉFI ★★★ (facultatif) : un mini query optimizer.

Polars et Spark (Catalyst) réécrivent le query plan avant de l'exécuter. Deux règles
font l'essentiel du gain :
- predicate pushdown : appliquer les filtres au plus près de la lecture ;
- projection pushdown (column pruning) : ne lire que les colonnes utiles.

Ici, un plan est un algebraic data type, et l'optimiseur est une fonction pure
Plan -> Plan écrite avec du pattern matching, comme les règles de Catalyst.
Les tests vérifient avec Hypothesis que, pour des plans et des tables aléatoires,
le plan optimisé donne exactement le même résultat que le plan d'origine.

Sémantique : `Scan(columns, predicate)` lit chaque ligne de la table, la garde si
`predicate` est vrai (évalué sur la ligne complète), puis ne renvoie que `columns`.
Une valeur absente vaut None ; une comparaison avec None est fausse.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import assert_never

type Value = float | str | None
type Row = Mapping[str, Value]


@dataclass(frozen=True)
class Gt:
    column: str
    value: float


@dataclass(frozen=True)
class Eq:
    column: str
    value: float | str


@dataclass(frozen=True)
class And:
    left: Pred
    right: Pred


type Pred = Gt | Eq | And


@dataclass(frozen=True)
class Scan:
    columns: tuple[str, ...]
    predicate: Pred | None = None


@dataclass(frozen=True)
class Filter:
    predicate: Pred
    child: Plan


@dataclass(frozen=True)
class Project:
    columns: tuple[str, ...]
    child: Plan


type Plan = Scan | Filter | Project


def output_columns(plan: Plan) -> tuple[str, ...]:
    """Fourni : les colonnes produites par un plan."""
    match plan:
        case Scan(cols, _) | Project(cols, _):
            return cols
        case Filter(_, child):
            return output_columns(child)
        case _:
            assert_never(plan)


# ---------------------------------------------------------------------------
# D1, D2 — évaluer
# ---------------------------------------------------------------------------


def pred_columns(p: Pred) -> frozenset[str]:
    """D1 ★ — les colonnes lues par un prédicat."""
    raise NotImplementedError("BD2 — à compléter")


def holds(p: Pred, row: Row) -> bool:
    """D1 ★ — le prédicat est-il vrai pour cette ligne ? (None : toujours faux)
    Gt ne s'applique qu'aux nombres (float ou int) ; Eq compare avec ==."""
    raise NotImplementedError("BD2 — à compléter")


def execute(plan: Plan, table: Sequence[Row]) -> list[dict[str, Value]]:
    """D2 ★★ — exécute le plan sur une table (liste de lignes), en respectant l'ordre des lignes."""
    raise NotImplementedError("BD2 — à compléter")


# ---------------------------------------------------------------------------
# D3, D4 — optimiser
# ---------------------------------------------------------------------------


def push_down(plan: Plan) -> Plan:
    """D3 ★★★ — predicate pushdown : après réécriture, il ne reste aucun Filter.

    - un Filter au-dessus d'un Scan rejoint le prédicat du Scan (And si le Scan en a déjà un) ;
    - un Filter au-dessus d'un Project passe sous le Project (c'est valide : les colonnes
      du prédicat sont forcément dans le Project) ;
    - réécrire les enfants d'abord.
    """
    raise NotImplementedError("BD2 — à compléter")


def prune(plan: Plan, needed: frozenset[str] | None = None) -> Plan:
    """D4 ★★★ — projection pushdown : chaque nœud ne garde que les colonnes utiles au-dessus de lui.

    `needed` = colonnes demandées par le parent (None à la racine : on garde la sortie telle quelle).
    - Scan : garder les colonnes de `needed` (dans l'ordre d'origine) ;
    - Project : idem pour ses colonnes, puis élaguer l'enfant avec ces colonnes ;
    - Filter : l'enfant doit fournir `needed` ET les colonnes du prédicat.
    """
    raise NotImplementedError("BD2 — à compléter")


def optimize(plan: Plan) -> Plan:
    """Fourni : les deux règles, dans l'ordre."""
    return prune(push_down(plan))


def columns_read(plan: Plan) -> frozenset[str]:
    """Fourni : colonnes lues sur le « disque » par les Scan (sortie + prédicat)."""
    match plan:
        case Scan(cols, pred):
            return frozenset(cols) | (pred_columns(pred) if pred is not None else frozenset())
        case Filter(_, child) | Project(_, child):
            return columns_read(child)
        case _:
            assert_never(plan)
