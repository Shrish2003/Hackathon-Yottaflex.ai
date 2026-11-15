"""
CLI Entry Point for O2C Revenue Leakage Detection Engine.
Usage:
    python -m app.detectors.run_detection
"""

import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parent.parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.detectors.engine import DetectionEngine


def main():
    try:
        engine = DetectionEngine()
        summary = engine.run()
        print("Detection Run Status: SUCCESS")
        sys.exit(0)
    except Exception as exc:
        print(f"\n❌ Error during detection execution: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
