from conftest import client
from helper import createuser


def test_logout_flow():
    response,payload= createuser()
    payload.pop("name",None)

    response2 = client.post(url="/login", json=payload)
    assert response2.status_code == 200, response2.json()

    response3 = client.post(url="/logout", cookies= {"refresh_token":response2.cookies["refresh_token"]})
    assert response3.status_code == 200, response3.json()

    response3 = client.post(url="/logout", cookies= {"refresh_token":response2.cookies["refresh_token"]})
    assert response3.status_code == 200, response3.json() #logout twice test expected 200 coz if logged out user tries again it doesnt matter.
    

    response = client.post("/refresh",cookies={"refresh_token": response2.cookies["refresh_token"]})
    assert response.status_code == 401, response.json()