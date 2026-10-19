"""Bloc BD4 (parcours Big Data) : uv sync --group bigdata"""

import pytest

jax = pytest.importorskip("jax")
import jax.numpy as jnp  # noqa: E402

from nimbus import s07_functional_ml as ml  # noqa: E402
from nimbus.s05_errors import load  # noqa: E402


def test_dual_numbers():
    f = lambda x: x ** 3 + 2 * x          # f'(x) = 3x² + 2
    assert ml.derivative(f)(2.0) == pytest.approx(14.0)
    g = lambda x: ml.exp_dual(x * 2.0)    # g'(x) = 2·exp(2x)
    assert ml.derivative(g)(0.5) == pytest.approx(2 * 2.718281828, rel=1e-6)


def test_duals_agree_with_jax():
    assert ml.derivative(lambda x: x * x * 3.0 - x)(1.5) == pytest.approx(
        float(jax.grad(lambda x: x * x * 3.0 - x)(1.5)))


@pytest.fixture(scope="module")
def dataset(csv_full):
    X, y = ml.build_dataset(load(csv_full).readings)
    return X, y


def test_build_dataset(dataset):
    X, y = dataset
    assert len(X) == len(y) > 800
    assert all(len(x) == 5 for x in X)
    assert set(y) == {0.0, 1.0}


def test_standardize():
    Xs, norm = ml.standardize(jnp.array([[1.0, 5.0], [3.0, 5.0]]))
    assert jnp.allclose(Xs.mean(axis=0), 0.0)
    assert jnp.allclose(norm.std_dev, jnp.array([1.0, 1.0]))   # colonne constante -> 1.0


def test_vmap_equals_a_loop():
    p = ml.Params(jnp.array([1.0, -2.0]), jnp.array(0.5))
    X = jnp.array([[0.0, 1.0], [2.0, 0.0], [1.0, 1.0]])
    loop = jnp.array([ml.predict_one(p, x) for x in X])
    assert jnp.allclose(ml.predict_batch(p, X), loop)


def test_gradient_step_is_pure():
    p0 = ml.init_params(2)
    X, y = jnp.array([[1.0, 0.0], [0.0, 1.0]]), jnp.array([1.0, 0.0])
    p1 = ml.gradient_step(p0, X, y, 0.1)
    assert float(jnp.abs(p0.w).sum()) == 0.0        # p0 inchangé
    assert float(ml.loss(p1, X, y)) < float(ml.loss(p0, X, y))


def test_training(dataset):
    X, y = dataset
    Xs, _ = ml.standardize(jnp.array(X))
    p, hist = ml.train(ml.init_params(5), Xs, jnp.array(y), lr=0.5, n_iter=200)
    assert hist.shape == (200,)
    assert float(hist[-1]) < float(hist[0])
    assert ml.accuracy(p, Xs, jnp.array(y)) > 0.65
