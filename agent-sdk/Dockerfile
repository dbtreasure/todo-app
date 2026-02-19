FROM python:3.11-slim

WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Install Claude Agent SDK
RUN uv pip install --system claude-agent-sdk

# Copy dependency files first for layer caching
COPY python/requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY python/ ./python/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

EXPOSE 8000

CMD ["uvicorn", "python.agent_service:app", "--host", "0.0.0.0", "--port", "8000"]
