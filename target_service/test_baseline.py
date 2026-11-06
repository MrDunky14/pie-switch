"""Baseline Pytest Suite for pie-Switch Target Microservice.

Validates normal functionality, edge cases, and verifies that the latent
ZeroDivisionError occurs deterministically under the poison payload.
"""

import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure environment uses temporary or local workspace log
os.environ["LOG_FILE_PATH"] = "./workspace/service.log"

from target_service.app import app, write_service_log

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_workspace():
    """Ensure workspace directory exists before test execution."""
    Path("./workspace").mkdir(parents=True, exist_ok=True)
    yield


def test_health_endpoint():
    """Validates liveness probe returns HTTP 200 and healthy metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "pie-switch-target"
    assert "version" in data
    assert "uptime_seconds" in data


def test_metrics_endpoint():
    """Validates metrics endpoint reports request telemetry counters."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "pie-switch-target"
    assert "total_requests" in data
    assert "successful_requests" in data
    assert "failed_requests" in data


def test_checkout_standard_order():
    """Validates standard checkout calculation with normal pricing and tax."""
    payload = {
        "cart_id": "cart_test_standard",
        "currency": "USD",
        "items": [
            {"id": "item_1", "name": "Basic Cloud Tier", "price": 50.00, "qty": 2}
        ],
        "coupon_code": None,
        "tax_rate": 0.08,
    }
    response = client.post("/api/v1/checkout", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["raw_subtotal"] == 100.00
    assert data["discount_amount"] == 0.00
    assert data["net_subtotal"] == 100.00
    assert data["processing_fee"] == 2.50
    assert data["fee_attribution_ratio"] == 0.025  # 2.50 / 100.0
    assert data["tax"] == 8.00  # 100 * 0.08
    assert data["total"] == 110.50  # 100 + 8 + 2.50


def test_checkout_partial_discount_coupon():
    """Validates 25% discount coupon (SAVE25) calculates correctly."""
    payload = {
        "cart_id": "cart_test_save25",
        "currency": "USD",
        "items": [
            {"id": "item_1", "name": "Standard License", "price": 200.00, "qty": 1}
        ],
        "coupon_code": "SAVE25",
        "tax_rate": 0.10,
    }
    response = client.post("/api/v1/checkout", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["raw_subtotal"] == 200.00
    assert data["discount_amount"] == 50.00
    assert data["net_subtotal"] == 150.00
    assert data["processing_fee"] == 2.50
    assert data["tax"] == 15.00
    assert data["total"] == 167.50


def test_indie_webhook_healthy_event():
    """Validates Track 02 (Indie Mode) webhook accepts healthy CI/CD telemetry."""
    payload = {
        "event": "workflow_run",
        "repository": "pie-switch",
        "sender": "developer",
        "status": "success",
        "metrics": {"duration_ms": 1200, "error_count": 0},
    }
    response = client.post("/api/v1/indie-webhook", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["guardian_mode"] == "sleep_mode_active"


def test_indie_webhook_failure_alert():
    """Validates Track 02 (Indie Mode) webhook triggers alert on pipeline failure."""
    payload = {
        "event": "workflow_run",
        "repository": "pie-switch",
        "sender": "ci-daemon",
        "status": "failure",
        "metrics": {"duration_ms": 450, "error_count": 1},
    }
    response = client.post("/api/v1/indie-webhook", json=payload)
    assert response.status_code == 500
    data = response.json()
    assert data["status"] == "alert_triggered"
    assert data["severity"] == "P1-HIGH"


def test_zero_division_deterministic_anomaly_behavior():
    """Validates the behavior under poison payload (PROMO100).

    In the unpatched buggy state, net_subtotal is 0.0, causing ZeroDivisionError (HTTP 500).
    In the patched state, safe ratio calculation returns HTTP 200.
    """
    payload = {
        "cart_id": "cart_poison_pill",
        "currency": "USD",
        "items": [
            {"id": "item_zero", "name": "Promo Promotional Package", "price": 75.00, "qty": 1}
        ],
        "coupon_code": "PROMO100",
        "tax_rate": 0.08,
    }
    response = client.post("/api/v1/checkout", json=payload)

    # If unpatched, response is 500 with ZeroDivisionError
    # If patched, response is 200 with fee_attribution_ratio == 0.0
    if response.status_code == 500:
        data = response.json()
        assert data["error"] == "ZeroDivisionError"
        assert data["severity"] == "P0-CRITICAL"
        assert "target_service/app.py" in data["file"].replace("\\", "/")

        # Verify structured log was written
        assert os.path.exists("./workspace/service.log")
        with open("./workspace/service.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert any("ZeroDivisionError" in line for line in lines)
    else:
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["discount_amount"] == 75.00
        assert data["net_subtotal"] == 0.00
        assert data["fee_attribution_ratio"] == 0.0
