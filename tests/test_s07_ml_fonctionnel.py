import jax
import jax.numpy as jnp
import pytest

from nimbus import s07_ml_fonctionnel as ml
from nimbus.s05_erreurs import charger


def test_nombres_duaux():
    f = lambda x: x ** 3 + 2 * x          # f'(x) = 3x² + 2
    assert ml.derivee(f)(2.0) == pytest.approx(14.0)
    g = lambda x: ml.exp_dual(x * 2.0)    # g'(x) = 2·exp(2x)
    assert ml.derivee(g)(0.5) == pytest.approx(2 * 2.718281828, rel=1e-6)


def test_duaux_coherents_avec_jax():
    assert ml.derivee(lambda x: x * x * 3.0 - x)(1.5) == pytest.approx(
        float(jax.grad(lambda x: x * x * 3.0 - x)(1.5)))


@pytest.fixture(scope="module")
def jeu(csv_complet):
    X, y = ml.construire_jeu(charger(csv_complet).releves)
    return X, y


def test_construire_jeu(jeu):
    X, y = jeu
    assert len(X) == len(y) > 800
    assert all(len(x) == 5 for x in X)
    assert set(y) == {0.0, 1.0}


def test_standardiser():
    Xs, norm = ml.standardiser(jnp.array([[1.0, 5.0], [3.0, 5.0]]))
    assert jnp.allclose(Xs.mean(axis=0), 0.0)
    assert jnp.allclose(norm.ecart_type, jnp.array([1.0, 1.0]))   # colonne constante -> 1.0


def test_vmap_equivaut_a_une_boucle():
    p = ml.Params(jnp.array([1.0, -2.0]), jnp.array(0.5))
    X = jnp.array([[0.0, 1.0], [2.0, 0.0], [1.0, 1.0]])
    boucle = jnp.array([ml.predire_un(p, x) for x in X])
    assert jnp.allclose(ml.predire_lot(p, X), boucle)


def test_pas_gradient_est_pur():
    p0 = ml.init_params(2)
    X, y = jnp.array([[1.0, 0.0], [0.0, 1.0]]), jnp.array([1.0, 0.0])
    p1 = ml.pas_gradient(p0, X, y, 0.1)
    assert float(jnp.abs(p0.w).sum()) == 0.0        # p0 inchangé
    assert float(ml.perte(p1, X, y)) < float(ml.perte(p0, X, y))


def test_entrainement(jeu):
    X, y = jeu
    Xs, _ = ml.standardiser(jnp.array(X))
    p, hist = ml.entrainer(ml.init_params(5), Xs, jnp.array(y), lr=0.5, n_iter=200)
    assert hist.shape == (200,)
    assert float(hist[-1]) < float(hist[0])
    assert ml.exactitude(p, Xs, jnp.array(y)) > 0.65
