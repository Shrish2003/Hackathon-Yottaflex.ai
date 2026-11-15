"""
O2C Revenue Leakage & Process Anomaly Detection Engine Package.
Deterministic, explainable rule-based detectors for all 12 O2C anomaly categories.
CRITICAL: This module NEVER accesses ground_truth_anomalies.
"""

from app.detectors.base import BaseDetector, DetectionResult, EvidenceItem
from app.detectors.engine import DetectionEngine

__all__ = ["BaseDetector", "DetectionResult", "EvidenceItem", "DetectionEngine"]
