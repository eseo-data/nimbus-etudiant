# Nimbus — fil rouge « Programmation fonctionnelle »

ESEO, cycle ingénieur 5e année, spécialité IA & Data, 8 blocs de 3 h 30 (4 en tronc commun, 4 pour le parcours Big Data).

On construit, séance après séance, un **pipeline météo 100 % fonctionnel** : données brutes
→ validation → nettoyage → agrégation → modèle « va-t-il pleuvoir demain ? » → programme
complet piloté par des effets. Les données sont **générées localement**, sans réseau ni GPU :
tout tourne sur un laptop ordinaire.

## Installation (10 minutes)

1. Installer **uv** (il installe aussi Python 3.12 si besoin) :
   - macOS / Linux : `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows (PowerShell) : `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. Dans ce dossier :
   ```bash
   uv sync                     # tronc commun
   uv run pytest               # presque tous les tests échouent au départ : c'est normal
   ```
3. Parcours Big Data uniquement :
   ```bash
   uv sync --group bigdata     # JAX (CPU), Polars, PySpark ; Spark demande Java 17 ou 21
   uv run python -m nimbus.datagen --massif data/meteo_massif.csv 1000   # ~3,65 M lignes
   ```

## Organisation

| Bloc (3 h 30) | Public | Modules | Thème |
|---|---|---|---|
| 1 | tous | `s01_purity.py`, `s01_legacy.py`, `s01_challenge_vector.py` | purity, immutability, refactoring, random sans side effect |
| 2 | tous | `s02_higher_order.py`, `s03_algebraic_types.py`, `s03_pipeline.py` (défi : `s02_challenge_rules.py`) | higher-order functions, lazy evaluation, algebraic data types |
| 3 | tous | `s04_recursion.py`, `s05_errors.py` | recursion, folds, errors as values |
| 4 | tous | `s09_effects.py`, `app.py`, `scala/` | functional effects, Scala 3, QCM |
| BD1 | Big Data | `s06_monoids.py` | monoids, property-based testing, MapReduce |
| BD2 | Big Data | `bd2_engine.py` | Polars lazy, Spark, query plan, lineage |
| BD3 | Big Data | `bd3_streaming.py` | stream processing : windows, watermark, idempotence |
| BD4 | Big Data | `s07_functional_ml.py`, `s08_trees.py` | JAX, decision tree en ADT, projet |

Les tests d'un bloc : `uv run pytest tests/test_s03_algebraic_types.py`, etc. Les tests qui
demandent JAX, Polars ou Spark sont sautés tant que le groupe `bigdata` n'est pas installé.

```bash
uv run nimbus        # tronc commun (fin du bloc 4) : qualité des données + stats par station
uv run nimbus-bd     # parcours Big Data (fin de BD4) : + monoids, JAX, decision tree
```

## Scala 3 (bloc 4)

```bash
# macOS : brew install Virtuslab/scala-cli/scala-cli    Windows : winget install virtuslab.scalacli
cd scala
scala-cli test .
```

Pas d'installation possible : copiez `scala/Nimbus.scala` dans <https://scastie.scala-lang.org>.

## Défis et bonus

- `tests/test_s01_properties.py` : vos premiers tests de propriétés (remplacez les `pytest.skip`).
- `s01_challenge_vector.py` ★★★ : un vecteur persistant à partage structurel. Facultatif, pour le plaisir
  du défi ; les tests vérifient que vous ne recopiez que le chemin modifié.

## Règles du jeu

- Pas de mutation visible depuis l'extérieur d'une fonction, pas de variable globale,
  pas d'exception pour signaler une erreur métier (on renvoie une valeur).
- Une boucle locale dans une fonction pure est tolérée quand elle est explicitement
  demandée (Python n'a pas d'optimisation de la récursion terminale).
- Les tests fournis ne doivent pas être modifiés ; ajoutez les vôtres dans `tests/`.
- Le code est en anglais (fichiers, fonctions, types), comme la littérature et les bibliothèques
  que vous utiliserez ; les explications restent en français.
