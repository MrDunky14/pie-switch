import httpx
import time
import os

webhook_url = os.getenv(
    "DISCORD_WEBHOOK_URL",
    "https://discord.com/api/webhooks/1568690508841099305/oP3WuISfXV71BtCxuvXzrjnmHj_DKXULTnkC7pnrbZEpfim60beqDbBtINynmdnma88C"
)

messages = [
    ("@watchdog-sse", "🚨 **[P0-CRITICAL] Telemetry Breach: ZeroDivisionError in /api/v1/checkout**\nRoot Cause: float division by zero (target_service/app.py:194)\nHandoff: @pie-triager please ingest crash report and route to repro sandbox."),
    ("@pie-triager", "🟣 **[P0-CRITICAL] Checkout Failure Confirmed (Severity: P0-CRITICAL)**\nRoot Cause: Zero division on 100% discount promo code in /api/v1/checkout\nHandoff: @pie-repro please synthesize isolated repro script and verify crash."),
    ("@pie-repro", "🟡 **[REPRO-CONFIRMED] Sandbox failure captured: exit code 1 (Traceback verified)**\nArtifact: `./workspace/repro/repro_bug.py` | Target: target_service/app.py:194\nHandoff: @pie-patcher please synthesize surgical patch and verify against test suite."),
    ("@pie-patcher", "🔵 **[PATCH-READY] Surgical fix validated in sandbox (8/8 baseline tests pass)**\nArtifact: `./workspace/patches/fix.patch` | Safe ratio calculation added\nAction Required: @alex please review diff. Reply with \"Approved. Deploy patch.\" to authorize @watchdog-sse."),
    ("@alex", "Approved. Deploy patch."),
    ("@watchdog-sse", "✅ **[DEPLOYMENT-VERIFIED] Hot-reload successful & zero-downtime healthcheck passed**\nArtifact: `target_service/app.py` patched | Repro test HTTP 200 OK (latency: 2.8ms)\nStatus: All systems operational. Incident #1 closed in Switch Decisions Log.")
]

for sender, content in messages:
    try:
        r = httpx.post(webhook_url, json={"username": sender, "content": content}, timeout=3.0)
        print(f"Posted {sender}: {r.status_code}")
        time.sleep(0.8)
    except Exception as e:
        print(f"Error {sender}: {e}")

print("Done broadcasting sequence to Discord!")
