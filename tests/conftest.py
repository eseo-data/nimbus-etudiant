import pytest

from nimbus.datagen import generate_csv


@pytest.fixture(scope="session")
def csv_small() -> str:
    return generate_csv(seed=7, n_days=60)


@pytest.fixture(scope="session")
def csv_full() -> str:
    return generate_csv()
