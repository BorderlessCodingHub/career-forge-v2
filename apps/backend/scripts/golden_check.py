"""CAR-18 — deterministic golden suite check (no OpenAI)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from career_forge.services.golden_cases import (  # noqa: E402
    check_suite,
    recommended_cutoff_from_seeds,
)
from career_forge.services.soft_gate import soft_gate_cutoff  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CAR-18 golden-check (deterministic)")
    parser.add_argument(
        "--cutoff",
        type=float,
        default=None,
        help="Override soft-gate cutoff (default: SOFT_GATE_CUTOFF / code default)",
    )
    args = parser.parse_args(argv)

    bar = args.cutoff if args.cutoff is not None else soft_gate_cutoff()
    recommended = recommended_cutoff_from_seeds()
    print("== golden-check (CAR-18) ==")
    suffix = f" recommended_midpoint={recommended:.2f}" if recommended is not None else ""
    print(f"cutoff={bar}{suffix}")

    results = check_suite(cutoff=bar)
    failed = 0
    for result in results:
        if result.ok:
            print(f"  PASS {result.case_id}")
            continue
        failed += 1
        print(f"  FAIL {result.case_id}")
        for err in result.errors:
            print(f"         - {err}")

    if failed:
        print(f"GOLDEN CHECK FAILED ({failed})")
        return 1
    print("GOLDEN CHECK OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
