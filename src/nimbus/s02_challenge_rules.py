r"""Bloc 2 — DÉFI ★★★ (facultatif) : un langage de règles d'alerte, avec des parser combinators.

Objectif : que l'ingénieur météo écrive ses règles en texte, par exemple

    temperature_c >= 30 and (wind_kmh > 60 or not rain_mm < 10)

et que le programme les transforme en un algebraic data type (l'AST), puis les évalue
sur des relevés.

Un parser est une FONCTION : (text, position) -> Parsed(value, new_position) | Failed(position, expected).
Les parser combinators sont des higher-order functions qui prennent des parsers et
renvoient un nouveau parser (séquence, alternative, répétition...). C'est la technique
de Parsec (Haskell), de FastParse (Scala) ou de nom (Rust).

Grammaire (du moins prioritaire au plus prioritaire) :

    expr        := term ("or" term)*              -- associatif à gauche
    term        := factor ("and" factor)*         -- associatif à gauche
    factor      := "not" factor | "(" expr ")" | comparison
    comparison  := variable comparator number
    variable    := une clé de BOUNDS (temperature_c, humidity_pct, pressure_hpa, wind_kmh, rain_mm)
    comparator  := ">=" | "<=" | "==" | "!=" | ">" | "<"
    number      := -?[0-9]+(\.[0-9]+)?

Les espaces sont ignorés avant chaque élément. Difficulté : D1-D3 ★★, D4-D5 ★★★, D7 ★★★★
(le test de round-trip est une propriété Hypothesis sur des AST aléatoires).
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, assert_never

from nimbus.s03_algebraic_types import BOUNDS, TypedReading, Valid

# ---------------------------------------------------------------------------
# Résultat d'un parser et AST (fournis)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Parsed[T]:
    value: T
    position: int


@dataclass(frozen=True)
class Failed:
    position: int
    expected: str


type ParseResult[T] = Parsed[T] | Failed
type Parser[T] = Callable[[str, int], ParseResult[T]]


@dataclass(frozen=True)
class Comparison:
    variable: str
    comparator: str
    value: float


@dataclass(frozen=True)
class And:
    left: Expr
    right: Expr


@dataclass(frozen=True)
class Or:
    left: Expr
    right: Expr


@dataclass(frozen=True)
class Not:
    expr: Expr


type Expr = Comparison | And | Or | Not

OPERATORS = (">=", "<=", "==", "!=", ">", "<")      # l'ordre compte : ">=" avant ">"


def skip_spaces(text: str, pos: int) -> int:
    """Fourni."""
    while pos < len(text) and text[pos].isspace():
        pos += 1
    return pos


# ---------------------------------------------------------------------------
# D1 à D4 — les combinators
# ---------------------------------------------------------------------------


def literal(s: str) -> Parser[str]:
    """D1 ★★ — reconnaît exactement `s` (après les espaces). Échec : Failed(pos après espaces, repr(s))."""
    raise NotImplementedError("S02 — à compléter")


def pattern(regex: str, name: str) -> Parser[str]:
    """D1 ★★ — reconnaît l'expression régulière `regex` (après les espaces), échec nommé `name`.
    Indice : `re.compile(regex).match(text, pos)`."""
    raise NotImplementedError("S02 — à compléter")


def fmap[A, B](p: Parser[A], f: Callable[[A], B]) -> Parser[B]:
    """D2 ★★ — applique f à la valeur lue (le « map » des parsers)."""
    raise NotImplementedError("S02 — à compléter")


def sequence(*ps: Parser[Any]) -> Parser[tuple[Any, ...]]:
    """D2 ★★ — applique les parsers l'un après l'autre ; renvoie le tuple des valeurs,
    ou le premier échec."""
    raise NotImplementedError("S02 — à compléter")


def alternative[A](*ps: Parser[A]) -> Parser[A]:
    """D3 ★★ — le premier parser qui réussit. Si tous échouent, renvoyer l'échec qui est
    allé le plus loin (position maximale) : c'est lui qui donne le meilleur message d'erreur."""
    raise NotImplementedError("S02 — à compléter")


def chain_left(element: Parser[Expr], separator: Parser[str],
                  build: Callable[[Expr, Expr], Expr]) -> Parser[Expr]:
    """D4 ★★★ — element (separateur element)*, combiné de façon associative à gauche :
    a or b or c  ->  build(build(a, b), c). C'est un fold (bloc 3) !"""
    raise NotImplementedError("S02 — à compléter")


# ---------------------------------------------------------------------------
# D5 — la grammaire complète
# ---------------------------------------------------------------------------


def parse(text: str) -> Expr | Failed:
    """D5 ★★★ — texte -> AST, ou Failed si le texte n'est pas une règle valide.

    Tout le texte doit être consommé (espaces finaux compris) ; sinon Failed(position, "end of rule").
    Les mots-clés "and", "or", "not" ne doivent pas être confondus avec le début d'une variable.
    La récursion (factor -> "(" expr ")") se règle avec une fonction qui appelle `expr` au moment
    du parsing, pas au moment de la construction.
    """
    raise NotImplementedError("S02 — à compléter")


# ---------------------------------------------------------------------------
# D6, D7 — interpréter et afficher l'AST
# ---------------------------------------------------------------------------


def evaluate(e: Expr, r: TypedReading) -> bool:
    """D6 ★★ — vrai si le relevé vérifie la règle. Une comparaison sur une mesure qui
    n'est pas Valid est fausse (et donc `negation` de cette comparaison est vraie)."""
    raise NotImplementedError("S02 — à compléter")


def render(e: Expr) -> str:
    """D7 ★★★★ — AST -> texte, tel que `parse(render(e)) == e` pour TOUT AST.

    Les nombres doivent se relire à l'identique (`repr(float)` convient). Le plus simple :
    parenthéser chaque And et chaque Or. Bonus : n'écrire que les parenthèses nécessaires.
    """
    raise NotImplementedError("S02 — à compléter")
