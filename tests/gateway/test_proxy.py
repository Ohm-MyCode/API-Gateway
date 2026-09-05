import httpx
import jwt
from httpx import Response

from auth_service.config import settings

token = jwt.encode({"sub":"123","type":"access"},settings.PRIVATE_KEY,algorithm=settings.JWT_ALGORITHM)
def test_loginroute(client, respx_mock):
    respx_mock.post("http://auth-service:8000/login").mock(return_value=Response(200,json={"message": "ok"}))
    response =client.post(url="http://auth-service:8000/auth/login")
    assert response.status_code == 200, response.json()

def test_signup(client, respx_mock):
    respx_mock.post("http://auth-service:8000/signup").mock(return_value=Response(200,json={"message": "ok"}))
    response =client.post(url="http://auth-service:8000/auth/signup")
    assert response.status_code == 200, response.json()

def test_refresh(client, respx_mock):
    respx_mock.post("http://auth-service:8000/refresh").mock(return_value=Response(200,json={"message": "ok"}))
    response =client.post(url="http://auth-service:8000/auth/refresh")
    assert response.status_code == 200, response.json()

def test_logout(client, respx_mock):
    respx_mock.post("http://auth-service:8000/logout").mock(return_value=Response(200,json={"message": "ok"}))
    response =client.post(url="http://auth-service:8000/auth/logout")
    assert response.status_code == 200, response.json()

def test_shortcode(client, respx_mock):
    respx_mock.get("http://url-service:8000/shortenn").mock(return_value=Response(200,json={"message": "ok"}))
    response =client.get(url="http://url-service:8000/shortenn")
    assert response.status_code == 200, response.json()

def test_shortcode_creation(client, respx_mock):
    respx_mock.post("http://url-service:8000/shorten").mock(return_value=Response(200,json={"message": "ok"}))
    response =client.post(url="http://url-service:8000/url/shorten",headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200, response.json()

def test_shortcode_deletion(client, respx_mock):
    respx_mock.delete("http://url-service:8000/delete/abc123xy").mock(return_value=Response(200,json={"message": "ok"}))
    response =client.delete(url="http://url-service:8000/url/delete/abc123xy",headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200, response.json()

def test_get_particular_shortcode(client, respx_mock):
    respx_mock.get("http://url-service:8000/get_url/shorten").mock(return_value=Response(200,json={"message": "ok"}))
    response =client.get(url="http://url-service:8000/url/get_url/shorten",headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200, response.json()

def test_getallshortcodes(client, respx_mock):
    respx_mock.get("http://url-service:8000/get_urls").mock(return_value=Response(200,json={"message": "ok"}))
    response =client.get(url="http://url-service:8000/url/get_urls",headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200, response.json()

def test_shortcode_update(client, respx_mock):
    respx_mock.patch("http://url-service:8000/update/abc123xy").mock(return_value=Response(200,json={"message": "ok"}))
    response =client.patch(url="http://url-service:8000/url/update/abc123xy",headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200, response.json()

def test_unknown_route(client, respx_mock):
    #respx_mock.get("http://url-service:8000/url/shorten").mock(return_value=Response(200,json={"message": "ok"}))
    response =client.patch(url="http://url-service:8000/unknown/route",headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 404, response.json()

def test_headerforwarding(client, respx_mock):
    route = respx_mock.post("http://auth-service:8000/login").mock(return_value=Response(200))

    client.post("/auth/login")
    request = route.calls[0].request
    assert "x-request-id" in request.headers

def test_upstreamfailure(client,respx_mock):
    respx_mock.post("http://auth-service:8000/login").mock(side_effect=httpx.ConnectError("boom"))

    response = client.post("/auth/login")
    assert response.status_code == 502