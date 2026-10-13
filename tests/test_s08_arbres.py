import random

from nimbus.s08_arbres import (
    Feuille, Noeud, construire, elaguer, fold_arbre, gini, meilleure_coupe, nb_feuilles,
    predire, profondeur,
)

A = Noeud(1, 70.0,
          Feuille(0.1, 50),
          Noeud(2, 1010.0, Feuille(0.8, 30), Feuille(0.4, 20)))


def test_predire():
    assert predire(A, [0, 60, 1000]) == 0.1
    assert predire(A, [0, 90, 1000]) == 0.8
    assert predire(A, [0, 90, 1020]) == 0.4


def test_fold_arbre():
    assert profondeur(A) == 2 and profondeur(Feuille(0.5, 1)) == 0
    assert nb_feuilles(A) == 3
    assert fold_arbre(A, lambda p, n: n, lambda v, s, g, d: g + d) == 100


def test_gini():
    assert gini([]) == 0.0 and gini([1, 1]) == 0.0
    assert gini([0, 1]) == 0.5


def test_meilleure_coupe_trouve_le_signal():
    rng = random.Random(0)
    X = [(rng.random(), rng.random() * 100) for _ in range(200)]
    y = [1.0 if x[1] > 50 else 0.0 for x in X]
    var, seuil, score = meilleure_coupe(X, y)
    assert var == 1 and 40 < seuil < 60 and score < 0.1


def test_construire_et_elaguer():
    rng = random.Random(1)
    X = [(rng.random() * 100,) for _ in range(300)]
    y = [1.0 if x[0] > 30 else 0.0 for x in X]
    arbre = construire(X, y, profondeur_max=4)
    assert isinstance(arbre, Noeud)
    assert profondeur(arbre) <= 4
    assert all((predire(arbre, x) > 0.5) == (v > 0.5) for x, v in zip(X, y) if abs(x[0] - 30) > 5)
    # élagage : deux feuilles de même classe fusionnent
    t = Noeud(0, 1.0, Feuille(0.9, 10), Feuille(0.7, 30))
    assert elaguer(t) == Feuille(0.75, 40)
    assert elaguer(A) == A
