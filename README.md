# Nimbus — fil rouge « Programmation fonctionnelle »

ESEO, cycle ingénieur 5e année, spécialité IA & Data, module de 30 h (10 séances de 3 h).

On construit, séance après séance, un **pipeline météo 100 % fonctionnel** : données brutes
→ validation → nettoyage → agrégation → modèle « va-t-il pleuvoir demain ? » → programme
complet piloté par des effets. Les données sont **générées localement**, sans réseau ni GPU :
tout tourne sur un laptop ordinaire.

## Installation (5 minutes)

1. Installer **uv** (gestionnaire Python ultra-rapide, il installe aussi Python 3.12 si besoin) :
   - macOS / Linux : `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows (PowerShell) : `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. Dans ce dossier :
   ```bash
   uv sync                 # crée .venv et installe jax (CPU), pytest, hypothesis, mypy
   uv run pytest           # tous les tests échouent au départ : c'est normal !
   ```
3. Éditeur conseillé : VS Code + extensions Python et Pylance (mode « strict »).

## Travailler une séance

Chaque séance correspond à un module `src/nimbus/sNN_*.py`. Remplacez chaque
`raise NotImplementedError` par votre code, puis :

```bash
uv run pytest tests/test_s03_types_algebriques.py     # les tests de la séance
uv run mypy                                           # le typeur : votre premier relecteur
```

| Séance | Module | Thème |
|---|---|---|
| S1 | `s01_purete.py` (+ `s01_legacy.py`, défi `s01_defi_vecteur.py`) | Pureté, immutabilité, refactoring, hasard pur |
| S2 | `s02_ordre_superieur.py` | Fonctions d'ordre supérieur, composition, curryfication, paresse |
| S3 | `s03_types_algebriques.py` | Types algébriques, filtrage par motif, exhaustivité |
| S4 | `s04_recursion.py` | Récursion, folds, listes persistantes, trampoline |
| S5 | `s05_erreurs.py` | Result, foncteur, monade, validation applicative |
| S6 | `s06_monoides.py` | Monoïdes, lois, tests de propriétés, agrégation parallèle |
| S7 | `s07_ml_fonctionnel.py` | Différentiation automatique, JAX (`grad`, `vmap`, `jit`, `scan`) |
| S8 | `s08_arbres.py` | Arbre de décision comme ADT récursif, catamorphismes |
| S9 | `s09_effets.py` + `app.py` | Effets fonctionnels à la ZIO, cœur pur / coquille impérative |
| S10 | `scala/` | Ouverture Scala 3 : même cœur, garanties du compilateur |

Quand S1 à S9 sont terminées :

```bash
uv run nimbus            # génère data/meteo.csv si besoin, analyse, écrit rapport.txt
```

## Séance 10 — Scala 3

```bash
# macOS : brew install Virtuslab/scala-cli/scala-cli      (ou : brew install scala)
# Windows : winget install virtuslab.scalacli
# Linux : curl -sSLf https://scala-cli.virtuslab.org/get | sh
cd scala
scala-cli test .          # télécharge automatiquement JVM + Scala au premier lancement
scala-cli run .           # lance la démo
```

Pas d'installation possible ? Copiez `scala/Nimbus.scala` dans <https://scastie.scala-lang.org>.

## Défis et bonus

- `tests/test_s01_proprietes.py` : vos premiers tests de propriétés (remplacez les `pytest.skip`).
- `s01_defi_vecteur.py` ★★★ : un vecteur persistant à partage structurel. Facultatif, pour le plaisir
  du défi ; les tests vérifient que vous ne recopiez que le chemin modifié.

## Règles du jeu

- Pas de mutation visible depuis l'extérieur d'une fonction, pas de variable globale,
  pas d'exception pour signaler une erreur métier (on renvoie une valeur).
- Une boucle locale dans une fonction pure est tolérée quand elle est explicitement
  demandée (Python n'a pas d'optimisation de la récursion terminale).
- Les tests fournis ne doivent pas être modifiés ; ajoutez les vôtres dans `tests/`.
