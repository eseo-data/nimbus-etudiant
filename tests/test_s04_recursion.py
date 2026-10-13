import operator

from nimbus.s03_types_algebriques import Aberrante, Manquante, Valide
from nimbus.s04_recursion import (
    VIDE, Cons, combler_trous, depuis, fold_left, fold_right, inverser, longueur, map_liste,
    scan_left, somme_trampoline, vers_liste_python,
)


def test_longueur():
    assert longueur(VIDE) == 0
    assert longueur(depuis([1, 2, 3])) == 3


def test_folds():
    l = depuis(["a", "b", "c"])
    assert fold_left(l, "", operator.add) == "abc"
    assert fold_right(l, "", operator.add) == "abc"
    assert fold_left(depuis([1, 2, 3]), 0, operator.sub) == -6        # ((0-1)-2)-3
    assert fold_right(depuis([1, 2, 3]), 0, operator.sub) == 2        # 1-(2-(3-0))


def test_inverser_et_map():
    assert vers_liste_python(inverser(depuis([1, 2, 3]))) == [3, 2, 1]
    assert vers_liste_python(map_liste(depuis([1, 2, 3]), lambda x: x * 10)) == [10, 20, 30]


def test_partage_structurel():
    queue = depuis([2, 3])
    l1, l2 = Cons(1, queue), Cons(0, queue)
    assert l1.queue is l2.queue     # rien n'a été copié


def test_scan_et_combler():
    assert scan_left([1, 2, 3], 0, operator.add) == [0, 1, 3, 6]
    ms = [Manquante(), Valide(1.0), Manquante(), Aberrante("x", "y"), Valide(4.0)]
    assert combler_trous(ms) == [None, 1.0, 1.0, 1.0, 4.0]


def test_trampoline_ne_depasse_pas_la_pile():
    grande = depuis(range(100_000))
    assert somme_trampoline(grande) == sum(range(100_000))
