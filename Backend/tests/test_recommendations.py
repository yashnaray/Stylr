import main as app
from tests.helpers_call import call_endpoint

def test_get_recommendations_basic_fields_and_filters(mocker, token):
    mocker.patch("userSetup.User.get_recs", return_value=[
        {"id": 1, "productDisplayName": "Blue Tee", "masterCategory": "Apparel",
         "subCategory": "Topwear", "articleType": "Tshirts", "baseColour": "Blue",
         "season": "Summer", "usage": "Casual", "imageURL": "http://x/1.jpg", "price": 12.99, "name": "Blue Tee"},
        {"id": 2, "productDisplayName": "Blue Shirt", "masterCategory": "Apparel",
         "subCategory": "Topwear", "articleType": "Shirts", "baseColour": "Blue",
         "season": "Summer", "usage": "Casual", "imageURL": "http://x/2.jpg", "price": 29.99, "name": "Blue Shirt"},
    ])
    q = f"limit=10&color=blue&context=casual&access_token={token}"
    resp = call_endpoint("GET", "/recommendations", q)
    assert resp.status == 200
    items = resp.body["items"]
    assert 1 <= len(items) <= 10
    required = ["name","productDisplayName","masterCategory","subCategory","articleType","baseColour","season","usage","imageURL"]
    for it in items:
        for f in required:
            assert f in it

def test_recommendations_sort_param_does_not_break(mocker, token):
    mocker.patch("userSetup.User.get_recs", return_value=[
        {"id": 1, "productDisplayName": "A", "imageURL": "http://x/1.jpg"},
        {"id": 2, "productDisplayName": "B", "imageURL": "http://x/2.jpg"},
    ])
    q = f"limit=5&sort=rank_desc&type=shirt&access_token={token}"
    resp = call_endpoint("GET", "/recommendations", q)
    assert resp.status == 200
    assert isinstance(resp.body.get("items"), list)
