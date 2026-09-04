from conftest import client
from nanoid import generate


def createuser():
    email = generate(size=6)
    name = generate(size=6)
    payload = {"email":f"{email}@gmail.com","name":f"{name}","password":"test"}
    response=client.post(url="/signup", json=payload)
    assert response.status_code == 201, response.json()
    return response, payload