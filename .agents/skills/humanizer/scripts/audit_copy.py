#!/usr/bin/env python3
"""Run project copy audit from the humanizer skill."""

import subprocess
import sys
from pathlib import Path

# .agents/skills/humanizer/scripts/ -> parent 4 is workspace root
ROOT = Path(__file__).resolve().parents[4]

if __name__ == "__main__":
    script_path = ROOT / "scripts" / "audit_copy.py"
    if not script_path.exists():
        print(f"Error: {script_path} not found", file=sys.stderr)
        sys.exit(1)
    result = subprocess.run([sys.executable, str(script_path)] + sys.argv[1:])
    sys.exit(result.returncode)
