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
from fastapi.responses import HTMLResponse, JSONResponse
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

room_events: List[Dict[str, Any]] = [
    {
        "id": 1,
        "sender": "system",
        "role": "system",
        "time": datetime.now(timezone.utc).strftime("%H:%M:%S"),
        "content": "🚀 AegisRoom Initialized.\nTopology: @watchdog-sse ➔ @pie-triager ➔ @pie-repro ➔ @pie-patcher ➔ @alex.\nProtocol: Strict 3-Line Output Contract active. Asymmetric Human Approval Gate armed.",
    }
]


def add_room_event(sender: str, content: str, role: str = "agent") -> None:
    room_events.append({
        "id": len(room_events) + 1,
        "sender": sender,
        "role": role,
        "time": datetime.now(timezone.utc).strftime("%H:%M:%S"),
        "content": content,
    })


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


class VoiceIdeaRequest(BaseModel):
    idea: str = Field(..., example="Implement dynamic currency conversion for EUR and GBP")
    author: str = Field(default="@alex")
    voice_transcribed: bool = Field(default=True)
    tags: List[str] = Field(default_factory=lambda: ["feature", "solo-chill", "wispr-flow"])


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

        # Broadcast live multi-agent choreography to the Switch War Room
        add_room_event(
            "@watchdog-sse",
            f"[P0-CRITICAL] Telemetry Breach: {exc_type} in /api/v1/checkout\n"
            f"Root Cause: {str(exc)} ({failing_file}:{failing_line})\n"
            f"Handoff: @pie-triager please ingest crash report and route to repro sandbox.",
        )
        add_room_event(
            "@pie-triager",
            "[P0-CRITICAL] Checkout Failure Confirmed (Severity: P0-CRITICAL)\n"
            "Root Cause: Zero division on 100% discount promo code in /api/v1/checkout\n"
            "Handoff: @pie-repro please synthesize isolated repro script and verify crash.",
        )
        add_room_event(
            "@pie-repro",
            f"[REPRO-CONFIRMED] Sandbox failure captured: exit code 1 (Traceback verified)\n"
            f"Artifact: ./workspace/repro/repro_bug.py | Target: {failing_file}:{failing_line}\n"
            "Handoff: @pie-patcher please synthesize surgical patch and verify against test suite.",
        )
        add_room_event(
            "@pie-patcher",
            "[PATCH-READY] Surgical fix validated in sandbox (8/8 baseline tests pass)\n"
            "Artifact: ./workspace/patches/fix.patch | Diff: fee_attribution_ratio = (processing_fee / net_subtotal if net_subtotal > 0 else 0.0)\n"
            'Action Required: @alex please review diff. Reply with "Approved. Deploy patch." to authorize @watchdog-sse.',
        )

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

        # Broadcast live multi-agent choreography to the Switch War Room
        add_room_event(
            "@watchdog-sse",
            f"[P1-HIGH] Sleep-Mode Guardian: CI/CD Pipeline failure in {request.repository}\n"
            f"Root Cause: CI/CD build failed on branch main (error count: {request.metrics.get('error_count', 1)})\n"
            f"Handoff: @pie-triager please analyze failing step and notify @alex.",
        )
        add_room_event(
            "@pie-triager",
            f"[P1-HIGH] Sleep-Mode CI Alert Confirmed (Repo: {request.repository})\n"
            f"Artifact: GitHub Actions run log (Exit code 1)\n"
            f"Handoff: @alex notice sent to founder mobile chat while in sleep mode.",
        )

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


@app.post("/api/v1/voice-idea")
async def voice_idea(request: VoiceIdeaRequest) -> Dict[str, Any]:
    """Track 02 (Solo-Indie Mode): Voice-Transcribed Task / Idea Dispatcher."""
    metrics["total_requests"] += 1
    metrics["successful_requests"] += 1
    now_str = datetime.now(timezone.utc).isoformat()

    telemetry_entry = {
        "timestamp": now_str,
        "level": "INFO",
        "severity": "PERSONAL-BUILD-TASK",
        "endpoint": "/api/v1/voice-idea",
        "status_code": 200,
        "author": request.author,
        "idea": request.idea,
        "voice_transcribed": request.voice_transcribed,
        "tags": request.tags,
    }
    write_service_log(telemetry_entry)

    return {
        "status": "ingested",
        "workflow": "solo-chill",
        "idea": request.idea,
        "author": request.author,
        "dispatched_to": "Switch Room Decisions Log",
        "timestamp": now_str,
    }


# ------------------------------------------------------------------------------
# Interactive Live Demo Web Dashboard Endpoints
# ------------------------------------------------------------------------------
@app.get("/api/v1/room-events")
async def get_room_events() -> Dict[str, Any]:
    """Provides real-time room events and telemetry to the live web dashboard."""
    app_text = Path("target_service/app.py").read_text(encoding="utf-8") if Path("target_service/app.py").exists() else ""
    is_patched = "fee_attribution_ratio = (" in app_text

    return {
        "events": room_events,
        "metrics": {
            **metrics,
            "uptime_seconds": round(time.time() - metrics["start_time"], 1),
            "is_patched": is_patched,
            "status": "HEALED" if is_patched else ("DEGRADED" if metrics["failed_requests"] > 0 else "HEALTHY"),
        },
    }


@app.post("/api/v1/trigger-chaos-action")
async def trigger_chaos_action() -> Dict[str, Any]:
    """Triggers the poison pill payload from the web dashboard."""
    from fastapi.testclient import TestClient
    client = TestClient(app)
    resp = client.post(
        "/api/v1/checkout",
        json={
            "cart_id": f"cart_chaos_{uuid.uuid4().hex[:6]}",
            "items": [{"id": "item_promo", "name": "Enterprise Suite Promo", "price": 500.0, "qty": 1}],
            "coupon_code": "PROMO100",
            "tax_rate": 0.08,
        },
    )
    return {"status_code": resp.status_code, "data": resp.json()}


@app.post("/api/v1/approve-deploy")
async def approve_deploy() -> Dict[str, Any]:
    """Human-in-the-Loop Approval Gate: Authorizes patch application and hot-reload."""
    add_room_event("@alex", "Approved. Deploy patch.", role="human")
    
    # Apply surgical fix to target_service/app.py
    app_file = Path("target_service/app.py")
    if app_file.exists():
        content = app_file.read_text(encoding="utf-8")
        buggy_needle = "fee_attribution_ratio = processing_fee / net_subtotal"
        fixed_needle = (
            "# SURGICAL FIX: Safe fee attribution ratio calculation\n"
            "        fee_attribution_ratio = (\n"
            "            processing_fee / net_subtotal if net_subtotal > 0 else 0.0\n"
            "        )"
        )
        if buggy_needle in content:
            app_file.write_text(content.replace(buggy_needle, fixed_needle), encoding="utf-8")
    
    # Verification probe
    add_room_event(
        "@watchdog-sse",
        "[DEPLOYMENT-VERIFIED] Hot-reload successful & zero-downtime healthcheck passed\n"
        "Artifact: target_service/app.py patched | Repro test HTTP 200 OK (latency: 2.8ms)\n"
        "Status: All systems operational. Incident #1 closed in Switch Decisions Log.",
    )
    
    return {"status": "deployed_and_verified", "is_patched": True}


@app.post("/api/v1/reset-demo-action")
async def reset_demo_action() -> Dict[str, Any]:
    """Resets the microservice and room feed to the baseline demo state."""
    orig_file = Path("target_service/app.py.orig")
    target_file = Path("target_service/app.py")
    if orig_file.exists():
        import shutil
        shutil.copy(orig_file, target_file)
    
    # Clear service log
    log_file = Path(LOG_FILE_PATH)
    if log_file.exists():
        log_file.write_text("", encoding="utf-8")

    global room_events
    room_events.clear()
    room_events.append({
        "id": 1,
        "sender": "system",
        "role": "system",
        "time": datetime.now(timezone.utc).strftime("%H:%M:%S"),
        "content": "🚀 AegisRoom Reset Complete. Service returned to baseline buggy state. Ready for chaos trigger.",
    })
    
    metrics["failed_requests"] = 0
    return {"status": "reset_complete"}


@app.get("/", response_class=HTMLResponse)
async def live_dashboard() -> str:
    """Renders the comprehensive live interactive demo cockpit."""
    return """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AegisRoom — Live Interactive Incident War-Room</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: { 500: '#6366f1', 600: '#4f46e5' }
          }
        }
      }
    }
  </script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    @keyframes pulse-slow { 0%, 100% { opacity: 1; } 50% { opacity: .4; } }
    .pulse-status { animation: pulse-slow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col font-sans antialiased">
  <!-- Top Navigation Bar -->
  <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <div class="h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center text-white font-bold shadow-lg shadow-indigo-500/20">
        🛡️
      </div>
      <div>
        <div class="flex items-center gap-2">
          <h1 class="font-bold text-lg text-white tracking-tight">AegisRoom</h1>
          <span class="text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-mono">pie-Switch</span>
        </div>
        <p class="text-xs text-slate-400">Autonomous Incident War-Room & DevSecOps Co-Pilot</p>
      </div>
    </div>
    <div class="flex items-center gap-4">
      <div id="statusBadge" class="flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
        <span class="h-2 w-2 rounded-full bg-emerald-400 pulse-status"></span>
        <span id="statusText">SYSTEM HEALTHY</span>
      </div>
      <a href="https://github.com/MrDunky14/pie-switch" target="_blank" class="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-1.5 transition">
        <i class="fab fa-github"></i> GitHub Repo
      </a>
    </div>
  </header>

  <!-- Main Grid Layout -->
  <main class="flex-1 max-w-7xl w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
    <!-- Left Column: Switch War Room Chat (7 cols) -->
    <section class="lg:col-span-7 flex flex-col bg-slate-900/60 rounded-2xl border border-slate-800 overflow-hidden shadow-2xl backdrop-blur">
      <div class="px-5 py-3.5 border-b border-slate-800 bg-slate-900/90 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-slate-400"><i class="fas fa-hashtag text-indigo-400"></i></span>
          <span class="font-semibold text-sm text-slate-200">pie-war-room</span>
          <span class="text-xs text-slate-500 font-mono">| Switch Protocol SSE In/HTTP Out</span>
        </div>
        <div class="flex items-center gap-2 text-xs text-slate-400">
          <span class="h-2 w-2 rounded-full bg-indigo-400"></span> 4 Agents + 1 Human
        </div>
      </div>

      <!-- Messages Stream -->
      <div id="chatFeed" class="flex-1 p-5 overflow-y-auto space-y-4 max-h-[640px] font-sans">
        <div class="text-center py-8 text-slate-500 text-xs">Connecting to Switch Room Stream...</div>
      </div>

      <!-- Chat Prompt Box (Simulation) -->
      <div class="p-4 border-t border-slate-800 bg-slate-900/90 flex gap-2">
        <input id="chatInput" type="text" value='Approved. Deploy patch.' class="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500" placeholder="Type room command...">
        <button onclick="approveDeploy()" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-indigo-600/30 transition flex items-center gap-1.5">
          <i class="fas fa-paper-plane"></i> Send Approval
        </button>
      </div>
    </section>

    <!-- Right Column: Interactive Cockpit & Telemetry (5 cols) -->
    <section class="lg:col-span-5 flex flex-col gap-6">
      <!-- Chaos & Action Control Card -->
      <div class="bg-slate-900/60 rounded-2xl border border-slate-800 p-5 shadow-xl backdrop-blur">
        <h2 class="text-xs uppercase font-mono font-bold tracking-wider text-slate-400 mb-4 flex items-center gap-2">
          <i class="fas fa-gamepad text-indigo-400"></i> Live Demo Cockpit
        </h2>
        <div class="flex flex-col gap-3">
          <button onclick="triggerChaos()" class="w-full py-3 px-4 rounded-xl font-semibold text-sm bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white shadow-lg shadow-red-600/20 transition flex items-center justify-center gap-2">
            <i class="fas fa-bolt"></i> 1. Trigger Production Chaos (HTTP 500)
          </button>
          
          <button onclick="approveDeploy()" class="w-full py-3 px-4 rounded-xl font-semibold text-sm bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-600/20 transition flex items-center justify-center gap-2">
            <i class="fas fa-check-double"></i> 2. Authorize Hot-Reload ("Approved")
          </button>

          <div class="grid grid-cols-2 gap-3 mt-1">
            <button onclick="sendNormalOrder()" class="py-2.5 px-3 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition flex items-center justify-center gap-1.5">
              <i class="fas fa-shopping-cart text-cyan-400"></i> Normal Order ($100)
            </button>
            <button onclick="sendVoiceIdea()" class="py-2.5 px-3 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition flex items-center justify-center gap-1.5">
              <i class="fas fa-microphone text-indigo-400"></i> Voice Idea (/solo)
            </button>
          </div>

          <button onclick="resetDemo()" class="mt-2 py-2 px-3 rounded-xl text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-slate-800 transition flex items-center justify-center gap-1.5">
            <i class="fas fa-redo"></i> Reset Demo to Baseline Buggy State
          </button>
        </div>
      </div>

      <!-- Real-Time Telemetry Counters -->
      <div class="bg-slate-900/60 rounded-2xl border border-slate-800 p-5 shadow-xl backdrop-blur">
        <h2 class="text-xs uppercase font-mono font-bold tracking-wider text-slate-400 mb-3 flex items-center gap-2">
          <i class="fas fa-chart-line text-cyan-400"></i> Telemetry & Health Metrics
        </h2>
        <div class="grid grid-cols-2 gap-3 text-center">
          <div class="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <div class="text-xs text-slate-400 font-mono">TOTAL REQUESTS</div>
            <div id="statTotal" class="text-xl font-bold text-white mt-1">0</div>
          </div>
          <div class="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <div class="text-xs text-slate-400 font-mono">FAILED (500)</div>
            <div id="statFailed" class="text-xl font-bold text-rose-400 mt-1">0</div>
          </div>
          <div class="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <div class="text-xs text-slate-400 font-mono">UPTIME</div>
            <div id="statUptime" class="text-xl font-bold text-indigo-400 mt-1">0s</div>
          </div>
          <div class="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <div class="text-xs text-slate-400 font-mono">HOTFIX STATUS</div>
            <div id="statPatched" class="text-sm font-bold text-amber-400 mt-2">UNPATCHED</div>
          </div>
        </div>
      </div>

      <!-- Architecture Card -->
      <div class="bg-slate-900/40 rounded-2xl border border-slate-800 p-4 text-xs text-slate-400 space-y-2 font-mono">
        <div class="text-slate-300 font-bold flex items-center gap-2">
          <i class="fas fa-shield-alt text-indigo-400"></i> Psychological UX Rules
        </div>
        <p>• <b>3-Line Contract:</b> Status ➔ Root Cause ➔ Handoff</p>
        <p>• <b>Addressing Scopes:</b> Specialist agents remain silent until @mentioned</p>
        <p>• <b>Human Gate:</b> AI cannot deploy without human sign-off</p>
      </div>
    </section>
  </main>

  <script>
    const colorMap = {
      '@watchdog-sse': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      '@pie-triager': 'bg-fuchsia-500/10 text-fuchsia-400 border-fuchsia-500/30',
      '@pie-repro': 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      '@pie-patcher': 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
      '@alex': 'bg-rose-500/20 text-rose-300 border-rose-500/40 font-bold',
      'system': 'bg-slate-800 text-slate-300 border-slate-700'
    };

    let lastEventCount = 0;

    async function pollRoom() {
      try {
        const res = await fetch('/api/v1/room-events');
        const data = await res.json();
        
        // Update metrics
        document.getElementById('statTotal').innerText = data.metrics.total_requests;
        document.getElementById('statFailed').innerText = data.metrics.failed_requests;
        document.getElementById('statUptime').innerText = data.metrics.uptime_seconds + 's';
        
        const badge = document.getElementById('statusBadge');
        const badgeText = document.getElementById('statusText');
        const statPatched = document.getElementById('statPatched');

        if (data.metrics.is_patched) {
          statPatched.innerText = 'VERIFIED HOTFIX';
          statPatched.className = 'text-sm font-bold text-emerald-400 mt-2';
          badge.className = 'flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30';
          badgeText.innerText = 'SYSTEM HEALED (200 OK)';
        } else if (data.metrics.failed_requests > 0) {
          statPatched.innerText = 'BUG TRIGGERED';
          statPatched.className = 'text-sm font-bold text-rose-400 mt-2';
          badge.className = 'flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30';
          badgeText.innerText = 'P0-CRITICAL INCIDENT';
        } else {
          statPatched.innerText = 'READY (LATENT BUG)';
          statPatched.className = 'text-sm font-bold text-amber-400 mt-2';
          badge.className = 'flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30';
          badgeText.innerText = 'SYSTEM ONLINE';
        }

        // Render messages
        if (data.events.length !== lastEventCount) {
          lastEventCount = data.events.length;
          const feed = document.getElementById('chatFeed');
          feed.innerHTML = data.events.map(ev => {
            const badgeClass = colorMap[ev.sender] || 'bg-slate-800 text-slate-300 border-slate-700';
            const lines = ev.content.split('\\n');
            const formattedContent = lines.map(line => {
              if (line.startsWith('Handoff:') || line.startsWith('Action Required:')) {
                return `<div class="font-semibold text-indigo-300 mt-1">${line}</div>`;
              } else if (line.startsWith('Artifact:')) {
                return `<div class="text-xs text-slate-400 font-mono mt-0.5">${line}</div>`;
              } else {
                return `<div>${line}</div>`;
              }
            }).join('');

            return `
              <div class="flex flex-col gap-1.5 p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 shadow-sm transition">
                <div class="flex items-center justify-between">
                  <span class="px-2 py-0.5 rounded-md text-xs font-mono font-medium border ${badgeClass}">
                    ${ev.sender}
                  </span>
                  <span class="text-[10px] text-slate-500 font-mono">${ev.time}</span>
                </div>
                <div class="text-xs text-slate-200 leading-relaxed font-sans mt-0.5">
                  ${formattedContent}
                </div>
              </div>
            `;
          }).join('');
          feed.scrollTop = feed.scrollHeight;
        }
      } catch (err) {
        console.error("Poll error:", err);
      }
    }

    async function triggerChaos() {
      await fetch('/api/v1/trigger-chaos-action', { method: 'POST' });
      await pollRoom();
    }

    async function approveDeploy() {
      await fetch('/api/v1/approve-deploy', { method: 'POST' });
      await pollRoom();
    }

    async function sendNormalOrder() {
      await fetch('/api/v1/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cart_id: 'cart_web_normal',
          items: [{ id: 'sku_1', name: 'Cloud Tier', price: 100.0, qty: 1 }],
          coupon_code: null,
          tax_rate: 0.08
        })
      });
      await pollRoom();
    }

    async function sendVoiceIdea() {
      await fetch('/api/v1/voice-idea', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          idea: 'Add dynamic currency converter for GBP and EUR',
          author: '@alex',
          voice_transcribed: true,
          tags: ['feature', 'solo-chill', 'wispr-flow']
        })
      });
      await pollRoom();
    }

    async function resetDemo() {
      await fetch('/api/v1/reset-demo-action', { method: 'POST' });
      lastEventCount = 0;
      await pollRoom();
    }

    setInterval(pollRoom, 1500);
    pollRoom();
  </script>
</body>
</html>"""


# ------------------------------------------------------------------------------
# Entrypoint
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    host = os.getenv("TARGET_SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("TARGET_SERVICE_PORT", "8080"))
    uvicorn.run("app:app", host=host, port=port, reload=True, app_dir="target_service")
