import dataclasses

import pytest

from nimbus.s01_purete import (
    Releve, ajouter, celsius_vers_fahrenheit, corriger_temperature, filtrer_plausibles,
    moyenne, nettoyer_pur, normaliser,
)

R = Releve("2025-01-01", "VELIZY", 10.0, 80.0)


def test_fahrenheit():
    assert celsius_vers_fahrenheit(0) == 32
    assert celsius_vers_fahrenheit(100) == 212


def test_filtrer_ne_mute_pas_l_entree():
    entree = [10.0, 999.0, 12.0]
    assert filtrer_plausibles(entree) == (10.0, 12.0)
    assert entree == [10.0, 999.0, 12.0]


def test_moyenne():
    assert moyenne([1.0, 2.0, 3.0]) == 2.0
    assert moyenne([]) is None


def test_normaliser():
    assert normaliser([0.0, 5.0, 10.0]) == (0.0, 0.5, 1.0)
    assert normaliser([3.0, 3.0]) == (0.0, 0.0)
    assert normaliser([]) == ()


def test_releve_est_immuable():
    with pytest.raises(dataclasses.FrozenInstanceError):
        R.temperature_c = 0  # type: ignore[misc]


def test_corriger_renvoie_un_nouveau_releve():
    r2 = corriger_temperature(R, 1.5)
    assert r2.temperature_c == 11.5 and R.temperature_c == 10.0
    assert r2.station == R.station


def test_ajouter():
    h = (R,)
    h2 = ajouter(h, R)
    assert len(h) == 1 and len(h2) == 2


def test_nettoyer_pur_transparence_referentielle():
    entree = [10.0, 99.0, 20.0]
    assert nettoyer_pur(entree) == nettoyer_pur(entree) == (15.0, ("nettoyage",))
    assert entree == [10.0, 99.0, 20.0]


# ---------------------------------------------------------------------------
# Partie B — refactoring du script hérité
# ---------------------------------------------------------------------------
import contextlib
import importlib
import io

from nimbus import s01_legacy
from nimbus.s01_purete import (
    alea, alea_n, decouper_apprentissage_test, ligne_station, lire_temperatures, melanger,
    rapport, regrouper, separer,
)

MINI = "en-tete\n2025-01-01,BREST,10.0,80,1010,5,0\n2025-01-01,LYON,NA,80,1010,5,0\n" \
       "2025-01-02,BREST,12.0,80,1010,5,0\ntronquee,BREST,3\n2025-01-03,BREST,999,80,1010,5,0\n"


def sortie_legacy(texte: str) -> str:
    module = importlib.reload(s01_legacy)          # repart d'un état global vierge
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        module.main(texte)
    return buf.getvalue()


def test_lire_temperatures():
    assert lire_temperatures(MINI) == ((("BREST", 10.0), ("BREST", 12.0)), 3)


def test_regrouper_trie():
    assert regrouper([("A", 3.0), ("B", 1.0), ("A", 1.0)]) == {"A": (1.0, 3.0), "B": (1.0,)}


def test_ligne_station():
    assert ligne_station("BREST", [10.0, 12.0]) == \
        "BREST    n=2    moyenne= 11.00  médiane= 12.00  min=  10.0  max=  12.0"


def test_rapport_identique_au_legacy(csv_complet):
    assert rapport(csv_complet) == sortie_legacy(csv_complet)
    assert rapport(MINI) == sortie_legacy(MINI)


def test_le_legacy_n_est_pas_idempotent_mais_rapport_oui(csv_petit):
    importlib.reload(s01_legacy)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        s01_legacy.main(csv_petit)
        premier = buf.getvalue()
        s01_legacy.main(csv_petit)                 # deuxième appel : l'état global s'accumule
    second = buf.getvalue()[len(premier):]
    assert premier != second
    assert rapport(csv_petit) == rapport(csv_petit) == premier


# ---------------------------------------------------------------------------
# Partie C — le hasard, purement
# ---------------------------------------------------------------------------


def test_alea_deterministe_et_uniforme():
    assert alea(42) == alea(42)
    x, e = alea(42)
    assert 0.0 <= x < 1.0 and e != 42
    xs, _ = alea_n(7, 10_000)
    assert len(xs) == 10_000 and abs(sum(xs) / len(xs) - 0.5) < 0.02


def test_alea_n_enchaine_les_etats():
    xs, e = alea_n(1, 3)
    x1, e1 = alea(1)
    x2, e2 = alea(e1)
    x3, e3 = alea(e2)
    assert xs == (x1, x2, x3) and e == e3


def test_melanger_ne_mute_pas_et_permute():
    xs = [1, 2, 3, 4, 5, 6, 7, 8]
    m, _ = melanger(xs, 3)
    assert xs == [1, 2, 3, 4, 5, 6, 7, 8]
    assert sorted(m) == xs and m != tuple(xs)
    assert melanger(xs, 3) == melanger(xs, 3)


def test_separer():
    a, b = separer(10)
    assert a != b
    assert alea_n(a, 5)[0] != alea_n(b, 5)[0]


def test_decoupage_reproductible():
    donnees = tuple(range(100))
    app, test, _ = decouper_apprentissage_test(donnees, 0.2, 2026)
    assert len(test) == 20 and len(app) == 80
    assert sorted(app + test) == list(donnees)
    assert decouper_apprentissage_test(donnees, 0.2, 2026)[:2] == (app, test)
