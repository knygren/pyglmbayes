#!/usr/bin/env python3
"""Run package checks: build validation, tests, and import smoke test."""

import subprocess
import sys
from pathlib import Path


def run_step(label: str, cmd: list[str], cwd: Path) -> bool:
    print(f"\n--- {label} ---")
    print(f"{' '.join(cmd)}")
    result = subprocess.call(cmd, cwd=cwd)
    if result != 0:
        print(f"FAILED: {label} (exit code {result})")
        return False
    print(f"OK: {label}")
    return True


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    py = sys.executable
    ok = True

    ok &= run_step(
        "Build package",
        [py, "-m", "build", "--outdir", "dist"],
        root,
    )
    ok &= run_step(
        "Run tests",
        [py, "-m", "pytest", "-v"],
        root,
    )
    ok &= run_step(
        "Import smoke test",
        [py, "-c", "import pyglmbayes; print('imported', pyglmbayes)"],
        root,
    )

    if ok:
        print("\nAll checks passed.")
        return 0

    print("\nSome checks failed. Try running: python scripts/install.py")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
