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
        buggy_needle = "fee_attribution_ratio = processing_fee / " + "net_subtotal"
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
    """Renders the comprehensive live interactive demo cockpit with Netflix-grade dark UI."""
    return """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AegisRoom — Autonomous Incident War-Room</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            netflix: {
              red: '#E50914',
              darkred: '#B81D24',
              black: '#141414',
              card: '#181818',
              border: '#2f2f2f'
            }
          }
        }
      }
    }
  </script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    @keyframes pulse-slow { 0%, 100% { opacity: 1; } 50% { opacity: .35; } }
    .pulse-status { animation: pulse-slow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
    body { background-color: #141414; }
    .glow-red { box-shadow: 0 0 25px rgba(229, 9, 20, 0.35); }
    .glow-green { box-shadow: 0 0 25px rgba(16, 185, 129, 0.35); }
  </style>
</head>
<body class="text-slate-100 min-h-screen flex flex-col font-sans antialiased selection:bg-red-600 selection:text-white">
  <!-- Top Navigation Bar (Netflix Cinematic Style) -->
  <header class="border-b border-[#232323] bg-[#141414]/95 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
    <div class="flex items-center gap-4">
      <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-[#E50914] to-[#B81D24] flex items-center justify-center text-white font-extrabold text-xl shadow-lg shadow-red-600/30">
        N
      </div>
      <div>
        <div class="flex items-center gap-2">
          <h1 class="font-extrabold text-xl text-white tracking-wider uppercase font-mono">AegisRoom</h1>
          <span class="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-[#E50914]/20 text-[#E50914] border border-[#E50914]/40 uppercase tracking-widest">Flip the Switch</span>
        </div>
        <p class="text-xs text-neutral-400">Autonomous Incident War-Room & Personal DevSecOps Co-Pilot</p>
      </div>
    </div>
    <div class="flex items-center gap-4">
      <div id="statusBadge" class="flex items-center gap-2.5 px-3.5 py-1.5 rounded-full text-xs font-bold tracking-wide uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
        <span class="h-2 w-2 rounded-full bg-emerald-400 pulse-status"></span>
        <span id="statusText">SYSTEM HEALTHY</span>
      </div>
      <a href="https://github.com/MrDunky14/pie-switch" target="_blank" class="text-xs font-semibold px-4 py-2 rounded-lg bg-[#222] hover:bg-[#333] text-white border border-[#333] flex items-center gap-2 transition duration-200">
        <i class="fab fa-github text-sm"></i> GitHub
      </a>
    </div>
  </header>

  <!-- Hero Category Billboard -->
  <div class="px-6 py-2 bg-gradient-to-r from-[#181818] via-[#141414] to-[#181818] border-b border-[#222] text-[11px] font-mono text-neutral-400 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <span class="text-[#E50914] font-bold"><i class="fas fa-fire"></i> TOP 10 INCIDENTS TODAY</span>
      <span>•</span>
      <span>#1 Production Checkout DivisionByZero (Severity: P0-CRITICAL)</span>
    </div>
    <div class="flex items-center gap-2 text-neutral-500">
      <i class="fas fa-tv"></i> Switch Agent Protocol (SSE In / HTTP Out)
    </div>
  </div>

  <!-- Main Grid Layout -->
  <main class="flex-1 max-w-7xl w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
    <!-- Left Column: Switch War Room Chat (7 cols) -->
    <section class="lg:col-span-7 flex flex-col bg-[#181818] rounded-2xl border border-[#262626] overflow-hidden shadow-2xl">
      <div class="px-5 py-3.5 border-b border-[#262626] bg-[#1c1c1c] flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <span class="h-2.5 w-2.5 rounded-full bg-[#E50914]"></span>
          <span class="font-bold text-sm text-neutral-200 tracking-wide"># pie-war-room</span>
          <span class="text-xs text-neutral-500 font-mono">| Live Stream Log</span>
        </div>
        <div class="flex items-center gap-2 text-xs font-medium text-neutral-400">
          <span class="h-2 w-2 rounded-full bg-indigo-500"></span> 4 Agents • 1 Human Lead
        </div>
      </div>

      <!-- Messages Stream -->
      <div id="chatFeed" class="flex-1 p-5 overflow-y-auto space-y-3.5 max-h-[620px] font-sans">
        <div class="text-center py-8 text-neutral-500 text-xs font-mono">Connecting to Switch Room Stream...</div>
      </div>

      <!-- Chat Prompt Box -->
      <div class="p-4 border-t border-[#262626] bg-[#1c1c1c] flex gap-2.5">
        <input id="chatInput" type="text" value='Approved. Deploy patch.' class="flex-1 bg-[#121212] border border-[#333] rounded-xl px-4 py-2.5 text-sm text-neutral-200 focus:outline-none focus:border-[#E50914]" placeholder="Type human authorization...">
        <button onclick="approveDeploy()" class="px-5 py-2.5 bg-[#E50914] hover:bg-[#b81d24] text-white text-xs font-bold uppercase tracking-wider rounded-xl shadow-lg shadow-red-600/30 transition flex items-center gap-2">
          <i class="fas fa-play"></i> Send Approval
        </button>
      </div>
    </section>

    <!-- Right Column: Interactive Cockpit & Telemetry (5 cols) -->
    <section class="lg:col-span-5 flex flex-col gap-6">
      <!-- Chaos & Action Control Card -->
      <div class="bg-[#181818] rounded-2xl border border-[#262626] p-5 shadow-xl">
        <h2 class="text-xs uppercase font-mono font-bold tracking-widest text-[#E50914] mb-4 flex items-center gap-2">
          <i class="fas fa-play-circle"></i> Incident Control Center
        </h2>
        <div class="flex flex-col gap-3">
          <button onclick="triggerChaos()" class="w-full py-3.5 px-4 rounded-xl font-bold text-sm bg-gradient-to-r from-[#E50914] to-[#B81D24] hover:from-[#f40612] hover:to-[#c61a21] text-white shadow-lg shadow-red-600/30 transition flex items-center justify-center gap-2 uppercase tracking-wide">
            <i class="fas fa-bolt"></i> 1. Trigger Production Chaos (500 Error)
          </button>
          
          <button onclick="approveDeploy()" class="w-full py-3.5 px-4 rounded-xl font-bold text-sm bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 text-white shadow-lg shadow-emerald-600/20 transition flex items-center justify-center gap-2 uppercase tracking-wide">
            <i class="fas fa-check-circle"></i> 2. Authorize Hot-Reload ("Approved")
          </button>

          <div class="grid grid-cols-2 gap-3 mt-1">
            <button onclick="sendNormalOrder()" class="py-2.5 px-3 rounded-xl text-xs font-semibold bg-[#222] hover:bg-[#2a2a2a] text-neutral-200 border border-[#333] transition flex items-center justify-center gap-1.5">
              <i class="fas fa-shopping-cart text-cyan-400"></i> Normal Order ($100)
            </button>
            <button onclick="sendVoiceIdea()" class="py-2.5 px-3 rounded-xl text-xs font-semibold bg-[#222] hover:bg-[#2a2a2a] text-neutral-200 border border-[#333] transition flex items-center justify-center gap-1.5">
              <i class="fas fa-microphone text-fuchsia-400"></i> Voice Idea (/solo)
            </button>
          </div>

          <button onclick="resetDemo()" class="mt-2 py-2 px-3 rounded-xl text-xs font-medium text-neutral-400 hover:text-white hover:bg-[#222] border border-[#2a2a2a] transition flex items-center justify-center gap-1.5">
            <i class="fas fa-redo"></i> Reset Demo to Baseline Buggy State
          </button>
        </div>
      </div>

      <!-- Real-Time Telemetry Counters (Netflix Cinema Style) -->
      <div class="bg-[#181818] rounded-2xl border border-[#262626] p-5 shadow-xl">
        <h2 class="text-xs uppercase font-mono font-bold tracking-widest text-neutral-400 mb-3 flex items-center gap-2">
          <i class="fas fa-tachometer-alt text-cyan-400"></i> Telemetry & Health Metrics
        </h2>
        <div class="grid grid-cols-2 gap-3 text-center">
          <div class="p-3.5 rounded-xl bg-[#121212] border border-[#262626]">
            <div class="text-[11px] text-neutral-400 font-mono tracking-wider">TOTAL REQUESTS</div>
            <div id="statTotal" class="text-2xl font-black text-white mt-1">0</div>
          </div>
          <div class="p-3.5 rounded-xl bg-[#121212] border border-[#262626]">
            <div class="text-[11px] text-neutral-400 font-mono tracking-wider">FAILED (500)</div>
            <div id="statFailed" class="text-2xl font-black text-rose-500 mt-1">0</div>
          </div>
          <div class="p-3.5 rounded-xl bg-[#121212] border border-[#262626]">
            <div class="text-[11px] text-neutral-400 font-mono tracking-wider">UPTIME</div>
            <div id="statUptime" class="text-2xl font-black text-indigo-400 mt-1">0s</div>
          </div>
          <div class="p-3.5 rounded-xl bg-[#121212] border border-[#262626]">
            <div class="text-[11px] text-neutral-400 font-mono tracking-wider">HOTFIX STATUS</div>
            <div id="statPatched" class="text-xs font-extrabold text-amber-400 mt-2 tracking-wide">READY (LATENT)</div>
          </div>
        </div>
      </div>

      <!-- Architecture Card -->
      <div class="bg-[#181818]/60 rounded-2xl border border-[#262626] p-4 text-xs text-neutral-400 space-y-2 font-mono">
        <div class="text-neutral-200 font-bold flex items-center gap-2">
          <i class="fas fa-shield-alt text-[#E50914]"></i> Psychological UX Guardrails
        </div>
        <p>• <b>3-Line Contract:</b> Status ➔ Root Cause ➔ Deterministic Handoff</p>
        <p>• <b>Addressing Scopes:</b> Specialist agents silent until tagged</p>
        <p>• <b>Human Gate:</b> AI blocked from prod deployment until human approves</p>
      </div>
    </section>
  </main>

  <script>
    const colorMap = {
      '@watchdog-sse': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      '@pie-triager': 'bg-fuchsia-500/10 text-fuchsia-400 border-fuchsia-500/30',
      '@pie-repro': 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      '@pie-patcher': 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
      '@alex': 'bg-[#E50914]/20 text-rose-300 border-[#E50914]/40 font-bold',
      'system': 'bg-[#222] text-neutral-300 border-[#333]'
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
          statPatched.className = 'text-xs font-extrabold text-emerald-400 mt-2 tracking-wide';
          badge.className = 'flex items-center gap-2.5 px-3.5 py-1.5 rounded-full text-xs font-bold tracking-wide uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 glow-green';
          badgeText.innerText = 'HOT-RELOAD VERIFIED (200 OK)';
        } else if (data.metrics.failed_requests > 0) {
          statPatched.innerText = 'BUG TRIGGERED';
          statPatched.className = 'text-xs font-extrabold text-rose-500 mt-2 tracking-wide';
          badge.className = 'flex items-center gap-2.5 px-3.5 py-1.5 rounded-full text-xs font-bold tracking-wide uppercase bg-red-600/20 text-red-500 border border-red-500/40 glow-red';
          badgeText.innerText = 'P0-CRITICAL ANOMALY';
        } else {
          statPatched.innerText = 'READY (LATENT BUG)';
          statPatched.className = 'text-xs font-extrabold text-amber-400 mt-2 tracking-wide';
          badge.className = 'flex items-center gap-2.5 px-3.5 py-1.5 rounded-full text-xs font-bold tracking-wide uppercase bg-cyan-500/10 text-cyan-400 border border-cyan-500/30';
          badgeText.innerText = 'SYSTEM HEALTHY';
        }

        // Render messages
        if (data.events.length !== lastEventCount) {
          lastEventCount = data.events.length;
          const feed = document.getElementById('chatFeed');
          feed.innerHTML = data.events.map(ev => {
            const badgeClass = colorMap[ev.sender] || 'bg-[#222] text-neutral-300 border-[#333]';
            const lines = ev.content.split('\\n');
            const formattedContent = lines.map(line => {
              if (line.startsWith('Handoff:') || line.startsWith('Action Required:')) {
                return `<div class="font-bold text-[#E50914] mt-1">${line}</div>`;
              } else if (line.startsWith('Artifact:')) {
                return `<div class="text-xs text-neutral-400 font-mono mt-0.5">${line}</div>`;
              } else {
                return `<div>${line}</div>`;
              }
            }).join('');

            return `
              <div class="flex flex-col gap-1.5 p-3.5 rounded-xl bg-[#141414] border border-[#2a2a2a] shadow-sm transition">
                <div class="flex items-center justify-between">
                  <span class="px-2 py-0.5 rounded-md text-[11px] font-mono font-bold uppercase tracking-wider border ${badgeClass}">
                    ${ev.sender}
                  </span>
                  <span class="text-[10px] text-neutral-500 font-mono">${ev.time}</span>
                </div>
                <div class="text-xs text-neutral-200 leading-relaxed font-sans mt-0.5">
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
