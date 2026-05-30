#!/usr/bin/env python3
"""Ensure required R packages (and dependencies) are installed from CRAN."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

CRAN_REPOS = "https://cloud.r-project.org"
REQUIRED_PACKAGES = ("glmbayes",)


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


def is_r_package_installed(name: str) -> bool:
    from rpy2.robjects.packages import isinstalled

    return bool(isinstalled(name))


def ensure_r_package(name: str, *, repos: str = CRAN_REPOS) -> None:
    from rpy2 import robjects as ro
    from rpy2.robjects.packages import importr

    if is_r_package_installed(name):
        print(f"OK: R package '{name}' is already installed")
        return

    print(f"Installing R package '{name}' from CRAN ({repos})...")
    utils = importr("utils")
    utils.install_packages(
        ro.StrVector([name]),
        repos=ro.StrVector([repos]),
        dependencies=ro.StrVector(["Depends", "Imports", "LinkingTo"]),
    )

    if not is_r_package_installed(name):
        raise RuntimeError(f"failed to install R package: {name}")

    print(f"OK: installed R package '{name}'")


def ensure_r_packages(packages: tuple[str, ...] | list[str] = REQUIRED_PACKAGES) -> None:
    try:
        import rpy2  # noqa: F401
    except ImportError as exc:
        raise RuntimeError("rpy2 is not installed. Run: python scripts/install.py") from exc

    configure_r()
    for name in packages:
        ensure_r_package(name)


def main() -> int:
    try:
        ensure_r_packages()
    except RuntimeError as exc:
        print(f"FAILED: {exc}")
        return 1
    except Exception as exc:
        print(f"FAILED: {exc}")
        print("Check that R is installed and on PATH (R.exe --version).")
        return 1

    print("OK: all required R packages are available")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
