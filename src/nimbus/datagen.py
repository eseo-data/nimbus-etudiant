"""Générateur de données météo synthétiques (fourni, rien à compléter).

Le générateur est lui-même une fonction pure : même graine -> même CSV.
Aucune connexion réseau ni GPU n'est nécessaire pour tout le module.

Le CSV contient volontairement des défauts que le pipeline devra gérer :
valeurs manquantes, valeurs aberrantes, lignes mal formées, dates invalides,
stations inconnues.

Usage en ligne de commande :
    uv run python -m nimbus.datagen data/meteo.csv
    uv run python -m nimbus.datagen --massif data/meteo_massif.csv 1000   # parcours Big Data
"""

from __future__ import annotations

import math
import random
import sys
from collections.abc import Iterator
from datetime import date, timedelta
from pathlib import Path

HEADER = "date,station,temperature_c,humidity_pct,pressure_hpa,wind_kmh,rain_mm"
STATIONS = ("VELIZY", "BREST", "LYON")

# Climat très simplifié par station : (température moyenne, amplitude saisonnière, biais humidité)
_CLIMATES = {
    "VELIZY": (11.5, 8.0, 0.0),
    "BREST": (12.0, 5.0, 8.0),
    "LYON": (12.5, 10.0, -4.0),
}


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _station_series(rng: random.Random, station: str, start: date, n_days: int,
                   climate: tuple[float, float, float] | None = None) -> list[list[str]]:
    t_mean, amplitude, hum_bias = climate or _CLIMATES[station]
    pressure = 1013.0
    lines: list[list[str]] = []
    for i in range(n_days):
        day = start + timedelta(days=i)
        season = math.cos(2 * math.pi * (day.timetuple().tm_yday - 200) / 365.25)
        # La pression suit une marche aléatoire rappelée vers 1013 hPa
        pressure += -0.12 * (pressure - 1013.0) + rng.gauss(0, 3.0)
        humidity = min(100.0, max(20.0, 72 + hum_bias - 1.1 * (pressure - 1013) + rng.gauss(0, 7)))
        temperature = t_mean + amplitude * season + rng.gauss(0, 2.5)
        wind = max(0.0, 12 - 0.6 * (pressure - 1013) + rng.gauss(0, 5))
        # Probabilité de pluie : forte si humidité élevée et pression basse
        p_rain = _sigmoid(0.12 * (humidity - 78) - 0.10 * (pressure - 1013))
        rain = rng.expovariate(1 / 4.0) if rng.random() < p_rain else 0.0
        lines.append([
            day.isoformat(), station, f"{temperature:.1f}", f"{humidity:.0f}",
            f"{pressure:.1f}", f"{wind:.1f}", f"{rain:.1f}",
        ])
    return lines


def _damage(rng: random.Random, line: list[str]) -> str:
    """Injecte des défauts réalistes dans une ligne (capteurs capricieux, saisie manuelle...)."""
    r = rng.random()
    fields = list(line)
    if r < 0.03:
        fields[rng.randint(2, 6)] = rng.choice(["", "NA", "-"])        # valeur manquante
    elif r < 0.045:
        fields[2] = rng.choice(["999.9", "-273.0", "85.0"])            # température aberrante
    elif r < 0.055:
        fields[3] = rng.choice(["130", "-5"])                          # humidité impossible
    elif r < 0.060:
        fields[2] = "vingt"                                            # texte au lieu d'un nombre
    elif r < 0.064:
        return ",".join(fields[:5])                                    # ligne tronquée
    elif r < 0.067:
        fields[0] = fields[0].replace("-", "/")                        # date au mauvais format
    elif r < 0.069:
        fields[1] = "ATLANTIS"                                         # station inconnue
    return ",".join(fields)


def generate_csv(seed: int = 42, n_days: int = 365, start: date = date(2025, 1, 1)) -> str:
    """Fonction pure : renvoie le contenu CSV complet (en-tête compris)."""
    rng = random.Random(seed)
    lines = [HEADER]
    for station in STATIONS:
        for line in _station_series(rng, station, start, n_days):
            lines.append(_damage(rng, line))
    return "\n".join(lines) + "\n"


def generate_massive_lines(seed: int, n_stations: int, n_days: int,
                            start: date = date(2016, 1, 1)) -> Iterator[str]:
    """Parcours Big Data : générateur paresseux de lignes CSV (en-tête compris).

    Stations ST0001, ST0002... avec un climat tiré au hasard (graine fixée : même
    graine, mêmes données). 1 000 stations × 3 650 jours ≈ 3,65 millions de lignes.
    """
    rng = random.Random(seed)
    yield HEADER
    for k in range(1, n_stations + 1):
        climate = (rng.uniform(6.0, 17.0), rng.uniform(3.0, 11.0), rng.uniform(-8.0, 10.0))
        for line in _station_series(rng, f"ST{k:04d}", start, n_days, climate):
            yield _damage(rng, line)


def write_massive_csv(path: Path, seed: int = 42, n_stations: int = 1000, n_days: int = 3650) -> int:
    """Coquille impérative : écrit le CSV massif ligne par ligne (mémoire constante)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8") as f:
        for line in generate_massive_lines(seed, n_stations, n_days):
            f.write(line + "\n")
            n += 1
    return n - 1


def main() -> None:  # pragma: no cover - coquille impérative
    args = sys.argv[1:]
    if args and args[0] == "--massif":
        path = Path(args[1] if len(args) > 1 else "data/meteo_massif.csv")
        n_stations = int(args[2]) if len(args) > 2 else 1000
        n = write_massive_csv(path, n_stations=n_stations)
        print(f"Écrit : {path} ({n} lignes)")
        return
    path = Path(args[0] if args else "data/meteo.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(generate_csv(), encoding="utf-8")
    print(f"Écrit : {path}")


if __name__ == "__main__":  # pragma: no cover
    main()
