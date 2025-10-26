import os

database_url = os.getenv("STYLR_DATABASE_URL", "sqlite:data/local.db")
backend, _, dsn = database_url.partition(":")

if backend == "sqlite":
    from sqlite3 import IntegrityError, connect
    def execute(cur, script, params=None):
        cur.execute(script, params)
elif backend == "psycopg2":
    from psycopg2 import IntegrityError, connect
    def execute(cur, script, params=None):
        cur.execute(script.replace("?", "%s"), params)

def transaction(fn):
    def wrapper(*args, **kwargs):
        conn = connect(dsn)
        cur = conn.cursor()
        try:
            res = fn(cur, *args, **kwargs)
            conn.commit()
        finally:
            conn.close()
        return res
    return wrapper

@transaction
def create_user(cur, username, passhash, salt, role=1):
    try:
        execute(cur,
            "INSERT INTO users (username, password, salt, role, fullname) "
            "VALUES (?, ?, ?, ?, ?)",
            (username, passhash, salt, role, username))
    except IntegrityError:
        return None
    execute(cur,
        "SELECT uid FROM users WHERE username == ?",
        (username,))
    return cur.fetchone()[0]

@transaction
def lookup_user(cur, username):
    execute(cur,
        "SELECT uid, password, salt FROM users WHERE username = ?",
        (username,))
    return cur.fetchone()

@transaction
def get_settings(cur, uid):
    execute(cur,
        "SELECT gender, prefs FROM users WHERE uid = ?",
        (uid,))
    return cur.fetchone()
