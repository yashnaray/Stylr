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
    from validation import validate_username, validate_password

    username = data.get("username")
    password = data.get("password")

    if not username or not validate_username(username):
        return Response(400, "Invalid username format. Use 3-32 lowercase letters or numbers.")
    if not password or not validate_password(password):
        return Response(400, "Password is required.")

    import database
    res = database.lookup_user(username)
    if res is None or hash_password(password, res[2]) != res[1]:
        return Response(401, "Invalid credentials. Please try again.")
    token = swt_encode(res[0])
    return Response(200, {"access_token": token})

@api("/register")
def POST(req):
    data = req.json()
    from validation import validate_username, validate_password

    username = data.get("username")
    password = data.get("password")

    if not username or not validate_username(username):
        return Response(400, "Invalid username format. Use 3-32 lowercase letters or numbers.")
    if not password or not validate_password(password):
        return Response(400, "Password is required.")

    import database
    salt = os.urandom(16).hex()
    passhash = hash_password(password, salt)
    uid = database.create_user(username, passhash, salt)
    if uid is None:
        return Response(400, "This username is already taken.")
    token = swt_encode(uid)
    return Response(200, {"access_token": token})

@api("/user")
def GET(req):
    uid = req.auth()
    import database
    user = database.get_user(uid)
    if user is None:
        return Response(401, "No such user")
    else:
        return Response(200, user, compact=True)

@api("/user")
def POST(req):
    uid = req.auth()
    data = req.json()
    from validation import validate_gender, validate_tags
    entries = {}

    gender = data.get("gender")
    if gender is not None:
        if not validate_gender(gender):
            return Response(400, "Invalid gender value. Must be 0, 1, or 2.")
        entries["gender"] = gender

    tags = data.get("tags")
    if tags is not None:
        if not validate_tags(tags):
            return Response(400, "Invalid tags format. Values must be 0 or 1.")
        entries["tags"] = ";".join(f"{key}={value}" for key, value in tags.items())

    if entries:
        import database
        database.set_user(uid, **entries)
    return Response(200)

@api("/schema")
def GET(req):
    import enums
    return Response(200, enums.preferences, compact=True)

@api("/match")
def GET(req):
    from validation import validate_limit
    limit = validate_limit(req.params.get("limit"), default=5, min_val=1, max_val=50)

    import match
    return Response(200, match.match(gender=0, tags=[1] * 256, limit=limit))

@api("/interactions")
def GET(req):
    uid = req.auth()
    try:
        from Analytics.db import SessionLocal
        from Analytics.models import ItemInfo, Interaction
        from database import get_user
        user = get_user(uid)
        if not user:
            return Response(200, [])
        username = str(uid)
        s = SessionLocal()
        try:
            interactions = s.query(Interaction, ItemInfo).join(
                ItemInfo, Interaction.item_id == ItemInfo.item_id
            ).filter(
                Interaction.username == username,
                Interaction.liked == True
            ).order_by(
                Interaction.ts.desc()
            ).all()
            items = []
            for interaction, item in interactions:
                tags = []
                if item.tags:
                    try:
                        import json
                        tags = json.loads(item.tags)
                    except:
                        pass
                items.append({
                    "id": item.item_id,
                    "name": item.name,
                    "category": item.category,
                    "subcategory": item.subcategory,
                    "article_type": item.article_type,
                    "base_colour": item.base_colour,
                    "season": item.season,
                    "usage": item.usage,
                    "url": item.image_url,
                    "price": item.price,
                    "liked_at": interaction.ts.isoformat() if interaction.ts else None,
                    "tags": tags
                }) 
            return Response(200, items)
        finally:
            s.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(200, [])
@api("/interactions")
def POST(req):
    uid = req.auth()

    data = req.json()
    item = data.get("item") or {}
    viewed = bool(data.get("viewed", True))
    liked = bool(data.get("liked", False))

    try:
        from Analytics.db import SessionLocal
        from Analytics.models import UserInfo, ItemInfo, Interaction
        from database import get_user
        user = get_user(uid)
        if not user:
            return Response(400, "User not found")
        username = str(uid)

        s = SessionLocal()
        try:
            db_user = s.query(UserInfo).filter_by(username=username).first()
            if not db_user:
                db_user = UserInfo(username=username, gender=None)
                s.add(db_user)
                s.flush()
            qid = item.get("id") 
            original_url = item.get("url", "")
            original_name = item.get("name", "")
            original_tags = item.get("tags", [])
            if not item.get("articleType"):
                try:
                    import csv
                    with open("data/styles.csv", "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row.get("productDisplayName", "").strip() == original_name.strip():
                                qid = int(row.get("id", qid))
                                item = {**row, "url": original_url, "id": qid, "tags": original_tags}
                                break
                except Exception as e:
                    print(f"Could not load item details from CSV: {e}")
            
            s.query(Interaction).filter_by(username=username, item_id=qid).delete()
            
            name = item.get("productDisplayName") or item.get("name") or ""
            category = item.get("masterCategory") or item.get("category") or ""
            subcategory = item.get("subCategory") or item.get("subcategory") or ""
            article_type_csv = item.get("articleType") or item.get("article_type") or ""
            base_colour_csv = item.get("baseColour") or item.get("base_colour") or ""
            season = item.get("season") or ""
            usage = item.get("usage") or ""
            image_url = item.get("url") or item.get("imageURL") or ""
            price = item.get("price")
            tags = item.get("tags", [])
            article_type = category if category else article_type_csv

            from colors import extract_color_from_name
            base_colour = extract_color_from_name(name) if name else ""
            if not base_colour:
                base_colour = base_colour_csv
            import json
            tags_json = json.dumps(tags) if tags else None

            db_item = None
            if isinstance(qid, int):
                db_item = s.query(ItemInfo).filter_by(item_id=qid).first()
            if not db_item:
                db_item = ItemInfo(
                    item_id=qid if isinstance(qid, int) else None,
                    name=name,
                    category=category,
                    subcategory=subcategory,
                    article_type=article_type,
                    base_colour=base_colour,
                    season=season,
                    usage=usage,
                    image_url=image_url,
                    price=price,
                    tags=tags_json,
                )
                s.add(db_item)
                s.flush()

            inter = Interaction(username=username, item_id=db_item.item_id, viewed=viewed, liked=liked)
            s.add(inter)
            s.commit()
            return Response(200, {"interaction_id": inter.id, "item_id": db_item.item_id, "saved": True})
        except Exception as e:
            s.rollback()
            import traceback
            traceback.print_exc()
            raise
        finally:
            s.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(200, {"saved": False, "error": str(e)})
@api("/interactions")
def DELETE(req):
    uid = req.auth()
    data = req.json()
    item_id = data.get("item_id")
    if not item_id:
        return Response(400, {"error": "item_id required"})
    try:
        from Analytics.db import SessionLocal
        from Analytics.models import Interaction
        from database import get_user
        user = get_user(uid)
        if not user:
            return Response(400, "User not found")
        username = str(uid)
        s = SessionLocal()
        try:
            deleted_count = s.query(Interaction).filter_by(
                username=username,
                item_id=item_id
            ).delete()
            s.commit()
            if deleted_count > 0:
                return Response(200, {"deleted": True, "count": deleted_count})
            else:
                return Response(404, {"error": "Interaction not found"})
        except Exception as e:
            s.rollback()
            import traceback
            traceback.print_exc()
            raise
        finally:
            s.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(500, {"error": str(e)})

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
