#!/usr/bin/env python3

import hashlib
import hmac
import http.server
import json
import os
import re
import selectors
import signal
import socket
import sys
import time
import urllib.parse

secret_key = b"12345"

class Response(Exception):
    def __init__(self, status, body=None):
        self.status = status
        self.body = {"message": body} if isinstance(body, str) else body

def swt_encode(uid, expire=86400):
    expire += time.time_ns() // 1000000000
    data = f"{uid}.{expire}"
    digest = hmac.new(secret_key, data.encode("utf-8"), "sha256").hexdigest()
    return f"{data}.{digest}"

def swt_decode(token):
    try:
        data, _, digest = token.rpartition(".")
        expected_digest = hmac.new(secret_key, data.encode("utf-8"), "sha256").hexdigest()
        assert digest == expected_digest
        uid, _, expire = data.partition(".")
        expire = int(expire)
        assert expire > time.time_ns() // 1000000000
        uid = int(uid)
        return uid
    except:
        return None

def hash_password(password, salt):
    h = hashlib.sha512()
    h.update(password.encode("utf-8") + salt)
    return h.hexdigest()

my_uid = 1000
my_username = "daniel"
my_salt = os.urandom(16)
my_passhash = hash_password("li", my_salt)

def verify_login(username, password):
    if username != my_username or hash_password(password, my_salt) != my_passhash:
        raise Response(401, "Invalid credentials")
    return swt_encode(1000)

#---------------------------------------

def GET_ok(req):
    return Response(200, "Welcome to Stylr!")

def GET_uid(req):
    uid = req.auth()
    return Response(200, {"uid": uid})

def POST_login(req):
    data = req.json()
    try:
        username = data["username"]
        assert isinstance(username, str)
        password = data["password"]
        assert isinstance(password, str)
    except:
        return Response(400, "Invalid request")
    token = verify_login(username, password)
    return Response(200, {"access_token": token})

def POST_register(req):
    pass

#---------------------------------------

path_regex = re.compile(r"^/[a-z/]*$")

class Request(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.do("GET")

    def do_POST(self):
        self.do("POST")

    def do(self, method):
        try:
            response = self.do_unprotected(method)
        except Response as e:
            response = e
        if response is None:
            response = Response(503, "Service Unavailable")
        self.send_response(response.status)
        self.send_header("content-type", "application/json")
        self.end_headers()
        if response.body is not None:
            self.wfile.write(json.dumps(response.body).encode("utf-8"))

    def do_unprotected(self, method):
        path, _, query = self.path.partition("?")
        path = urllib.parse.unquote(path)
        if path.startswith("/api/"):
            path = path[4:]
        if not path_regex.match(path):
            raise Response(404, "Not Found")
        handler = globals().get(method + path.replace("/", "_"))
        if handler is None:
            raise Response(404, "Not Found")
        self.path = path
        self.params = urllib.parse.parse_qs(query)
        return handler(self)

    def log_message(self, format, *args):
        pass

    def auth(self):
        if "access_token" not in self.params:
            raise Response(401, "No credentials provided")
        token = self.params["access_token"][0]
        uid = swt_decode(token)
        if uid is None:
            raise Response(401, "Invalid credentials")
        return uid

    def json(self):
        data = self.rfile.read(int(self.headers['content-length']))
        try:
            return json.loads(data)
        except:
            raise Response(400, "Invalid request body")

def main():
    address = ("", 3031)

    # https://docs.python.org/3/library/signal.html#note-on-signal-handlers-and-exceptions
    termination_read, termination_write = socket.socketpair()
    def handle_termination_signal(signum, frame):
        termination_write.send(b"\0")
    signal.signal(signal.SIGINT, handle_termination_signal)
    signal.signal(signal.SIGTERM, handle_termination_signal)

    with http.server.ThreadingHTTPServer(address, Request) as server:
        selector = selectors.DefaultSelector()
        selector.register(termination_read, selectors.EVENT_READ)
        selector.register(server, selectors.EVENT_READ)
        terminate = False
        sys.stdout.write("Listening on port 3031\n")
        while not terminate:
            for key, _ in selector.select():
                if key.fileobj == termination_read:
                    termination_read.recv(1)
                    terminate = True
                elif key.fileobj == server:
                    server.handle_request()

    sys.stdout.write("Terminating\n")

if __name__ == "__main__":
    main()
