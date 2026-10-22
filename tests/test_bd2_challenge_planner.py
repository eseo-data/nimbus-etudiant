"""Défi BD2 (facultatif) : uv run pytest tests/test_bd2_challenge_planner.py"""

from hypothesis import given, settings
from hypothesis import strategies as st

from nimbus.bd2_challenge_planner import (
    And, Eq, Filter, Gt, Project, Scan, columns_read, execute, holds, optimize, output_columns,
    pred_columns, prune, push_down,
)

COLS = ("a", "b", "c", "d", "e")
TABLE = [{"a": 1.0, "b": "x", "c": 5.0}, {"a": 3.0, "b": "y", "c": None}, {"a": None, "b": "x", "c": 9.0}]


def test_holds_et_colonnes():
    p = And(Gt("a", 2.0), Eq("b", "y"))
    assert pred_columns(p) == {"a", "b"}
    assert [holds(p, r) for r in TABLE] == [False, True, False]
    assert not holds(Gt("c", 0.0), TABLE[1])                 # None : faux


def test_execute():
    plan = Project(("a",), Filter(Gt("c", 4.0), Scan(("a", "b", "c"))))
    assert execute(plan, TABLE) == [{"a": 1.0}, {"a": None}]


def test_push_down_et_prune_sur_un_exemple():
    plan = Project(("a",), Filter(Gt("c", 4.0), Scan(("a", "b", "c"))))
    assert push_down(plan) == Project(("a",), Scan(("a", "b", "c"), Gt("c", 4.0)))
    assert optimize(plan) == Project(("a",), Scan(("a",), Gt("c", 4.0)))
    assert columns_read(optimize(plan)) == {"a", "c"}        # b n'est plus lu


def test_filtres_empiles():
    plan = Filter(Eq("b", "x"), Filter(Gt("a", 0.0), Scan(COLS)))
    assert push_down(plan) == Scan(COLS, And(Gt("a", 0.0), Eq("b", "x")))


# ---------------------------------------------------------------------------
# Propriétés : plans valides et tables aléatoires
# ---------------------------------------------------------------------------

values = st.one_of(st.none(), st.floats(-5, 5, allow_nan=False), st.sampled_from(["x", "y"]))
tables = st.lists(st.fixed_dictionaries({c: values for c in COLS}), max_size=12)


def preds(cols):
    leaf = st.one_of(
        st.builds(Gt, st.sampled_from(cols), st.floats(-5, 5, allow_nan=False)),
        st.builds(Eq, st.sampled_from(cols), st.one_of(st.sampled_from(["x", "y"]), st.floats(-5, 5, allow_nan=False))),
    )
    return st.recursive(leaf, lambda sub: st.builds(And, sub, sub), max_leaves=3)


@st.composite
def plans(draw, depth=0):
    if depth >= 4 or draw(st.booleans()) and depth > 0:
        cols = tuple(draw(st.lists(st.sampled_from(COLS), min_size=1, unique=True)))
        return Scan(cols, draw(st.none() | preds(cols)))
    child = draw(plans(depth + 1))
    cols = output_columns(child)
    if draw(st.booleans()):
        return Filter(draw(preds(cols)), child)
    sub = tuple(draw(st.lists(st.sampled_from(cols), min_size=1, unique=True)))
    return Project(sub, child)


def has_filter(plan):
    match plan:
        case Filter():
            return True
        case Project(_, child):
            return has_filter(child)
        case _:
            return False


@settings(max_examples=300, deadline=None)
@given(plans(), tables)
def test_push_down_preserve_le_resultat_et_retire_les_filtres(plan, table):
    p = push_down(plan)
    assert not has_filter(p)
    assert execute(p, table) == execute(plan, table)


@settings(max_examples=300, deadline=None)
@given(plans(), tables)
def test_optimize_preserve_le_resultat_et_lit_moins(plan, table):
    o = optimize(plan)
    assert execute(o, table) == execute(plan, table)
    assert columns_read(o) <= columns_read(push_down(plan))
    assert output_columns(o) == output_columns(plan)


@settings(max_examples=200, deadline=None)
@given(plans())
def test_prune_est_idempotent(plan):
    o = optimize(plan)
    assert prune(o) == o
