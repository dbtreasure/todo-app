"""
Agent Service — FastAPI Wrapper

Exposes the Claude Code Agent as an HTTP service with:
- POST /agent/run — Run an agent task
- GET /health — Health check endpoint
- GET /metrics — Basic usage metrics

Usage:
    uv run agent-sdk/python/agent_service.py
"""

import asyncio
import time
from collections import defaultdict
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from claude_code_sdk import ClaudeCodeAgent, AgentConfig
from claude_code_sdk.exceptions import AgentError

load_dotenv()

# ── Metrics ───────────────────────────────────────────────────────

metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "total_input_tokens": 0,
    "total_output_tokens": 0,
    "requests_by_model": defaultdict(int),
}
start_time = time.time()


# ── App Setup ─────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Agent service starting...")
    yield
    print("Agent service shutting down...")


app = FastAPI(
    title="Claude Code Agent Service",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Models ────────────────────────────────────────────────────────

class AgentRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=10000, description="The task for the agent")
    model: str = Field(default="sonnet", description="Model to use: haiku, sonnet, or opus")
    max_turns: int = Field(default=10, ge=1, le=50, description="Maximum agent turns")
    permission_mode: str = Field(default="read-only", description="Permission mode")


class AgentResponse(BaseModel):
    text: str
    input_tokens: int
    output_tokens: int
    model: str
    turns: int


# ── Routes ────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "uptime_seconds": int(time.time() - start_time),
    }


@app.get("/metrics")
async def get_metrics():
    return {
        **metrics,
        "uptime_seconds": int(time.time() - start_time),
        "requests_by_model": dict(metrics["requests_by_model"]),
    }


@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    metrics["total_requests"] += 1
    metrics["requests_by_model"][request.model] += 1

    try:
        agent = ClaudeCodeAgent(
            config=AgentConfig(
                model=request.model,
                permission_mode=request.permission_mode,
                max_turns=request.max_turns,
            ),
        )

        result = await agent.run(request.task)

        metrics["successful_requests"] += 1
        metrics["total_input_tokens"] += result.usage.input_tokens
        metrics["total_output_tokens"] += result.usage.output_tokens

        return AgentResponse(
            text=result.text,
            input_tokens=result.usage.input_tokens,
            output_tokens=result.usage.output_tokens,
            model=request.model,
            turns=result.turns,
        )

    except AgentError as e:
        metrics["failed_requests"] += 1
        raise HTTPException(status_code=500, detail=str(e))


# ── Entry Point ───────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
