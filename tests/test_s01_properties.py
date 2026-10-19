"""BONUS séance 1 — vos premiers tests de propriétés (Hypothesis).

Au lieu d'écrire des exemples à la main, on énonce une PROPRIÉTÉ vraie pour toutes
les entrées, et Hypothesis cherche un contre-exemple (puis le simplifie).
Ce n'est possible que parce que les fonctions testées sont pures.

Remplacez chaque `pytest.skip(...)` par le corps du test.
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from nimbus.s01_purity import celsius_to_fahrenheit, filter_plausible, shuffle, normalize

finite_floats = st.floats(min_value=-1e6, max_value=1e6, allow_nan=False)


@given(st.lists(finite_floats))
def test_normalize_stays_in_0_1(xs):
    """P1 — toute valeur normalisée est dans [0, 1], et la longueur est conservée."""
    pytest.skip("P1 à écrire")


@given(st.lists(finite_floats))
def test_filter_is_idempotent(xs):
    """P2 — filtrer deux fois revient à filtrer une fois."""
    pytest.skip("P2 à écrire")


@given(finite_floats, finite_floats)
def test_fahrenheit_is_increasing(a, b):
    """P3 — la conversion préserve l'ordre : a <= b  =>  F(a) <= F(b)."""
    pytest.skip("P3 à écrire")


@given(st.lists(st.integers()), st.integers(min_value=0, max_value=2**64 - 1))
def test_shuffle_is_a_permutation(xs, seed):
    """P4 — mélanger ne perd ni n'invente aucun élément, quelle que soit la graine."""
    pytest.skip("P4 à écrire")
