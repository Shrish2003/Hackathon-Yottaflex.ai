"""
Synthetic Data Generation & Anomaly Injection Module for O2C Revenue Assurance Platform.
"""

from app.generators.config import GeneratorConfig
from app.generators.pipeline import run_pipeline

__all__ = ["GeneratorConfig", "run_pipeline"]
