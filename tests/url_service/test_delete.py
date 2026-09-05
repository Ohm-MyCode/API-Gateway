def test_delete(client):

    client.post(url = "/shorten",headers={"x-user-id": "1"},json={"url":"https://google.com"})
    response = client.get(url ="/get_urls",headers={"x-user-id": "1"})

    payload = response.json()
    
    response = client.delete(url=f"/delete/{payload[0]['shortcode']}",headers={"x-user-id": "1"})
    assert response.status_code == 200, response.json()

def test_delete_from_diff_user(client):
    client.post(url = "/shorten",headers={"x-user-id": "1"},json={"url":"https://google.com"})
    response = client.get(url ="/get_urls",headers={"x-user-id": "1"})

    payload = response.json()
        
    response = client.delete(url=f"/delete/{payload[0]['shortcode']}",headers={"x-user-id": "3"})
    assert response.status_code == 409, response.json()


def test_no_userid_delete(client):
    client.post(url = "/shorten",headers={"x-user-id": "1"},json={"url":"https://google.com"})
    response = client.get(url ="/get_urls",headers={"x-user-id": "1"})

    payload = response.json()

    response = client.delete(url=f"/delete/{payload[0]['shortcode']}",headers={"x-user-id": ""})
    assert response.status_code == 401, response.json()

def test_no_url_delete(client):
    client.post(url = "/shorten",headers={"x-user-id": "1"},json={"url":"https://google.com"})
    response = client.get(url ="/get_urls",headers={"x-user-id": "1"})
    
    response = client.delete(url="/delete/ ",headers={"x-user-id": "1"})
    assert response.status_code == 422, response.json()

def test_wrongurl_delete(client):
    client.post(url = "/shorten",headers={"x-user-id": "1"},json={"url":"https://google.com"})
    response = client.get(url ="/get_urls",headers={"x-user-id": "1"})
    
    response = client.delete(url="/delete/zyteyhns",headers={"x-user-id": "1"})
    assert response.status_code == 409, response.json()

def test_malformed_url_delete(client):
    client.post(url = "/shorten",headers={"x-user-id": "1"},json={"url":"https://google.com"})
    response = client.get(url ="/get_urls",headers={"x-user-id": "1"})
    
    response = client.delete(url="/delete/zyteyhns32efd",headers={"x-user-id": "1"})
    assert response.status_code == 422, response.json()

def test_for_deletion(client):
    client.post(url = "/shorten",headers={"x-user-id": "1"},json={"url":"https://google.com"})
    response = client.get(url ="/get_urls",headers={"x-user-id": "1"})

    payload = response.json()

    response = client.delete(url=f"/delete/{payload[0]['shortcode']}",headers={"x-user-id": "1"})
    assert response.status_code == 200, response.json()

    response = client.get(url=f"/{payload[0]['shortcode']}")
    assert response.status_code == 404, response.json()

def test_for_repeateddeletion(client):
    client.post(url = "/shorten",headers={"x-user-id": "1"},json={"url":"https://google.com"})
    response = client.get(url ="/get_urls",headers={"x-user-id": "1"})

    payload = response.json()

    response = client.delete(url=f"/delete/{payload[0]['shortcode']}",headers={"x-user-id": "1"})
    assert response.status_code == 200, response.json()

    response = client.delete(url=f"/delete/{payload[0]['shortcode']}",headers={"x-user-id": "1"})
    assert response.status_code == 409, response.json()