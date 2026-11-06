#!/usr/bin/env python3
"""Minimal Standalone Bug Reproduction Script for pie-Switch.

Target: target_service/app.py (/api/v1/checkout)
Expected Defect: ZeroDivisionError when net_subtotal is 0.0 under 100% discount.
Behavior:
- Exits with 1 when bug is present (HTTP 500 / ZeroDivisionError).
- Exits with 0 when bug is fixed (HTTP 200 OK).
"""

import json
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

POISON_PAYLOAD = {
    "cart_id": "cart_repro_zero_div",
    "currency": "USD",
    "items": [
        {"id": "sku_edge_01", "name": "Hackathon Demo Package", "price": 99.00, "qty": 1}
    ],
    "coupon_code": "PROMO100",
    "tax_rate": 0.08,
    "metadata": {"test_run": "repro_bug"},
}

TARGET_URL = "http://127.0.0.1:8080/api/v1/checkout"


def run_repro() -> int:
    """Executes the reproduction against the target service."""
    # Attempt live HTTP request first
    try:
        import httpx
        try:
            resp = httpx.post(TARGET_URL, json=POISON_PAYLOAD, timeout=2.0)
            status_code = resp.status_code
            resp_data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text
        except (httpx.ConnectError, httpx.TimeoutException, httpx.RequestError):
            # Fall back to in-memory TestClient if daemon is not running externally
            from fastapi.testclient import TestClient
            from target_service.app import app
            client = TestClient(app)
            resp = client.post("/api/v1/checkout", json=POISON_PAYLOAD)
            status_code = resp.status_code
            resp_data = resp.json()
    except Exception as exc:
        sys.stderr.write(f"[REPRO-ERROR] Failed to execute repro request: {exc}\n")
        return 1

    if status_code == 500:
        sys.stderr.write("=" * 60 + "\n")
        sys.stderr.write("[REPRO-CONFIRMED] Latent Bug Triggered (HTTP 500)\n")
        sys.stderr.write(f"Response: {json.dumps(resp_data, indent=2)}\n")
        sys.stderr.write("=" * 60 + "\n")
        return 1
    elif status_code == 200:
        sys.stdout.write("=" * 60 + "\n")
        sys.stdout.write("[REPRO-RESOLVED] Bug not triggered (HTTP 200 OK)\n")
        sys.stdout.write(f"Response: {json.dumps(resp_data, indent=2)}\n")
        sys.stdout.write("=" * 60 + "\n")
        return 0
    else:
        sys.stderr.write(f"[REPRO-UNEXPECTED] Unexpected HTTP {status_code}\n")
        return 2


if __name__ == "__main__":
    sys.exit(run_repro())
