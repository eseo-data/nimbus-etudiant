"""Bloc BD2 — Un moteur Big Data en style fonctionnel : Polars (lazy) et Spark.

Les deux moteurs appliquent les idées du tronc commun à grande échelle :
- un DataFrame est immutable : chaque transformation renvoie un nouveau DataFrame ;
- les transformations sont lazy : on construit un query plan (une valeur), rien
  n'est calculé avant `collect()` (Polars) ou une action comme `count()` (Spark) ;
- le moteur optimise le plan (predicate pushdown, projection pushdown) parce que
  les transformations sont des pure functions décrites, pas des boucles exécutées ;
- Spark garde la lineage de chaque RDD : une partition perdue est recalculée en
  rejouant les transformations, ce qui n'est possible que parce qu'elles sont pures ;
- `aggregateByKey(zero, seqOp, combOp)` est exactement un monoid (bloc BD1).

Organisation du TP :
- partie A (BD2.1 à BD2.4) : Polars lazy ;
- partie B (BD2.5) : réécrire en lazy le rapport eager de `bd2_legacy_report.py` ;
- partie C (BD2.6 à BD2.9) : les mêmes calculs avec Spark, et le monoid de BD1 en RDD ;
- défi : `bd2_challenge_planner.py`, un mini query optimizer.

Données : `uv run python -m nimbus.datagen --massif data/meteo_massif.csv 1000`
(environ 3,65 millions de lignes, 1 000 stations sur 10 ans).

Règles de nettoyage communes aux deux moteurs (les tests en dépendent) :
- une ligne est gardée si sa date est au format ISO AAAA-MM-JJ ;
- une mesure numérique est castée en Float64 ; une valeur non numérique devient null ;
- une valeur hors de ses BOUNDS devient null (même table qu'au bloc 2).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import polars as pl

from nimbus.s03_algebraic_types import BOUNDS
from nimbus.s06_monoids import STATS, Stats, stats_of

if TYPE_CHECKING:  # pragma: no cover
    from pyspark.rdd import RDD
    from pyspark.sql import DataFrame, SparkSession

MEASUREMENT_COLUMNS = tuple(BOUNDS)          # temperature_c, humidity_pct, pressure_hpa, wind_kmh, rain_mm
RAIN_THRESHOLD_MM = 0.2

# ===========================================================================
# Partie A — Polars lazy
# ===========================================================================


def scan_lazy(path: str) -> pl.LazyFrame:
    """Fourni : lecture lazy, toutes les colonnes en texte brut. Rien n'est lu ici."""
    schema = {"date": pl.String, "station": pl.String, **{c: pl.String for c in MEASUREMENT_COLUMNS}}
    return pl.scan_csv(path, schema=schema)


def clean(lf: pl.LazyFrame) -> pl.LazyFrame:
    """Exercice BD2.1 — applique les règles de nettoyage, sans rien exécuter.

    Colonnes de sortie : date (pl.Date), station, puis les 5 mesures en Float64.
    Indices : `str.to_date("%Y-%m-%d", strict=False)`, `cast(pl.Float64, strict=False)`,
    `pl.when(col.is_between(lo, hi)).then(col)` (sans `otherwise` : null).
    """
    raise NotImplementedError("BD2 — à compléter")


def stats_by_station(lf: pl.LazyFrame) -> pl.LazyFrame:
    """Exercice BD2.2 — par station : n (températures non nulles), mean, min, max.

    Colonnes : station, n (UInt32 ou Int), mean, min, max ; trié par station.
    """
    raise NotImplementedError("BD2 — à compléter")


def rain_frequency(lf: pl.LazyFrame) -> pl.LazyFrame:
    """Exercice BD2.3 — par station et par année : part des jours avec rain_mm > RAIN_THRESHOLD_MM
    (parmi les jours où rain_mm n'est pas null).

    Colonnes : station, year (Int32), days (nombre de jours avec mesure), frequency ; trié.
    """
    raise NotImplementedError("BD2 — à compléter")


def plan(lf: pl.LazyFrame) -> str:
    """Fourni : le query plan optimisé, sous forme de texte (`lf.explain()`)."""
    return str(lf.explain())


def temperature_anomalies(lf: pl.LazyFrame) -> pl.LazyFrame:
    """Exercice BD2.4 — écart de chaque température à la moyenne de sa station (window function).

    Colonnes : date, station, temperature_c, anomaly ; lignes où temperature_c n'est pas null,
    triées par station puis date. Indice : `pl.col("temperature_c").mean().over("station")`.
    """
    raise NotImplementedError("BD2 — à compléter")


# ===========================================================================
# Partie B — réécrire un rapport eager en lazy
# ===========================================================================


def wettest_months(lf: pl.LazyFrame, year: int, n: int) -> pl.LazyFrame:
    """Exercice BD2.5 — même résultat que `bd2_legacy_report.wettest_months`, en lazy.

    Sur des données déjà nettoyées (`clean`) : pour l'année `year`, cumul de rain_mm par
    (station, mois), les n plus grands. Colonnes : station, month (Int8 ou Int32), rain_mm ;
    tri par rain_mm décroissant puis station puis month (pour départager les égalités).
    Arrondir le cumul à 1 décimale, comme le legacy.
    """
    raise NotImplementedError("BD2 — à compléter")


# ===========================================================================
# Partie C — Spark (PySpark en mode local)
# ===========================================================================


def session(name: str = "nimbus") -> SparkSession:
    """Fourni : une SparkSession locale, tous les cœurs du laptop, sans interface web."""
    from pyspark.sql import SparkSession

    return (
        SparkSession.builder.master("local[*]").appName(name)
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def spark_read(spark: SparkSession, path: str) -> DataFrame:
    """Fourni : lecture CSV, toutes les colonnes en texte, lignes incomplètes complétées par null."""
    from pyspark.sql.types import StringType, StructField, StructType

    schema = StructType([StructField(c, StringType()) for c in ("date", "station", *MEASUREMENT_COLUMNS)])
    return spark.read.csv(path, header=True, schema=schema, mode="PERMISSIVE")


def spark_clean(df: DataFrame) -> DataFrame:
    """Exercice BD2.6 — mêmes règles que `clean`, avec l'API DataFrame de Spark.

    Indices : `F.try_to_date(col, "yyyy-MM-dd")` (ou `F.to_date` avec ANSI désactivé),
    `col.try_cast("double")`, `F.when(cond, value)` (null sinon).
    """
    raise NotImplementedError("BD2 — à compléter")


def spark_stats_by_station(df: DataFrame) -> DataFrame:
    """Exercice BD2.7 — même résultat que `stats_by_station`, en Spark (colonnes et tri identiques)."""
    raise NotImplementedError("BD2 — à compléter")


def rdd_stats_by_station(rdd: RDD[tuple[str, float]]) -> dict[str, Stats]:
    """Exercice BD2.8 — le monoid Stats du bloc BD1, distribué avec `aggregateByKey`.

    `rdd` contient des paires (station, température). Utilisez STATS.empty comme zéro,
    une seqOp qui combine l'accumulateur avec `stats_of(t)`, et STATS.combine comme
    combOp. Renvoyez le résultat collecté sous forme de dict.
    Question : pourquoi Spark exige-t-il que combOp soit associative ?
    """
    raise NotImplementedError("BD2 — à compléter")


def spark_wettest_months(df: DataFrame, year: int, n: int) -> DataFrame:
    """Exercice BD2.9 — `wettest_months` avec l'API DataFrame de Spark (mêmes colonnes, même tri).

    `df` sort de `spark_clean`. Indices : `F.year`, `F.month`, `F.round(F.sum(...), 1)`,
    `orderBy(F.desc("rain_mm"), "station", "month")`, `limit(n)`.
    """
    raise NotImplementedError("BD2 — à compléter")


def lineage(rdd: RDD[Any]) -> str:
    """Fourni : la lineage d'un RDD, telle que Spark la conserve pour recalculer une partition perdue."""
    raw = rdd.toDebugString()
    return raw.decode() if isinstance(raw, bytes) else str(raw)
