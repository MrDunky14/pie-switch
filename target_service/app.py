"""Target Microservice for pie-Switch Incident Management Pipeline.

Supports dual modes:
- Business Mode: Production E-Commerce Checkout API with latent pricing ratio bug.
- Indie Mode: Sleep-Mode DevOps Sidekick Webhook Guardian.
"""

import json
import logging
import os
import sys
import time
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# ------------------------------------------------------------------------------
# Configuration & Environment
# ------------------------------------------------------------------------------
MODE = os.getenv("MODE", "business").lower()
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "./workspace/service.log")
SERVICE_NAME = "pie-switch-target"
SERVICE_VERSION = "1.0.0"

# Ensure workspace directory exists for log tailing
log_dir = Path(LOG_FILE_PATH).parent
log_dir.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------------------
# Telemetry Metrics Store
# ------------------------------------------------------------------------------
metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "last_error_timestamp": None,
    "start_time": time.time(),
}


def write_service_log(entry: Dict[str, Any]) -> None:
    """Appends structured JSON telemetry log entry to `./workspace/service.log`."""
    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()
    except Exception as exc:
        sys.stderr.write(f"Failed to write service log: {exc}\n")


# ------------------------------------------------------------------------------
# FastAPI Application Initialization
# ------------------------------------------------------------------------------
app = FastAPI(
    title="pie-Switch Target Microservice",
    description="Vulnerable target service demonstrating autonomous incident triage & repair.",
    version=SERVICE_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------------------
# Request / Response Schemas
# ------------------------------------------------------------------------------
class CartItem(BaseModel):
    id: str = Field(..., example="sku_cloud_01")
    name: str = Field(..., example="Enterprise Cloud License")
    price: float = Field(..., gt=0, example=120.00)
    qty: int = Field(default=1, gt=0, example=1)


class CheckoutRequest(BaseModel):
    cart_id: str = Field(default_factory=lambda: f"cart_{uuid.uuid4().hex[:8]}")
    currency: str = Field(default="USD")
    items: List[CartItem]
    coupon_code: Optional[str] = Field(default=None, example="PROMO100")
    tax_rate: float = Field(default=0.08, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IndieWebhookRequest(BaseModel):
    event: str = Field(..., example="workflow_run")
    repository: str = Field(..., example="pie-switch")
    sender: str = Field(default="indie-dev")
    status: str = Field(..., example="success")
    metrics: Dict[str, Any] = Field(default_factory=dict)


# ------------------------------------------------------------------------------
# Core Endpoints
# ------------------------------------------------------------------------------
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Liveness & readiness probe."""
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "mode": MODE,
        "uptime_seconds": round(time.time() - metrics["start_time"], 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Exposes real-time telemetry metrics."""
    return {
        "service": SERVICE_NAME,
        "mode": MODE,
        "total_requests": metrics["total_requests"],
        "successful_requests": metrics["successful_requests"],
        "failed_requests": metrics["failed_requests"],
        "last_error_timestamp": metrics["last_error_timestamp"],
        "uptime_seconds": round(time.time() - metrics["start_time"], 2),
    }


@app.post("/api/v1/checkout")
async def checkout(request: CheckoutRequest) -> Dict[str, Any]:
    """E-Commerce Checkout Endpoint (Business Mode).

    Contains a realistic latent bug:
    When a 100% discount promotion (`PROMO100`) is applied, `net_subtotal` drops to 0.0.
    The subsequent dynamic fee allocation ratio calculation attempts a division by `net_subtotal`,
    triggering an uncaught `ZeroDivisionError` and logging structured JSON traceback.
    """
    metrics["total_requests"] += 1
    raw_subtotal = round(sum(item.price * item.qty for item in request.items), 2)

    # Calculate discount amount
    coupon = (request.coupon_code or "").strip().upper()
    if coupon in ["PROMO100", "FREEBIE", "ZEROCOST"]:
        discount_amount = raw_subtotal  # 100% off
    elif coupon == "SAVE25":
        discount_amount = round(raw_subtotal * 0.25, 2)
    elif coupon == "WELCOME10":
        discount_amount = round(raw_subtotal * 0.10, 2)
    else:
        discount_amount = 0.0

    discount_amount = min(discount_amount, raw_subtotal)
    net_subtotal = round(raw_subtotal - discount_amount, 2)
    processing_fee = 2.50

    try:
        # ----------------------------------------------------------------------
        # LATENT DEFECT (ZeroDivisionError)
        # ----------------------------------------------------------------------
        # Calculating dynamic merchant fee attribution ratio relative to net subtotal.
        # BUG: If coupon is 100% off (net_subtotal == 0.0), this crashes with ZeroDivisionError!
        fee_attribution_ratio = processing_fee / net_subtotal

        tax = round(net_subtotal * request.tax_rate, 2)
        total = round(net_subtotal + tax + processing_fee, 2)

        order_id = f"ord_{uuid.uuid4().hex[:12]}"
        metrics["successful_requests"] += 1

        response_payload = {
            "status": "success",
            "order_id": order_id,
            "cart_id": request.cart_id,
            "currency": request.currency,
            "raw_subtotal": raw_subtotal,
            "discount_amount": discount_amount,
            "net_subtotal": net_subtotal,
            "processing_fee": processing_fee,
            "fee_attribution_ratio": round(fee_attribution_ratio, 4),
            "tax": tax,
            "total": total,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Log normal transaction
        write_service_log({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "INFO",
            "endpoint": "/api/v1/checkout",
            "status_code": 200,
            "order_id": order_id,
            "total": total,
            "cart_id": request.cart_id,
        })

        return response_payload

    except Exception as exc:
        metrics["failed_requests"] += 1
        now_str = datetime.now(timezone.utc).isoformat()
        metrics["last_error_timestamp"] = now_str
        tb_str = traceback.format_exc()

        # Extract offending code line details
        exc_type = type(exc).__name__
        tb_lines = traceback.extract_tb(sys.exc_info()[2])
        failing_frame = tb_lines[-1] if tb_lines else None
        failing_file = failing_frame.filename if failing_frame else "target_service/app.py"
        failing_line = failing_frame.lineno if failing_frame else 0

        # Structured crash telemetry logged to `./workspace/service.log`
        error_telemetry = {
            "timestamp": now_str,
            "level": "ERROR",
            "severity": "P0-CRITICAL",
            "endpoint": "/api/v1/checkout",
            "status_code": 500,
            "exception_type": exc_type,
            "exception_message": str(exc),
            "file": failing_file,
            "line": failing_line,
            "traceback": tb_str,
            "payload": request.model_dump(),
        }
        write_service_log(error_telemetry)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "error": exc_type,
                "message": str(exc),
                "severity": "P0-CRITICAL",
                "endpoint": "/api/v1/checkout",
                "file": failing_file,
                "line": failing_line,
                "timestamp": now_str,
            },
        )


@app.post("/api/v1/indie-webhook")
async def indie_webhook(request: IndieWebhookRequest) -> Dict[str, Any]:
    """Indie-Hacker 'Sleep-Mode' DevOps Sidekick Guardian Webhook."""
    metrics["total_requests"] += 1
    now_str = datetime.now(timezone.utc).isoformat()

    if request.status == "failure" or request.metrics.get("error_count", 0) > 0:
        metrics["failed_requests"] += 1
        metrics["last_error_timestamp"] = now_str

        error_telemetry = {
            "timestamp": now_str,
            "level": "ERROR",
            "severity": "P1-HIGH",
            "endpoint": "/api/v1/indie-webhook",
            "status_code": 500,
            "exception_type": "IndieTelemetryAlert",
            "exception_message": f"CI/CD build failed in repo: {request.repository}",
            "file": "target_service/app.py",
            "line": 210,
            "traceback": f"Traceback (most recent call last):\n  File 'target_service/app.py', line 210, in indie_webhook\n    raise RuntimeError('CI/CD Pipeline failed on branch main')\nRuntimeError: CI/CD Pipeline failed on branch main",
            "payload": request.model_dump(),
        }
        write_service_log(error_telemetry)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "alert_triggered",
                "severity": "P1-HIGH",
                "repository": request.repository,
                "message": "Sleep-Mode Guardian captured pipeline failure",
                "timestamp": now_str,
            },
        )

    metrics["successful_requests"] += 1
    write_service_log({
        "timestamp": now_str,
        "level": "INFO",
        "endpoint": "/api/v1/indie-webhook",
        "status_code": 200,
        "repository": request.repository,
        "event": request.event,
    })

    return {
        "status": "healthy",
        "repository": request.repository,
        "guardian_mode": "sleep_mode_active",
        "timestamp": now_str,
    }


# ------------------------------------------------------------------------------
# Entrypoint
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    host = os.getenv("TARGET_SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("TARGET_SERVICE_PORT", "8080"))
    uvicorn.run("app:app", host=host, port=port, reload=True, app_dir="target_service")
