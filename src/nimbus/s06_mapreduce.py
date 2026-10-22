"""BD1, parties B et C — MapReduce avec des monoids.

Partie B : réécrire le rapport legacy (`s06_legacy_mapreduce.py`) pour que le
résultat ne dépende plus du découpage. Partie C : un vrai MapReduce sur plusieurs
processus, chaque worker générant et agrégeant son propre shard de données.

Bonus : un monoid numériquement stable pour la variance (Welford / Chan).
"""

from __future__ import annotations

import sys
import time
from collections.abc import Iterable, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass

from nimbus.datagen import generate_massive_lines
from nimbus.s06_monoids import STATS, Monoid, Stats, dict_monoid, fold_map, fold_map_parallel, stats_of

type Key = tuple[str, str]          # (station, mois "AAAA-MM")

# ===========================================================================
# Partie B — réécrire le rapport legacy
# ===========================================================================


def parse_line(line: str) -> tuple[Key, float] | None:
    """Exercice 6.9 — ((station, mois), température) pour une ligne valide, sinon None.

    Mêmes règles que le legacy : 7 colonnes, date au format AAAA-MM-JJ (longueur 10,
    tiret en 5e position), température numérique dans [-40, 50]. Le mois est date[:7].
    """
    raise NotImplementedError("S06 — à compléter")


def monthly_stats(lines: Sequence[str], workers: int = 4) -> Mapping[Key, Stats]:
    """Exercice 6.10 — Stats par (station, mois), en une passe `fold_map_parallel`.

    `lines` contient l'en-tête en première position (à ignorer). Les lignes invalides
    contribuent l'élément neutre de `dict_monoid(STATS)`.

    Piège : l'addition de flottants n'est pas exactement associative. Selon le découpage,
    la somme peut différer au dernier bit et changer l'arrondi affiché. Les températures
    ont une décimale : agrégez des dixièmes de degré entiers, `stats_of(round(t * 10))`.
    Une somme d'entiers est exacte (jusqu'à 2**53), donc associative.
    """
    raise NotImplementedError("S06 — à compléter")


def monthly_report(lines: Sequence[str], workers: int = 4) -> list[str]:
    """Exercice 6.11 — le rapport, au format du legacy, trié par (station, mois) :

        "ST0001 2016-01 n=31 mean=3.27 max=9.4"

    Il doit être identique quel que soit `workers`. Les Stats sont en dixièmes de degré.
    """
    raise NotImplementedError("S06 — à compléter")


# ===========================================================================
# Partie C — MapReduce sur plusieurs processus
# ===========================================================================
# Chaque shard est une « région » : ses stations s'appellent R03-ST0001, etc.
# Un worker reçoit seulement (numéro de shard, taille) et génère ses lignes lui-même :
# rien de volumineux ne transite entre processus, comme quand chaque nœud d'un
# cluster lit sa propre partition sur disque.


@dataclass(frozen=True)
class Shard:
    """Fourni : la description d'un shard (petite, donc peu coûteuse à envoyer)."""

    index: int
    n_stations: int
    n_days: int


def shard_lines(shard: Shard) -> Iterable[str]:
    """Fourni : les lignes du shard, sans en-tête, stations préfixées par la région."""
    prefix = f"R{shard.index:02d}-"
    lines = generate_massive_lines(1000 + shard.index, shard.n_stations, shard.n_days)
    next(lines)
    for line in lines:
        f = line.split(",", 2)
        if len(f) == 3:
            yield f"{f[0]},{prefix}{f[1]},{f[2]}"
        else:
            yield line


def map_shard(shard: Shard) -> Mapping[str, Stats]:
    """Exercice 6.12 — phase map : Stats de température par station pour UN shard.

    Doit être une fonction de module (pas une lambda) : ProcessPoolExecutor envoie la
    fonction aux autres processus par pickle. Réutilisez `parse_line`.
    """
    raise NotImplementedError("S06 — à compléter")


def map_reduce(shards: Sequence[Shard], workers: int) -> Mapping[str, Stats]:
    """Exercice 6.13 — map en parallèle sur `workers` processus, puis reduce avec le monoid.

    Indice : `ProcessPoolExecutor(max_workers=workers).map(map_shard, shards)`.
    Pourquoi des processus et pas des threads ici ? (le GIL de CPython)
    """
    raise NotImplementedError("S06 — à compléter")


def benchmark(n_shards: int = 8, n_stations: int = 25, n_days: int = 3650) -> None:  # pragma: no cover
    """Fourni : uv run python -m nimbus.s06_mapreduce  (affiche le temps selon le nombre de workers)."""
    shards = [Shard(i, n_stations, n_days) for i in range(n_shards)]
    print(f"{n_shards * n_stations * n_days:,} lignes".replace(",", " "))
    reference = None
    for w in (1, 2, 4, 8):
        t0 = time.perf_counter()
        r = map_reduce(shards, w)
        print(f"  workers={w}  {time.perf_counter() - t0:5.1f} s")
        reference = reference or r
        assert r == reference


# ===========================================================================
# Bonus — variance numériquement stable (Welford, Chan et al.)
# ===========================================================================
# Stats.variance calcule E[x²] - E[x]² : si les valeurs valent 1e9 + bruit, les deux
# termes sont énormes et presque égaux, et la soustraction perd tous les chiffres
# significatifs. On garde plutôt (n, moyenne, M2 = somme des carrés des écarts).


@dataclass(frozen=True)
class MeanVar:
    n: int
    mean: float
    m2: float

    @property
    def variance(self) -> float | None:
        return self.m2 / self.n if self.n else None


def mean_var_of(x: float) -> MeanVar:
    """Bonus 6.14 — un seul point."""
    raise NotImplementedError("S06 — à compléter")


def combine_mean_var(a: MeanVar, b: MeanVar) -> MeanVar:
    """Bonus 6.15 — formule de Chan : avec d = b.mean - a.mean et n = a.n + b.n,
    mean = a.mean + d * b.n / n ;  m2 = a.m2 + b.m2 + d² * a.n * b.n / n.
    Attention au cas n == 0."""
    raise NotImplementedError("S06 — à compléter")


MEAN_VAR: Monoid[MeanVar] = Monoid(MeanVar(0, 0.0, 0.0), combine_mean_var)


if __name__ == "__main__":  # pragma: no cover
    benchmark(*map(int, sys.argv[1:]))
