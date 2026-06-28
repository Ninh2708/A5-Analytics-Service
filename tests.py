"""
Test examples - Ví dụ test API endpoints

Để chạy:
    pip install pytest httpx
    pytest tests/
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/analytics/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Analytics Service"
        assert data["status"] == "running"


@pytest.mark.asyncio
async def test_metrics_daily_default_date():
    """Test daily metrics endpoint with default date"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/analytics/metrics/daily")
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "total_access" in data
        assert "avg_temperature" in data
        assert "total_alerts" in data


@pytest.mark.asyncio
async def test_metrics_daily_specific_date():
    """Test daily metrics endpoint with specific date"""
    test_date = "2026-05-02"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/api/analytics/metrics/daily?date={test_date}")
        assert response.status_code == 200
        data = response.json()
        assert data["date"] == test_date


@pytest.mark.asyncio
async def test_metrics_daily_invalid_date():
    """Test daily metrics endpoint with invalid date"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/analytics/metrics/daily?date=invalid-date")
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_daily_report():
    """Test daily report endpoint"""
    test_date = "2026-05-02"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/api/analytics/report/daily?date={test_date}")
        assert response.status_code == 200
        data = response.json()
        assert data["date"] == test_date
        assert "summary" in data
        assert "hourly_breakdown" in data
        assert "status" in data


@pytest.mark.asyncio
async def test_metrics_summary():
    """Test metrics summary endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/analytics/metrics/summary")
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "total_access" in data


@pytest.mark.asyncio
async def test_metrics_range():
    """Test metrics range endpoint"""
    start_date = "2026-05-01"
    end_date = "2026-05-03"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            f"/api/analytics/metrics/range?start_date={start_date}&end_date={end_date}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["start_date"] == start_date
        assert data["end_date"] == end_date
        assert "data" in data
        assert "count" in data


@pytest.mark.asyncio
async def test_metrics_range_invalid_dates():
    """Test metrics range with invalid date order"""
    start_date = "2026-05-05"
    end_date = "2026-05-01"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            f"/api/analytics/metrics/range?start_date={start_date}&end_date={end_date}"
        )
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_webhook_access():
    """Test access webhook endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "person_id": "PERSON001",
            "access_type": "entry",
            "timestamp": datetime.now().isoformat()
        }
        response = await ac.post("/api/analytics/webhook/access", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"


@pytest.mark.asyncio
async def test_webhook_iot():
    """Test IoT webhook endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "temperature": 30.5,
            "humidity": 65,
            "sensor_id": "SENSOR001"
        }
        response = await ac.post("/api/analytics/webhook/iot", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"


@pytest.mark.asyncio
async def test_webhook_camera():
    """Test camera webhook endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "camera_id": "CAMERA001",
            "detected": True,
            "confidence": 0.95
        }
        response = await ac.post("/api/analytics/webhook/camera", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"


@pytest.mark.asyncio
async def test_webhook_alerts():
    """Test alerts webhook endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "alert_type": "security",
            "severity": "high",
            "description": "Unauthorized access detected"
        }
        response = await ac.post("/api/analytics/webhook/alerts", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
