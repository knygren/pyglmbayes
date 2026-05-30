#!/usr/bin/env python3
"""Smoke test: confirm rpy2 can call R (stats::pnorm)."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def configure_r() -> None:
    """Help rpy2 find R and load base packages on Windows."""
    if os.environ.get("R_HOME"):
        r_home = Path(os.environ["R_HOME"])
    else:
        r_exe = shutil.which("R.exe") or shutil.which("R")
        if r_exe is None:
            return
        r_home = Path(r_exe).resolve().parent.parent

    os.environ.setdefault("R_HOME", str(r_home))

    r_bin = r_home / "bin"
    r_bin_x64 = r_bin / "x64"
    prepend = os.pathsep.join(str(path) for path in (r_bin_x64, r_bin) if path.is_dir())
    if prepend:
        path = os.environ.get("PATH", "")
        if prepend not in path:
            os.environ["PATH"] = prepend + os.pathsep + path


def main() -> int:
    configure_r()

    try:
        from rpy2.robjects.packages import importr
    except ImportError:
        print("rpy2 is not installed. Run: python scripts/install.py")
        return 1

    try:
        stats = importr("stats")
        x = 0.0
        result = float(stats.pnorm(x)[0])
    except Exception as exc:
        print(f"FAILED: could not call stats::pnorm via rpy2: {exc}")
        print("Check that R is installed and on PATH (R.exe --version).")
        return 1

    expected = 0.5

    print(f"Python {sys.version.split()[0]} ({sys.executable})")
    print(f"R_HOME: {os.environ.get('R_HOME', '(not set)')}")
    print(f"stats::pnorm({x}) = {result}")
    print(f"Expected:              {expected}")

    if abs(result - expected) > 1e-10:
        print("FAILED: result does not match expected value")
        return 1

    print("OK: rpy2 integration works")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
