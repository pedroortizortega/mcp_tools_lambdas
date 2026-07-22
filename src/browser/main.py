"""FastAPI trigger endpoint + MCP SSE server.

Endpoints:
  POST /trigger-search    →  Launches an async browser search.
  GET  /results/{task_id} →  Polls the result of a search.
  GET  /health            →  Health check.

MCP tool:
  get_search_results(task_id) → Returns the result for a given task.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from .config import BrowserOrchestratorConfig
from .orchestrator import Orchestrator, SearchResult

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── State ────────────────────────────────────────────────────────────────────
config = BrowserOrchestratorConfig()
results_store: dict[str, SearchResult] = {}


# ── FastAPI ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Browser Agent Orchestrator starting on %s:%s", config.host, config.port)
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Browser Agent Orchestrator",
    description="Trigger endpoint for Bedrock-powered browser agent",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    url: str


class TriggerResponse(BaseModel):
    task_id: str
    status: str


class SearchResultResponse(BaseModel):
    task_id: str
    query: str
    url: str
    status: str
    answer: str | None = None
    error: str | None = None


# ── Background task runner ───────────────────────────────────────────────────

async def _run_search(task_id: str, query: str, url: str) -> None:
    orchestrator = Orchestrator(config)
    result = await orchestrator.search(query, url)
    results_store[task_id] = result
    logger.info("Task %s completed: %s", task_id, result.status)


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.post("/trigger-search", response_model=TriggerResponse)
async def trigger_search(request: SearchRequest):
    """Launch an asynchronous browser search."""
    task_id = str(uuid.uuid4())
    results_store[task_id] = SearchResult(
        query=request.query, url=request.url, status="in_progress"
    )
    asyncio.create_task(_run_search(task_id, request.query, request.url))
    return TriggerResponse(task_id=task_id, status="searching")


@app.get("/results/{task_id}", response_model=SearchResultResponse)
async def get_results(task_id: str):
    """Check the status / result of a search task."""
    result = results_store.get(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return SearchResultResponse(
        task_id=task_id,
        query=result.query,
        url=result.url,
        status=result.status,
        answer=result.answer or None,
        error=result.error,
    )


@app.get("/health")
async def health():
    return {"status": "ok", "active_tasks": len(results_store)}


# ── MCP SSE Server ───────────────────────────────────────────────────────────

mcp = FastMCP("BrowserSearchAgent")


@mcp.tool()
async def get_search_results(task_id: str) -> str:
    """Retrieve the results of a browser search triggered via /trigger-search.

    Args:
        task_id: The task ID returned by the trigger endpoint.
    """
    result = results_store.get(task_id)
    if result is None:
        return "Task not found."
    if result.status == "in_progress":
        return "Search still in progress. Try again shortly."
    if result.status == "error":
        return f"Search failed: {result.error}"
    return result.answer


@mcp.tool()
async def trigger_browser_search(query: str, url: str) -> str:
    """Trigger a new browser search and return the task_id.

    Args:
        query: The search query or question.
        url: The URL to navigate to.
    """
    task_id = str(uuid.uuid4())
    results_store[task_id] = SearchResult(query=query, url=url, status="in_progress")
    asyncio.create_task(_run_search(task_id, query, url))
    return f"Search started. task_id: {task_id}"


# ── Entrypoint ───────────────────────────────────────────────────────────────

def start():
    """Run FastAPI + MCP on the same port via mounting."""
    import uvicorn

    # Mount MCP SSE app under /mcp
    mcp_app = mcp.sse_app()
    app.mount("/mcp", mcp_app)

    uvicorn.run(app, host=config.host, port=config.port)


if __name__ == "__main__":
    start()
