"""Défi BD1 (facultatif) : uv run pytest tests/test_s06_challenge_hll.py"""

import time

from hypothesis import given, settings
from hypothesis import strategies as st

from nimbus.s06_challenge_hll import HLL_MONOID, M, P, combine_hll, estimate, hll_of
from nimbus.s06_monoids import fold_map, fold_map_parallel

sketches = st.lists(st.text(max_size=6), max_size=30).map(lambda xs: fold_map(xs, hll_of, HLL_MONOID))


def test_un_element():
    h = hll_of("VELIZY")
    assert len(h.registers) == M == 1 << P
    assert sum(1 for r in h.registers if r) == 1
    assert 1 <= max(h.registers) <= 64 - P + 1
    assert hll_of("VELIZY") == h                       # déterministe


@settings(max_examples=60, deadline=None)
@given(sketches, sketches, sketches)
def test_lois_du_monoid_et_idempotence(a, b, c):
    e = HLL_MONOID.empty
    assert combine_hll(e, a) == a == combine_hll(a, e)
    assert combine_hll(a, combine_hll(b, c)) == combine_hll(combine_hll(a, b), c)
    assert combine_hll(a, b) == combine_hll(b, a)
    assert combine_hll(a, a) == a                      # les doublons ne comptent pas


@settings(max_examples=30, deadline=None)
@given(st.lists(st.text(max_size=5), max_size=40), st.lists(st.text(max_size=5), max_size=40))
def test_fusion_egale_sketch_de_l_union(xs, ys):
    a, b = fold_map(xs, hll_of, HLL_MONOID), fold_map(ys, hll_of, HLL_MONOID)
    assert combine_hll(a, b) == fold_map(xs + ys, hll_of, HLL_MONOID)


def test_estimation_petits_et_grands_effectifs():
    assert estimate(HLL_MONOID.empty) == 0
    small = fold_map([f"x{i}" for i in range(100)], hll_of, HLL_MONOID)
    assert abs(estimate(small) - 100) <= 3
    big = fold_map_parallel([f"user-{i}" for i in range(60_000)], hll_of, HLL_MONOID, 4)
    assert abs(estimate(big) - 60_000) / 60_000 < 0.05


def test_doublons_ignores():
    xs = [f"s{i % 500}" for i in range(20_000)]        # 500 distincts, répétés 40 fois
    assert abs(estimate(fold_map(xs, hll_of, HLL_MONOID)) - 500) / 500 < 0.05
