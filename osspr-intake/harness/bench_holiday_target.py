"""Steady-state timing for Calendar.holiday_target.

EUR swap schedules and TARGET holiday lists ask, for each weekday in a
multi-year window, whether that date is a bank holiday. Dates are built
before the timer. The timed section only calls is_business_day, which on
weekdays is holiday_target.
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
from financepy.utils.calendar import Calendar, CalendarTypes  # noqa: E402
from financepy.utils.date import Date  # noqa: E402

sys.stdout = sys.__stdout__

# Weekdays from 2000-01-03 (Monday) to 2040-01-02. Built once, outside the timer.
_cal = Calendar(CalendarTypes.TARGET)
_dates = []
_dt = Date(3, 1, 2000)
_end = Date(2, 1, 2040).excel_dt
while _dt.excel_dt < _end:
    if not _dt.is_weekend():
        _dates.append(_dt)
    _dt = _dt.add_days(1)
_DATES = tuple(_dates)
REPEATS = 20


def scan_target_holidays() -> int:
    cal = _cal
    holidays = 0
    for dt in _DATES:
        # is_business_day is the call schedule adjustment makes. Weekends are
        # already removed, so each call reaches holiday_target.
        if not cal.is_business_day(dt):
            holidays += 1
    return holidays


def main() -> None:
    holidays = scan_target_holidays()
    t0 = time.perf_counter()
    for _ in range(REPEATS):
        holidays = scan_target_holidays()
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    print(f"{elapsed_ms:.4f}", flush=True)
    print(f"holidays={holidays} dates={len(_DATES)}", file=sys.stderr)


if __name__ == "__main__":
    main()
