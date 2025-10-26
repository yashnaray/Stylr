from conftest import api
import pytest

def validate_item(item):
    for prop in ["id", "gender", "categories", "color", "context", "name", "url"]:
        assert prop in item

def test_match(auth_user, database):
    # use a strange number that can't be the default
    res = api("GET", "/match", {"limit": 9})
    assert res.status == 200
    assert isinstance(res.body, list)
    assert len(res.body) == 9
    for item in res.body:
        validate_item(item)

def test_match_requires_auth(database):
    res = api("GET", "/match")
    assert res.status == 401

@pytest.mark.skip
def test_recommendations_sort_param_does_not_break(mocker, token):
    mocker.patch("userSetup.User.get_recs", return_value=[
        {"id": 1, "productDisplayName": "A", "imageURL": "http://x/1.jpg"},
        {"id": 2, "productDisplayName": "B", "imageURL": "http://x/2.jpg"},
    ])
    q = f"limit=5&sort=rank_desc&type=shirt&access_token={token}"
    resp = call_endpoint("GET", "/recommendations", q)
    assert resp.status == 200
    assert isinstance(resp.body.get("items"), list)
