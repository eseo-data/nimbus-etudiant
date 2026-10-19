"""Assemblage final (bloc 4) : functional core, imperative shell.

    uv run nimbus                     # tronc commun : qualité des données + stats par station
    uv run nimbus data/meteo.csv rapport.txt
    uv run nimbus-bd                  # parcours Big Data : + monoids, JAX, decision tree

Tout ce qui est au-dessus de `main()` est pur ou décrit des effets sans les exécuter.
Seul `main()` appelle l'interpréteur.
"""

from __future__ import annotations

import sys
from pathlib import Path

from collections.abc import Callable, Sequence

from nimbus.datagen import generate_csv
from nimbus.s03_algebraic_types import TypedReading, Valid, count_by_kind, measurements
from nimbus.s05_errors import Loaded, Err, Ok, load
from nimbus.s09_effects import Effect, Services, display, write_file, read_file, success


def temperatures_by_station(readings: Sequence[TypedReading]) -> dict[str, tuple[float, ...]]:
    """Fourni : températures valides par station (tronc commun, sans monoid)."""
    stations = sorted({r.station for r in readings})
    return {st: tuple(r.temperature_c.value for r in readings
                      if r.station == st and isinstance(r.temperature_c, Valid))
            for st in stations}


def quality_lines(ch: Loaded) -> list[str]:
    """Fourni : en-tête du rapport et qualité des données (blocs 2 et 3)."""
    quality = count_by_kind(m for r in ch.readings for m in measurements(r))
    return [
        "=== Rapport Nimbus ===",
        "",
        f"Relevés acceptés : {len(ch.readings)}   lignes rejetées : {len(ch.rejected)}",
        f"Mesures : {quality}",
        *(f"  ligne {n} : {'; '.join(es)}" for n, es in ch.rejected[:5]),
        "",
    ]


def analyze(ch: Loaded) -> str:
    """CŒUR PUR (tronc commun, blocs 1 à 4) : un chargement -> un rapport texte."""
    lines = [*quality_lines(ch), "Température par station :"]
    for station, ts in temperatures_by_station(ch.readings).items():
        if ts:
            lines.append(f"  {station:<7} n={len(ts):<4} moy={sum(ts) / len(ts):5.1f}°C  "
                          f"min={min(ts):5.1f}  max={max(ts):5.1f}")
    return "\n".join(lines)


def analyze_full(ch: Loaded) -> str:
    """CŒUR PUR (parcours Big Data, BD1 et BD4) : tronc commun + monoids + modèles."""
    import jax.numpy as jnp

    from nimbus import s07_functional_ml as ml
    from nimbus.s06_monoids import temperature_stats_by_station
    from nimbus.s08_trees import display as render_tree
    from nimbus.s08_trees import build, prune, predict

    lines = quality_lines(ch)
    lines.append("Température par station (monoid Stats, agrégation parallèle) :")
    for station, s in sorted(temperature_stats_by_station(ch.readings).items()):
        lines.append(f"  {station:<7} n={s.n:<4} moy={s.average:5.1f}°C  min={s.minimum:5.1f}  max={s.maximum:5.1f}")
    lines.append("")

    # Modèles (BD4) — découpage déterministe 80/20
    X, y = ml.build_dataset(ch.readings)
    if len(y) < 50:
        return "\n".join(lines + ["Pas assez de données pour entraîner un modèle."])
    test = [i % 5 == 0 for i in range(len(y))]
    Xa = [x for x, t in zip(X, test) if not t]
    ya = [v for v, t in zip(y, test) if not t]
    Xt = [x for x, t in zip(X, test) if t]
    yt = [v for v, t in zip(y, test) if t]

    base = max(sum(yt), len(yt) - sum(yt)) / len(yt)
    lines.append(f"Référence (classe majoritaire) : {base:.1%}")

    Xa_j, norm = ml.standardize(jnp.array(Xa))
    Xt_j = (jnp.array(Xt) - norm.average) / norm.std_dev
    params, losses = ml.train(ml.init_params(Xa_j.shape[1]), Xa_j, jnp.array(ya))
    lines.append(
        f"Régression logistique (JAX) : exactitude test {ml.accuracy(params, Xt_j, jnp.array(yt)):.1%}"
        f"   (perte {float(losses[0]):.3f} -> {float(losses[-1]):.3f})"
    )

    tree = prune(build(Xa, ya, max_depth=3))
    acc_tree = sum((predict(tree, x) > 0.5) == (v > 0.5) for x, v in zip(Xt, yt)) / len(yt)
    lines += [f"Tree de décision : exactitude test {acc_tree:.1%}", "", render_tree(tree)]
    return "\n".join(lines)


def program(s: Services, csv_path: str, report_path: str,
              analysis: Callable[[Loaded], str] = analyze) -> Effect[str]:
    """DESCRIPTION du programme complet. Rien ne s'exécute ici.

    `analysis` est une higher-order function : `analyze` (tronc commun) ou `analyze_full`.
    """
    return (
        read_file(s, csv_path)
        .retry(2)
        .map(load)
        .tap(lambda ch: display(s, f"Chargé : {len(ch.readings)} relevés, {len(ch.rejected)} rejets"))
        .map(analysis)
        .tap(lambda report: write_file(s, report_path, report))
        .tap(lambda report: display(s, report))
        .catch_all(lambda e: display(s, f"Échec : {e}").flat_map(lambda _: success("")))
    )


def real_services() -> Services:
    def save(path: str, content: str) -> None:
        Path(path).write_text(content, encoding="utf-8")

    return Services(read=lambda p: Path(p).read_text(encoding="utf-8"), save=save, display=print)


def main(analysis: Callable[[Loaded], str] = analyze) -> None:  # pragma: no cover - coquille impérative
    from nimbus.s09_effects import execute

    csv_path = sys.argv[1] if len(sys.argv) > 1 else "data/meteo.csv"
    report_path = sys.argv[2] if len(sys.argv) > 2 else "rapport.txt"
    if not Path(csv_path).exists():
        Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
        Path(csv_path).write_text(generate_csv(), encoding="utf-8")
    match execute(program(real_services(), csv_path, report_path, analysis)):
        case Ok(_):
            pass
        case Err(e):
            print(f"Erreur fatale : {e}", file=sys.stderr)
            sys.exit(1)


def main_bd() -> None:  # pragma: no cover
    main(analyze_full)


if __name__ == "__main__":  # pragma: no cover
    main()
