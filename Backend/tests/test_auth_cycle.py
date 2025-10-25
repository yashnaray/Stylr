from tests.helpers_call import call_endpoint
import main as app

def test_uid_requires_token():
    try:
        call_endpoint("GET", "/uid", "")
        assert False, "Expected Response(401)"
    except app.Response as e:
        assert e.status == 401

def test_uid_with_token(token):
    resp = call_endpoint("GET", "/uid", f"access_token={token}")
    assert resp.status == 200
    assert resp.body.get("uid") == app.swt_decode(token)
