import os
import sys

# Add project root to python path to resolve modules in Vercel
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.main import app
