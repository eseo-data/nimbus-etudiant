"""Séance 5 — Gestion fonctionnelle des erreurs : Option, Result, Validation.

Une exception est un `goto` invisible dans la signature. Ici l'échec devient une
VALEUR : `Result[T, E] = Ok[T] | Err[E]` (Either en Scala/Haskell).

- `map`      : transformer la valeur si succès       -> foncteur
- `flat_map` : enchaîner une opération qui peut échouer -> monade (s'arrête au 1er échec)
- `Validation` : combiner des vérifications INDÉPENDANTES en accumulant TOUTES les
  erreurs -> foncteur applicatif. Indispensable pour un rapport de qualité de données.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import date
from typing import Any

from nimbus.datagen import STATIONS
from nimbus.s02_higher_order import COLUMNS, split_csv
from nimbus.s03_algebraic_types import BOUNDS, TypedReading, parse_reading

# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Ok[T]:
    value: T

    def map[U](self, f: Callable[[T], U]) -> Ok[U]:
        """Exercice 5.1a"""
        raise NotImplementedError("S05 — à compléter")

    def flat_map[U, E](self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Exercice 5.1b"""
        raise NotImplementedError("S05 — à compléter")

    def get_or(self, default: Any) -> T:
        return self.value

    def is_ok(self) -> bool:
        return True


@dataclass(frozen=True)
class Err[E]:
    error: E

    def map(self, f: Callable[[Any], Any]) -> Err[E]:
        """Exercice 5.1c — un échec reste un échec."""
        raise NotImplementedError("S05 — à compléter")

    def flat_map(self, f: Callable[[Any], Any]) -> Err[E]:
        """Exercice 5.1d"""
        raise NotImplementedError("S05 — à compléter")

    def get_or[T](self, default: T) -> T:
        return default

    def is_ok(self) -> bool:
        return False


type Result[T, E] = Ok[T] | Err[E]


def attempt[T](f: Callable[[], T]) -> Result[T, str]:
    """Exercice 5.2 — pont avec le monde à exceptions : exécute f, capture l'exception en Err(message)."""
    raise NotImplementedError("S05 — à compléter")


def traverse[A, B, E](xs: Iterable[A], f: Callable[[A], Result[B, E]]) -> Result[list[B], E]:
    """Exercice 5.3 — applique f à chaque élément ; Ok(liste) si tout réussit, sinon le PREMIER Err."""
    raise NotImplementedError("S05 — à compléter")


# ---------------------------------------------------------------------------
# Validation (accumule les erreurs)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Success[T]:
    value: T


@dataclass(frozen=True)
class Failures:
    errors: tuple[str, ...]


type Validation[T] = Success[T] | Failures


def validate[T](condition: bool, value: T, message: str) -> Validation[T]:
    """Fourni."""
    return Success(value) if condition else Failures((message,))


def combine(*validations: Validation[Any]) -> Validation[tuple[Any, ...]]:
    """Exercice 5.4 — combine N validations INDÉPENDANTES.

    Tous Success -> Success(tuple des valeurs) ; sinon Failures(concaténation de TOUTES les erreurs).
    """
    raise NotImplementedError("S05 — à compléter")


def _date_iso(s: str) -> Validation[str]:
    """Fourni (utilise `attempt`)."""
    match attempt(lambda: date.fromisoformat(s)):
        case Ok(_):
            return Success(s)
        case Err(_):
            return Failures((f"date invalide {s!r}",))
    raise AssertionError  # inatteignable


def validate_line(fields: list[str]) -> Validation[TypedReading]:
    """Exercice 5.5 — valide la STRUCTURE d'une ligne et construit le TypedReading.

    Vérifications (toutes, sans s'arrêter à la première) :
      - nombre de colonnes == len(COLUMNS)         sinon "attendu 7 colonnes, reçu N"
        (si ce test échoue, inutile d'aller plus loin : renvoyer directement l'échec)
      - date au format ISO (utiliser `_date_iso`)
      - station dans STATIONS                         sinon "station inconnue 'X'"
    Les mesures elles-mêmes ne font PAS échouer la ligne : elles deviennent des
    `Measurement` via `parse_reading` (séance 3).
    """
    raise NotImplementedError("S05 — à compléter")


@dataclass(frozen=True)
class Loaded:
    readings: tuple[TypedReading, ...]
    rejected: tuple[tuple[int, tuple[str, ...]], ...]  # (numéro de ligne dans le fichier, errors)


def load(csv_text: str) -> Loaded:
    """Exercice 5.6 — découpe (séance 2) puis valide chaque ligne et partitionne.

    Numéro de ligne : 2 pour la première ligne de données (l'en-tête est la ligne 1).
    """
    raise NotImplementedError("S05 — à compléter")
