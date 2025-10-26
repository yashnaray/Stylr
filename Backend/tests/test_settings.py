from conftest import api
import pytest
import enums
import main

def test_get_settings(auth_user, database):
    res = api("GET", "/settings")
    assert res.status == 200
    assert res.body == {
        "gender": "Unisex",
        "categories": [[name, 0] for name in enums.category_names],
        "colors": [[name, 0] for name in enums.color_names],
        "contexts": [[name, 0] for name in enums.context_names]
    }
