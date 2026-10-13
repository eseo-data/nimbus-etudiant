"""Assemblage final (séance 9) : cœur fonctionnel, coquille impérative.

    uv run nimbus                     # génère les données si besoin, analyse, écrit le rapport
    uv run nimbus data/meteo.csv rapport.txt

Tout ce qui est au-dessus de `main()` est pur ou décrit des effets sans les exécuter.
Seul `main()` appelle l'interpréteur.
"""

from __future__ import annotations

import sys
from pathlib import Path

import jax.numpy as jnp

from nimbus import s07_ml_fonctionnel as ml
from nimbus.donnees import generer_csv
from nimbus.s03_types_algebriques import compter_par_type, mesures
from nimbus.s05_erreurs import Chargement, Err, Ok, charger
from nimbus.s06_monoides import stats_temperature_par_station
from nimbus.s08_arbres import afficher as afficher_arbre
from nimbus.s08_arbres import construire, elaguer, predire
from nimbus.s09_effets import Effet, Services, afficher, ecrire_fichier, lire_fichier, succes


def analyser(ch: Chargement) -> str:
    """CŒUR PUR : un chargement -> un rapport texte. Testable sans aucun fichier."""
    lignes = ["=== Rapport Nimbus ===", ""]

    # Qualité des données (séances 3 et 5)
    qualite = compter_par_type(m for r in ch.releves for m in mesures(r))
    lignes += [
        f"Relevés acceptés : {len(ch.releves)}   lignes rejetées : {len(ch.rejets)}",
        f"Mesures : {qualite}",
        *(f"  ligne {n} : {'; '.join(es)}" for n, es in ch.rejets[:5]),
        "",
    ]

    # Statistiques par station (séance 6)
    lignes.append("Température par station :")
    for station, s in sorted(stats_temperature_par_station(ch.releves).items()):
        lignes.append(f"  {station:<7} n={s.n:<4} moy={s.moyenne:5.1f}°C  min={s.mini:5.1f}  max={s.maxi:5.1f}")
    lignes.append("")

    # Modèles (séances 7 et 8) — découpage déterministe 80/20
    X, y = ml.construire_jeu(ch.releves)
    if len(y) < 50:
        return "\n".join(lignes + ["Pas assez de données pour entraîner un modèle."])
    test = [i % 5 == 0 for i in range(len(y))]
    Xa = [x for x, t in zip(X, test) if not t]
    ya = [v for v, t in zip(y, test) if not t]
    Xt = [x for x, t in zip(X, test) if t]
    yt = [v for v, t in zip(y, test) if t]

    base = max(sum(yt), len(yt) - sum(yt)) / len(yt)
    lignes.append(f"Référence (classe majoritaire) : {base:.1%}")

    Xa_j, norm = ml.standardiser(jnp.array(Xa))
    Xt_j = (jnp.array(Xt) - norm.moyenne) / norm.ecart_type
    params, pertes = ml.entrainer(ml.init_params(Xa_j.shape[1]), Xa_j, jnp.array(ya))
    lignes.append(
        f"Régression logistique (JAX) : exactitude test {ml.exactitude(params, Xt_j, jnp.array(yt)):.1%}"
        f"   (perte {float(pertes[0]):.3f} -> {float(pertes[-1]):.3f})"
    )

    arbre = elaguer(construire(Xa, ya, profondeur_max=3))
    acc_arbre = sum((predire(arbre, x) > 0.5) == (v > 0.5) for x, v in zip(Xt, yt)) / len(yt)
    lignes += [f"Arbre de décision : exactitude test {acc_arbre:.1%}", "", afficher_arbre(arbre)]
    return "\n".join(lignes)


def programme(s: Services, chemin_csv: str, chemin_rapport: str) -> Effet[str]:
    """DESCRIPTION du programme complet. Rien ne s'exécute ici."""
    return (
        lire_fichier(s, chemin_csv)
        .retry(2)
        .map(charger)
        .tap(lambda ch: afficher(s, f"Chargé : {len(ch.releves)} relevés, {len(ch.rejets)} rejets"))
        .map(analyser)
        .tap(lambda rapport: ecrire_fichier(s, chemin_rapport, rapport))
        .tap(lambda rapport: afficher(s, rapport))
        .catch_all(lambda e: afficher(s, f"Échec : {e}").flat_map(lambda _: succes("")))
    )


def services_reels() -> Services:
    def ecrire(chemin: str, contenu: str) -> None:
        Path(chemin).write_text(contenu, encoding="utf-8")

    return Services(lire=lambda p: Path(p).read_text(encoding="utf-8"), ecrire=ecrire, afficher=print)


def main() -> None:  # pragma: no cover - coquille impérative
    from nimbus.s09_effets import executer

    chemin_csv = sys.argv[1] if len(sys.argv) > 1 else "data/meteo.csv"
    chemin_rapport = sys.argv[2] if len(sys.argv) > 2 else "rapport.txt"
    if not Path(chemin_csv).exists():
        Path(chemin_csv).parent.mkdir(parents=True, exist_ok=True)
        Path(chemin_csv).write_text(generer_csv(), encoding="utf-8")
    match executer(programme(services_reels(), chemin_csv, chemin_rapport)):
        case Ok(_):
            pass
        case Err(e):
            print(f"Erreur fatale : {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
