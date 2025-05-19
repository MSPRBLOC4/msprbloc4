import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from msprbloc4.client.controllers.app import app, get_db
from msprbloc4.client.models.models import Base

# 1) URL de connexion PostgreSQL pour la base de tests
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://openpg:openpgpwd@localhost:5432/client_test_db"

# 2) Crée l'engine connecté à PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3) Crée un sessionmaker associé à cet engine
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Fixture qui se lance au début de la session de tests :
      - crée les tables avant tous les tests
      - les supprime à la fin
    """
    print("==== Création des tables dans la base de tests PostgreSQL ====")
    Base.metadata.create_all(bind=engine)
    yield
    print("==== Suppression des tables après la session de tests ====")
    Base.metadata.drop_all(bind=engine)

def _override_get_db():
    """
    Remplace la dépendance get_db pour que les endpoints
    utilisent la base de tests (TestingSessionLocal).
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    """
    Fixture Pytest pour fournir un TestClient,
    en overrideant la dépendance get_db avant de le créer.
    """
    # Override la dépendance
    app.dependency_overrides[get_db] = _override_get_db

    # Crée le TestClient
    with TestClient(app) as c:
        yield c

    # Nettoyage : retire l'override
    app.dependency_overrides.clear()

def test_create_client_success(client):
    """
    Test de création d'un client en base PostgreSQL de test.
    """
    payload = {"name": "Alice", "email": "alice@example.com"}
    response = client.post("/clients", json=payload)
    assert response.status_code == 201, response.text

    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data

    print("==== Test test_create_client_success passé ====")
