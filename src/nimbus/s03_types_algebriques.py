"""Séance 3 Types algébriques de données (ADT) et filtrage par motif.

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
# Le type somme `Mesure` (fourni)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Valide:
    valeur: float


@dataclass(frozen=True)
class Manquante:
    pass


@dataclass(frozen=True)
class Aberrante:
    brute: str
    raison: str


type Mesure = Valide | Manquante | Aberrante

VALEURS_MANQUANTES = frozenset({"", "NA", "-", "null"})

# Bornes physiquement plausibles par variable (fourni)
BORNES: dict[str, tuple[float, float]] = {
    "temperature_c": (-40.0, 50.0),
    "humidite_pct": (0.0, 100.0),
    "pression_hpa": (900.0, 1080.0),
    "vent_kmh": (0.0, 250.0),
    "pluie_mm": (0.0, 300.0),
}


@dataclass(frozen=True)
class ReleveMesure:
    """Type produit dont les champs sont des types sommes."""

    date: str
    station: str
    temperature_c: Mesure
    humidite_pct: Mesure
    pression_hpa: Mesure
    vent_kmh: Mesure
    pluie_mm: Mesure


# ---------------------------------------------------------------------------
# Exercices
# ---------------------------------------------------------------------------


def lire_mesure(brute: str, borne_min: float, borne_max: float) -> Mesure:
    """Exercice 3.1 transforme une chaîne brute en Mesure. Ne lève JAMAIS d'exception.

    - chaîne (strippée) dans VALEURS_MANQUANTES        -> Manquante()
    - non convertible en float                          -> Aberrante(brute, "non numérique")
    - hors [borne_min, borne_max]                       -> Aberrante(brute, "hors bornes")
    - sinon                                             -> Valide(valeur)
    """
    raise NotImplementedError("S03 — à compléter")


def valeur_ou(m: Mesure, defaut: float) -> float:
    """Exercice 3.2 la valeur si Valide, sinon `defaut`. Utiliser `match`."""
    raise NotImplementedError("S03 — à compléter")


def decrire(m: Mesure) -> str:
    """Exercice 3.3 — description lisible, `match` exhaustif terminé par assert_never.

    Valide(12.5)                    -> "12.5"
    Manquante()                     -> "manquante"
    Aberrante("999", "hors bornes") -> "aberrante (hors bornes) : '999'"
    """
    raise NotImplementedError("S03 — à compléter")


def lire_releve(date: str, station: str, champs: dict[str, str]) -> ReleveMesure:
    """Exercice 3.4 construit un ReleveMesure à partir des champs bruts.

    `champs` associe chaque nom de BORNES à sa chaîne brute.
    """
    raise NotImplementedError("S03 — à compléter")


def mesures(r: ReleveMesure) -> tuple[Mesure, ...]:
    """Fourni : les 5 mesures d'un relevé, dans l'ordre de BORNES."""
    return (r.temperature_c, r.humidite_pct, r.pression_hpa, r.vent_kmh, r.pluie_mm)


def est_complet(r: ReleveMesure) -> bool:
    """Exercice 3.5 vrai si toutes les mesures du relevé sont Valide."""
    raise NotImplementedError("S03 — à compléter")


def compter_par_type(ms: Iterable[Mesure]) -> dict[str, int]:
    """Exercice 3.6 {"valide": n1, "manquante": n2, "aberrante": n3} (toujours les 3 clés)."""
    raise NotImplementedError("S03 — à compléter")
