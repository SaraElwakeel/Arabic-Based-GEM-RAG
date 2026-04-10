from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent


def run(script: str) -> None:
    script_path = BASE / "scripts" / script
    subprocess.run([sys.executable, str(script_path)], check=True)


if __name__ == "__main__":
    run("01_scrape_sites.py")
    run("02_prepare_chunks.py")
    run("03_build_indexes.py")
    print("\nBuild complete. Run: python scripts/04_ask_cli.py")
