import itertools
import operator

from nimbus.s02_ordre_superieur import (
    compose, curry2, decouper_csv, fenetres, memoiser, moyenne_mobile, mon_filter, mon_map,
    mon_reduce, pipe, prendre,
)


def inc(x): return x + 1
def double(x): return x * 2


def test_compose_et_pipe():
    assert compose(inc, double)(3) == 7       # inc(double(3))
    assert pipe(3, inc, double) == 8          # double(inc(3))
    assert compose()(42) == 42


def test_curry2():
    assert curry2(operator.sub)(10)(3) == 7


def test_map_filter_paresseux_sur_infini():
    pairs_doubles = mon_map(double, mon_filter(lambda x: x % 2 == 0, itertools.count()))
    assert prendre(3, pairs_doubles) == [0, 4, 8]


def test_reduce():
    assert mon_reduce(operator.add, [1, 2, 3], 10) == 16
    assert mon_reduce(lambda acc, x: acc + [x], "abc", []) == ["a", "b", "c"]


def test_fenetres_et_moyenne_mobile():
    assert list(fenetres([1, 2, 3, 4], 2)) == [(1, 2), (2, 3), (3, 4)]
    assert list(moyenne_mobile([1.0, 2.0, 3.0, 4.0], 3)) == [2.0, 3.0]
    assert prendre(2, fenetres(itertools.count(), 3)) == [(0, 1, 2), (1, 2, 3)]


def test_memoiser_appelle_une_seule_fois():
    appels = []
    f = memoiser(lambda x: appels.append(x) or x * x)
    assert f(4) == 16 and f(4) == 16
    assert appels == [4]


def test_decouper_csv(csv_petit):
    lignes = list(decouper_csv(csv_petit))
    assert lignes[0][0] == "2025-01-01"
    assert all(isinstance(l, list) for l in lignes)
    assert len(lignes) == 3 * 60
