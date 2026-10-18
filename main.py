from __future__ import annotations

import time
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from starlette.middleware.cors import CORSMiddleware

ALLOWED_ORIGIN = "https://dash-1yzyce.example.com"
USER_EMAIL = "24f2009112@ds.study.iitm.ac.in"

api = FastAPI(title="CORS-Aware Metrics API", version="1.0.0")


@api.get("/stats")
async def get_stats(values: str = Query(..., description="Comma-separated integers")) -> dict[str, Any]:
    """Compute descriptive statistics for a comma-separated batch of integers."""
    parts = [part.strip() for part in values.split(",")]
    if not parts or any(part == "" for part in parts):
        raise HTTPException(status_code=400, detail="values must be comma-separated integers")

    try:
        numbers = [int(part) for part in parts]
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="values must be comma-separated integers",
        ) from exc

    if not numbers:
        raise HTTPException(status_code=400, detail="provide at least one integer")

    total = sum(numbers)
    return {
        "email": USER_EMAIL,
        "count": len(numbers),
        "sum": total,
        "min": min(numbers),
        "max": max(numbers),
        "mean": total / len(numbers),
    }


class ResponseHeadersMiddleware:
    """Add request ID and elapsed processing time to every HTTP response."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid.uuid4())
        started_at = time.perf_counter()

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                elapsed = max(0.0, time.perf_counter() - started_at)
                headers = list(message.get("headers", []))
                # Replace these headers if an inner component already set them.
                headers = [
                    (name, value)
                    for name, value in headers
                    if name.lower() not in (b"x-request-id", b"x-process-time")
                ]
                headers.extend(
                    [
                        (b"x-request-id", request_id.encode("ascii")),
                        (b"x-process-time", f"{elapsed:.6f}".encode("ascii")),
                    ]
                )
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_headers)


# Wrap CORS outside FastAPI, then wrap that with the header middleware.
# This ensures headers are added even to OPTIONS preflight responses.
cors_app = CORSMiddleware(
    api,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["GET"],
    allow_headers=["*"],
    allow_credentials=False,
)
app = ResponseHeadersMiddleware(cors_app)
