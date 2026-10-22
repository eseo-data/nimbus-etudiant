# mypy: ignore-errors
"""BD2, partie B — rapport « mois les plus pluvieux », version eager. NE PAS MODIFIER.

Le script charge TOUT le CSV en mémoire (une liste de dicts, toutes les colonnes),
nettoie, filtre, agrège puis trie. Sur 3,65 millions de lignes, il faut plusieurs
Go de RAM et de longues minutes. Réécrivez-le en Polars lazy (exercice BD2.5) :
même résultat, mais le moteur ne lit que les colonnes utiles.
"""

import csv
from datetime import date

BOUNDS_RAIN = (0.0, 300.0)


def load(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def wettest_months(path, year, n):
    rows = load(path)
    totals = {}
    for row in rows:
        try:
            d = date.fromisoformat(row["date"] or "")
        except ValueError:
            continue
        if d.year != year:
            continue
        try:
            rain = float(row["rain_mm"])
        except (TypeError, ValueError):
            continue
        if not BOUNDS_RAIN[0] <= rain <= BOUNDS_RAIN[1]:
            continue
        key = (row["station"], d.month)
        totals[key] = totals.get(key, 0.0) + rain
    ranked = sorted(totals.items(), key=lambda kv: (-round(kv[1], 1), kv[0][0], kv[0][1]))
    return [(station, month, round(total, 1)) for (station, month), total in ranked[:n]]
