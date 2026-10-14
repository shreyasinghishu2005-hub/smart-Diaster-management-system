"""Automated test cases for rule-based priority triage and scikit-learn ML demonstration."""

import pytest
from services.priority_service import classify_incident_priority, ml_classifier


def test_critical_priority_with_trapped_and_casualty_keywords():
    """Verify that dangerous keywords elevate incident to Critical priority."""
    priority, score, reasons = classify_incident_priority(
        disaster_type="Fire",
        title="Commercial Warehouse Fire",
        description="Massive fire erupted with multiple trapped workers and structural collapse.",
        has_trapped_or_injured=True,
    )
    assert priority == "Critical"
    assert score >= 70
    assert any("trapped" in r.lower() for r in reasons)


def test_high_priority_for_road_accident_with_injuries():
    """Verify that accidents with injuries and bleeding receive High priority."""
    priority, score, reasons = classify_incident_priority(
        disaster_type="Road Accident",
        title="Highway Collision",
        description="Two cars collided on expressway with severe injuries and bleeding.",
        has_trapped_or_injured=False,
    )
    assert priority in ["High", "Critical"]
    assert score >= 45


def test_low_priority_for_controlled_minor_incident():
    """Verify that mitigating keywords reduce priority score to Low."""
    priority, score, reasons = classify_incident_priority(
        disaster_type="Other",
        title="Routine Safety Inspection",
        description="Controlled drill conducted on campus with all areas safe and no injuries reported.",
        has_trapped_or_injured=False,
    )
    assert priority == "Low"
    assert score < 20
    assert any("drill" in r.lower() or "safe" in r.lower() or "no injuries" in r.lower() for r in reasons)


def test_score_clamping():
    """Verify that calculated score remains within [0, 100]."""
    # Extreme scenario
    _, max_score, _ = classify_incident_priority(
        disaster_type="Earthquake",
        title="Catastrophic earthquake explosion fatal death casualty collapsed building",
        description="massive fire trapped victims drowning explosion toxic leak heart attack multiple victims",
        has_trapped_or_injured=True,
        is_hazard_spreading=True,
        has_structural_collapse=True,
    )
    assert 0 <= max_score <= 100

    # Negative extreme
    _, min_score, _ = classify_incident_priority(
        disaster_type="Other",
        title="Minor drill false alarm safe",
        description="routine inspection controlled contained cleared safe no injuries",
    )
    assert 0 <= min_score <= 100


def test_scikit_learn_ml_classifier_prediction():
    """Verify that scikit-learn demonstration predictor returns a class and confidence."""
    result = ml_classifier.predict("Building collapsed with trapped casualties inside")
    assert result.get("available") is True
    assert result.get("prediction") in ["Critical", "High", "Medium", "Low"]
    assert "confidence" in result
    assert result["confidence"] > 0
