import pytest

from nimbus.donnees import generer_csv


@pytest.fixture(scope="session")
def csv_petit() -> str:
    return generer_csv(graine=7, n_jours=60)


@pytest.fixture(scope="session")
def csv_complet() -> str:
    return generer_csv()
