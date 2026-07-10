# Forwarding entry point to backend/main.py with path priority overrides
# to avoid import conflicts with third-party 'backend' library in site-packages.

import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.main import app
