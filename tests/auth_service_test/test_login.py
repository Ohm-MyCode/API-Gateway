from conftest import client
from helper import createuser


def test_login_flow():
    _,payload= createuser()
    payload.pop("name",None)
    response2 = client.post(url="/login", json=payload)
    assert response2.status_code == 200, response2.json()
    assert "refresh_token" in response2.cookies
    assert "access_token" in response2.json()

    payload2 = payload.copy()

    payload2["email"]= "notemail"
    response3=client.post(url="/login", json=payload2)
    assert response3.status_code == 422, response3.json()

    payload2["email"]= ""
    response3=client.post(url="/login", json=payload2)
    assert response3.status_code == 422, response3.json()

    payload["password"]= "wrongpass"
    response3=client.post(url="/login", json=payload)
    assert response3.status_code == 401, response3.json()

    payload.pop("password",None)
    response3=client.post(url="/login", json=payload)
    assert response3.status_code == 422, response3.json()