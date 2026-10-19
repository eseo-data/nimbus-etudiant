import random

from nimbus.s08_trees import (
    Leaf, Node, build, prune, fold_tree, gini, best_split, n_leaves,
    predict, depth,
)

A = Node(1, 70.0,
          Leaf(0.1, 50),
          Node(2, 1010.0, Leaf(0.8, 30), Leaf(0.4, 20)))


def test_predict():
    assert predict(A, [0, 60, 1000]) == 0.1
    assert predict(A, [0, 90, 1000]) == 0.8
    assert predict(A, [0, 90, 1020]) == 0.4


def test_fold_tree():
    assert depth(A) == 2 and depth(Leaf(0.5, 1)) == 0
    assert n_leaves(A) == 3
    assert fold_tree(A, lambda p, n: n, lambda v, s, g, d: g + d) == 100


def test_gini():
    assert gini([]) == 0.0 and gini([1, 1]) == 0.0
    assert gini([0, 1]) == 0.5


def test_best_split_finds_the_signal():
    rng = random.Random(0)
    X = [(rng.random(), rng.random() * 100) for _ in range(200)]
    y = [1.0 if x[1] > 50 else 0.0 for x in X]
    var, threshold, score = best_split(X, y)
    assert var == 1 and 40 < threshold < 60 and score < 0.1


def test_build_and_prune():
    rng = random.Random(1)
    X = [(rng.random() * 100,) for _ in range(300)]
    y = [1.0 if x[0] > 30 else 0.0 for x in X]
    tree = build(X, y, max_depth=4)
    assert isinstance(tree, Node)
    assert depth(tree) <= 4
    assert all((predict(tree, x) > 0.5) == (v > 0.5) for x, v in zip(X, y) if abs(x[0] - 30) > 5)
    # élagage : deux feuilles de même classe fusionnent
    t = Node(0, 1.0, Leaf(0.9, 10), Leaf(0.7, 30))
    assert prune(t) == Leaf(0.75, 40)
    assert prune(A) == A
