#!/usr/bin/env python3

import hmac
import json
import os
import sys
import time

SECRET_KEY = os.getenv("STYLR_SECRET_KEY", "gurleen_dhillon").encode()

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
    digest = hmac.new(SECRET_KEY, data.encode(), "sha256").hexdigest()
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
        digest == hmac.new(SECRET_KEY, data.encode(), "sha256").hexdigest()
        else None)

class Request:
    def __init__(self, method, path, params):
        self.method = method
        self.path = path
        self.params = params

    def auth(self):
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
    def __init__(self, status, body=None):
        self.status = status
        self.body = body

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

    from database import Connection
    conn = Connection()
    uid = conn.verify_user(username, password)
    conn.close()
    if uid is None:
        return Response(401, "Invalid credentials. Please try again.")
    token = swt_encode(uid)
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

    from database import Connection
    conn = Connection()
    uid = conn.create_user(username, password)
    if uid is None:
        return Response(401, "This username is already taken.")
    token = swt_encode(uid)
    return Response(200, {"access_token": token})

@api("/match")
def GET(req):
    import match
    return Response(200, match.match())

@api("/recommendations")
def GET(req):
    uid = req.auth()
    try:
        limit = int(req.params.get("limit", "30"))
    except:
        limit = 30
    if limit < 1:
        limit = 1
    if limit > 50:
        limit = 50
    items = []
    try:
        from userSetup import User
        user = User(uid)
        recs = user.get_recs(num_recs=limit) or []
        for x in recs[:limit]:
            items.append({
                "id": x.get("id") or x.get("index") or 0,
                "productDisplayName": x.get("productDisplayName") or x.get("name") or "",
                "masterCategory": x.get("masterCategory") or x.get("category") or "",
                "subCategory": x.get("subCategory") or x.get("subcategory") or "",
                "articleType": x.get("articleType") or x.get("article_type") or "",
                "baseColour": x.get("baseColour") or x.get("base_colour") or "",
                "season": x.get("season") or "",
                "usage": x.get("usage") or "",
                "imageURL": x.get("imageURL") or x.get("url") or "",
                "price": x.get("price"),
                "name": x.get("name") or x.get("productDisplayName") or ""
            })
    except Exception:
        import match
        for _ in range(limit):
            x = match.match()
            items.append({
                "id": x.get("id") or 0,
                "productDisplayName": x.get("name") or "",
                "masterCategory": x.get("category") or "",
                "subCategory": x.get("subcategory") or "",
                "articleType": x.get("article_type") or "",
                "baseColour": x.get("base_colour") or "",
                "season": x.get("season") or "",
                "usage": x.get("usage") or "",
                "imageURL": x.get("url") or "",
                "price": x.get("price"),
                "name": x.get("name") or ""
            })

    return Response(200, {"items": items})


@api("/interactions/log")
def POST(req):
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

    response = api(method, path, query)
    prefix = "HTTP/1.1" if direct else "status:"
    phrase = http_status_map[response.status]
    body = response.body
    body = ({"message": phrase} if body is None else
            {"message": body} if isinstance(body, str) else body)

    sys.stdout.write(
        f"{prefix} {response.status} {phrase}\r\n"
        "access-control-allow-origin: *\r\n"
        "content-type: application/json\r\n"
        "\r\n"
        f"{json.dumps(body, indent=2)}\n"
    )

if __name__ == "__main__":
    main()
