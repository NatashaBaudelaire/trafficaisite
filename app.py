"""TrafficAI — root entry point for Railway deployment.

Loads the Flask application from api/app.py, adding api/ to sys.path first
so that the sibling predictor module resolves correctly. The server listens on
the PORT environment variable (default: 5000).
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

# Ensure api/ is on the path so `from predictor import ...` inside api/app.py works.
API_DIR = Path(__file__).resolve().parent / "api"
sys.path.insert(0, str(API_DIR))

# Load api/app.py as a module without triggering the api package __init__.
_spec = importlib.util.spec_from_file_location("trafficai_api", API_DIR / "app.py")
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

app = _module.app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
