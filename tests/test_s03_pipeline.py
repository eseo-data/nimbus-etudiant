"""Bloc 2, partie C : uv run pytest tests/test_s03_pipeline.py"""

import itertools
import tracemalloc

from nimbus.datagen import generate_csv, generate_massive_lines
from nimbus.s02_higher_order import split_csv
from nimbus.s03_pipeline import (
    count_alerts, is_alert, first_n, readings, max_temperature_by_station,
)
from nimbus.s03_algebraic_types import detect, alert_report

N_STATIONS, N_DAYS = 20, 3650             # 73 000 lignes
PEAK_MAX = 4 * 1024 * 1024                  # 4 Mo ; list(readings(...)) en prend environ 56, la liste des lignes brutes 8


def stream():
    return generate_massive_lines(seed=7, n_stations=N_STATIONS, n_days=N_DAYS)


def test_readings_consistent_with_part_b():
    text = generate_csv(seed=42)
    rs = list(readings(text.splitlines()))
    lines = split_csv(text)
    assert len(rs) == sum(1 for c in lines if len(c) == 7)
    total = sum(count_alerts(rs).values())
    assert total == len(alert_report(split_csv(text)))


def test_readings_is_lazy():
    def lines():
        yield "date,station,temperature_c,humidity_pct,pressure_hpa,wind_kmh,rain_mm"
        yield "2025-01-01,X,10,50,1000,5,0"
        raise AssertionError("releves a lu trop loin")

    assert next(readings(lines())).station == "X"


def test_first_n_stops_early():
    assert first_n(lambda x: x % 7 == 0, 3, itertools.count(1)) == [7, 14, 21]

    def then_explode():
        yield from [1, 2, 3, 4]
        raise AssertionError("trop loin")

    assert first_n(lambda x: x > 1, 2, then_explode()) == [2, 3]


def _peak(f):
    tracemalloc.start()
    try:
        result = f()
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return result, peak


def test_count_alerts_in_constant_memory():
    counts, peak = _peak(lambda: count_alerts(readings(stream())))
    assert set(counts) == {"storm", "flood", "heatwave", "frost"}
    assert sum(counts.values()) > 0
    assert peak < PEAK_MAX, f"pic mémoire {peak / 1e6:.0f} Mo : une liste a été construite"


def test_max_temperature_by_station_in_constant_memory():
    maximum, peak = _peak(lambda: max_temperature_by_station(readings(stream())))
    assert sum(1 for s in maximum if s.startswith("ST")) == N_STATIONS   # + stations fantômes
    assert all(-40 <= t <= 50 for t in maximum.values())
    assert peak < PEAK_MAX, f"pic mémoire {peak / 1e6:.0f} Mo"


def test_first_alerts_on_massive_stream():
    three = first_n(is_alert, 3, map(detect, readings(stream())))
    assert len(three) == 3 and all(is_alert(a) for a in three)
