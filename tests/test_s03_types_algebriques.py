from nimbus.s03_types_algebriques import (
    Aberrante, Manquante, Valide, compter_par_type, decrire, est_complet, lire_mesure, lire_releve,
    valeur_ou,
)


def test_lire_mesure():
    assert lire_mesure("12.5", -40, 50) == Valide(12.5)
    assert lire_mesure(" NA ", -40, 50) == Manquante()
    assert lire_mesure("", -40, 50) == Manquante()
    assert lire_mesure("vingt", -40, 50) == Aberrante("vingt", "non numérique")
    assert lire_mesure("999.9", -40, 50) == Aberrante("999.9", "hors bornes")


def test_valeur_ou_et_decrire():
    assert valeur_ou(Valide(3.0), 0.0) == 3.0
    assert valeur_ou(Manquante(), -1.0) == -1.0
    assert decrire(Valide(12.5)) == "12.5"
    assert decrire(Manquante()) == "manquante"
    assert decrire(Aberrante("999", "hors bornes")) == "aberrante (hors bornes) : '999'"


CHAMPS = {"temperature_c": "10", "humidite_pct": "80", "pression_hpa": "1010", "vent_kmh": "5", "pluie_mm": "0"}


def test_lire_releve_et_est_complet():
    r = lire_releve("2025-01-01", "BREST", CHAMPS)
    assert r.temperature_c == Valide(10.0) and est_complet(r)
    r2 = lire_releve("2025-01-01", "BREST", {**CHAMPS, "humidite_pct": "130"})
    assert isinstance(r2.humidite_pct, Aberrante) and not est_complet(r2)


def test_compter_par_type():
    ms = [Valide(1), Valide(2), Manquante(), Aberrante("x", "y")]
    assert compter_par_type(ms) == {"valide": 2, "manquante": 1, "aberrante": 1}
    assert compter_par_type([]) == {"valide": 0, "manquante": 0, "aberrante": 0}
