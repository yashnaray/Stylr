from conftest import api
import pytest

def validate_item(item):
    assert type(item) is dict
    assert item["gender"] in ("Unisex", "Women", "Men")
    assert type(item["tags"]) is list
    assert all(type(tag) is str for tag in item["tags"])
    assert type(item["name"]) is str
    assert type(item["url"]) is str

def test_match(database):
    res = api("GET", "/match")
    assert res.status == 200
    assert type(res.body) is list
    for item in res.body:
        validate_item(item)

def test_match_limit(database):
    # use a strange number that can't be the default
    res = api("GET", "/match", {"limit": 9})
    assert res.status == 200
    assert type(res.body) is list
    assert len(res.body) == 9
    for item in res.body:
        validate_item(item)
