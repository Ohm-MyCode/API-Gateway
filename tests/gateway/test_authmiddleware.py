import jwt

from auth_service.config import settings


def test_missing_token(client):
    response = client.get("/protected/test")
    assert response.status_code == 401

def test_malformed_token(client):
    response = client.get("/protected/test", headers={"Authorization":"bearer abc123.saddsa.asdas"})
    assert response.status_code == 401, response.json()

def test_empty_token(client):
    response = client.get("/protected/test", headers={"Authorization":""})
    assert response.status_code == 401, response.json()

def test_actual_token(client):
    token = jwt.encode({"sub":"123","type":"access"}, settings.PRIVATE_KEY ,algorithm=settings.JWT_ALGORITHM)
    response = client.get("/protected/test", headers={"Authorization":f"bearer {token}"})
    assert response.status_code == 200, response.json()
    payload= response.json()
    assert int(payload["userid"])== 123

    #testing for incorrect token type
    response = client.get("/protected/test", headers={"Authorization":f"Buttons {token}"})
    assert response.status_code == 401, response.json()

def test_wrongtokentype(client):
    token = jwt.encode({"sub":"123","type":"refresh"}, settings.PRIVATE_KEY ,
                       algorithm=settings.JWT_ALGORITHM)
    response = client.get("/protected/test", headers={"Authorization":f"bearer {token}"})
    assert response.status_code == 401, response.json()