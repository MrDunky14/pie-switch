# ==============================================================================
# pie-Switch Hackathon Automation Makefile
# 1-Command Setup, Test, Execution, Chaos, and Reset
# ==============================================================================

.PHONY: help setup test run run-watchdog chaos chaos-indie repro reset docker-up docker-down

PYTHON ?= python

help:
	@echo "pie-Switch Orchestration Commands:"
	@echo "  make setup         Install Python dependencies and verify environment"
	@echo "  make test          Run full baseline Pytest suite"
	@echo "  make run           Launch target microservice on port 8080"
	@echo "  make run-watchdog  Launch watchdog SSE protocol agent (local simulation)"
	@echo "  make chaos         Inject poison-pill checkout anomaly (Business Mode)"
	@echo "  make chaos-indie   Inject Sleep-Mode webhook anomaly (Indie Mode)"
	@echo "  make repro         Execute sandbox reproduction script"
	@echo "  make reset         Reset target service and logs to baseline buggy state"
	@echo "  make docker-up     Spin up target service and watchdog via Docker Compose"
	@echo "  make docker-down   Tear down Docker Compose containers"

setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -c "import os; [os.makedirs(d, exist_ok=True) for d in ['workspace/repro', 'workspace/patches', 'assets']]"
	@echo "✔ Setup complete. All dependencies and workspace volumes verified."

test:
	$(PYTHON) -m pytest target_service/test_baseline.py -v

run:
	$(PYTHON) -m uvicorn target_service.app:app --host 0.0.0.0 --port 8080 --reload

run-watchdog:
	$(PYTHON) agents/watchdog_sse_agent.py --local-sim

chaos:
	$(PYTHON) scripts/trigger_chaos.py --mode business

chaos-indie:
	$(PYTHON) scripts/trigger_chaos.py --mode indie

chaos-voice:
	$(PYTHON) scripts/trigger_chaos.py --mode voice

voice:
	$(PYTHON) scripts/trigger_chaos.py --mode voice

repro:
	$(PYTHON) workspace/repro/repro_bug.py

reset:
	@if [ -f scripts/reset_demo.sh ]; then \
		bash scripts/reset_demo.sh; \
	elif [ -f scripts/reset_demo.ps1 ]; then \
		powershell -ExecutionPolicy Bypass -File scripts/reset_demo.ps1; \
	fi

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down -v
