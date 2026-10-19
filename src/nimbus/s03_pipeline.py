"""Bloc 2, partie C — Un pipeline lazy à grande échelle, en mémoire constante.

On assemble les briques de la partie A (higher-order functions, generators) et de
la partie B (ADT) pour traiter des centaines de milliers de lignes sans les charger en mémoire.
Chaque étape est un generator : une ligne entre, une valeur sort, rien n'est stocké.
C'est le principe des transformations lazy de Spark et Polars (parcours Big Data).

Les tests mesurent le pic mémoire avec `tracemalloc` : une solution qui construit
une liste de toutes les lignes échoue, même si le résultat est juste.
"""

from __future__ import annotations

import itertools
from collections.abc import Callable, Iterable, Iterator
from nimbus.s03_algebraic_types import (
    BOUNDS, Alert, Heatwave, Frost, Flood, TypedReading, NoAlert, Storm, Valid, detect,
    parse_reading,
)


def readings(lines: Iterable[str]) -> Iterator[TypedReading]:
    """Exercice 3.10 — lignes CSV brutes (en-tête compris) -> relevés, en lazy.

    Sauter l'en-tête, découper sur ",", ignorer les lignes qui n'ont pas 7 colonnes,
    construire chaque relevé avec `parse_reading`. Aucune liste intermédiaire.
    """
    raise NotImplementedError("S03 — à compléter")


def count_alerts(rs: Iterable[TypedReading]) -> dict[str, int]:
    """Exercice 3.11 — nombre d'alertes par type sur tout le flux, en une seule passe.

    Clés : "storm", "flood", "heatwave", "frost" (toujours présentes, NoAlert n'est pas compté).
    """
    raise NotImplementedError("S03 — à compléter")


def first_n[A](predicate: Callable[[A], bool], n: int, xs: Iterable[A]) -> list[A]:
    """Exercice 3.12 — les n premiers éléments qui vérifient le prédicat.

    Doit s'arrêter dès que n éléments sont trouvés : les tests passent un flux infini,
    ou un flux qui lève une exception au-delà du point attendu.
    """
    raise NotImplementedError("S03 — à compléter")


def is_alert(a: Alert) -> bool:
    """Fourni."""
    return not isinstance(a, NoAlert)


def max_temperature_by_station(rs: Iterable[TypedReading]) -> dict[str, float]:
    """Exercice 3.13 — température Valid maximale par station, en une passe et en mémoire
    proportionnelle au nombre de stations (pas au nombre de lignes)."""
    raise NotImplementedError("S03 — à compléter")
