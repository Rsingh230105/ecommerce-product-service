from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "product-service"
    }
    
def test_create_product():
    response = client.post(
        "/products",
        json={
            "name": "Test Laptop",
            "description": "Test laptop for pytest",
            "price": 50000,
            "quantity": 10
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test Laptop"
    assert data["price"] == 50000
    assert data["quantity"] == 10
    assert "id" in data
    
    
def test_get_products():
    response = client.get("/products")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    

def test_get_product_by_id():
    create_response = client.post(
        "/products",
        json={
            "name": "Test Phone",
            "description": "Phone for pytest",
            "price": 25000,
            "quantity": 5
        }
    )

    assert create_response.status_code == 200

    product_id = create_response.json()["id"]

    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert data["name"] == "Test Phone"
    assert data["price"] == 25000
    
    
def test_update_product():
    create_response = client.post(
        "/products",
        json={
            "name": "Old Laptop",
            "description": "Old description",
            "price": 40000,
            "quantity": 5
        }
    )

    assert create_response.status_code == 200

    product_id = create_response.json()["id"]

    response = client.put(
        f"/products/{product_id}",
        json={
            "name": "Updated Laptop",
            "description": "Updated description",
            "price": 45000,
            "quantity": 10
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert data["name"] == "Updated Laptop"
    assert data["price"] == 45000
    assert data["quantity"] == 10
    

def test_delete_product():
    create_response = client.post(
        "/products",
        json={
            "name": "Delete Laptop",
            "description": "Product for delete test",
            "price": 30000,
            "quantity": 3
        }
    )

    assert create_response.status_code == 200

    product_id = create_response.json()["id"]

    response = client.delete(f"/products/{product_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Product deleted successfully"

    get_response = client.get(f"/products/{product_id}")

    assert get_response.status_code == 404
    
def test_get_product_not_found():
    response = client.get("/products/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Product not found"
    }
    
    
def test_create_product_validation():
    response = client.post(
        "/products",
        json={
            "name": "",
            "description": "Invalid product",
            "price": -100,
            "quantity": -5
        }
    )

    assert response.status_code == 422