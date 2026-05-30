#!/usr/bin/env python3
"""Install pyglmbayes in editable mode with dev dependencies."""

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    cmd = [sys.executable, "-m", "pip", "install", "-e", f"{root}[dev]"]
    print(f"Running: {' '.join(cmd)}")
    return subprocess.call(cmd, cwd=root)


if __name__ == "__main__":
    raise SystemExit(main())
