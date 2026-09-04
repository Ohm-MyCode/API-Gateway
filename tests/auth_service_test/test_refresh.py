from conftest import client
from helper import createuser


def test_refresh_flow():
    _,payload= createuser()
    payload.pop("name",None)
    response2 = client.post(url="/login", json=payload)
    assert response2.status_code == 200, response2.json()

    response3 = client.post("/refresh",cookies={"refresh_token": response2.cookies["refresh_token"]})
    assert response3.status_code == 200,response3.json()
    assert response3.cookies["refresh_token"]!=response2.cookies["refresh_token"]

    response4=client.post("/refresh",cookies={"refresh_token": response2.cookies["refresh_token"]})
    assert response4.status_code == 401, response4.json()

    response5=client.post("/refresh", cookies={"refresh_token":""})
    assert response5.status_code == 401, response5.json()

    response6=client.post("/refresh", cookies={"refresh_token":"12345"})
    assert response6.status_code == 401, response5.json()

def test_refresh_two_users_do_not_interfere():
    _, payload_a = createuser()
    _, payload_b = createuser()
    payload_a.pop("name", None)
    payload_b.pop("name", None)
 
    login_a = client.post(url="/login", json=payload_a)
    login_b = client.post(url="/login", json=payload_b)
 
    refresh_a = client.post("/refresh", cookies={"refresh_token": login_a.cookies["refresh_token"]})
    assert refresh_a.status_code == 200, refresh_a.json()
 
    refresh_b = client.post("/refresh", cookies={"refresh_token": login_b.cookies["refresh_token"]})
    assert refresh_b.status_code == 200, refresh_b.json()
