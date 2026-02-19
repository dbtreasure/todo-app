"""
Agent Service — FastAPI Wrapper

Exposes the Claude Agent as an HTTP service with:
- POST /agent/run — Run an agent task
- GET /health — Health check endpoint
- GET /metrics — Basic usage metrics

Usage:
    uv run agent-sdk/python/agent_service.py
"""

import sys
import asyncio
import time
from collections import defaultdict
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ProcessError,
)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()

# -- Metrics ---------------------------------------------------------------

metrics: dict = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "total_cost_usd": 0.0,
    "total_duration_ms": 0,
    "requests_by_model": defaultdict(int),
}
start_time = time.time()


# -- App Setup -------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Agent service starting...")
    yield
    print("Agent service shutting down...")


app = FastAPI(
    title="Claude Agent Service",
    version="1.0.0",
    lifespan=lifespan,
)


# -- Models ----------------------------------------------------------------

class AgentRequest(BaseModel):
    prompt: str = Field(
        ..., min_length=1, max_length=10000, description="The prompt for the agent"
    )
    model: str = Field(
        default="claude-sonnet-4-5", description="Model to use"
    )


class AgentResponse(BaseModel):
    text: str
    cost_usd: float
    duration_ms: int
    session_id: str
    model: str


# -- Routes ----------------------------------------------------------------

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
        options = ClaudeAgentOptions(
            permission_mode="bypassPermissions",
            model=request.model,
        )

        collected_text: list[str] = []
        cost_usd = 0.0
        duration_ms = 0
        session_id = ""

        async for message in query(prompt=request.prompt, options=options, cwd="/tmp/work"):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        collected_text.append(block.text)
            elif isinstance(message, ResultMessage):
                cost_usd = message.total_cost_usd
                duration_ms = message.duration_ms
                session_id = message.session_id

        metrics["successful_requests"] += 1
        metrics["total_cost_usd"] += cost_usd
        metrics["total_duration_ms"] += duration_ms

        return AgentResponse(
            text="\n".join(collected_text),
            cost_usd=cost_usd,
            duration_ms=duration_ms,
            session_id=session_id,
            model=request.model,
        )

    except ProcessError as e:
        metrics["failed_requests"] += 1
        raise HTTPException(status_code=500, detail=str(e))


# -- Entry Point -----------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
