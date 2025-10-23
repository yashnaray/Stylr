import hashlib
import json
import os
import psycopg2

DATABASE_URL = os.getenv("STYLR_DATABASE_URL", "postgresql://stylr:stylr@localhost/stylr")

def hash_password(password, salt):
    h = hashlib.sha512()
    h.update(password.encode() + salt.encode())
    return h.hexdigest()

class Connection:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.conn.autocommit = True

    def close(self):
        self.conn.close()

    def create_user(self, username, password):
        salt = os.urandom(16).hex()
        passhash = hash_password(password, salt)
        try:
            with self.conn:
                cur = self.conn.cursor()
                cur.execute(
                    "INSERT INTO users (username, password, salt) "
                    "VALUES (%s, %s, %s) RETURNING uid",
                    (username, passhash, salt))
        except psycopg2.IntegrityError:
            return None
        (uid,) = cur.fetchone()
        return uid

    def verify_user(self, username, password):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT uid, password, salt FROM users WHERE username = %s",
                (username,))
        result = cur.fetchone()
        if result is None:
            return None
        uid, passhash, salt = result
        if hash_password(password, salt) != passhash:
            return None
        return uid
