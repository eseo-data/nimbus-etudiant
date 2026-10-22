"""BD1 — DÉFI ★★★ (facultatif) : HyperLogLog, un monoid pour compter les éléments distincts.

Compter exactement les valeurs distinctes demande de les garder toutes en mémoire
(un set). HyperLogLog (Flajolet et al., 2007) estime ce nombre avec m petits
registres, soit quelques kilo-octets, avec une erreur relative d'environ 1,04 / √m.
Spark l'utilise pour `approx_count_distinct`, Redis pour PFCOUNT, BigQuery pour
APPROX_COUNT_DISTINCT.

Le point qui nous intéresse : deux sketches se fusionnent par un max registre par
registre. C'est un monoid (et même un semilattice : la fusion est idempotente).
On peut donc compter les distincts en parallèle avec `fold_map_parallel`, ou dans
un MapReduce, sans jamais rassembler les données.

Principe : on hache chaque élément sur 64 bits. Les P premiers bits choisissent un
registre (m = 2**P registres). Dans les 64 - P bits restants, on compte la position
du premier bit à 1 en partant de la gauche (rang = nombre de zéros en tête + 1).
Chaque registre garde le plus grand rang observé. Un rang de k a une probabilité
2**-k : voir un grand rang indique beaucoup d'éléments distincts.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

from nimbus.s06_monoids import Monoid

P = 12                      # 4096 registres : erreur type ≈ 1,6 %
M = 1 << P
ALPHA = 0.7213 / (1 + 1.079 / M)


def hash64(x: str) -> int:
    """Fourni : hachage 64 bits déterministe (hash() de Python change à chaque exécution)."""
    return int.from_bytes(hashlib.blake2b(x.encode(), digest_size=8).digest(), "big")


@dataclass(frozen=True)
class HLL:
    registers: tuple[int, ...]       # longueur M


def hll_of(x: str) -> HLL:
    """D1 ★★ — le sketch d'un seul élément : tous les registres à 0 sauf un.

    index = les P bits de poids fort de hash64(x) ; w = les 64 - P bits restants ;
    rang = (64 - P) - w.bit_length() + 1.
    """
    raise NotImplementedError("S06 — à compléter")


def combine_hll(a: HLL, b: HLL) -> HLL:
    """D2 ★★ — fusion : maximum registre par registre."""
    raise NotImplementedError("S06 — à compléter")


HLL_MONOID: Monoid[HLL] = Monoid(HLL((0,) * M), combine_hll)


def estimate(h: HLL) -> float:
    """D3 ★★★ — estimation du nombre d'éléments distincts.

    E = ALPHA * M² / Σ 2**(-registre).
    Correction pour les petits effectifs : si E <= 2,5 M et qu'il reste V registres à 0,
    renvoyer M * ln(M / V) (linear counting).
    """
    raise NotImplementedError("S06 — à compléter")
