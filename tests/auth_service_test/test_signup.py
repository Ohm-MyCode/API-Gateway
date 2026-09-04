from conftest import client


def test_signup():
    response = client.post(url="/signup", json={"email":"abc123@gmail.com","name":"daddy","password":"test"})
    assert response.status_code == 201, response.json()
    response = client.post(url="/signup", json={"email":"abc123@gmail.com","name":"daddy","password":"test"})
    assert response.status_code == 409 , response.json()
    
def test_signup_empty_password():
    response = client.post(url="/signup", json={"email": "emptypass@gmail.com", "name": "daddy", "password": ""})
    assert response.status_code in (400, 422), response.json()

def test_signup_malformed_fields():
    response = client.post(url="/signup", json={"email": "not-an-email", "name": "daddy", "password": "test"})
    assert response.status_code == 422, response.json()
    response = client.post(url="/signup", json={"email":"abc123@gmail.com","name":123,"password":"test"})
    assert response.status_code == 422 , response.json()
    

def test_signup_missing_fields():
    response = client.post(url="/signup", json={"name": "daddy", "password": "test"})
    assert response.status_code == 422, response.json()
 
    response = client.post(url="/signup", json={"email": "nofield@gmail.com", "name": "daddy"})
    assert response.status_code == 422, response.json()
