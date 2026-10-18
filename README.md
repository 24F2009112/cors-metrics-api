# CORS-Aware Metrics API

FastAPI service for the IITM metrics API assignment.

## Endpoint

`GET /stats?values=1,2,3`

Returns `email`, `count`, `sum`, `min`, `max`, and `mean`, computed from the query string on each request.

## CORS

Only `https://dash-1yzyce.example.com` is allowed. The API uses exact-origin matching and does not allow wildcard origins.

## Required response headers

Every HTTP response includes a unique `X-Request-ID` and a non-negative decimal `X-Process-Time` in seconds, including CORS preflight and error responses.

## Deploy on Render

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
