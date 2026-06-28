"""
Example data file - Ví dụ dữ liệu cho testing

Sử dụng dữ liệu này để test API endpoints
"""

EXAMPLE_ACCESS_DATA = [
    {
        "timestamp": "2026-05-02T08:30:00",
        "person_id": "PERSON001",
        "access_type": "entry",
        "gate_id": "GATE001",
        "location": "Main Entrance"
    },
    {
        "timestamp": "2026-05-02T08:45:00",
        "person_id": "PERSON002",
        "access_type": "entry",
        "gate_id": "GATE001",
        "location": "Main Entrance"
    },
    {
        "timestamp": "2026-05-02T17:00:00",
        "person_id": "PERSON001",
        "access_type": "exit",
        "gate_id": "GATE001",
        "location": "Main Entrance"
    }
]

EXAMPLE_TEMPERATURE_DATA = [
    {
        "timestamp": "2026-05-02T08:00:00",
        "sensor_id": "SENSOR001",
        "temperature": 30.5,
        "room_id": "ROOM001",
        "room_name": "Room A",
        "humidity": 65
    },
    {
        "timestamp": "2026-05-02T09:00:00",
        "sensor_id": "SENSOR001",
        "temperature": 30.8,
        "room_id": "ROOM001",
        "room_name": "Room A",
        "humidity": 64
    },
    {
        "timestamp": "2026-05-02T08:00:00",
        "sensor_id": "SENSOR002",
        "temperature": 31.2,
        "room_id": "ROOM002",
        "room_name": "Room B",
        "humidity": 68
    }
]

EXAMPLE_MOTION_DATA = [
    {
        "timestamp": "2026-05-02T09:30:00",
        "camera_id": "CAMERA001",
        "detected": True,
        "location": "Corridor A",
        "confidence": 0.95
    },
    {
        "timestamp": "2026-05-02T10:00:00",
        "camera_id": "CAMERA002",
        "detected": True,
        "location": "Corridor B",
        "confidence": 0.87
    },
    {
        "timestamp": "2026-05-02T14:30:00",
        "camera_id": "CAMERA001",
        "detected": False,
        "location": "Corridor A",
        "confidence": 0.05
    }
]

EXAMPLE_ALERT_DATA = [
    {
        "timestamp": "2026-05-02T11:00:00",
        "alert_id": "ALERT001",
        "alert_type": "security",
        "severity": "high",
        "description": "Unauthorized access attempt",
        "source": "Access Gate"
    },
    {
        "timestamp": "2026-05-02T12:00:00",
        "alert_id": "ALERT002",
        "alert_type": "maintenance",
        "severity": "low",
        "description": "Temperature sensor malfunction",
        "source": "IoT System"
    }
]

EXAMPLE_ANOMALY_DATA = [
    {
        "timestamp": "2026-05-02T13:00:00",
        "event_type": "unusual_pattern",
        "description": "Unusual motion pattern detected in Corridor A",
        "severity": "medium",
        "source": "AI Vision"
    }
]

# Test case để POST webhook
EXAMPLE_WEBHOOK_ACCESS = {
    "timestamp": "2026-05-02T15:30:00",
    "person_id": "PERSON003",
    "access_type": "entry",
    "gate_id": "GATE001",
    "location": "Main Entrance"
}

EXAMPLE_WEBHOOK_IOT = {
    "timestamp": "2026-05-02T15:30:00",
    "sensor_id": "SENSOR003",
    "temperature": 31.0,
    "room_id": "ROOM003",
    "room_name": "Meeting Room",
    "humidity": 62
}

EXAMPLE_WEBHOOK_CAMERA = {
    "timestamp": "2026-05-02T15:30:00",
    "camera_id": "CAMERA003",
    "detected": True,
    "location": "Lobby",
    "confidence": 0.92
}

EXAMPLE_WEBHOOK_ALERT = {
    "timestamp": "2026-05-02T15:30:00",
    "alert_id": "ALERT003",
    "alert_type": "security",
    "severity": "medium",
    "description": "Unusual activity detected",
    "source": "Core Business"
}

# Expected response format
EXPECTED_METRIC_RESPONSE = {
    "date": "2026-05-02",
    "total_access": 0,  # Will be 0 if no real data
    "total_access_in": 0,
    "total_access_out": 0,
    "access_by_hour": {},
    "avg_temperature": 0.0,
    "temperature_by_room": {},
    "total_alerts": 0,
    "alerts_by_type": {},
    "total_motion_detections": 0,
    "total_anomaly_events": 0
}

EXPECTED_DAILY_REPORT_RESPONSE = {
    "date": "2026-05-02",
    "summary": {},  # MetricResponse
    "hourly_breakdown": {},
    "status": "success",
    "generated_at": "2026-05-02T15:30:00"
}

# cURL command examples

CURL_EXAMPLES = """
# Health check
curl http://localhost:8000/api/analytics/health

# Get daily metrics (today)
curl http://localhost:8000/api/analytics/metrics/daily

# Get daily metrics (specific date)
curl "http://localhost:8000/api/analytics/metrics/daily?date=2026-05-02"

# Get daily report
curl "http://localhost:8000/api/analytics/report/daily?date=2026-05-02"

# Get metrics summary
curl http://localhost:8000/api/analytics/metrics/summary

# Get metrics for date range
curl "http://localhost:8000/api/analytics/metrics/range?start_date=2026-05-01&end_date=2026-05-03"

# POST access webhook
curl -X POST http://localhost:8000/api/analytics/webhook/access \\
  -H "Content-Type: application/json" \\
  -d '{
    "timestamp": "2026-05-02T15:30:00",
    "person_id": "PERSON003",
    "access_type": "entry",
    "gate_id": "GATE001",
    "location": "Main Entrance"
  }'

# POST IoT webhook
curl -X POST http://localhost:8000/api/analytics/webhook/iot \\
  -H "Content-Type: application/json" \\
  -d '{
    "timestamp": "2026-05-02T15:30:00",
    "sensor_id": "SENSOR003",
    "temperature": 31.0,
    "room_id": "ROOM003",
    "room_name": "Meeting Room",
    "humidity": 62
  }'

# View Swagger UI
open http://localhost:8000/docs
"""
