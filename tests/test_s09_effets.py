from nimbus.app import analyser, programme
from nimbus.donnees import generer_csv
from nimbus.s05_erreurs import Err, Ok, charger
from nimbus.s09_effets import (
    Services, echec, executer, pour_chaque, succes, suspendre,
)


def test_un_programme_est_une_valeur():
    journal = []
    p = suspendre(lambda: journal.append("effet!"))
    assert journal == []                   # construire n'exécute rien
    executer(p)
    executer(p)
    assert journal == ["effet!", "effet!"]  # on peut l'exécuter plusieurs fois


def test_map_zip_tap():
    assert executer(succes(2).map(lambda x: x * 10)) == Ok(20)
    assert executer(succes(1).zip(succes("a"))) == Ok((1, "a"))
    vu = []
    assert executer(succes(3).tap(lambda x: suspendre(lambda: vu.append(x)))) == Ok(3)
    assert vu == [3]


def test_echecs_et_rattrapage():
    boom = suspendre(lambda: 1 / 0)
    r = executer(boom.map(lambda x: x + 1))
    assert isinstance(r, Err) and isinstance(r.erreur, ZeroDivisionError)
    assert executer(boom.or_else(succes(0))) == Ok(0)
    assert executer(echec(ValueError("x")).catch_all(lambda e: succes(str(e)))) == Ok("x")


def test_retry_capteur_instable():
    tentatives = []

    def capteur():
        tentatives.append(1)
        if len(tentatives) < 3:
            raise IOError("capteur muet")
        return 21.5

    assert executer(suspendre(capteur).retry(5)) == Ok(21.5)
    assert len(tentatives) == 3
    tentatives.clear()
    assert isinstance(executer(suspendre(capteur).retry(1)), Err)


def test_pile_sure():
    p = succes(0)
    for _ in range(50_000):
        p = p.flat_map(lambda x: succes(x + 1))
    assert executer(p) == Ok(50_000)
    assert executer(pour_chaque(range(1000), lambda i: succes(i * i))).valeur[-1] == 999 * 999


def test_programme_complet_avec_faux_services():
    fichiers = {"in.csv": generer_csv(n_jours=120)}
    console = []
    s = Services(lire=fichiers.__getitem__, ecrire=fichiers.__setitem__, afficher=console.append)
    r = executer(programme(s, "in.csv", "out.txt"))
    assert isinstance(r, Ok)
    assert "Rapport Nimbus" in fichiers["out.txt"]
    assert console[0].startswith("Chargé")


def test_fichier_absent_gere_proprement():
    console = []
    s = Services(lire={}.__getitem__, ecrire=lambda p, c: None, afficher=console.append)
    assert executer(programme(s, "absent.csv", "out.txt")) == Ok("")
    assert console[-1].startswith("Échec")


def test_analyser_est_pur():
    ch = charger(generer_csv(n_jours=90))
    assert analyser(ch) == analyser(ch)
