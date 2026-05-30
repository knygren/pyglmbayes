#!/usr/bin/env python3
"""Run package checks: build validation, tests, and import smoke test."""

import subprocess
import sys
from pathlib import Path


def run_step(label: str, cmd: list[str], cwd: Path, *, ok_codes: set[int] | None = None) -> bool:
    print(f"\n--- {label} ---")
    print(f"{' '.join(cmd)}")
    result = subprocess.call(cmd, cwd=cwd)
    allowed = ok_codes or {0}
    if result not in allowed:
        print(f"FAILED: {label} (exit code {result})")
        return False
    if result != 0:
        print(f"OK: {label} (exit code {result})")
    else:
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
        ok_codes={0, 5},  # 5 = no tests collected
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
