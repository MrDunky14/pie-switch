# ==============================================================================
# pie-Switch Production & Sandbox Container Definition
# ==============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (curl for healthcheck, git for patch diffing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source trees
COPY target_service/ ./target_service/
COPY agents/ ./agents/
COPY scripts/ ./scripts/
COPY switch.template.yaml pytest.ini .env.example ./

# Create workspace directory structure
RUN mkdir -p workspace/repro workspace/patches

ENV PYTHONPATH=/app
ENV MODE=business
ENV TARGET_SERVICE_HOST=0.0.0.0
ENV TARGET_SERVICE_PORT=8080

EXPOSE 8080

CMD ["uvicorn", "target_service.app:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
