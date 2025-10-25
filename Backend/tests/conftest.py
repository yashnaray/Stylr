import sys, pathlib, os, types
BACKEND_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("STYLR_SECRET_KEY", "for_tests_only")
os.environ.setdefault("DATABASE_URL", "sqlite:///tests/test.db")

import pytest
import main as app

@pytest.fixture(scope="session")
def token() -> str:
    return app.swt_encode(1001)

@pytest.fixture(scope="session", autouse=True)
def bootstrap_db():
    try:
        from tests.util_db_bootstrap import init_db
        init_db()
    except Exception:
        pass
    yield

@pytest.fixture(scope="session", autouse=True)
def stub_usersetup_module():
    if "userSetup" not in sys.modules:
        m = types.ModuleType("userSetup")
        class User:
            def __init__(self, uid):
                self.uid = uid
            def get_recs(self, num_recs=30):
                return []
        m.User = User
        sys.modules["userSetup"] = m
    yield

@pytest.fixture(autouse=True)
def safe_match_fallback(mocker):
    mocker.patch("match.match", return_value={
        "id": 0,
        "name": "Fallback",
        "category": "",
        "subcategory": "",
        "article_type": "",
        "base_colour": "",
        "season": "",
        "usage": "",
        "url": "http://x/fallback.jpg",
        "price": 0
    })
    yield
