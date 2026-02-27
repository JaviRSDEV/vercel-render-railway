import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db, Base

# 1. Configuración de Base de Datos de Test (SQLite en memoria/archivo)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Sobrescribimos la dependencia para que la API use la DB de tests
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# 3. Fixture: Crea y destruye las tablas antes y después de cada test
@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# --- TESTS ---

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_items_protected():
    """Verifica que el endpoint rechaza a usuarios sin token"""
    response = client.get("/api/items")
    assert response.status_code == 401

def test_full_auth_flow():
    """Prueba el registro, el login y el acceso con token"""
    user_data = {"username": "testuser", "password": "testpassword"}
    
    # 1. Registro (Usa JSON)
    res_register = client.post("/api/auth/register", json=user_data)
    assert res_register.status_code == 201
    
    # 2. Login (Debe usar data= para simular un formulario, no json)
    res_login = client.post("/token", data=user_data)
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]
    
    # 3. Acceder a ruta protegida enviando el Token en las cabeceras
    headers = {"Authorization": f"Bearer {token}"}
    res_items = client.get("/api/items", headers=headers)
    assert res_items.status_code == 200