from nimbus.s03_algebraic_types import Outlier
from nimbus.s05_errors import (
    Failures, Err, Ok, Success, load, combine, attempt, traverse, validate, validate_line,
)


def inverse(x: float):
    return Err("division par zéro") if x == 0 else Ok(1 / x)


def test_functor_and_monad():
    assert Ok(2).map(lambda x: x + 1) == Ok(3)
    assert Err("e").map(lambda x: x + 1) == Err("e")
    assert Ok(4).flat_map(inverse) == Ok(0.25)
    assert Ok(0).flat_map(inverse).map(lambda x: x * 2) == Err("division par zéro")


def test_functor_laws():
    for r in (Ok(3), Err("x")):
        assert r.map(lambda x: x) == r
        f, g = (lambda x: x + 1), (lambda x: x * 2)
        assert r.map(f).map(g) == r.map(lambda x: g(f(x)))


def test_attempt():
    assert attempt(lambda: int("42")) == Ok(42)
    r = attempt(lambda: int("quarante"))
    assert isinstance(r, Err) and r.error.startswith("ValueError")


def test_traverse_stops_at_first_failure():
    assert traverse([1, 2, 4], inverse) == Ok([1.0, 0.5, 0.25])
    assert traverse([1, 0, 0], inverse) == Err("division par zéro")


def test_combine_accumulates():
    assert combine(Success(1), Success("a")) == Success((1, "a"))
    assert combine(validate(False, 1, "e1"), Success(2), validate(False, 3, "e2")) == Failures(("e1", "e2"))


def test_validate_line():
    ok = validate_line("2025-01-01,BREST,10,80,1010,5,0".split(","))
    assert isinstance(ok, Success) and ok.value.station == "BREST"
    # une mesure aberrante ne fait PAS échouer la ligne
    ab = validate_line("2025-01-01,BREST,999,80,1010,5,0".split(","))
    assert isinstance(ab, Success) and isinstance(ab.value.temperature_c, Outlier)
    # deux erreurs structurelles sont TOUTES les deux signalées
    ko = validate_line("2025/01/01,ATLANTIS,10,80,1010,5,0".split(","))
    assert isinstance(ko, Failures) and len(ko.errors) == 2
    assert validate_line(["a", "b"]) == Failures(("attendu 7 colonnes, reçu 2",))


def test_load(csv_full):
    ch = load(csv_full)
    assert len(ch.readings) + len(ch.rejected) == 3 * 365
    assert len(ch.rejected) > 0
    assert all(n >= 2 for n, _ in ch.rejected)
