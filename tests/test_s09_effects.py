import pytest

from nimbus.app import analyze, analyze_full, program
from nimbus.datagen import generate_csv
from nimbus.s05_errors import Err, Ok, load
from nimbus.s09_effects import (
    Services, failure, execute, for_each, success, suspend,
)


def test_a_program_is_a_value():
    log_entries = []
    p = suspend(lambda: log_entries.append("effet!"))
    assert log_entries == []                   # construire n'exécute rien
    execute(p)
    execute(p)
    assert log_entries == ["effet!", "effet!"]  # on peut l'exécuter plusieurs fois


def test_map_zip_tap():
    assert execute(success(2).map(lambda x: x * 10)) == Ok(20)
    assert execute(success(1).zip(success("a"))) == Ok((1, "a"))
    seen = []
    assert execute(success(3).tap(lambda x: suspend(lambda: seen.append(x)))) == Ok(3)
    assert seen == [3]


def test_failures_and_recovery():
    boom = suspend(lambda: 1 / 0)
    r = execute(boom.map(lambda x: x + 1))
    assert isinstance(r, Err) and isinstance(r.error, ZeroDivisionError)
    assert execute(boom.or_else(success(0))) == Ok(0)
    assert execute(failure(ValueError("x")).catch_all(lambda e: success(str(e)))) == Ok("x")


def test_retry_flaky_sensor():
    attempts = []

    def sensor():
        attempts.append(1)
        if len(attempts) < 3:
            raise IOError("capteur muet")
        return 21.5

    assert execute(suspend(sensor).retry(5)) == Ok(21.5)
    assert len(attempts) == 3
    attempts.clear()
    assert isinstance(execute(suspend(sensor).retry(1)), Err)


def test_stack_safe():
    p = success(0)
    for _ in range(50_000):
        p = p.flat_map(lambda x: success(x + 1))
    assert execute(p) == Ok(50_000)
    assert execute(for_each(range(1000), lambda i: success(i * i))).value[-1] == 999 * 999


def test_full_program_with_fake_services():
    filepaths = {"in.csv": generate_csv(n_days=120)}
    console = []
    s = Services(read=filepaths.__getitem__, save=filepaths.__setitem__, display=console.append)
    r = execute(program(s, "in.csv", "out.txt"))
    assert isinstance(r, Ok)
    assert "Rapport Nimbus" in filepaths["out.txt"]
    assert console[0].startswith("Chargé")


def test_missing_file_handled_cleanly():
    console = []
    s = Services(read={}.__getitem__, save=lambda p, c: None, display=console.append)
    assert execute(program(s, "absent.csv", "out.txt")) == Ok("")
    assert console[-1].startswith("Échec")


def test_analyze_is_pure():
    ch = load(generate_csv(n_days=90))
    assert analyze(ch) == analyze(ch)


def test_core_report_without_big_data_dependency():
    report = analyze(load(generate_csv(n_days=60)))
    assert "Température par station" in report and "JAX" not in report


def test_full_program_big_data():
    pytest.importorskip("jax")
    filepaths = {"in.csv": generate_csv(n_days=200)}
    s = Services(read=filepaths.__getitem__, save=filepaths.__setitem__, display=lambda m: None)
    assert isinstance(execute(program(s, "in.csv", "out.txt", analyze_full)), Ok)
    assert "Régression logistique (JAX)" in filepaths["out.txt"]
    assert "monoid Stats" in filepaths["out.txt"]
