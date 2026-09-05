
def test_redirect(client):
    client.post(url = "/shorten",headers={"x-user-id": "1"},json={"url":"https://google.com"})
    response = client.get(url ="/get_urls",headers={"x-user-id": "1"})


    payload = response.json()

    response = client.get(url=f"/{payload[0]['shortcode']}",follow_redirects=False)
    assert response.status_code == 307, response.json()


    response = client.get(url="/wrongcodelength")
    assert response.status_code == 422, response.json()

    response = client.get(url="/notexist")
    assert response.status_code == 404, response.json()