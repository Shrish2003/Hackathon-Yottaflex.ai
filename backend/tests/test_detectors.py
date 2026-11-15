"""
Smoke and unit tests for O2C Revenue Leakage Detection Engine.
Verifies detector registration, result structure, and strict ground truth isolation.
"""

import inspect
import pytest
from app.detectors.engine import DetectionEngine
from app.detectors.base import BaseDetector, DetectionResult
import app.detectors.rules as rules_module
import app.detectors.engine as engine_module


def test_engine_detectors_registration():
    """Verify all 12 detectors are registered in the engine."""
    engine = DetectionEngine()
    assert len(engine.detectors) == 12

    registered_types = {d.issue_type for d in engine.detectors}
    expected_types = {
        "OVERBILLING_QUANTITY",
        "OVERBILLING_AMOUNT",
        "UNDERBILLING",
        "DUPLICATE_INVOICE",
        "DUPLICATE_PAYMENT_ALLOCATION",
        "EXCESSIVE_PAYMENT_ALLOCATION",
        "PREMATURE_ORDER_CLOSURE",
        "INVALID_STATUS_TRANSITION",
        "DISPUTE_AR_DISCONNECT",
        "SHORT_PAYMENT",
        "SLA_AGING_BREACH",
        "OVERDUE_UNPAID_INVOICE",
    }
    assert registered_types == expected_types


def test_ground_truth_isolation():
    """
    CRITICAL ARCHITECTURAL GUARANTEE:
    Verify that detection modules NEVER import or reference GroundTruthAnomaly.
    """
    rules_src = inspect.getsource(rules_module)
    engine_src = inspect.getsource(engine_module)

    assert "ground_truth_anomalies" not in rules_src.split('"""')[2], "rules.py queries ground_truth_anomalies table!"
    assert "GroundTruthAnomaly" not in rules_src, "rules.py imports GroundTruthAnomaly!"
    assert "GroundTruthAnomaly" not in engine_src, "engine.py imports GroundTruthAnomaly!"
    assert "from app.models.ground_truth" not in rules_src
    assert "from app.models.ground_truth" not in engine_src


def test_detection_result_structure():
    """Verify DetectionResult dataclass field types."""
    import uuid
    from decimal import Decimal
    from datetime import datetime, timezone

    res = DetectionResult(
        issue_type="OVERBILLING_QUANTITY",
        severity="HIGH",
        entity_type="Invoice",
        entity_id=uuid.uuid4(),
        business_id="INV-2026-000001",
        leakage_amount=Decimal("5000.00"),
        explanation="Test explanation",
        recommended_action="Test action",
    )
    assert res.issue_type == "OVERBILLING_QUANTITY"
    assert res.severity == "HIGH"
    assert res.leakage_amount == Decimal("5000.00")
