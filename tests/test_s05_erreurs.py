from nimbus.s03_types_algebriques import Aberrante
from nimbus.s05_erreurs import (
    Echecs, Err, Ok, Succes, charger, combiner, essayer, traverse, valider, valider_ligne,
)


def inverse(x: float):
    return Err("division par zéro") if x == 0 else Ok(1 / x)


def test_foncteur_et_monade():
    assert Ok(2).map(lambda x: x + 1) == Ok(3)
    assert Err("e").map(lambda x: x + 1) == Err("e")
    assert Ok(4).flat_map(inverse) == Ok(0.25)
    assert Ok(0).flat_map(inverse).map(lambda x: x * 2) == Err("division par zéro")


def test_lois_du_foncteur():
    for r in (Ok(3), Err("x")):
        assert r.map(lambda x: x) == r
        f, g = (lambda x: x + 1), (lambda x: x * 2)
        assert r.map(f).map(g) == r.map(lambda x: g(f(x)))


def test_essayer():
    assert essayer(lambda: int("42")) == Ok(42)
    r = essayer(lambda: int("quarante"))
    assert isinstance(r, Err) and r.erreur.startswith("ValueError")


def test_traverse_s_arrete_au_premier_echec():
    assert traverse([1, 2, 4], inverse) == Ok([1.0, 0.5, 0.25])
    assert traverse([1, 0, 0], inverse) == Err("division par zéro")


def test_combiner_accumule():
    assert combiner(Succes(1), Succes("a")) == Succes((1, "a"))
    assert combiner(valider(False, 1, "e1"), Succes(2), valider(False, 3, "e2")) == Echecs(("e1", "e2"))


def test_valider_ligne():
    ok = valider_ligne("2025-01-01,BREST,10,80,1010,5,0".split(","))
    assert isinstance(ok, Succes) and ok.valeur.station == "BREST"
    # une mesure aberrante ne fait PAS échouer la ligne
    ab = valider_ligne("2025-01-01,BREST,999,80,1010,5,0".split(","))
    assert isinstance(ab, Succes) and isinstance(ab.valeur.temperature_c, Aberrante)
    # deux erreurs structurelles sont TOUTES les deux signalées
    ko = valider_ligne("2025/01/01,ATLANTIS,10,80,1010,5,0".split(","))
    assert isinstance(ko, Echecs) and len(ko.erreurs) == 2
    assert valider_ligne(["a", "b"]) == Echecs(("attendu 7 colonnes, reçu 2",))


def test_charger(csv_complet):
    ch = charger(csv_complet)
    assert len(ch.releves) + len(ch.rejets) == 3 * 365
    assert len(ch.rejets) > 0
    assert all(n >= 2 for n, _ in ch.rejets)
