import operator

from nimbus.s03_algebraic_types import Outlier, Missing, Valid
from nimbus.s04_recursion import (
    EMPTY, Cons, fill_gaps, from_iterable, fold_left, fold_right, reverse, length, map_list,
    scan_left, sum_trampoline, to_python_list,
)


def test_length():
    assert length(EMPTY) == 0
    assert length(from_iterable([1, 2, 3])) == 3


def test_folds():
    l = from_iterable(["a", "b", "c"])
    assert fold_left(l, "", operator.add) == "abc"
    assert fold_right(l, "", operator.add) == "abc"
    assert fold_left(from_iterable([1, 2, 3]), 0, operator.sub) == -6        # ((0-1)-2)-3
    assert fold_right(from_iterable([1, 2, 3]), 0, operator.sub) == 2        # 1-(2-(3-0))


def test_reverse_and_map():
    assert to_python_list(reverse(from_iterable([1, 2, 3]))) == [3, 2, 1]
    assert to_python_list(map_list(from_iterable([1, 2, 3]), lambda x: x * 10)) == [10, 20, 30]


def test_structural_sharing():
    queue = from_iterable([2, 3])
    l1, l2 = Cons(1, queue), Cons(0, queue)
    assert l1.queue is l2.queue     # rien n'a été copié


def test_scan_and_fill():
    assert scan_left([1, 2, 3], 0, operator.add) == [0, 1, 3, 6]
    ms = [Missing(), Valid(1.0), Missing(), Outlier("x", "y"), Valid(4.0)]
    assert fill_gaps(ms) == [None, 1.0, 1.0, 1.0, 4.0]


def test_trampoline_does_not_overflow():
    large = from_iterable(range(100_000))
    assert sum_trampoline(large) == sum(range(100_000))
