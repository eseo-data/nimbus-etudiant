# mypy: ignore-errors
"""Séance 1, partie B — script HÉRITÉ, écrit « à l'ancienne ». NE PAS MODIFIER.

Il lit le CSV Nimbus et affiche des statistiques de température par station.
Il fonctionne… une fois. Lisez-le, repérez tout ce qui le rend impur, puis
réécrivez-le en fonctions pures dans `s01_purete.py` (exercices 1.8 à 1.11).

Le test `test_rapport_identique_au_legacy` vérifie que votre version produit
EXACTEMENT le même texte que ce script.
"""

STATS = {}          # station -> liste de températures (mutée au fil de la lecture)
REJETS = 0          # compteur global
DERNIERE_STATION = None


def traiter(texte):
    global REJETS, DERNIERE_STATION
    lignes = texte.splitlines()
    lignes.pop(0)                                   # on jette l'en-tête (mutation)
    for ligne in lignes:
        champs = ligne.split(",")
        if len(champs) != 7:
            REJETS += 1
            continue
        station = champs[1]
        try:
            t = float(champs[2])
        except ValueError:
            REJETS += 1
            continue
        if t < -40 or t > 50:
            REJETS += 1
            continue
        if station not in STATS:
            STATS[station] = []
        STATS[station].append(t)
        DERNIERE_STATION = station


def afficher():
    for station in sorted(STATS):
        ts = STATS[station]
        ts.sort()                                   # trie EN PLACE les données globales
        moyenne = sum(ts) / len(ts)
        mediane = ts[len(ts) // 2]
        print(f"{station:<8} n={len(ts):<4} moyenne={moyenne:6.2f}  médiane={mediane:6.2f}  "
              f"min={ts[0]:6.1f}  max={ts[-1]:6.1f}")
    print(f"Rejets : {REJETS}")


def main(texte):
    traiter(texte)
    afficher()
