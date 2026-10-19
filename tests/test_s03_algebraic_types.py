from nimbus.s03_algebraic_types import (
    Outlier, Missing, Valid, count_by_kind, describe, is_complete, parse_measurement, parse_reading,
    value_or,
)


def test_parse_measurement():
    assert parse_measurement("12.5", -40, 50) == Valid(12.5)
    assert parse_measurement(" NA ", -40, 50) == Missing()
    assert parse_measurement("", -40, 50) == Missing()
    assert parse_measurement("vingt", -40, 50) == Outlier("vingt", "non numérique")
    assert parse_measurement("999.9", -40, 50) == Outlier("999.9", "hors bornes")


def test_value_or_and_describe():
    assert value_or(Valid(3.0), 0.0) == 3.0
    assert value_or(Missing(), -1.0) == -1.0
    assert describe(Valid(12.5)) == "12.5"
    assert describe(Missing()) == "manquante"
    assert describe(Outlier("999", "hors bornes")) == "aberrante (hors bornes) : '999'"


FIELDS = {"temperature_c": "10", "humidity_pct": "80", "pressure_hpa": "1010", "wind_kmh": "5", "rain_mm": "0"}


def test_parse_reading_and_is_complete():
    r = parse_reading("2025-01-01", "BREST", FIELDS)
    assert r.temperature_c == Valid(10.0) and is_complete(r)
    r2 = parse_reading("2025-01-01", "BREST", {**FIELDS, "humidity_pct": "130"})
    assert isinstance(r2.humidity_pct, Outlier) and not is_complete(r2)


def test_count_by_kind():
    ms = [Valid(1), Valid(2), Missing(), Outlier("x", "y")]
    assert count_by_kind(ms) == {"valid": 2, "missing": 1, "outlier": 1}
    assert count_by_kind([]) == {"valid": 0, "missing": 0, "outlier": 0}


# ---------------------------------------------------------------------------
# Partie B (bloc 2) — alertes en ADT
# ---------------------------------------------------------------------------

from nimbus.datagen import generate_csv  # noqa: E402
from nimbus.s02_higher_order import split_csv  # noqa: E402
from nimbus.s03_legacy_alerts import alerts as legacy_alerts  # noqa: E402
from nimbus.s03_algebraic_types import (  # noqa: E402
    BOUNDS, Heatwave, Frost, Flood, NoAlert, Storm, detect, message, alert_report,
)


def _reading(t="12", wind="10", rain="0"):
    return parse_reading("2025-01-01", "BREST", {"temperature_c": t, "humidity_pct": "80",
                                                "pressure_hpa": "1013", "wind_kmh": wind, "rain_mm": rain})


def test_detect_priorities():
    assert detect(_reading(t="31", wind="40", rain="20")) == Storm(40.0)
    assert detect(_reading(t="31", rain="20")) == Flood(20.0)
    assert detect(_reading(t="31")) == Heatwave(31.0)
    assert detect(_reading(t="-3")) == Frost(-3.0)
    assert detect(_reading()) == NoAlert()


def test_detect_ignores_invalid_measurements():
    assert detect(_reading(t="999.9")) == NoAlert()          # Outlier
    assert detect(_reading(t="NA", wind="abc")) == NoAlert()  # Missing, non numérique
    assert detect(_reading(t="-273", wind="NA", rain="12")) == NoAlert()


def test_message_legacy_format():
    assert message("d", "S", Storm(41.25)) == "d S : tempête, vent 41.2 km/h"
    assert message("d", "S", Flood(20)) == "d S : risque d'inondation, 20.0 mm"
    assert message("d", "S", Heatwave(31)) == "d S : canicule, 31.0 °C"
    assert message("d", "S", Frost(-0.04)) == "d S : gel, -0.0 °C"
    assert message("d", "S", NoAlert()) is None


def test_alert_report_removes_exactly_the_false_alerts():
    """Critère de réussite : même rapport que le legacy, moins les alertes dues à des
    valeurs aberrantes (et uniquement celles-là)."""
    text = generate_csv(seed=42)
    new = alert_report(split_csv(text))
    old = legacy_alerts(text)
    assert set(new) <= set(old)
    removed = [a for a in old if a not in set(new)]
    assert removed, "le legacy contient des fausses alertes : il doit y en avoir de retirées"
    variable = {"tempête": "wind_kmh", "risque d'inondation": "rain_mm",
                "canicule": "temperature_c", "gel": "temperature_c"}
    for a in removed:
        kind = a.split(" : ")[1].split(",")[0]
        value = float(a.rsplit(" ", 2)[-2])
        lo, hi = BOUNDS[variable[kind]]
        assert not lo <= value <= hi, a                              # toutes sont aberrantes
    assert [a for a in old if a in set(new)] == new        # ordre conservé


def test_non_exhaustive_match_rejected_by_mypy(tmp_path, monkeypatch):
    """Si un cas est oublié dans `message`, mypy --strict doit le signaler."""
    import pathlib

    import nimbus

    api = __import__("pytest").importorskip("mypy.api")
    monkeypatch.setenv("MYPYPATH", str(pathlib.Path(nimbus.__file__).parent.parent))
    f = tmp_path / "oubli.py"
    f.write_text(
        "from typing import assert_never\n"
        "from nimbus.s03_algebraic_types import Alert, Storm, Flood, Heatwave, NoAlert\n"
        "def m(a: Alert) -> str:\n"
        "    match a:\n"
        "        case Storm() | Flood() | Heatwave() | NoAlert():\n"
        "            return 'x'\n"
        "        case _:\n"
        "            assert_never(a)\n"
    )
    output, _, code = api.run(["--strict", "--no-incremental", str(f)])
    assert code != 0 and "Frost" in output
