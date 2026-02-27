import pytest
from fastapi.testclient import TestClient
from main import app  # Asegúrate de que el import coincida con tu archivo

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_items_protected():
    response = client.get("/api/items")
    assert response.status_code == 401

def test_full_auth_flow():
    """Test de Registro -> Login -> Acceso Protegido"""
    user_data = {"username": "testuser", "password": "testpassword"}
    
    # 1. Registro
    client.post("/api/auth/register", json=user_data)
    
    # 2. Login para obtener token
    login_response = client.post("/token", data=user_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Acceder a ruta protegida
    response = client.get("/api/items", headers=headers)
    assert response.status_code == 200