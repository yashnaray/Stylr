from conftest import api
import pytest

def test_get_settings(auth_user, database):
    res = api("GET", "/user")
    assert res.status == 200
    assert res.body == {
        "role": 1,
        "gender": 0,
        "tags": {}
    }

def test_get_settings_admin(auth_admin, database):
    res = api("GET", "/user")
    assert res.status == 200
    assert res.body["role"] == 0

def test_set_nothing(auth_user, database):
    res = api("POST", "/user", body={})
    assert res.status == 200

def test_set_gender(auth_user, database):
    res = api("POST", "/user", body={ "gender": 1 })
    assert res.status == 200
    res = api("GET", "/user")
    assert res.status == 200
    assert res.body["gender"] == 1

def test_set_gender_invalid(auth_user, database):
    res = api("POST", "/user", body={ "gender": 3 })
    assert res.status == 400
    res = api("GET", "/user")
    assert res.status == 200
    assert res.body["gender"] == 0

def test_set_tags(auth_user, database):
    res = api("POST", "/user", body={ "tags": {"Test": 0} })
    assert res.status == 200
    res = api("GET", "/user")
    assert res.status == 200
    assert res.body["gender"] == 0
    assert res.body["tags"] == {"Test": 0}

    res = api("POST", "/user", body={ "gender": 2, "tags": {} })
    assert res.status == 200
    res = api("GET", "/user")
    assert res.status == 200
    assert res.body["gender"] == 2
    assert res.body["tags"] == {}
