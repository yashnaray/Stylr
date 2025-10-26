#!/usr/bin/env python3

import hmac
import json
import os
import sys
import time

secret_key = "gurleen_dhillon"
direct = True
bypass_auth = None

http_status_map = {
    200: "OK",
    400: "Bad Request",
    401: "Unauthorized",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
}

def swt_encode(uid, expire=86400):
    expire += time.time_ns() // 1000000000
    data = f"{uid}.{expire}"
    digest = hmac.new(secret_key.encode(), data.encode(), "sha256").hexdigest()
    return f"{data}.{digest}"

def swt_decode(token):
    data, _, digest = token.rpartition(".")
    uid, _, expire = data.partition(".")
    try:
        uid = int(uid)
        expire = int(expire)
    except ValueError:
        return None
    return (uid if
        expire > time.time_ns() // 1000000000 and
        digest == hmac.new(secret_key.encode(), data.encode(), "sha256").hexdigest()
        else None)

def hash_password(password, salt):
    import hashlib
    h = hashlib.sha512()
    h.update(password.encode() + salt.encode())
    return h.hexdigest()

class Request:
    def __init__(self, method, path, params):
        self.method = method
        self.path = path
        self.params = params

    def auth(self):
        if bypass_auth:
            return bypass_auth
        if "access_token" not in self.params:
            raise Response(401, "No access token supplied")
        token = self.params["access_token"]
        uid = swt_decode(token)
        if uid is None:
            raise Response(401, "Invalid access token")
        return uid

    def json(self):
        data = sys.stdin.read()
        try:
            return json.loads(data)
        except:
            raise Response(400, "Could not parse request body")

class Response(Exception):
    def __init__(self, status, body=None, *, compact=False):
        self.status = status
        self.phrase = http_status_map[self.status]
        self.body = (
            {"message": self.phrase} if body is None else
            {"message": body} if isinstance(body, str) else body
        )
        self.compact = compact

endpoints = {}

def api(path):
    if path not in endpoints:
        endpoints[path] = {}
    def decorator(fn):
        endpoints[path][fn.__name__] = fn
    return decorator

#---------------------------------------

@api("/ok")
def GET(req):
    return Response(200, "Welcome to Stylr!")

@api("/uid")
def GET(req):
    uid = req.auth()
    return Response(200, {"uid": uid})

@api("/login")
def POST(req):
    data = req.json()
    try:
        username = data["username"]
        assert isinstance(username, str)
        password = data["password"]
        assert isinstance(password, str)
    except:
        return Response(400)

    import database
    res = database.lookup_user(username)
    if res is None or hash_password(password, res[2]) != res[1]:
        return Response(401, "Invalid credentials. Please try again.")
    token = swt_encode(res[0])
    return Response(200, {"access_token": token})

@api("/register")
def POST(req):
    data = req.json()
    try:
        username = data["username"]
        assert isinstance(username, str)
        password = data["password"]
        assert isinstance(password, str)
    except:
        return Response(400)

    import database
    salt = os.urandom(16).hex()
    passhash = hash_password(password, salt)
    uid = database.create_user(username, passhash, salt)
    if uid is None:
        return Response(401, "This username is already taken.")
    token = swt_encode(uid)
    return Response(200, {"access_token": token})

@api("/settings")
def GET(req):
    uid = req.auth()
    import database
    import enums
    res = database.get_settings(uid)
    if res is None:
        return Response(401, "User not found")
    gender, prefs = res
    prefs = int(prefs, 16) << 1
    return Response(200, {
        "gender": enums.gender_names[gender],
        "categories": [[name, (prefs := prefs >> 1) & 1] for name in enums.category_names],
        "colors": [[name, (prefs := prefs >> 1) & 1] for name in enums.color_names],
        "contexts": [[name, (prefs := prefs >> 1) & 1] for name in enums.context_names]
    }, compact=True)

@api("/settings")
def POST(req):
    uid = req.auth()

@api("/match")
def GET(req):
    uid = req.auth()
    try:
        limit = int(req.params["limit"])
    except:
        limit = 5
    if limit < 1:
        limit = 1
    elif limit > 50:
        limit = 50

    # TODO
    import match
    return Response(200, match.match(
        gender=1,
        categories=-1,
        colors=-1,
        contexts=-1,
        limit=limit))

@api("/interactions")
def POST(req):
    return Response(500)
    uid = req.auth()

    data = req.json()
    item = data.get("item") or {}
    viewed = bool(data.get("viewed", True))
    liked = bool(data.get("liked", False))

#backup incase user data isn't restored
    try:
        from db import Session
        from Analytics.model_interactions import Item, Interaction

        s = Session()
        try:
            qid = item.get("id")
            name = item.get("productDisplayName") or item.get("name") or ""
            category = item.get("masterCategory") or item.get("category") or ""
            subcategory = item.get("subCategory") or item.get("subcategory") or ""
            article_type = item.get("articleType") or item.get("article_type") or ""
            base_colour = item.get("baseColour") or item.get("base_colour") or ""
            season = item.get("season") or ""
            usage = item.get("usage") or ""
            image_url = item.get("imageURL") or item.get("url") or ""
            price = item.get("price")

            db_item = None
            if isinstance(qid, int):
                db_item = s.query(Item).filter_by(id=qid).first()
            if not db_item:
                db_item = Item(
                    id=qid if isinstance(qid, int) else None,
                    name=name,
                    category=category,
                    subcategory=subcategory,
                    article_type=article_type,
                    base_colour=base_colour,
                    season=season,
                    usage=usage,
                    image_url=image_url,
                    price=price,
                )
                s.add(db_item)
                s.flush()

            inter = Interaction(user_id=uid, item_id=db_item.id, viewed=viewed, liked=liked)
            s.add(inter)
            s.commit()
            return Response(200, {"interaction_id": inter.id, "item_id": db_item.id, "saved": True})
        except:
            s.rollback()
            raise
        finally:
            s.close()

    except Exception:
        return Response(200, {"saved": False})

#---------------------------------------

def api(method, path, query=None):
    params = {}
    if query:
        for item in query.split("&"):
            key, _, value = item.partition("=")
            if key:
                params[key] = value
    if path.startswith("/api/"):
        path = path[4:]
    methods = endpoints.get(path)
    if methods is None:
        return Response(404)
    handler = methods.get(method)
    if handler is None:
        return Response(405)
    try:
        return handler(Request(method, path, params))
    except Response as response:
        return response

def main():
    global bypass_auth

    if direct:
        import optparse
        parser = optparse.OptionParser(usage="%prog METHOD URL [PARAMS...]")
        parser.add_option("-u", "--uid", type="int", help="bypass authentication")
        opts, args = parser.parse_args()
        if len(args) < 2:
            parser.error("not enough arguments")
        bypass_auth = opts.uid
        method, url = args[:2]
        path, _, query = url.partition("?")
        for arg in args[2:]:
            query = query + "&" + arg if query else arg
    else:
        method = os.environ["REQUEST_METHOD"]
        path = os.environ.get("PATH_INFO", "")
        query = os.environ.get("QUERY_STRING", "")

    prefix = "HTTP/1.1" if direct else "status:"
    res = api(method, path, query)
    body = (json.dumps(res.body, separators=(",", ":")) if res.compact else
            json.dumps(res.body, indent=2))

    sys.stdout.write(f"""\
{prefix} {res.status} {res.phrase}\r
access-control-allow-origin: *\r
content-type: application/json\r
\r
{body}
""")

if __name__ == "__main__":
    main()
