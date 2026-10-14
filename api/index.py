import sys
from pathlib import Path

# Add project root to sys.path so Vercel serverless functions can import application modules
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import app
