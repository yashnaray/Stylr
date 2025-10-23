#!/usr/bin/env python3

from http import HTTPStatus as HTTP
from urllib.parse import parse_qs
import hmac
import json
import os
import sys
import time

SECRET_KEY = os.getenv("STYLR_SECRET_KEY", "gurleen_dhillon").encode()

class Request:
    def __init__(self, method, path, query):
        self.method = method
        self.path = path
        self.query = query
        self.params = parse_qs(query)

    def auth(self):
        if "access_token" not in self.params:
            raise Response(HTTP.UNAUTHORIZED, "No access token supplied")
        token = self.params["access_token"][0]
        uid = swt_decode(token)
        if uid is None:
            raise Response(HTTP.UNAUTHORIZED, "Invalid access token")
        return uid

    def json(self):
        data = sys.stdin.read()
        try:
            return json.loads(data)
        except:
            raise Response(HTTP.BAD_REQUEST, "Could not parse request body")

class Response(Exception):
    def __init__(self, status, body=None):
        self.status = status
        self.body = ({"message": status.phrase} if body is None else
                     {"message": body} if isinstance(body, str) else body)

def swt_encode(uid, expire=86400):
    expire += time.time_ns() // 1000000000
    data = f"{uid}.{expire}"
    digest = hmac.new(SECRET_KEY, data.encode(), "sha256").hexdigest()
    return f"{data}.{digest}"

def swt_decode(token):
    try:
        data, _, digest = token.rpartition(".")
        expected_digest = hmac.new(SECRET_KEY, data.encode(), "sha256").hexdigest()
        assert digest == expected_digest
        uid, _, expire = data.partition(".")
        expire = int(expire)
        assert expire > time.time_ns() // 1000000000
        uid = int(uid)
        return uid
    except:
        return None

def api(path):
    if path not in api.endpoints:
        api.endpoints[path] = {}
    def decorator(fn):
        api.endpoints[path][fn.__name__] = fn
    return decorator

api.endpoints = {}

#---------------------------------------

@api("/ok")
def GET(req):
    return Response(HTTP.OK, "Welcome to Stylr!")

@api("/uid")
def GET(req):
    uid = req.auth()
    return Response(HTTP.OK, {"uid": uid})

@api("/login")
def POST(req):
    data = req.json()
    try:
        username = data["username"]
        assert isinstance(username, str)
        password = data["password"]
        assert isinstance(password, str)
    except:
        return Response(HTTP.BAD_REQUEST)

    from database import Connection
    conn = Connection()
    uid = conn.verify_user(username, password)
    conn.close()
    if uid is None:
        return Response(HTTP.UNAUTHORIZED, "Invalid credentials. Please try again.")
    token = swt_encode(uid)
    return Response(HTTP.OK, {"access_token": token})

@api("/register")
def POST(req):
    data = req.json()
    try:
        username = data["username"]
        assert isinstance(username, str)
        password = data["password"]
        assert isinstance(password, str)
    except:
        return Response(HTTP.BAD_REQUEST)

    from database import Connection
    conn = Connection()
    uid = conn.create_user(username, password)
    if uid is None:
        return Response(HTTP.UNAUTHORIZED, "This username is already taken.")
    token = swt_encode(uid)
    return Response(HTTP.OK, {"access_token": token})

#---------------------------------------

def main():
    direct = "REQUEST_METHOD" not in os.environ

    if direct:
        if len(sys.argv) != 3:
            sys.stderr.write(f"usage: {sys.argv[0]} METHOD URL\n")
            sys.exit(2)
        method, url = sys.argv[1:]
        path, _, query = url.partition("?")
    else:
        method = os.environ["REQUEST_METHOD"]
        path = os.environ.get("PATH_INFO", "")
        query = os.environ.get("QUERY_STRING", "")

    try:
        if path.startswith("/api/"):
            path = path[4:]
        methods = api.endpoints.get(path)
        if methods is None:
            raise Response(HTTP.NOT_FOUND)
        handler = methods.get(method)
        if handler is None:
            raise Response(HTTP.METHOD_NOT_ALLOWED)
        response = handler(Request(method, path, query))
    except Response as e:
        response = e
    if response is None:
        response = Response(HTTP.NOT_IMPLEMENTED)

    prefix = "HTTP/1.1" if direct else "status:"
    sys.stdout.write(
        f"{prefix} {response.status} {response.status.phrase}\r\n"
        "access-control-allow-origin: *\r\n"
        "content-type: application/json\r\n"
        "\r\n"
    )

    if response.body is not None:
        sys.stdout.write(json.dumps(response.body, indent=2) + "\n")

if __name__ == "__main__":
    main()
