"""
CLI Entry Point for O2C Synthetic Data Generation.
Usage:
    python -m app.generators.generate_data
    python -m app.generators.generate_data --profile full
    python -m app.generators.generate_data --profile sample
    python -m app.generators.generate_data --profile test
    python -m app.generators.generate_data --seed 20261022 --scale 1.0
"""

import argparse
import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parent.parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.generators.config import GeneratorConfig
from app.generators.pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Deterministic O2C Synthetic Data Generator & Anomaly Injector"
    )
    parser.add_argument(
        "--profile",
        choices=["full", "sample", "test"],
        default="full",
        help="Volume profile: full (100%), sample (10%), test (1%) [default: full]",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=None,
        help="Custom scaling multiplier (overrides profile scale if set)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20261022,
        help="Master random seed for bitwise reproducibility [default: 20261022]",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=2500,
        help="SQLAlchemy bulk insert batch chunk size [default: 2500]",
    )
    parser.add_argument(
        "--export-csv",
        action="store_true",
        help="Export all generated tables to CSV in the output directory",
    )

    args = parser.parse_args()

    # Initialize configuration
    cfg = GeneratorConfig(
        seed=args.seed,
        profile=args.profile,
        batch_size=args.batch_size,
        export_csv=args.export_csv,
    )

    if args.scale is not None:
        cfg.scale = args.scale
        cfg.__post_init__()

    try:
        manifest = run_pipeline(cfg)
        print(f"Status: SUCCESS")
        sys.exit(0)
    except Exception as exc:
        print(f"\n❌ Error during generation: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
