#!/usr/bin/env python3
"""Smoke test: confirm Python is installed and runnable."""

import sys


def main() -> int:
    print("Hello, world!")
    print(f"Python {sys.version}")
    print(f"Executable: {sys.executable}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
