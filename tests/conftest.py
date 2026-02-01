# tests/conftest.py (fragment - zastępuje zwykły import api)
import pytest
import time
from threading import Thread
from werkzeug.serving import make_server
import importlib.util
from pathlib import Path

# wczytaj api.py z katalogu projektu (rodzic tests/)
project_root = Path(__file__).resolve().parents[1]
api_path = project_root / "api.py"

spec = importlib.util.spec_from_file_location("project_api", str(api_path))
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)

@pytest.fixture(scope="session", autouse=True)
def start_live_server():
    server = make_server("127.0.0.1", 5000, api.app)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)
    yield
    server.shutdown()
    thread.join()


@pytest.fixture
def client():
    api.app.config["TESTING"] = True
    with api.app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clear_registry():
    api.registry.accounts.clear()
    yield
    api.registry.accounts.clear()