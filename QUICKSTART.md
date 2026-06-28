# Quick Start Guide - Analytics Service

## Project Overview

Analytics Service aggregates data from IoT, Camera, Access Gate, and Core Business services, then exposes metrics, reports, and proxy endpoints for dashboards.

## Run Quickly

### 1. Start the app

```bash
# Windows
start.bat

# Linux/Mac
bash start.sh
```

### 2. Or run manually

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Open docs

```text
http://26.52.94.169:8000/docs
```

## Endpoints

> Full contract matrix: [API_CONTRACT_MATRIX.md](API_CONTRACT_MATRIX.md)

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/analytics/health` | GET | Service health check |
| `/api/v1/analytics/metrics/daily` | GET | Daily metrics |
| `/api/v1/analytics/report/daily` | GET | Daily report |
| `/api/v1/analytics/metrics/range` | GET | Metrics for a date range |
| `/api/v1/analytics/webhook/access` | POST | Webhook from Access Gate |
| `/api/v1/analytics/webhook/iot` | POST | Webhook from IoT |
| `/api/v1/analytics/webhook/camera` | POST | Webhook from Camera |
| `/api/v1/analytics/webhook/alerts` | POST | Webhook from Core Business |
| `/api/v1/analytics/vision-detections` | POST | AI Vision detection log |
| `/api/v1/analytics/camera` | POST | Store camera event |
| `/api/v1/analytics/camera` | GET | List camera events |
| `/api/v1/analytics/sensor` | POST | Store sensor event |
| `/api/v1/analytics/sensor` | GET | List sensor events |
| `/api/v1/analytics/core/events/anomaly` | GET | Proxy anomaly events from Core Business |
| `/api/v1/analytics/dashboard` | GET | Aggregated dashboard |

## cURL Examples

```bash
curl http://26.52.94.169:8000/api/v1/analytics/health
curl "http://26.52.94.169:8000/api/v1/analytics/metrics/daily?date=2026-05-02"
curl "http://26.52.94.169:8000/api/v1/analytics/report/daily?date=2026-05-02"
```

## External Services

Analytics Service depends on these services:

| Service | Endpoint |
|---|---|
| IoT | `/api/iot/sensors/temperature?date=YYYY-MM-DD` |
| Camera | `/api/camera/detections/motion?date=YYYY-MM-DD` |
| Access Gate | `/api/access/logs?date=YYYY-MM-DD` |
| Core Business | `/api/alerts?date=YYYY-MM-DD` |
| Core Business | `/api/anomaly-events?date=YYYY-MM-DD` |

## Troubleshooting

- If port `8000` is busy, stop the process or change `PORT` in `.env`.
- If a module is missing, run `pip install -r requirements.txt`.
- If the database is not available, the service can still run for most read endpoints.
