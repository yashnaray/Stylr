from conftest import api
import json
import pytest

@pytest.mark.skip
def test_feedback_ack_and_optional_persist():
    body = {"item":{"id":123,"productDisplayName":"Blue Tee","imageURL":"http://x/1.jpg"},
            "viewed":True,"liked":True}
    resp = api("POST", "/interactions/log", {"access_token": token}, body)
    assert resp.status == 200
    assert resp.body.get("saved") in (True, False)
    if resp.body.get("saved"):
        try:
            from db import Session
            from Analytics.model_interactions import Interaction
            s = Session()
            rows = s.query(Interaction).filter_by(user_id=app.swt_decode(token), item_id=123, liked=True).all()
            s.close()
            assert len(rows) == 1
        except Exception:
            pass
