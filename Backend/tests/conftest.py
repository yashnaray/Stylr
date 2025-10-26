import io
import json
import pytest
import os
import sqlite3
import sys

os.environ["STYLR_DATABASE_URL"] = "sqlite:"

backend_dir = os.path.join(os.path.dirname(__file__), "..")
if backend_dir not in sys.path:
    sys.path.insert(1, backend_dir)

import database
import main

main.secret_key = "for_tests_only"
database.connect = None
database.close = lambda conn: None

def api(method, path, params=None, body=None):
    query = None
    if params is not None:
        query = "&".join(f"{key}={value}" for key, value in params.items())
    stdin = sys.stdin
    if body is not None:
        sys.stdin = io.StringIO(json.dumps(body))
    try:
        return main.api(method, path, query)
    finally:
        sys.stdin = stdin

class MockConnection(sqlite3.Connection):
    def close(self):
        pass

@pytest.fixture
def database(monkeypatch):
    import database
    import hashlib
    conn = sqlite3.connect(":memory:", factory=MockConnection)
    try:
        cur = conn.cursor()
        with open(os.path.join(backend_dir, "init.sql")) as file:
            cur.executescript(file.read())
        cur.close()
        conn.commit()
        monkeypatch.setattr(database, "connect", lambda url: conn)
        yield database
    finally:
        sqlite3.Connection.close(conn)

@pytest.fixture
def auth_admin(monkeypatch):
    monkeypatch.setattr(main, "bypass_auth", 1)

@pytest.fixture
def auth_user(monkeypatch):
    monkeypatch.setattr(main, "bypass_auth", 2)
