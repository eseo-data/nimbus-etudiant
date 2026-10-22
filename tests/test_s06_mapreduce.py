"""BD1, parties B et C : uv run pytest tests/test_s06_mapreduce.py"""

import math
import statistics

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from nimbus.datagen import generate_massive_lines
from nimbus.s06_legacy_mapreduce import monthly_report as legacy_report
from nimbus.s06_mapreduce import (
    MEAN_VAR, MeanVar, Shard, combine_mean_var, map_reduce, map_shard, mean_var_of, monthly_report,
    monthly_stats, parse_line, shard_lines,
)
from nimbus.s06_monoids import fold_map

LINES = list(generate_massive_lines(1, 6, 365))


def test_parse_line():
    assert parse_line("2016-03-02,ST0001,4.5,80,1010,5,0") == (("ST0001", "2016-03"), 4.5)
    assert parse_line("2016-03-02,ST0001,NA,80,1010,5,0") is None
    assert parse_line("2016-03-02,ST0001,999.9,80,1010,5,0") is None
    assert parse_line("2016/03/02,ST0001,4.5,80,1010,5,0") is None
    assert parse_line("2016-03-02,ST0001,4.5") is None


def reference():
    groups: dict = {}
    for line in LINES[1:]:
        p = parse_line(line)
        if p:
            groups.setdefault(p[0], []).append(round(p[1] * 10))
    return [f"{st} {m} n={len(ts)} mean={sum(ts) / len(ts) / 10:.2f} max={max(ts) / 10:.1f}"
            for (st, m), ts in sorted(groups.items())]


def test_le_legacy_depend_du_nombre_de_workers():
    assert legacy_report(LINES, 1) != legacy_report(LINES, 4)


@pytest.mark.parametrize("workers", [1, 2, 3, 4, 7, 8])
def test_rapport_identique_quel_que_soit_le_decoupage(workers):
    assert monthly_report(LINES, workers) == reference()


def test_le_legacy_se_trompe_sur_max_meme_avec_un_worker():
    """max démarre à 0.0 au lieu de l'élément neutre -inf : faux dès que tout le mois est < 0."""
    def maxima(lines):
        return {tuple(line.split()[:2]): line.rsplit("max=", 1)[1] for line in lines}

    ref, legacy = maxima(reference()), maxima(legacy_report(LINES, 1))
    wrong = [k for k in ref if legacy[k] != ref[k]]
    assert wrong and all(legacy[k] == "0.0" and ref[k].startswith("-") for k in wrong)


def test_monthly_stats_cles():
    stats = monthly_stats(LINES, 3)
    assert ("ST0001", "2016-01") in stats
    assert all(s.n >= 1 and s.total == int(s.total) for s in stats.values())   # dixièmes entiers


def test_map_shard_prefixe_et_contenu():
    s = Shard(2, 3, 60)
    stats = map_shard(s)
    assert {st.split("-")[0] for st in stats} == {"R02"}
    n_valid = sum(1 for line in shard_lines(s) if parse_line(line) is not None)
    assert sum(x.n for x in stats.values()) == n_valid


def test_map_reduce_independant_du_nombre_de_processus():
    shards = [Shard(i, 3, 120) for i in range(4)]
    one = map_reduce(shards, 1)
    assert map_reduce(shards, 4) == one
    assert len(one) >= 12


# ---------------------------------------------------------------------------
# Bonus
# ---------------------------------------------------------------------------

floats = st.floats(min_value=-1e3, max_value=1e3, allow_nan=False)
mvs = st.lists(floats, max_size=20).map(lambda xs: fold_map(xs, mean_var_of, MEAN_VAR))


def close(a: MeanVar, b: MeanVar) -> bool:
    return a.n == b.n and math.isclose(a.mean, b.mean, abs_tol=1e-6) and math.isclose(a.m2, b.m2, rel_tol=1e-6, abs_tol=1e-6)


@settings(deadline=None)
@given(mvs, mvs, mvs)
def test_bonus_lois_mean_var(a, b, c):
    e = MEAN_VAR.empty
    assert close(combine_mean_var(e, a), a) and close(combine_mean_var(a, e), a)
    assert close(combine_mean_var(a, combine_mean_var(b, c)), combine_mean_var(combine_mean_var(a, b), c))


def test_bonus_stabilite_numerique():
    from nimbus.s06_monoids import STATS, stats_of
    xs = [1e9 + (i % 7) * 0.1 for i in range(10_000)]
    exact = statistics.pvariance(xs)
    naive = fold_map(xs, stats_of, STATS).variance
    stable = fold_map(xs, mean_var_of, MEAN_VAR).variance
    assert not math.isclose(naive, exact, rel_tol=1e-3)          # la formule naïve se trompe
    assert math.isclose(stable, exact, rel_tol=1e-6)
