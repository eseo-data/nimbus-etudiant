"""Séance 3 — Types algébriques de données (ADT) et filtrage par motif.

Type produit  : « A ET B »  -> dataclass (un relevé a une date ET une station ET ...)
Type somme    : « A OU B »  -> union de dataclasses (une mesure est valide OU manquante OU aberrante)

Principe : « make illegal states unrepresentable » (Yaron Minsky).
Le `match` + `assert_never` laisse le vérificateur de types (mypy --strict)
signaler tout cas oublié.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import assert_never

# ---------------------------------------------------------------------------
# Le type somme `Measurement` (fourni)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Valid:
    value: float


@dataclass(frozen=True)
class Missing:
    pass


@dataclass(frozen=True)
class Outlier:
    raw: str
    reason: str


type Measurement = Valid | Missing | Outlier

MISSING_VALUES = frozenset({"", "NA", "-", "null"})

# Bornes physiquement plausibles par variable (fourni)
BOUNDS: dict[str, tuple[float, float]] = {
    "temperature_c": (-40.0, 50.0),
    "humidity_pct": (0.0, 100.0),
    "pressure_hpa": (900.0, 1080.0),
    "wind_kmh": (0.0, 250.0),
    "rain_mm": (0.0, 300.0),
}


@dataclass(frozen=True)
class TypedReading:
    """Type produit dont les champs sont des types sommes."""

    date: str
    station: str
    temperature_c: Measurement
    humidity_pct: Measurement
    pressure_hpa: Measurement
    wind_kmh: Measurement
    rain_mm: Measurement


# ---------------------------------------------------------------------------
# Exercices
# ---------------------------------------------------------------------------


def parse_measurement(raw: str, lower: float, upper: float) -> Measurement:
    """Exercice 3.1 — transforme une chaîne brute en Measurement. Ne lève JAMAIS d'exception.

    - chaîne (strippée) dans MISSING_VALUES             -> Missing()
    - non convertible en float                          -> Outlier(raw, "non numérique")
    - hors [lower, upper]                               -> Outlier(raw, "hors bornes")
    - sinon                                             -> Valid(value)
    """
    raise NotImplementedError("S03 — à compléter")


def value_or(m: Measurement, default: float) -> float:
    """Exercice 3.2 — la valeur si Valid, sinon `default`. Utiliser `match`."""
    raise NotImplementedError("S03 — à compléter")


def describe(m: Measurement) -> str:
    """Exercice 3.3 — description lisible, `match` exhaustif terminé par assert_never.

    Valid(12.5)                   -> "12.5"
    Missing()                     -> "manquante"
    Outlier("999", "hors bornes") -> "aberrante (hors bornes) : '999'"
    """
    raise NotImplementedError("S03 — à compléter")


def parse_reading(date: str, station: str, fields: dict[str, str]) -> TypedReading:
    """Exercice 3.4 — construit un TypedReading à partir des champs bruts.

    `fields` associe chaque nom de BOUNDS à sa chaîne brute.
    """
    raise NotImplementedError("S03 — à compléter")


def measurements(r: TypedReading) -> tuple[Measurement, ...]:
    """Fourni : les 5 mesures d'un relevé, dans l'ordre de BOUNDS."""
    return (r.temperature_c, r.humidity_pct, r.pressure_hpa, r.wind_kmh, r.rain_mm)


def is_complete(r: TypedReading) -> bool:
    """Exercice 3.5 — vrai si toutes les mesures du relevé sont Valid."""
    raise NotImplementedError("S03 — à compléter")


def count_by_kind(ms: Iterable[Measurement]) -> dict[str, int]:
    """Exercice 3.6 — {"valid": n1, "missing": n2, "outlier": n3} (toujours les 3 clés)."""
    raise NotImplementedError("S03 — à compléter")


# ===========================================================================
# PARTIE B — Remplacer des valeurs magiques par un ADT (bloc 2)
# ===========================================================================
# Lisez `nimbus/s03_legacy_alerts.py` : -999 pour « pas de valeur », des
# chaînes pour le type d'alerte, None pour « rien ». Ci-dessous, le même domaine
# modélisé par un sum type. Les seuils sont ceux du legacy.

HEATWAVE_THRESHOLD = 25.0
FROST_THRESHOLD = 0.0
STORM_THRESHOLD = 28.0
FLOOD_THRESHOLD = 15.0


@dataclass(frozen=True)
class Storm:
    wind_kmh: float


@dataclass(frozen=True)
class Flood:
    rain_mm: float


@dataclass(frozen=True)
class Heatwave:
    temperature_c: float


@dataclass(frozen=True)
class Frost:
    temperature_c: float


@dataclass(frozen=True)
class NoAlert:
    pass


type Alert = Storm | Flood | Heatwave | Frost | NoAlert


def detect(r: TypedReading) -> Alert:
    """Exercice 3.7 — l'alerte d'un relevé, avec la priorité du legacy :
    Storm > Flood > Heatwave > Frost > NoAlert.

    Seules les mesures Valid comptent : une valeur Missing ou Outlier ne
    déclenche jamais d'alerte (c'est ce qui supprime les fausses alertes du legacy).
    Indice : `match (r.wind_kmh, r.rain_mm, r.temperature_c)` avec des guards
    (`case (Valid(v), _, _) if v >= STORM_THRESHOLD:`).
    """
    raise NotImplementedError("S03 — à compléter")


def message(date: str, station: str, a: Alert) -> str | None:
    """Exercice 3.8 — le texte de l'alerte, au format exact du legacy ; None pour NoAlert.

    `match` exhaustif terminé par `assert_never(a)` : si on ajoute un cas à Alert,
    mypy signale cette fonction.
    """
    raise NotImplementedError("S03 — à compléter")


def alert_report(lines: Iterable[list[str]]) -> list[str]:
    """Exercice 3.9 — les messages d'alerte de toutes les lignes à 7 colonnes, dans l'ordre.

    `lines` est le résultat de `split_csv` (bloc 2, partie A) : en-tête déjà retiré.
    Utilisez `parse_reading`, `detect` et `message`.
    """
    raise NotImplementedError("S03 — à compléter")
