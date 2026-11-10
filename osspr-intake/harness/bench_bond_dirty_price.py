"""Steady-state timing for Bond.dirty_price_from_discount_curve.

Price a book of coupon bonds off one bootstrapped-style discount curve.
Curve and bonds are built before the timer. The timed section is only
dirty_price_from_discount_curve.
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
import numpy as np  # noqa: E402

from financepy.market.curves.discount_curve import DiscountCurve  # noqa: E402
from financepy.market.curves.interpolator import InterpTypes  # noqa: E402
from financepy.products.bonds.bond import Bond  # noqa: E402
from financepy.utils.calendar import BusDayAdjustTypes, CalendarTypes  # noqa: E402
from financepy.utils.date import Date  # noqa: E402
from financepy.utils.day_count import DayCountTypes  # noqa: E402
from financepy.utils.frequency import FrequencyTypes  # noqa: E402

sys.stdout = sys.__stdout__

ANCHOR = Date(15, 11, 2024)
SETTLE = Date(18, 11, 2024)

_knot_dates = [ANCHOR]
_knot_dfs = [1.0]
for year in range(1, 41):
    knot = Date(15, 11, 2024 + year)
    t = year * 1.0
    _knot_dates.append(knot)
    _knot_dfs.append(float(np.exp(-0.035 * t)))

CURVE = DiscountCurve(
    ANCHOR,
    _knot_dates,
    _knot_dfs,
    interp_type=InterpTypes.FLAT_FWD_RATES,
)

BONDS = []
for year in range(2027, 2057):
    for coupon in (0.015, 0.025, 0.035, 0.045, 0.055):
        BONDS.append(
            Bond(
                Date(15, 11, 2020),
                Date(15, 11, year),
                coupon,
                FrequencyTypes.SEMI_ANNUAL,
                DayCountTypes.ACT_ACT_ICMA,
                ex_div_days=0,
                cal_type=CalendarTypes.UNITED_STATES,
                bd_type=BusDayAdjustTypes.FOLLOWING,
            )
        )

REPEATS = 40


def price_book() -> float:
    total = 0.0
    curve = CURVE
    settle = SETTLE
    for bond in BONDS:
        total += bond.dirty_price_from_discount_curve(settle, curve)
    return total


def main() -> None:
    checksum = price_book()
    t0 = time.perf_counter()
    for _ in range(REPEATS):
        checksum = price_book()
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    print(f"{elapsed_ms:.4f}", flush=True)
    print(f"checksum={checksum:.10f} bonds={len(BONDS)}", file=sys.stderr)


if __name__ == "__main__":
    main()
