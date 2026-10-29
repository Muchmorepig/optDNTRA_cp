#!/usr/bin/env python3
"""Run upstream Trinity with a narrowly scoped Salmon 2 compatibility adapter."""
import os
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    trinity = shutil.which("Trinity")
    salmon = shutil.which("salmon")
    if not trinity or not salmon:
        sys.exit("Activate optDNTRA-trinity first; Trinity and salmon must be on PATH.")
    env = os.environ.copy()
    env["OPTDNTRA_REAL_SALMON"] = str(Path(salmon).resolve())
    env["PATH"] = str(Path(__file__).resolve().parent / "compat") + os.pathsep + env["PATH"]
    env["R_PROFILE_USER"] = os.devnull
    env["R_ENVIRON_USER"] = os.devnull
    sys.exit(subprocess.call([trinity, *sys.argv[1:]], env=env))


if __name__ == "__main__":
    main()
