"""Tests du défi (facultatif). Lancer : uv run pytest tests/test_s01_defi_vecteur.py"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from nimbus.s01_defi_vecteur import (
    BITS, VIDE, Vecteur, ajouter, depuis, obtenir, profondeur, remplacer, retirer_dernier,
    vers_tuple,
)


def noeuds(v: Vecteur) -> dict[int, tuple]:
    """Tous les nœuds internes et feuilles de l'arbre, indexés par identité."""
    vus: dict[int, tuple] = {}

    def visiter(n, niveau):
        vus[id(n)] = n
        if niveau > 0:
            for e in n:
                visiter(e, niveau - BITS)

    if v.taille:
        visiter(v.racine, v.decalage)
    return vus


def invariants(v: Vecteur) -> None:
    def verifier(n, niveau):
        assert isinstance(n, tuple) and 0 < len(n) <= 1 << BITS
        if niveau > 0:
            for e in n:
                verifier(e, niveau - BITS)

    if v.taille == 0:
        assert v.racine == ()
        return
    verifier(v.racine, v.decalage)
    if v.decalage > 0:
        assert len(v.racine) >= 2, "une racine à un seul enfant doit être aplatie"
    assert v.taille <= 1 << (v.decalage + BITS)


@pytest.mark.parametrize("n", [0, 1, 31, 32, 33, 1023, 1024, 1025, 40_000])
def test_depuis_et_vers_tuple(n):
    v = depuis(range(n))
    assert len(v) == n
    assert vers_tuple(v) == tuple(range(n))
    invariants(v)


def test_obtenir():
    v = depuis(range(1100))
    assert all(obtenir(v, i) == i for i in range(1100))
    with pytest.raises(IndexError):
        obtenir(v, 1100)
    with pytest.raises(IndexError):
        obtenir(VIDE, 0)


def test_hauteur_logarithmique():
    assert profondeur(depuis(range(32))) == 1
    assert profondeur(depuis(range(33))) == 2
    assert profondeur(depuis(range(32 ** 2 + 1))) == 3


def test_remplacer_est_persistant():
    v1 = depuis(range(100))
    v2 = remplacer(v1, 50, "x")
    assert obtenir(v2, 50) == "x" and obtenir(v1, 50) == 50
    assert vers_tuple(v1) == tuple(range(100))


@pytest.mark.parametrize("operation", ["remplacer", "ajouter", "retirer_dernier"])
def test_partage_structurel(operation):
    v1 = depuis(range(40_000))                       # 4 niveaux
    v2 = {"remplacer": lambda: remplacer(v1, 12_345, -1),
          "ajouter": lambda: ajouter(v1, -1),
          "retirer_dernier": lambda: retirer_dernier(v1)}[operation]()
    anciens, nouveaux = noeuds(v1), noeuds(v2)
    crees = set(nouveaux) - set(anciens)
    assert len(crees) <= profondeur(v1) + 1, \
        f"{len(crees)} nœuds recréés : le chemin seul doit être recopié"
    assert len(nouveaux) - len(crees) > 1000, "l'essentiel de l'arbre doit être partagé"


def test_retirer_dernier():
    v = depuis(range(33))
    v = retirer_dernier(v)
    assert vers_tuple(v) == tuple(range(32)) and v.decalage == 0
    invariants(v)
    assert retirer_dernier(depuis([1])) == VIDE
    with pytest.raises(IndexError):
        retirer_dernier(VIDE)


operations = st.lists(
    st.one_of(
        st.tuples(st.just("ajouter"), st.integers()),
        st.tuples(st.just("remplacer"), st.integers(min_value=0), st.integers()),
        st.just(("retirer",)),
    ),
    max_size=120,
)


@settings(max_examples=150, deadline=None)
@given(st.integers(min_value=0, max_value=2_100), operations)
def test_equivalent_au_modele_tuple(n_initial, ops):
    """Le vecteur se comporte exactement comme un tuple, quelle que soit la séquence d'opérations."""
    v, modele = depuis(range(n_initial)), tuple(range(n_initial))
    for op in ops:
        if op[0] == "ajouter":
            v, modele = ajouter(v, op[1]), (*modele, op[1])
        elif op[0] == "remplacer" and modele:
            i = op[1] % len(modele)
            v, modele = remplacer(v, i, op[2]), (*modele[:i], op[2], *modele[i + 1:])
        elif op[0] == "retirer" and modele:
            v, modele = retirer_dernier(v), modele[:-1]
        assert len(v) == len(modele)
    assert vers_tuple(v) == modele
    invariants(v)
