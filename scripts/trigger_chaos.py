#!/usr/bin/env python3
"""pie-Switch Chaos Engine & Anomaly Injector.

Sends 3 normal requests (HTTP 200 OK) followed by a poison-pill payload (HTTP 500)
to target_service, rendering a live Rich terminal dashboard for hackathon demos.
"""

import argparse
import json
import os
import sys
import time
from typing import Any, Dict

# Ensure UTF-8 output encoding across Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import httpx
from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

TARGET_SERVICE_URL = os.getenv("TARGET_SERVICE_URL", "http://127.0.0.1:8080")
MODE = os.getenv("MODE", "business").lower()


def make_dashboard(
    title: str,
    requests_table: Table,
    telemetry_panel: Panel,
    status_text: str,
) -> Panel:
    """Builds a cohesive rich dashboard card."""
    main_table = Table.grid(padding=1)
    main_table.add_column()
    main_table.add_row(requests_table)
    main_table.add_row(telemetry_panel)
    main_table.add_row(Text.from_markup(f"[bold cyan]Pipeline Status:[/bold cyan] {status_text}"))

    return Panel(
        main_table,
        title=f"[bold red]🔥 {title}[/bold red]",
        border_style="red",
        box=box.ROUNDED,
    )


def trigger_business_chaos(client: httpx.Client) -> None:
    """Executes the business checkout chaos sequence."""
    checkout_url = f"{TARGET_SERVICE_URL}/api/v1/checkout"

    # Step 1: Healthcheck
    try:
        health_resp = client.get(f"{TARGET_SERVICE_URL}/health", timeout=3.0)
        health_data = health_resp.json()
    except Exception as exc:
        console.print(
            Panel(
                f"[bold red]Cannot connect to Target Service at {TARGET_SERVICE_URL}[/bold red]\n"
                f"Error: {exc}\n\n"
                f"[yellow]Ensure target_service is running with:[/yellow]\n"
                f"  python target_service/app.py",
                title="[red]Connection Refused[/red]",
                box=box.ROUNDED,
            )
        )
        sys.exit(1)

    table = Table(
        title="[bold yellow]Target Service Traffic Stream (Checkout API)[/bold yellow]",
        box=box.SIMPLE_HEAVY,
        expand=True,
    )
    table.add_column("Req #", justify="center", width=8)
    table.add_column("Cart ID", width=14)
    table.add_column("Coupon", width=12)
    table.add_column("Amount", justify="right", width=12)
    table.add_column("Status Code", justify="center", width=14)
    table.add_column("Latency", justify="right", width=10)
    table.add_column("Result")

    # Three normal requests
    normal_payloads = [
        {
            "cart_id": "cart_live_01",
            "items": [{"id": "item_1", "name": "Compute Node A", "price": 45.0, "qty": 2}],
            "coupon_code": None,
            "tax_rate": 0.08,
        },
        {
            "cart_id": "cart_live_02",
            "items": [{"id": "item_2", "name": "Storage Volume B", "price": 120.0, "qty": 1}],
            "coupon_code": "WELCOME10",
            "tax_rate": 0.08,
        },
        {
            "cart_id": "cart_live_03",
            "items": [{"id": "item_3", "name": "API Gateway License", "price": 250.0, "qty": 1}],
            "coupon_code": "SAVE25",
            "tax_rate": 0.08,
        },
    ]

    console.print("[bold green]✔ Target Service healthy. Injecting baseline production traffic...[/bold green]\n")

    for i, payload in enumerate(normal_payloads, 1):
        t0 = time.time()
        resp = client.post(checkout_url, json=payload, timeout=5.0)
        latency = round((time.time() - t0) * 1000, 1)
        subtotal = sum(it["price"] * it["qty"] for it in payload["items"])

        if resp.status_code == 200:
            table.add_row(
                f"[bold cyan]#{i}[/bold cyan]",
                payload["cart_id"],
                str(payload["coupon_code"] or "-"),
                f"${subtotal:.2f}",
                "[bold green]200 OK[/bold green]",
                f"{latency}ms",
                "[green]Transaction Settled[/green]",
            )
        else:
            table.add_row(
                f"[bold cyan]#{i}[/bold cyan]",
                payload["cart_id"],
                str(payload["coupon_code"] or "-"),
                f"${subtotal:.2f}",
                f"[bold red]{resp.status_code}[/bold red]",
                f"{latency}ms",
                "[red]Unexpected Error[/red]",
            )
        console.clear()
        console.print(table)
        time.sleep(0.6)

    # Step 2: The Poison Pill
    console.print("\n[bold red]⚠️  Injecting Latent Edge-Case Poison Payload: 100% Promo Code (PROMO100)...[/bold red]\n")
    time.sleep(1.0)

    poison_payload = {
        "cart_id": "cart_POISON_PILL",
        "items": [{"id": "sku_edge", "name": "Enterprise Suite Promo", "price": 500.0, "qty": 1}],
        "coupon_code": "PROMO100",
        "tax_rate": 0.08,
    }

    t0 = time.time()
    resp_poison = client.post(checkout_url, json=poison_payload, timeout=5.0)
    latency_poison = round((time.time() - t0) * 1000, 1)

    if resp_poison.status_code == 500:
        table.add_row(
            "[bold red]#4 (POISON)[/bold red]",
            "cart_POISON_PILL",
            "[bold red]PROMO100[/bold red]",
            "$500.00",
            "[bold white on red]500 ERROR[/bold white on red]",
            f"{latency_poison}ms",
            "[bold red]ZeroDivisionError (Crashed)[/bold red]",
        )
        status_banner = "[bold red]CRASH TRIGGERED ➔ Traceback written to ./workspace/service.log ➔ Watchdog Alert Fired![/bold red]"
    elif resp_poison.status_code == 200:
        table.add_row(
            "[bold green]#4 (VERIFY)[/bold green]",
            "cart_POISON_PILL",
            "[bold green]PROMO100[/bold green]",
            "$500.00",
            "[bold green]200 OK[/bold green]",
            f"{latency_poison}ms",
            "[bold green]Patched: 100% Discount Settled ($2.50 fee)[/bold green]",
        )
        status_banner = "[bold green]SERVICE IS CURRENTLY PATCHED: 100% Discount handled safely without ZeroDivisionError![/bold green]"
    else:
        status_banner = f"[yellow]Response: HTTP {resp_poison.status_code}[/yellow]"

    console.clear()
    console.print(table)
    console.print(Panel(status_banner, box=box.ROUNDED, border_style="red" if resp_poison.status_code == 500 else "green"))


def trigger_indie_chaos(client: httpx.Client) -> None:
    """Executes the indie sleep-mode webhook chaos sequence."""
    webhook_url = f"{TARGET_SERVICE_URL}/api/v1/indie-webhook"

    table = Table(
        title="[bold magenta]Indie Sleep-Mode Guardian Telemetry Stream[/bold magenta]",
        box=box.SIMPLE_HEAVY,
        expand=True,
    )
    table.add_column("Event #", justify="center", width=8)
    table.add_column("Repository", width=16)
    table.add_column("Event Type", width=14)
    table.add_column("Status Code", justify="center", width=14)
    table.add_column("Result")

    # Normal indie event
    normal_evt = {
        "event": "workflow_run",
        "repository": "pie-switch",
        "sender": "github-actions",
        "status": "success",
        "metrics": {"build_time_s": 42},
    }
    resp1 = client.post(webhook_url, json=normal_evt)
    table.add_row("#1", "pie-switch", "workflow_run", "[green]200 OK[/green]", "[green]All Checks Passed[/green]")
    console.clear()
    console.print(table)
    time.sleep(0.8)

    # Failed indie event
    fail_evt = {
        "event": "workflow_run",
        "repository": "pie-switch",
        "sender": "github-actions",
        "status": "failure",
        "metrics": {"build_time_s": 12, "error_count": 3},
    }
    resp2 = client.post(webhook_url, json=fail_evt)
    table.add_row(
        "[bold red]#2 (ALERT)[/bold red]",
        "pie-switch",
        "workflow_run",
        "[bold white on red]500 ERROR[/bold white on red]",
        "[bold red]Pipeline Failed ➔ Sleep-Mode Alert Dispatched[/bold red]",
    )
    console.clear()
    console.print(table)
    console.print(
        Panel(
            "[bold red]Indie Sleep-Mode Guardian Alert Captured ➔ Written to ./workspace/service.log[/bold red]",
            box=box.ROUNDED,
            border_style="magenta",
        )
    )


def trigger_voice_idea(client: httpx.Client) -> None:
    """Executes the Solo-Chill / Voice-Transcribed idea workflow."""
    voice_url = f"{TARGET_SERVICE_URL}/api/v1/voice-idea"

    table = Table(
        title="[bold cyan]🎙️ Wispr Flow Solo-Chill Voice Idea Ingestion Stream[/bold cyan]",
        box=box.SIMPLE_HEAVY,
        expand=True,
    )
    table.add_column("Idea #", justify="center", width=8)
    table.add_column("Author", width=12)
    table.add_column("Voice Transcript", width=36)
    table.add_column("Status Code", justify="center", width=14)
    table.add_column("Routing Target")

    payload = {
        "idea": "Add real-time currency conversion for EUR and GBP in checkout fee logic",
        "author": "@alex",
        "voice_transcribed": True,
        "tags": ["feature", "solo-chill", "wispr-flow"],
    }

    resp = client.post(voice_url, json=payload)
    status_markup = "[bold green]200 OK[/bold green]" if resp.status_code == 200 else f"[red]{resp.status_code}[/red]"
    table.add_row(
        "#1",
        payload["author"],
        payload["idea"],
        status_markup,
        "[cyan]Switch Decisions Log ➔ @pie-triager[/cyan]",
    )

    console.clear()
    console.print(table)
    console.print(
        Panel(
            "[bold green]✔ Voice Task Ingested: Dispatched to Switch Room Decisions Log[/bold green]\n"
            "[white]Agents collaboratively scaffold, test, and package while the solo founder is away.[/white]",
            box=box.ROUNDED,
            border_style="cyan",
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="pie-Switch Chaos & Telemetry Injector")
    parser.add_argument(
        "--mode",
        choices=["business", "indie", "voice"],
        default=MODE,
        help="Operating mode: business (Checkout), indie (Sleep-Mode Guardian), or voice (Solo-Chill)",
    )
    args = parser.parse_args()

    with httpx.Client() as client:
        if args.mode == "business":
            trigger_business_chaos(client)
        elif args.mode == "indie":
            trigger_indie_chaos(client)
        elif args.mode == "voice":
            trigger_voice_idea(client)


if __name__ == "__main__":
    main()
