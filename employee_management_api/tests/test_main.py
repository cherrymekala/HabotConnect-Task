from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from auth import hash_password
from models import User

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

test_user = {"username": "testuser", "password": "securepassword123"}
test_employee = {
    "name": "Alice",
    "email": "alice@example.com",
    "department": "HR",
    "role": "Manager"
}

def test_register_user():
    response = client.post("/register", json=test_user)
    assert response.status_code == 201
    assert response.json() == {"message": "User created successfully"}

def test_login_user():
    response = client.post("/token", data={"username": test_user["username"], "password": test_user["password"]})
    assert response.status_code == 200
    assert "access_token" in response.json()
    return response.json()["access_token"]

def test_create_employee():
    token = test_login_user()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/employees/", json=test_employee, headers=headers)
    assert response.status_code == 201
    assert response.json()["name"] == test_employee["name"]

def test_list_employees():
    token = test_login_user()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/employees/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["name"] == test_employee["name"]

def test_retrieve_employee():
    token = test_login_user()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/employees/1", headers=headers) 
    assert response.status_code == 200
    assert response.json()["name"] == test_employee["name"]

def test_update_employee():
    token = test_login_user()
    headers = {"Authorization": f"Bearer {token}"}
    updated_employee = {"name": "Alice", "email": "alice@example.com", "department": "HR", "role": "Senior Manager"}
    response = client.put("/api/employees/1", json=updated_employee, headers=headers) 
    assert response.status_code == 200
    assert response.json()["role"] == "Senior Manager"

def test_delete_employee():
    token = test_login_user()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/api/employees/1", headers=headers) 
    assert response.status_code == 204
    response = client.get("/api/employees/1", headers=headers)
    assert response.status_code == 404

