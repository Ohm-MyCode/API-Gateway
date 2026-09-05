
def test_shortcode_creation(client):

    response = client.post(url = "/shorten",headers={"x-user-id": "1"},json={"url":"google.com"})
    assert response.status_code == 200, response.json()

def test_emptyheader(client):
    response = client.post(url = "/shorten",headers={"x-user-id": ""},json={"url":"google.com"})
    assert response.status_code == 401, response.json()

def test_noheaders(client):
    response = client.post(url = "/shorten",json={"url":"google.com"})
    assert response.status_code == 401, response.json()
    