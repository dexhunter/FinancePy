"""Peak resident memory of one American put on a CRR binomial tree.

EquityBinomialTree.value prices by calling _value_once twice (N and N+1
steps) and averaging. _value_once keeps the whole triangular stock and
option grids. ru_maxrss is the process high-water mark, so a tiny warmup
compiles numba without setting the mark, and one steady-state pricing
records the grid.

The printed value is the increase in peak RSS, in bytes, caused by that
pricing call.
"""

from __future__ import annotations

import io
import resource
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_banner = io.StringIO()
sys.stdout = _banner
import numpy as np  # noqa: E402

from financepy.market.curves.flat_discount_curve import FlatDiscountCurve  # noqa: E402
from financepy.products.equity.equity_binomial_tree import (  # noqa: E402
    EquityBinomialTree,
    EquityTreeExerciseTypes,
    EquityTreePayoffTypes,
)
from financepy.utils.date import Date  # noqa: E402

sys.stdout = sys.__stdout__

VALUE_DT = Date(1, 1, 2024)
EXPIRY_DT = Date(1, 1, 2025)
DISCOUNT = FlatDiscountCurve(VALUE_DT, 0.05)
DIVIDEND = FlatDiscountCurve(VALUE_DT, 0.02)
TREE = EquityBinomialTree()
PAYOFF_PARAMS = np.array([-1.0, 100.0])
# Large enough that the triangular grids dominate the new high-water mark.
NUM_STEPS = 3000


def price_american_put(num_steps: int):
    return TREE.value(
        100.0,
        DISCOUNT,
        DIVIDEND,
        0.20,
        num_steps,
        VALUE_DT,
        None,
        EXPIRY_DT,
        EquityTreePayoffTypes.VANILLA_OPTION,
        EquityTreeExerciseTypes.AMERICAN,
        PAYOFF_PARAMS,
    )


def _maxrss_bytes() -> int:
    # Linux reports ru_maxrss in kilobytes.
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def main() -> None:
    # Compile and touch the kernel with a tree far smaller than the sample.
    warmup = price_american_put(32)
    before = _maxrss_bytes()
    value = price_american_put(NUM_STEPS)
    after = _maxrss_bytes()
    peak_bytes = after - before
    print(f"{peak_bytes}", flush=True)
    print(
        f"price={float(value[0]):.10f} warmup={float(warmup[0]):.6f} "
        f"steps={NUM_STEPS}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
