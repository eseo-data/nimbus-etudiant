import math

from hypothesis import given
from hypothesis import strategies as st

from nimbus.s05_erreurs import charger
from nimbus.s06_monoides import (
    MAXIMUM, MINIMUM, SOMME, STATS, Monoide, Stats, concat_tuples, fold_map, fold_map_parallele,
    monoide_dict, stats_de, stats_temperature_par_station,
)

# Flottants « raisonnables » : l'addition flottante n'est associative qu'approximativement !
flottants = st.floats(min_value=-1e3, max_value=1e3, allow_nan=False)
stats = st.lists(flottants, max_size=20).map(lambda xs: fold_map(xs, stats_de, STATS))


def proches(a: Stats, b: Stats) -> bool:
    return (a.n == b.n and math.isclose(a.somme, b.somme, abs_tol=1e-6)
            and math.isclose(a.somme_carres, b.somme_carres, rel_tol=1e-9, abs_tol=1e-6)
            and a.mini == b.mini and a.maxi == b.maxi)


@given(flottants, flottants, flottants)
def test_max_min_lois(a, b, c):
    for m in (MAXIMUM, MINIMUM):
        assert m.combiner(m.vide, a) == a == m.combiner(a, m.vide)
        assert m.combiner(a, m.combiner(b, c)) == m.combiner(m.combiner(a, b), c)


@given(st.lists(st.integers()), st.lists(st.integers()), st.lists(st.integers()))
def test_concat_lois(a, b, c):
    m: Monoide[tuple[int, ...]] = concat_tuples()
    a, b, c = tuple(a), tuple(b), tuple(c)
    assert m.combiner(m.vide, a) == a == m.combiner(a, m.vide)
    assert m.combiner(a, m.combiner(b, c)) == m.combiner(m.combiner(a, b), c)


@given(stats, stats, stats)
def test_stats_lois(a, b, c):
    assert proches(STATS.combiner(STATS.vide, a), a)
    assert proches(STATS.combiner(a, STATS.vide), a)
    assert proches(STATS.combiner(a, STATS.combiner(b, c)), STATS.combiner(STATS.combiner(a, b), c))


def test_stats_valeurs():
    s = fold_map([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0], stats_de, STATS)
    assert (s.n, s.moyenne, s.variance, s.mini, s.maxi) == (8, 5.0, 4.0, 2.0, 9.0)
    assert STATS.vide.moyenne is None


@given(st.lists(st.integers(min_value=-1000, max_value=1000)), st.integers(min_value=1, max_value=8))
def test_parallele_egal_sequentiel(xs, n):
    assert fold_map_parallele(xs, float, SOMME, n) == fold_map(xs, float, SOMME)


def test_monoide_dict():
    m = monoide_dict(SOMME)
    assert m.combiner({"a": 1.0}, {"a": 2.0, "b": 3.0}) == {"a": 3.0, "b": 3.0}
    assert m.combiner(m.vide, {"x": 1.0}) == {"x": 1.0}


def test_stats_par_station(csv_complet):
    par_station = stats_temperature_par_station(charger(csv_complet).releves)
    assert set(par_station) == {"VELIZY", "BREST", "LYON"}
    assert all(-40 <= s.mini <= s.maxi <= 50 for s in par_station.values())
