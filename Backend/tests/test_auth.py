from conftest import api
from main import Response, swt_decode, swt_encode

def test_swt():
    assert swt_decode(swt_encode(5)) == 5

def test_swt_expired():
    assert swt_decode(swt_encode(5, -1)) is None

def test_uid():
    token = swt_encode(3031)
    res = api("GET", "/uid", {"access_token": token})
    assert res.status == 200
    assert res.body["uid"] == 3031

def test_uid_requires_token():
    res = api("GET", "/uid")
    assert res.status == 401

def test_login(database):
    res = api("POST", "/login", body={
        "username": "yash",
        "password": "narayan"
    })
    assert res.status == 200
    assert swt_decode(res.body["access_token"]) == 1

def test_login_invalid(database):
    res1 = api("POST", "/login", body={
        "username": "not",
        "password": "narayan"
    })
    res2 = api("POST", "/login", body={
        "username": "yash",
        "password": "naray"
    })
    assert (
        res1.status == 401 and
        res2.status == 401 and
        res1.body["message"] == res2.body["message"]
    )

def test_register(database):
    res = api("POST", "/register", body={
        "username": "gavin",
        "password": "shroeder"
    })
    assert res.status == 200
    token = res.body["access_token"]
    res = api("GET", "/uid", {"access_token": token})
    assert res.status == 200
    assert res.body["uid"] == swt_decode(token)

def test_register_conflict(database):
    res = api("POST", "/register", body={
        "username": "daniel",
        "password": "lee"
    })
    assert res.status == 401
