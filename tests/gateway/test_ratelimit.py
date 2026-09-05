import jwt
from httpx import Response

from auth_service.config import settings


def test_authenticateduser_ratelimit(client):
    valid_auth = jwt.encode({"sub":"123","type":"access"}, settings.PRIVATE_KEY ,
                           algorithm=settings.JWT_ALGORITHM)
    r1 = client.get("/protected/test", headers={"Authorization":f"bearer {valid_auth}"})
    assert r1.status_code == 200

    r2 = client.get("/protected/test", headers={"Authorization":f"bearer {valid_auth}"})
    assert r2.status_code == 200

    r3 = client.get("/protected/test", headers={"Authorization":f"bearer {valid_auth}"})
    assert r3.status_code == 429

    valid_auth = jwt.encode({"sub":"1234","type":"access"}, settings.PRIVATE_KEY ,
                               algorithm=settings.JWT_ALGORITHM)
    r4 = client.get("/protected/test", headers={"Authorization":f"bearer {valid_auth}"})
    assert r4.status_code == 200

def test_unautheticated_user_limit(client, respx_mock):
    respx_mock.get("http://auth-service:8000/login").mock(return_value=Response(200,json={"message": "ok"}))
    response =client.get(url="http://auth-service:8000/auth/login")
    assert response.status_code == 200, response.json()
    response =client.get(url="http://auth-service:8000/auth/login")
    assert response.status_code == 429, response.json()