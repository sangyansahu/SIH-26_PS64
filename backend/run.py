import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from config import Config

app = create_app(Config)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Starting AICTE Integrated Complaint Portal API on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)
