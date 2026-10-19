import itertools
import operator

from nimbus.s02_higher_order import (
    compose, curry2, split_csv, sliding_windows, memoize, moving_average, my_filter, my_map,
    my_reduce, pipe, take,
)


def inc(x): return x + 1
def double(x): return x * 2


def test_compose_and_pipe():
    assert compose(inc, double)(3) == 7       # inc(double(3))
    assert pipe(3, inc, double) == 8          # double(inc(3))
    assert compose()(42) == 42


def test_curry2():
    assert curry2(operator.sub)(10)(3) == 7


def test_lazy_map_filter_on_infinite():
    pairs_doubles = my_map(double, my_filter(lambda x: x % 2 == 0, itertools.count()))
    assert take(3, pairs_doubles) == [0, 4, 8]


def test_reduce():
    assert my_reduce(operator.add, [1, 2, 3], 10) == 16
    assert my_reduce(lambda acc, x: acc + [x], "abc", []) == ["a", "b", "c"]


def test_sliding_windows_and_moving_average():
    assert list(sliding_windows([1, 2, 3, 4], 2)) == [(1, 2), (2, 3), (3, 4)]
    assert list(moving_average([1.0, 2.0, 3.0, 4.0], 3)) == [2.0, 3.0]
    assert take(2, sliding_windows(itertools.count(), 3)) == [(0, 1, 2), (1, 2, 3)]


def test_memoize_calls_once():
    calls = []
    f = memoize(lambda x: calls.append(x) or x * x)
    assert f(4) == 16 and f(4) == 16
    assert calls == [4]


def test_split_csv(csv_small):
    lines = list(split_csv(csv_small))
    assert lines[0][0] == "2025-01-01"
    assert all(isinstance(l, list) for l in lines)
    assert len(lines) == 3 * 60
