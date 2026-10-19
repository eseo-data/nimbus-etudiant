"""Bloc BD3 — Stream processing, en pur.

Un moteur de streaming (Spark Structured Streaming, Flink, Kafka Streams) se ramène
à une fonction pure appelée pour chaque événement :

    etape : (état, événement) -> (nouvel état, résultats émis)

Le flux entier est alors un fold (bloc 3) sur les événements. Comme l'état est une
valeur immutable :
- on peut le sauvegarder entre deux lots (checkpoint) et reprendre exactement au même point ;
- rejouer le même flux donne le même résultat (replay) ;
- les doublons sont ignorés si on garde les identifiants déjà vus (idempotence) ;
- les agrégats de fenêtre sont des monoids (bloc BD1), donc l'ordre d'arrivée dans
  une fenêtre ne change pas le résultat.

Vocabulaire :
- event time : l'horodatage porté par l'événement (ici, un numéro de jour) ;
- tumbling window : fenêtres de taille fixe, sans recouvrement ;
- watermark : « je ne m'attends plus à recevoir d'événement antérieur à ce temps ».
  watermark = (plus grand event time vu) - max_delay. Une fenêtre se ferme, et est
  émise, quand sa fin est inférieure ou égale au watermark. Un événement qui arrive
  pour une fenêtre déjà fermée est en retard (late) : il est compté puis ignoré.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, replace
from datetime import date
from types import MappingProxyType

from nimbus.s01_purity import advance
from nimbus.s06_monoids import STATS, Stats, stats_of

ORIGIN = date(2016, 1, 1)


@dataclass(frozen=True)
class Event:
    id: str            # identifiant unique (sert à dédupliquer)
    station: str
    timestamp: int         # event time : numéro de jour depuis ORIGIN
    value: float      # température


@dataclass(frozen=True)
class Window:
    station: str
    start: int         # inclus
    end: int           # exclue
    stats: Stats


type Key = tuple[str, int]   # (station, début de fenêtre)


@dataclass(frozen=True)
class State:
    watermark: int = -(10**9)
    open_windows: Mapping[Key, Stats] = MappingProxyType({})
    seen_set: frozenset[str] = frozenset()
    delays: int = 0
    duplicates: int = 0


def window_start(timestamp: int, size: int) -> int:
    """Exercice BD3.1 — début de la tumbling window qui contient `timestamp` (fenêtres [k·taille, (k+1)·taille))."""
    raise NotImplementedError("BD3 — à compléter")


def step(state: State, e: Event, size: int, max_delay: int) -> tuple[State, tuple[Window, ...]]:
    """Exercice BD3.2 — traite UN événement. Ne mute rien : renvoie un nouvel State.

    Dans l'ordre :
    1. si e.id est déjà dans `seen_set` : duplicates + 1, rien d'autre ne change, aucune sortie ;
    2. si la fenêtre de e est déjà fermée (start + size <= watermark) : delays + 1,
       e.id est ajouté à `seen_set`, aucune sortie ;
    3. sinon : combiner stats_of(e.value) dans la fenêtre (station, start) avec STATS ;
    4. watermark = max(watermark, e.timestamp - max_delay) ;
    5. émettre (et retirer de `open_windows`) toutes les fenêtres dont la fin <= watermark,
       triées par (station, start).
    `open_windows` doit rester immutable : construisez un nouveau dict et enveloppez-le
    dans MappingProxyType.
    """
    raise NotImplementedError("BD3 — à compléter")


def process(events: Iterable[Event], size: int, max_delay: int,
            state: State = State()) -> tuple[State, tuple[Window, ...]]:
    """Exercice BD3.3 — fold de `step` sur tout le flux : (état final, toutes les sorties dans l'ordre).

    Le paramètre `state` permet de reprendre après un checkpoint.
    """
    raise NotImplementedError("BD3 — à compléter")


def flush(state: State, size: int) -> tuple[State, tuple[Window, ...]]:
    """Exercice BD3.4 — fin de flux : émet toutes les fenêtres encore ouvertes, triées par (station, start)."""
    raise NotImplementedError("BD3 — à compléter")


def aggregate_batch(events: Iterable[Event], size: int) -> dict[Key, Stats]:
    """Exercice BD3.5 — la même agrégation en mode batch (sans watermark, doublons retirés par id).

    Sert de référence : sur un flux sans retard, streaming et batch doivent coïncider.
    """
    raise NotImplementedError("BD3 — à compléter")


# ---------------------------------------------------------------------------
# Fournis : source d'événements et désordre contrôlé
# ---------------------------------------------------------------------------


def events_from_csv(lines: Iterable[str]) -> Iterator[Event]:
    """Fourni : convertit des lignes CSV Nimbus en événements (lignes invalides ignorées)."""
    for i, line in enumerate(lines):
        fields = line.split(",")
        if i == 0 or len(fields) < 3:
            continue
        try:
            day = (date.fromisoformat(fields[0]) - ORIGIN).days
            value = float(fields[2])
        except ValueError:
            continue
        if -40.0 <= value <= 50.0:
            yield Event(f"{fields[1]}-{fields[0]}", fields[1], day, value)


def disorder(events: Iterable[Event], window: int, rng_state: int) -> list[Event]:
    """Fourni : mélange les événements par paquets de `window` (désordre borné, reproductible).

    Utilise le générateur pur du bloc 1 (`advance`) : même graine, même désordre.
    """
    result: list[Event] = []
    bundle: list[Event] = []
    for e in events:
        bundle.append(e)
        if len(bundle) == window:
            result.extend(_shuffle(bundle, rng_state))
            rng_state = advance(rng_state)
            bundle = []
    result.extend(_shuffle(bundle, rng_state))
    return result


def _shuffle(xs: list[Event], state: int) -> list[Event]:
    copied = list(xs)
    for i in range(len(copied) - 1, 0, -1):
        state = advance(state)
        j = int(((state >> 11) / 2**53) * (i + 1))
        copied[i], copied[j] = copied[j], copied[i]
    return copied
