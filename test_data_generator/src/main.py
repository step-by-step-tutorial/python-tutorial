"""Script entry point, so `python ./src/main.py --config ...` keeps working.

The implementation lives in :mod:`cli`; installing the project also provides a
``csv-data-generator`` command.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):  # run as a script, not imported
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from cli import main

if __name__ == "__main__":
    raise SystemExit(main())
