import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_successful_formula(client):
    response = client.post("/api/execute-formula", json={
        "data": [
            {"id": 1, "product": "Laptop", "unitPrice": "1000 USD", "quantity": 5, "discount": "10%"},
            {"id": 2, "product": "Smartphone", "unitPrice": "500 USD", "quantity": 10, "discount": "5%"}
        ],
        "formulas": [
            {
                "outputVar": "revenue",
                "expression": "((unitPrice * quantity) - (unitPrice * quantity * (discount / 100)))",
                "inputs": [
                    {"varName": "unitPrice", "varType": "currency"},
                    {"varName": "quantity", "varType": "number"},
                    {"varName": "discount", "varType": "percentage"}
                ]
            }
        ]
    })
    assert response.status_code == 200
    response_json = response.json()
    assert "revenue" in response_json["results"]
    assert response_json["status"] == "success"
    assert "message" in response_json
    assert len(response_json["results"]["revenue"]) == 2

def test_successful_formula_with_multiple_formulas(client):
    response = client.post("/api/execute-formula", json={
        "data": [
            {"id": 1, "product": "Laptop", "unitPrice": "1000 USD", "quantity": 5, "discount": "10%"},
            {"id": 2, "product": "Smartphone", "unitPrice": "500 USD", "quantity": 10, "discount": "5%"}
        ],
        "formulas": [
            {
                "outputVar": "revenue",
                "expression": "((unitPrice * quantity) - (unitPrice * quantity * (discount / 100)))",
                "inputs": [
                    {"varName": "unitPrice", "varType": "currency"},
                    {"varName": "quantity", "varType": "number"},
                    {"varName": "discount", "varType": "percentage"}
                ]
            },
            {
                "outputVar": "totalRevenue",
                "expression": "sum(revenue)",
                "inputs": [
                    {"varName": "revenue", "varType": "currency"}
                ]
            }
        ]
    })
    assert response.status_code == 200
    response_json = response.json()
    assert "revenue" in response_json["results"]
    assert "totalRevenue" in response_json["results"]
    assert response_json["status"] == "success"
    assert "message" in response_json

def test_invalid_expression(client):
    response = client.post("/api/execute-formula", json={
        "data": [{"id": 1, "product": "Laptop", "unitPrice": "1000 USD", "quantity": 5, "discount": "10%"}],
        "formulas": [{"outputVar": "revenue", "expression": "unitPrice *", "inputs": [{"varName": "unitPrice", "varType": "currency"}, {"varName": "quantity", "varType": "number"}]}]
    })
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["status"] == "error"
    assert "message" in response_json

def test_invalid_variable(client):
    response = client.post("/api/execute-formula", json={
        "data": [{"id": 1, "product": "Laptop", "unitPrice": "1000 USD", "quantity": 5, "discount": "10%"}],
        "formulas": [{"outputVar": "revenue", "expression": "unitPrice * invalidVariable", "inputs": [{"varName": "unitPrice", "varType": "currency"}]}]
    })
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["status"] == "error"
    assert "message" in response_json

def test_empty_data(client):
    response = client.post("/api/execute-formula", json={
        "data": [],
        "formulas": [{"outputVar": "revenue", "expression": "unitPrice * quantity", "inputs": [{"varName": "unitPrice", "varType": "currency"}, {"varName": "quantity", "varType": "number"}]}]
    })
    assert response.status_code == 200
    response_json = response.json()
    assert "revenue" in response_json["results"]
    assert response_json["status"] == "success"
    assert response_json["message"] == "The formulas were executed successfully."
    assert response_json["results"]["revenue"] == []

def test_large_dataset(client):
    data = [{"id": i, "product": "Product", "unitPrice": "100 USD", "quantity": 10, "discount": "5%"} for i in range(1000)]
    response = client.post("/api/execute-formula", json={
        "data": data,
        "formulas": [{"outputVar": "revenue", "expression": "unitPrice * quantity - (unitPrice * quantity * (discount / 100))", "inputs": [{"varName": "unitPrice", "varType": "currency"}, {"varName": "quantity", "varType": "number"}, {"varName": "discount", "varType": "percentage"}]}]
    })
    assert response.status_code == 200
    response_json = response.json()
    assert "revenue" in response_json["results"]
    assert response_json["status"] == "success"
    assert len(response_json["results"]["revenue"]) == 1000

def test_edge_cases(client):
    response = client.post("/api/execute-formula", json={
        "data": [{"id": 1, "product": "Laptop", "unitPrice": "1000 USD", "quantity": 5, "discount": "10%"}],
        "formulas": [{"outputVar": "revenue", "expression": "unitPrice * quantity / 0", "inputs": [{"varName": "unitPrice", "varType": "currency"}, {"varName": "quantity", "varType": "number"}]}]
    })
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["status"] == "error"
    assert "message" in response_json
