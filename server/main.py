"""ASGI entrypoint for Uvicorn deployment on Render, Railway, and cloud platforms."""

import sys
from pathlib import Path

# Ensure root directory is on the python search path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from a2wsgi import WSGIMiddleware
from app import app as flask_app

# Wrap Flask WSGI application into ASGI for Uvicorn
app = WSGIMiddleware(flask_app)
