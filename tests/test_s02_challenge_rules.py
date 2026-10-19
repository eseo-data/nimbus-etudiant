"""Défi bloc 2 (facultatif) : uv run pytest tests/test_s02_challenge_rules.py"""

from hypothesis import given, settings
from hypothesis import strategies as st

from nimbus.s02_challenge_rules import (
    BOUNDS, Comparison, And, Parsed, Not, Or, Failed, render, alternative, parse, chain_left,
    evaluate, literal, pattern, sequence, fmap,
)
from nimbus.s03_algebraic_types import parse_reading

C = lambda v, o, x: Comparison(v, o, float(x))  # noqa: E731


def test_literal_and_pattern():
    assert literal("and")("  and x", 0) == Parsed("and", 5)
    assert literal("and")("or", 0) == Failed(0, "'and'")
    assert pattern(r"[0-9]+", "integer")(" 42a", 0) == Parsed("42", 3)
    assert pattern(r"[0-9]+", "integer")("abc", 0) == Failed(0, "integer")


def test_fmap_sequence_alternative():
    integer = fmap(pattern(r"[0-9]+", "integer"), int)
    assert integer("12", 0) == Parsed(12, 2)
    assert sequence(integer, literal("+"), integer)("1 + 2", 0) == Parsed((1, "+", 2), 5)
    assert sequence(integer, literal("+"))("1 - 2", 0) == Failed(2, "'+'")
    p = alternative(sequence(literal("a"), literal("b"), literal("c")), sequence(literal("a"), literal("x")))
    assert p("a b d", 0) == Failed(4, "'c'")            # l'échec le plus lointain


def test_chain_left_is_left_associative():
    integer = fmap(pattern(r"[0-9]+", "integer"), lambda s: C("wind_kmh", ">", s))
    p = chain_left(integer, literal("or"), Or)
    assert p("1 or 2 or 3", 0) == Parsed(Or(Or(C("wind_kmh", ">", 1), C("wind_kmh", ">", 2)), C("wind_kmh", ">", 3)), 11)


def test_precedence_and_parentheses():
    a, b, c = C("wind_kmh", ">", 60), C("rain_mm", ">=", 10), C("temperature_c", "<", 0)
    assert parse("wind_kmh > 60 or rain_mm >= 10 and temperature_c < 0") == Or(a, And(b, c))
    assert parse("(wind_kmh > 60 or rain_mm >= 10) and temperature_c < 0") == And(Or(a, b), c)
    assert parse("not not wind_kmh > 60") == Not(Not(a))
    assert parse("  temperature_c >= -5.5  ") == C("temperature_c", ">=", -5.5)


def test_errors():
    assert isinstance(parse("wind_kmh >"), Failed)
    assert parse("wind_kmh > 60 and") == Failed(14, "end of rule")   # « and » sans suite n'est pas consommé
    r = parse("wind_kmh > 60 xyz")
    assert isinstance(r, Failed) and r.position == 14
    assert isinstance(parse("speed > 3"), Failed)
    assert isinstance(parse("order > 3"), Failed)        # "or" n'est pas un préfixe de variable


def _reading():
    return parse_reading("2025-07-01", "LYON", {"temperature_c": "31", "humidity_pct": "40",
                                                "pressure_hpa": "1012", "wind_kmh": "NA", "rain_mm": "0"})


def test_evaluate():
    READING = _reading()
    assert evaluate(parse("temperature_c >= 30"), READING)
    assert not evaluate(parse("wind_kmh > 0"), READING)          # mesure manquante -> faux
    assert evaluate(parse("not wind_kmh > 0"), READING)
    assert evaluate(parse("temperature_c > 40 or (rain_mm == 0 and humidity_pct < 50)"), READING)


variables = st.sampled_from(sorted(BOUNDS))
comparators = st.sampled_from([">=", "<=", "==", "!=", ">", "<"])
vals = st.floats(min_value=-500, max_value=500, allow_nan=False).map(lambda x: round(x, 3))
leaves = st.builds(Comparison, variables, comparators, vals)
trees = st.recursive(leaves, lambda subtree: st.one_of(
    st.builds(And, subtree, subtree), st.builds(Or, subtree, subtree), st.builds(Not, subtree)), max_leaves=12)


@settings(max_examples=200, deadline=None)
@given(trees)
def test_round_trip(e):
    assert parse(render(e)) == e
