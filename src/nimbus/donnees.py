"""Générateur de données météo synthétiques (fourni, rien à compléter).

Le générateur est lui-même une fonction pure : même graine -> même CSV.
Aucune connexion réseau ni GPU n'est nécessaire pour tout le module.

Le CSV contient volontairement des défauts que le pipeline devra gérer :
valeurs manquantes, valeurs aberrantes, lignes mal formées, dates invalides,
stations inconnues.

Usage en ligne de commande :
    uv run python -m nimbus.donnees data/meteo.csv
"""

from __future__ import annotations

import math
import random
import sys
from datetime import date, timedelta
from pathlib import Path

EN_TETE = "date,station,temperature_c,humidite_pct,pression_hpa,vent_kmh,pluie_mm"
STATIONS = ("VELIZY", "BREST", "LYON")

# Climat très simplifié par station : (température moyenne, amplitude saisonnière, biais humidité)
_CLIMATS = {
    "VELIZY": (11.5, 8.0, 0.0),
    "BREST": (12.0, 5.0, 8.0),
    "LYON": (12.5, 10.0, -4.0),
}


def _sigmoide(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _serie_station(rng: random.Random, station: str, debut: date, n_jours: int) -> list[list[str]]:
    t_moy, amplitude, biais_hum = _CLIMATS[station]
    pression = 1013.0
    lignes: list[list[str]] = []
    for i in range(n_jours):
        jour = debut + timedelta(days=i)
        saison = math.cos(2 * math.pi * (jour.timetuple().tm_yday - 200) / 365.25)
        # La pression suit une marche aléatoire rappelée vers 1013 hPa
        pression += -0.12 * (pression - 1013.0) + rng.gauss(0, 3.0)
        humidite = min(100.0, max(20.0, 72 + biais_hum - 1.1 * (pression - 1013) + rng.gauss(0, 7)))
        temperature = t_moy + amplitude * saison + rng.gauss(0, 2.5)
        vent = max(0.0, 12 - 0.6 * (pression - 1013) + rng.gauss(0, 5))
        # Probabilité de pluie : forte si humidité élevée et pression basse
        p_pluie = _sigmoide(0.12 * (humidite - 78) - 0.10 * (pression - 1013))
        pluie = rng.expovariate(1 / 4.0) if rng.random() < p_pluie else 0.0
        lignes.append([
            jour.isoformat(), station, f"{temperature:.1f}", f"{humidite:.0f}",
            f"{pression:.1f}", f"{vent:.1f}", f"{pluie:.1f}",
        ])
    return lignes


def _abimer(rng: random.Random, ligne: list[str]) -> str:
    """Injecte des défauts réalistes dans une ligne (capteurs capricieux, saisie manuelle...)."""
    r = rng.random()
    champs = list(ligne)
    if r < 0.03:
        champs[rng.randint(2, 6)] = rng.choice(["", "NA", "-"])        # valeur manquante
    elif r < 0.045:
        champs[2] = rng.choice(["999.9", "-273.0", "85.0"])            # température aberrante
    elif r < 0.055:
        champs[3] = rng.choice(["130", "-5"])                          # humidité impossible
    elif r < 0.060:
        champs[2] = "vingt"                                            # texte au lieu d'un nombre
    elif r < 0.064:
        return ",".join(champs[:5])                                    # ligne tronquée
    elif r < 0.067:
        champs[0] = champs[0].replace("-", "/")                        # date au mauvais format
    elif r < 0.069:
        champs[1] = "ATLANTIS"                                         # station inconnue
    return ",".join(champs)


def generer_csv(graine: int = 42, n_jours: int = 365, debut: date = date(2025, 1, 1)) -> str:
    """Fonction pure : renvoie le contenu CSV complet (en-tête compris)."""
    rng = random.Random(graine)
    lignes = [EN_TETE]
    for station in STATIONS:
        for ligne in _serie_station(rng, station, debut, n_jours):
            lignes.append(_abimer(rng, ligne))
    return "\n".join(lignes) + "\n"


def main() -> None:  # pragma: no cover - coquille impérative
    chemin = Path(sys.argv[1] if len(sys.argv) > 1 else "data/meteo.csv")
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(generer_csv(), encoding="utf-8")
    print(f"Écrit : {chemin}")


if __name__ == "__main__":  # pragma: no cover
    main()
