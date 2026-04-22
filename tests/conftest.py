import os
import sys
import time
import subprocess
import pytest
import requests
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Задаём переменные окружения
os.environ["POSTGRES_USER"] = "sVlads4"
os.environ["POSTGRES_PASSWORD"] = "simplepass"
os.environ["POSTGRES_DB"] = "marketplace_db"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DATABASE_URL"] = f"postgresql+asyncpg://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['POSTGRES_DB']}"
os.environ["SECRET_KEY"] = "test-secret-key"

API_BASE_URL = "http://localhost:8000"

class ApiClient:
    """Обёртка над requests.Session, автоматически подставляющая базовый URL."""
    def __init__(self):
        self.session = requests.Session()

    def request(self, method, url, **kwargs):
        full_url = f"{API_BASE_URL}{url}"
        return self.session.request(method, full_url, **kwargs)

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self.request("PUT", url, **kwargs)

    def patch(self, url, **kwargs):
        return self.request("PATCH", url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)

@pytest.fixture(scope="session", autouse=True)
def create_tables():
    from sqlalchemy import create_engine
    from src.database.database import Base
    from src.auth.models import User
    from src.publications.models import Publication, DeletedPublication
    from src.categories.models import Category
    sync_url = f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['POSTGRES_DB']}"
    engine = create_engine(sync_url, echo=False)
    Base.metadata.create_all(bind=engine)
    engine.dispose()
    yield

@pytest.fixture(autouse=True)
def clean_db():
    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"]
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE publications, deleted_publications, users, categories RESTART IDENTITY CASCADE;")
    cur.close()
    conn.close()

@pytest.fixture(scope="session", autouse=True)
def start_server():
    try:
        r = requests.get(f"{API_BASE_URL}/docs", timeout=1)
        if r.status_code == 200:
            yield
            return
    except requests.ConnectionError:
        pass

    env = os.environ.copy()
    cmd = [sys.executable, "-m", "uvicorn", "src:app", "--host", "0.0.0.0", "--port", "8000"]
    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    timeout = 10
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{API_BASE_URL}/docs", timeout=1)
            if r.status_code == 200:
                break
        except requests.ConnectionError:
            time.sleep(0.5)
    else:
        proc.terminate()
        raise RuntimeError("Server did not start")

    yield proc
    proc.terminate()
    proc.wait()

@pytest.fixture
def api_client():
    return ApiClient()

@pytest.fixture
def test_user(api_client):
    # Удаляем пользователя, если он уже существует
    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"]
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE username = 'testuser'")
    cur.close()
    conn.close()

    resp = api_client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass"
    })
    assert resp.status_code == 200, f"Ошибка регистрации: {resp.text}"
    return resp.json()

@pytest.fixture
def auth_token(api_client, test_user):
    resp = api_client.post("/auth/login", data={"username": "testuser", "password": "testpass"})
    assert resp.status_code == 200
    return resp.json()["access_token"]