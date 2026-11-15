"""
Configuration schema and defaults for deterministic synthetic data generation.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class GeneratorConfig:
    """Configuration parameters for the O2C synthetic data generator."""

    # Deterministic Random Seed
    seed: int = 20261022

    # Fixed Simulation Dates (UTC)
    start_date: datetime = field(
        default_factory=lambda: datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    simulation_date: datetime = field(
        default_factory=lambda: datetime(2026, 10, 31, 23, 59, 59, tzinfo=timezone.utc)
    )

    # Generation Profile & Scale Factor
    profile: str = "full"  # "full", "sample", "test"
    scale: float = 1.0

    # Batch Insert Size for PostgreSQL Performance
    batch_size: int = 2500

    # Output directory for manifest and optional CSV exports
    output_dir: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent / "outputs"
    )
    export_csv: bool = False

    # Base Target Volumes (at scale = 1.0)
    base_accounts: int = 100
    base_quotes: int = 10000
    base_orders: int = 7000
    base_shipments: int = 7500
    base_invoices: int = 8000
    base_payments: int = 15000
    base_allocations: int = 20000
    base_disputes: int = 500

    def __post_init__(self):
        # Adjust scale based on profile if profile was passed
        if self.profile == "sample":
            self.scale = 0.1
        elif self.profile == "test":
            self.scale = 0.01

        # Calculate actual target counts
        self.num_accounts = max(10, int(self.base_accounts * min(1.0, self.scale * 2)))
        self.num_quotes = max(10, int(self.base_quotes * self.scale))
        self.num_orders = max(7, int(self.base_orders * self.scale))
        self.num_shipments = max(7, int(self.base_shipments * self.scale))
        self.num_invoices = max(8, int(self.base_invoices * self.scale))
        self.num_payments = max(15, int(self.base_payments * self.scale))
        self.num_allocations = max(20, int(self.base_allocations * self.scale))
        self.num_disputes = max(5, int(self.base_disputes * self.scale))

        self.output_dir.mkdir(parents=True, exist_ok=True)
