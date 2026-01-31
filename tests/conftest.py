import pytest
import api

@pytest.fixture
def client():
    api.app.config["TESTING"] = True
    with api.app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def clear_registry():
    api.registry.accounts.clear()
