import math

from hypothesis import given
from hypothesis import strategies as st

from nimbus.s05_errors import load
from nimbus.s06_monoids import (
    MAXIMUM, MINIMUM, SUM, STATS, Monoid, Stats, concat_tuples, fold_map, fold_map_parallel,
    dict_monoid, stats_of, temperature_stats_by_station,
)

# Flottants « raisonnables » : l'addition flottante n'est associative qu'approximativement !
finite_floats = st.floats(min_value=-1e3, max_value=1e3, allow_nan=False)
stats = st.lists(finite_floats, max_size=20).map(lambda xs: fold_map(xs, stats_of, STATS))


def nearby(a: Stats, b: Stats) -> bool:
    return (a.n == b.n and math.isclose(a.total, b.total, abs_tol=1e-6)
            and math.isclose(a.sum_squares, b.sum_squares, rel_tol=1e-9, abs_tol=1e-6)
            and a.minimum == b.minimum and a.maximum == b.maximum)


@given(finite_floats, finite_floats, finite_floats)
def test_max_min_laws(a, b, c):
    for m in (MAXIMUM, MINIMUM):
        assert m.combine(m.empty, a) == a == m.combine(a, m.empty)
        assert m.combine(a, m.combine(b, c)) == m.combine(m.combine(a, b), c)


@given(st.lists(st.integers()), st.lists(st.integers()), st.lists(st.integers()))
def test_concat_laws(a, b, c):
    m: Monoid[tuple[int, ...]] = concat_tuples()
    a, b, c = tuple(a), tuple(b), tuple(c)
    assert m.combine(m.empty, a) == a == m.combine(a, m.empty)
    assert m.combine(a, m.combine(b, c)) == m.combine(m.combine(a, b), c)


@given(stats, stats, stats)
def test_stats_laws(a, b, c):
    assert nearby(STATS.combine(STATS.empty, a), a)
    assert nearby(STATS.combine(a, STATS.empty), a)
    assert nearby(STATS.combine(a, STATS.combine(b, c)), STATS.combine(STATS.combine(a, b), c))


def test_stats_values():
    s = fold_map([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0], stats_of, STATS)
    assert (s.n, s.average, s.variance, s.minimum, s.maximum) == (8, 5.0, 4.0, 2.0, 9.0)
    assert STATS.empty.average is None


@given(st.lists(st.integers(min_value=-1000, max_value=1000)), st.integers(min_value=1, max_value=8))
def test_parallel_equals_sequential(xs, n):
    assert fold_map_parallel(xs, float, SUM, n) == fold_map(xs, float, SUM)


def test_dict_monoid():
    m = dict_monoid(SUM)
    assert m.combine({"a": 1.0}, {"a": 2.0, "b": 3.0}) == {"a": 3.0, "b": 3.0}
    assert m.combine(m.empty, {"x": 1.0}) == {"x": 1.0}


def test_stats_by_station(csv_full):
    by_station = temperature_stats_by_station(load(csv_full).readings)
    assert set(by_station) == {"VELIZY", "BREST", "LYON"}
    assert all(-40 <= s.minimum <= s.maximum <= 50 for s in by_station.values())
