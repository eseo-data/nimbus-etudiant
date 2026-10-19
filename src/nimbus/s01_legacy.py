# mypy: ignore-errors
"""Séance 1, partie B — script HÉRITÉ, écrit « à l'ancienne ». NE PAS MODIFIER.

Il lit le CSV Nimbus et affiche des statistiques de température par station.
Il fonctionne… une fois. Lisez-le, repérez tout ce qui le rend impur, puis
réécrivez-le en fonctions pures dans `s01_purity.py` (exercices 1.8 à 1.11).

Le test `test_report_identical_to_legacy` vérifie que votre version produit
EXACTEMENT le même texte que ce script.
"""

STATS = {}          # station -> liste de températures (mutée au fil de la lecture)
REJECTED = 0          # compteur global
LAST_STATION = None


def process(text):
    global REJECTED, LAST_STATION
    lines = text.splitlines()
    lines.pop(0)                                   # on jette l'en-tête (mutation)
    for line in lines:
        fields = line.split(",")
        if len(fields) != 7:
            REJECTED += 1
            continue
        station = fields[1]
        try:
            t = float(fields[2])
        except ValueError:
            REJECTED += 1
            continue
        if t < -40 or t > 50:
            REJECTED += 1
            continue
        if station not in STATS:
            STATS[station] = []
        STATS[station].append(t)
        LAST_STATION = station


def render():
    for station in sorted(STATS):
        ts = STATS[station]
        ts.sort()                                   # trie EN PLACE les données globales
        average = sum(ts) / len(ts)
        median = ts[len(ts) // 2]
        print(f"{station:<8} n={len(ts):<4} moyenne={average:6.2f}  médiane={median:6.2f}  "
              f"min={ts[0]:6.1f}  max={ts[-1]:6.1f}")
    print(f"Rejets : {REJECTED}")


def main(text):
    process(text)
    render()
