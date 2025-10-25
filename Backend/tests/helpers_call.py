import sys, pathlib
BACKEND_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from typing import Optional
import main as app

def call_endpoint(method: str, path: str, query: str = "", body: Optional[dict] = None):
    methods = app.api.endpoints.get(path)
    if not methods:
        raise RuntimeError(f"No route for {path}")
    handler = methods.get(method.upper())
    if not handler:
        raise RuntimeError(f"Method {method} not allowed for {path}")
    req = app.Request(method.upper(), path, query)
    if body is not None:
        req.json = lambda: body
    return handler(req)

