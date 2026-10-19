import dataclasses

import pytest

from nimbus.s01_purity import (
    Reading, append, celsius_to_fahrenheit, correct_temperature, filter_plausible,
    average, clean_pure, normalize,
)

R = Reading("2025-01-01", "VELIZY", 10.0, 80.0)


def test_fahrenheit():
    assert celsius_to_fahrenheit(0) == 32
    assert celsius_to_fahrenheit(100) == 212


def test_filter_does_not_mutate_input():
    input_data = [10.0, 999.0, 12.0]
    assert filter_plausible(input_data) == (10.0, 12.0)
    assert input_data == [10.0, 999.0, 12.0]


def test_average():
    assert average([1.0, 2.0, 3.0]) == 2.0
    assert average([]) is None


def test_normalize():
    assert normalize([0.0, 5.0, 10.0]) == (0.0, 0.5, 1.0)
    assert normalize([3.0, 3.0]) == (0.0, 0.0)
    assert normalize([]) == ()


def test_reading_is_immutable():
    with pytest.raises(dataclasses.FrozenInstanceError):
        R.temperature_c = 0  # type: ignore[misc]


def test_correct_returns_a_new_reading():
    r2 = correct_temperature(R, 1.5)
    assert r2.temperature_c == 11.5 and R.temperature_c == 10.0
    assert r2.station == R.station


def test_append():
    h = (R,)
    h2 = append(h, R)
    assert len(h) == 1 and len(h2) == 2


def test_clean_pure_referential_transparency():
    input_data = [10.0, 99.0, 20.0]
    assert clean_pure(input_data) == clean_pure(input_data) == (15.0, ("nettoyage",))
    assert input_data == [10.0, 99.0, 20.0]


# ---------------------------------------------------------------------------
# Partie B — refactoring du script hérité
# ---------------------------------------------------------------------------
import contextlib
import importlib
import io

from nimbus import s01_legacy
from nimbus.s01_purity import (
    rand, rand_n, train_test_split, station_line, parse_temperatures, shuffle,
    report, group_by_station, split_state,
)

SAMPLE_CSV = "en-tete\n2025-01-01,BREST,10.0,80,1010,5,0\n2025-01-01,LYON,NA,80,1010,5,0\n" \
       "2025-01-02,BREST,12.0,80,1010,5,0\ntronquee,BREST,3\n2025-01-03,BREST,999,80,1010,5,0\n"


def legacy_output(text: str) -> str:
    module = importlib.reload(s01_legacy)          # repart d'un état global vierge
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        module.main(text)
    return buf.getvalue()


def test_parse_temperatures():
    assert parse_temperatures(SAMPLE_CSV) == ((("BREST", 10.0), ("BREST", 12.0)), 3)


def test_group_by_station_sorts():
    assert group_by_station([("A", 3.0), ("B", 1.0), ("A", 1.0)]) == {"A": (1.0, 3.0), "B": (1.0,)}


def test_station_line():
    assert station_line("BREST", [10.0, 12.0]) == \
        "BREST    n=2    moyenne= 11.00  médiane= 12.00  min=  10.0  max=  12.0"


def test_report_identical_to_legacy(csv_full):
    assert report(csv_full) == legacy_output(csv_full)
    assert report(SAMPLE_CSV) == legacy_output(SAMPLE_CSV)


def test_legacy_is_not_idempotent_but_report_is(csv_small):
    importlib.reload(s01_legacy)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        s01_legacy.main(csv_small)
        first = buf.getvalue()
        s01_legacy.main(csv_small)                 # deuxième appel : l'état global s'accumule
    second = buf.getvalue()[len(first):]
    assert first != second
    assert report(csv_small) == report(csv_small) == first


# ---------------------------------------------------------------------------
# Partie C — le hasard, purement
# ---------------------------------------------------------------------------


def test_rand_is_deterministic_and_uniform():
    assert rand(42) == rand(42)
    x, e = rand(42)
    assert 0.0 <= x < 1.0 and e != 42
    xs, _ = rand_n(7, 10_000)
    assert len(xs) == 10_000 and abs(sum(xs) / len(xs) - 0.5) < 0.02


def test_rand_n_threads_the_state():
    xs, e = rand_n(1, 3)
    x1, e1 = rand(1)
    x2, e2 = rand(e1)
    x3, e3 = rand(e2)
    assert xs == (x1, x2, x3) and e == e3


def test_shuffle_does_not_mutate_and_permutes():
    xs = [1, 2, 3, 4, 5, 6, 7, 8]
    m, _ = shuffle(xs, 3)
    assert xs == [1, 2, 3, 4, 5, 6, 7, 8]
    assert sorted(m) == xs and m != tuple(xs)
    assert shuffle(xs, 3) == shuffle(xs, 3)


def test_split_state():
    a, b = split_state(10)
    assert a != b
    assert rand_n(a, 5)[0] != rand_n(b, 5)[0]


def test_split_is_reproducible():
    datagen = tuple(range(100))
    app, test, _ = train_test_split(datagen, 0.2, 2026)
    assert len(test) == 20 and len(app) == 80
    assert sorted(app + test) == list(datagen)
    assert train_test_split(datagen, 0.2, 2026)[:2] == (app, test)
