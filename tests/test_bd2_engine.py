"""Bloc BD2 — tests Polars (et Spark si Java et PySpark sont disponibles).

    uv sync --group bigdata
    uv run pytest tests/test_bd2_engine.py
"""

import csv
import io
import math
import shutil
from datetime import date

import pytest

pl = pytest.importorskip("polars")

from nimbus import bd2_engine as bd  # noqa: E402
from nimbus.datagen import generate_massive_lines  # noqa: E402
from nimbus.s03_algebraic_types import BOUNDS  # noqa: E402


@pytest.fixture(scope="module")
def csv_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("bd2") / "meteo.csv"
    path.write_text("\n".join(generate_massive_lines(3, 12, 730)) + "\n", encoding="utf-8")
    return str(path)


def reference(path):
    """Calcul de référence en Python pur, avec les mêmes règles de nettoyage."""
    timestamp: dict[str, list[float]] = {}
    lo, hi = BOUNDS["temperature_c"]
    with open(path, encoding="utf-8") as f:
        for i, fields in enumerate(csv.reader(f)):
            if i == 0 or len(fields) < 3:
                continue
            try:
                date.fromisoformat(fields[0])
            except ValueError:
                continue
            timestamp.setdefault(fields[1], [])
            try:
                t = float(fields[2])
            except ValueError:
                continue
            if lo <= t <= hi:
                timestamp[fields[1]].append(t)
    return {st: (len(ts), sum(ts) / len(ts), min(ts), max(ts)) for st, ts in timestamp.items()}


def test_clean_is_lazy_and_typed(csv_path):
    lf = bd.clean(bd.scan_lazy(csv_path))
    assert isinstance(lf, pl.LazyFrame)                       # rien n'est encore calculé
    df = lf.collect()
    assert df.schema["date"] == pl.Date
    assert all(df.schema[c] == pl.Float64 for c in BOUNDS)
    assert df["temperature_c"].drop_nulls().is_between(-40, 50).all()
    assert df["date"].null_count() == 0


def test_stats_identical_to_reference(csv_path):
    ref = reference(csv_path)
    df = bd.stats_by_station(bd.clean(bd.scan_lazy(csv_path))).collect()
    assert df["station"].to_list() == sorted(ref)
    for st, n, avg, minimum, maximum in df.select("station", "n", "mean", "min", "max").iter_rows():
        rn, rmean, rmin, rmax = ref[st]
        assert n == rn and math.isclose(avg, rmean) and minimum == rmin and maximum == rmax


def test_rain_frequency(csv_path):
    df = bd.rain_frequency(bd.clean(bd.scan_lazy(csv_path))).collect()
    assert set(df["year"].unique().to_list()) == {2016, 2017}
    assert df["frequency"].is_between(0, 1).all()
    real_stations = df.filter(pl.col("station").str.starts_with("ST"))
    assert len(real_stations) == 12 * 2          # (+ la station inconnue ATLANTIS injectée)


def test_plan_is_optimized(csv_path):
    lf = bd.clean(bd.scan_lazy(csv_path)).filter(pl.col("station") == "ST0003").select("temperature_c")
    text = bd.plan(lf)
    assert "ST0003" in text                                  # le filtre est poussé vers la lecture


# ---------------------------------------------------------------------------
# Spark (sauté si PySpark ou Java manquent)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def spark():
    pytest.importorskip("pyspark")
    if shutil.which("java") is None:
        pytest.skip("Java 17 ou 21 requis pour Spark")
    s = bd.session("tests")
    yield s
    s.stop()


def test_spark_identical_to_polars(spark, csv_path):
    expected = bd.stats_by_station(bd.clean(bd.scan_lazy(csv_path))).collect()
    actual = bd.spark_stats_by_station(bd.spark_clean(bd.spark_read(spark, csv_path))).collect()
    assert [r["station"] for r in actual] == expected["station"].to_list()
    for r, (n, avg, minimum, maximum) in zip(actual, expected.select("n", "mean", "min", "max").iter_rows()):
        assert r["n"] == n and math.isclose(r["mean"], avg) and r["min"] == minimum and r["max"] == maximum


def test_rdd_monoid_and_lineage(spark, csv_path):
    df = bd.spark_clean(bd.spark_read(spark, csv_path)).where("temperature_c IS NOT NULL")
    pairs = df.rdd.map(lambda r: (r["station"], r["temperature_c"]))
    stats = bd.rdd_stats_by_station(pairs.repartition(7))
    ref = reference(csv_path)
    assert set(stats) == set(ref)
    for st, s in stats.items():
        assert s.n == ref[st][0] and math.isclose(s.average, ref[st][1])
    assert "MapPartitionsRDD" in bd.lineage(pairs) or "PythonRDD" in bd.lineage(pairs)


# ---------------------------------------------------------------------------
# Ajouts : window function, legacy eager, Spark
# ---------------------------------------------------------------------------

from nimbus.bd2_legacy_report import wettest_months as legacy_wettest  # noqa: E402


def test_temperature_anomalies(csv_path):
    df = bd.temperature_anomalies(bd.clean(bd.scan_lazy(csv_path))).collect()
    assert df.columns == ["date", "station", "temperature_c", "anomaly"]
    means = df.group_by("station").agg(pl.col("anomaly").mean())
    assert means["anomaly"].abs().max() < 1e-9               # écart moyen nul par station
    assert df["temperature_c"].null_count() == 0


def as_triples(df):
    return [(r[0], int(r[1]), r[2]) for r in df.select("station", "month", "rain_mm").iter_rows()]


def test_wettest_months_identique_au_legacy(csv_path):
    expected = legacy_wettest(csv_path, 2017, 10)
    actual = as_triples(bd.wettest_months(bd.clean(bd.scan_lazy(csv_path)), 2017, 10).collect())
    assert [(s, m) for s, m, _ in actual] == [(s, m) for s, m, _ in expected]
    assert all(math.isclose(a[2], e[2], abs_tol=0.051) for a, e in zip(actual, expected))


def test_wettest_months_ne_lit_que_trois_colonnes(csv_path):
    text = bd.plan(bd.wettest_months(bd.clean(bd.scan_lazy(csv_path)), 2017, 10))
    assert "3/7" in text                                     # projection pushdown : date, station, rain_mm


def test_spark_wettest_months_identique(spark, csv_path):
    expected = as_triples(bd.wettest_months(bd.clean(bd.scan_lazy(csv_path)), 2017, 10).collect())
    rows = bd.spark_wettest_months(bd.spark_clean(bd.spark_read(spark, csv_path)), 2017, 10).collect()
    actual = [(r["station"], int(r["month"]), r["rain_mm"]) for r in rows]
    assert [(s, m) for s, m, _ in actual] == [(s, m) for s, m, _ in expected]
    assert all(math.isclose(a[2], e[2], abs_tol=0.051) for a, e in zip(actual, expected))
