"""Tests du défi (facultatif). Lancer : uv run pytest tests/test_s01_challenge_vector.py"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from nimbus.s01_challenge_vector import (
    BITS, EMPTY, Vector, append, from_iterable, lookup, depth, update, pop_last,
    to_tuple,
)


def nodes(v: Vector) -> dict[int, tuple]:
    """Tous les nœuds internes et feuilles de l'arbre, indexés par identité."""
    seen_set: dict[int, tuple] = {}

    def visit(n, level):
        seen_set[id(n)] = n
        if level > 0:
            for e in n:
                visit(e, level - BITS)

    if v.size:
        visit(v.root, v.offset)
    return seen_set


def invariants(v: Vector) -> None:
    def check(n, level):
        assert isinstance(n, tuple) and 0 < len(n) <= 1 << BITS
        if level > 0:
            for e in n:
                check(e, level - BITS)

    if v.size == 0:
        assert v.root == ()
        return
    check(v.root, v.offset)
    if v.offset > 0:
        assert len(v.root) >= 2, "une racine à un seul enfant doit être aplatie"
    assert v.size <= 1 << (v.offset + BITS)


@pytest.mark.parametrize("n", [0, 1, 31, 32, 33, 1023, 1024, 1025, 40_000])
def test_from_iterable_and_to_tuple(n):
    v = from_iterable(range(n))
    assert len(v) == n
    assert to_tuple(v) == tuple(range(n))
    invariants(v)


def test_lookup():
    v = from_iterable(range(1100))
    assert all(lookup(v, i) == i for i in range(1100))
    with pytest.raises(IndexError):
        lookup(v, 1100)
    with pytest.raises(IndexError):
        lookup(EMPTY, 0)


def test_logarithmic_height():
    assert depth(from_iterable(range(32))) == 1
    assert depth(from_iterable(range(33))) == 2
    assert depth(from_iterable(range(32 ** 2 + 1))) == 3


def test_update_is_persistent():
    v1 = from_iterable(range(100))
    v2 = update(v1, 50, "x")
    assert lookup(v2, 50) == "x" and lookup(v1, 50) == 50
    assert to_tuple(v1) == tuple(range(100))


@pytest.mark.parametrize("operation", ["update", "append", "pop_last"])
def test_structural_sharing(operation):
    v1 = from_iterable(range(40_000))                       # 4 niveaux
    v2 = {"update": lambda: update(v1, 12_345, -1),
          "append": lambda: append(v1, -1),
          "pop_last": lambda: pop_last(v1)}[operation]()
    olds, new_items = nodes(v1), nodes(v2)
    created = set(new_items) - set(olds)
    assert len(created) <= depth(v1) + 1, \
        f"{len(created)} nœuds recréés : le chemin seul doit être recopié"
    assert len(new_items) - len(created) > 1000, "l'essentiel de l'arbre doit être partagé"


def test_pop_last():
    v = from_iterable(range(33))
    v = pop_last(v)
    assert to_tuple(v) == tuple(range(32)) and v.offset == 0
    invariants(v)
    assert pop_last(from_iterable([1])) == EMPTY
    with pytest.raises(IndexError):
        pop_last(EMPTY)


operations = st.lists(
    st.one_of(
        st.tuples(st.just("append"), st.integers()),
        st.tuples(st.just("update"), st.integers(min_value=0), st.integers()),
        st.just(("remove",)),
    ),
    max_size=120,
)


@settings(max_examples=150, deadline=None)
@given(st.integers(min_value=0, max_value=2_100), operations)
def test_equivalent_to_tuple_model(n_initial, ops):
    """Le vecteur se comporte exactement comme un tuple, quelle que soit la séquence d'opérations."""
    v, model = from_iterable(range(n_initial)), tuple(range(n_initial))
    for op in ops:
        if op[0] == "append":
            v, model = append(v, op[1]), (*model, op[1])
        elif op[0] == "update" and model:
            i = op[1] % len(model)
            v, model = update(v, i, op[2]), (*model[:i], op[2], *model[i + 1:])
        elif op[0] == "remove" and model:
            v, model = pop_last(v), model[:-1]
        assert len(v) == len(model)
    assert to_tuple(v) == model
    invariants(v)
