# mypy: ignore-errors
"""BD1, partie B — rapport mensuel « parallélisé ». NE PAS MODIFIER.

Un premier développeur a accéléré le rapport en découpant les lignes en morceaux
traités par plusieurs threads, puis en fusionnant les résultats partiels. Le code
tourne sans erreur, mais le rapport change selon le nombre de workers.

Réécrivez-le avec des monoids dans `s06_mapreduce.py` (exercices 6.9 à 6.11).
"""

from concurrent.futures import ThreadPoolExecutor


def _process_chunk(lines):
    stats = {}
    for line in lines:
        f = line.split(",")
        if len(f) != 7 or len(f[0]) != 10 or f[0][4] != "-":
            continue
        try:
            t = float(f[2])
        except ValueError:
            continue
        if not -40 <= t <= 50:
            continue
        key = (f[1], f[0][:7])                       # (station, mois AAAA-MM)
        s = stats.setdefault(key, {"n": 0, "mean": 0.0, "max": 0.0})
        s["n"] += 1
        s["mean"] += (t - s["mean"]) / s["n"]        # moyenne glissante
        s["max"] = max(s["max"], t)
    return stats


def monthly_report(lines, workers=4):
    lines = list(lines)[1:]                          # sans l'en-tête
    size = max(1, -(-len(lines) // workers))
    chunks = [lines[i:i + size] for i in range(0, len(lines), size)]
    with ThreadPoolExecutor(workers) as pool:
        partials = list(pool.map(_process_chunk, chunks))
    out = {}
    for p in partials:
        for key, s in p.items():
            if key not in out:
                out[key] = dict(s)
            else:
                o = out[key]
                o["n"] += s["n"]
                o["mean"] = (o["mean"] + s["mean"]) / 2
                o["max"] = max(o["max"], s["max"])
    return [f"{st} {month} n={s['n']} mean={s['mean']:.2f} max={s['max']:.1f}"
            for (st, month), s in sorted(out.items())]
