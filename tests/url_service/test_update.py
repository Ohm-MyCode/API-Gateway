def test_update(client):
    client.post("/shorten",headers={"x-user-id": "1"},json={"url": "https://google.com"})

    response = client.get("/get_urls",headers={"x-user-id": "1"})

    shortcode = response.json()[0]["shortcode"]

    response = client.patch(f"/update/{shortcode}",headers={"x-user-id": "1"},
                            json={"url": "https://youtube.com"})

    assert response.status_code == 200, response.json()

def test_if_getting_updated(client):
    client.post("/shorten",headers={"x-user-id": "1"},json={"url": "https://google.com"})

    response = client.get("/get_urls",headers={"x-user-id": "1"})

    shortcode = response.json()[0]["shortcode"]
    originalurl = response.json()[0]["original_url"]

    response = client.patch(f"/update/{shortcode}",headers={"x-user-id": "1"},
                            json={"url": "https://youtube.com"})

    assert response.status_code == 200, response.json()

    response = client.get("/get_urls",headers={"x-user-id": "1"})
    new_url = response.json()[0]["original_url"]
    assert new_url!=originalurl
    assert new_url == "https://youtube.com"


def test_update_from_diff_user(client):
    client.post("/shorten",headers={"x-user-id": "1"},json={"url": "https://google.com"})

    response = client.get("/get_urls",headers={"x-user-id": "1"})

    shortcode = response.json()[0]["shortcode"]

    response = client.patch(f"/update/{shortcode}",headers={"x-user-id": "3"},
                            json={"url": "https://youtube.com"})

    assert response.status_code == 409, response.json()

def test_nonexistent_shortcode_update(client):
    response = client.patch("/update/ABCDEFGH",headers={"x-user-id": "1"},
                            json={"url": "https://youtube.com"})

    assert response.status_code == 409, response.json()