# HƯỚNG DẪN CHI TIẾT - Analytics Service

## 1. Chuẩn bị Môi trường

### Option A: Local Development (Không Docker)

#### 1.1 Tạo Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 1.2 Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

#### 1.3 Tạo file .env

```bash
cp .env.example .env
```

Sửa file `.env` nếu cần:
```
DATABASE_URL=postgresql://analytics_user:analytics_pass@localhost:5432/analytics_db
IOT_SERVICE_URL=http://localhost:8001
CAMERA_SERVICE_URL=http://localhost:8002
ACCESS_GATE_URL=http://localhost:8003
CORE_BUSINESS_URL=http://localhost:8004
```

### Option B: Docker Development

#### 2.1 Chạy với Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f analytics-service

# Stop services
docker-compose down
```

## 2. Chạy Application

### Local (No Docker):
```bash
# Từ root directory của project
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Truy cập:
- API: http://26.52.94.169:8000
- Docs: http://26.52.94.169:8000/docs
- ReDoc: http://26.52.94.169:8000/redoc

### Docker:
```bash
# Services sẽ start automatically với docker-compose
# Analytics Service: http://26.52.94.169:8000
# PostgreSQL: localhost:5432
# PgAdmin: http://localhost:5050
```

## 3. Kiểm Tra API

### Health Check
```bash
curl http://26.52.94.169:8000/api/analytics/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-05-02T15:30:45.123456"
}
```

### Get Daily Metrics
```bash
curl "http://26.52.94.169:8000/api/analytics/metrics/daily?date=2026-05-02"
```

Response:
```json
{
  "date": "2026-05-02",
  "total_access": 0,
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
```

### Get Daily Report
```bash
curl "http://26.52.94.169:8000/api/analytics/report/daily?date=2026-05-02"
```

### Get Metrics Range
```bash
curl "http://26.52.94.169:8000/api/analytics/metrics/range?start_date=2026-05-01&end_date=2026-05-03"
```

## 4. Cấu Trúc Project

```
analytics-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Settings
│   ├── database.py             # SQLAlchemy models
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic schemas
│   ├── services/               # Business logic
│   │   ├── iot_service.py
│   │   ├── camera_service.py
│   │   ├── access_gate_service.py
│   │   ├── core_business_service.py
│   │   └── analytics_engine.py # Main engine
│   └── routes/
│       └── analytics.py        # API endpoints
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── setup_db.py                 # Database setup
├── example_data.py             # Example data
├── tests.py                    # Test cases
├── SETUP.md                    # This file
└── README.md
```

## 5. Luồng Xử Lý

```
Client Request
    ↓
API Endpoint (/api/analytics/...)
    ↓
Analytics Engine
    ↓
Parallel Requests to:
    ├─ Access Gate Service → /api/access/logs
    ├─ IoT Service → /api/iot/sensors/temperature
    ├─ Camera Service → /api/camera/detections/motion
    └─ Core Business → /api/alerts & /api/anomaly-events
    ↓
Data Aggregation
    ├─ Total access count
    ├─ Access by hour
    ├─ Average temperature
    ├─ Temperature by room
    ├─ Alert statistics
    ├─ Motion detections
    └─ Anomaly events
    ↓
JSON Response
```

## 6. Service Endpoints Được Kết Nối

Các endpoint dưới đây phải được cung cấp bởi các service khác:

### IoT Service (Port 8001)
- `GET /api/iot/sensors/temperature?date=YYYY-MM-DD`
  
Expected response:
```json
{
  "data": [
    {
      "timestamp": "2026-05-02T08:00:00",
      "sensor_id": "SENSOR001",
      "temperature": 30.5,
      "room_id": "ROOM001",
      "room_name": "Room A",
      "humidity": 65
    }
  ]
}
```

### Camera Service (Port 8002)
- `GET /api/camera/detections/motion?date=YYYY-MM-DD`

Expected response:
```json
{
  "data": [
    {
      "timestamp": "2026-05-02T09:30:00",
      "camera_id": "CAMERA001",
      "detected": true,
      "location": "Corridor A",
      "confidence": 0.95
    }
  ]
}
```

### Access Gate Service (Port 8003)
- `GET /api/access/logs?date=YYYY-MM-DD`

Expected response:
```json
{
  "data": [
    {
      "timestamp": "2026-05-02T08:30:00",
      "person_id": "PERSON001",
      "access_type": "entry",
      "gate_id": "GATE001",
      "location": "Main Entrance"
    }
  ]
}
```

### Core Business Service (Port 8004)
- `GET /api/alerts?date=YYYY-MM-DD`
- `GET /api/anomaly-events?date=YYYY-MM-DD`

Expected response for alerts:
```json
{
  "data": [
    {
      "timestamp": "2026-05-02T11:00:00",
      "alert_id": "ALERT001",
      "alert_type": "security",
      "severity": "high",
      "description": "Unauthorized access",
      "source": "Access Gate"
    }
  ]
}
```

## 7. Database Setup (Tuỳ Chọn)

Nếu muốn lưu historical data vào database:

```bash
# Setup database
python setup_db.py

# Run migrations (nếu cần)
# alembic upgrade head
```

## 8. Testing

### Run Tests
```bash
pip install pytest pytest-asyncio
pytest tests.py -v
```

### Test Với cURL
```bash
# Health check
curl http://26.52.94.169:8000/api/analytics/health

# Metrics
curl "http://26.52.94.169:8000/api/analytics/metrics/daily"

# Webhook
curl -X POST http://26.52.94.169:8000/api/analytics/webhook/access \
  -H "Content-Type: application/json" \
  -d '{"person_id": "TEST", "access_type": "entry"}'
```

## 9. Troubleshooting

### Error: Connection refused to service
- Kiểm tra xem các service khác (IoT, Camera, Access Gate, Core Business) đã chạy chưa
- Kiểm tra service URLs trong `.env`
- Services không cần thiết để chạy - API sẽ return 0 values nếu không thể kết nối

### Error: Database connection failed
- Kiểm tra PostgreSQL đang chạy
- Kiểm tra DATABASE_URL trong `.env`
- Kiểm tra username/password

### Port already in use
```bash
# Linux/Mac: Kill process on port
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

## 10. Production Deployment

### Environment Variables
- Đặt `DEBUG=False`
- Sử dụng strong database password
- Cấu hình service URLs đúng với production endpoints
- Thiết lập proper logging

### Docker Build
```bash
docker build -t analytics-service:1.0 .

# Run
docker run -p 8000:8000 --env-file .env analytics-service:1.0
```

### Performance Tips
- Sử dụng PostgreSQL với indexing trên date columns
- Implement caching nếu queries lặp lại
- Setup rate limiting nếu cần
- Use async operations (đã implement)

## 11. Monitoring

### Logs
```bash
# View logs từ Docker
docker-compose logs -f analytics-service

# View logs từ file (nếu configured)
tail -f logs/analytics.log
```

### Health Monitoring
```bash
# Continuous health check
watch -n 5 'curl http://26.52.94.169:8000/api/analytics/health'
```

## 12. Mở Rộng Tương Lai

- [ ] Time-series database (TimescaleDB)
- [ ] Real-time updates (WebSocket)
- [ ] Advanced analytics (ML models)
- [ ] Report scheduling
- [ ] Data export (CSV, Excel, PDF)
- [ ] Multi-user authentication
- [ ] Custom dashboards
- [ ] Alerting system

---

**Support**: Liên hệ FIT4110 team
