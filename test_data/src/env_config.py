from os import getenv
from pathlib import Path

PROJECT_ROOT = Path(getenv("PROJECT_ROOT", Path(__file__).resolve().parents[1])).resolve()
CONFIG_DIR = Path(getenv("CONFIG_DIR", Path(PROJECT_ROOT, "config"))).resolve()
OUTPUT_DIR = Path(getenv("OUTPUT_DIR", Path(PROJECT_ROOT, "output"))).resolve()
