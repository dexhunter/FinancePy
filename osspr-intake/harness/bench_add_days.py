"""Steady-state timing for Date.add_days on a multi-decade daily walk.

A daily schedule (date_range with tenor 1D, fixing calendars, accrued-day
counts) advances one serial day at a time. The timed section is only that
walk, repeated so the sample is long enough to measure.
"""

from __future__ import annotations

import io
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_banner = io.StringIO()
sys.stdout = _banner
from financepy.utils.date import Date  # noqa: E402

sys.stdout = sys.__stdout__

# 1 Jan 1990 through 1 Jan 2070 is 29,220 steps. Thirty walks is the sample.
REPEATS = 30
START = Date(1, 1, 1990)
END_EXCEL = Date(1, 1, 2070).excel_dt


def walk_days() -> int:
    dt = START
    end_excel = END_EXCEL
    checksum = 0
    while dt.excel_dt < end_excel:
        dt = dt.add_days(1)
        checksum += dt.d
    return checksum


def main() -> None:
    checksum = walk_days()
    t0 = time.perf_counter()
    for _ in range(REPEATS):
        checksum = walk_days()
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    print(f"{elapsed_ms:.4f}", flush=True)
    print(f"checksum={checksum}", file=sys.stderr)


if __name__ == "__main__":
    main()
