# Analytics Service - Camera Integration Guide

Tài liệu này hướng dẫn Camera Stream Service (A2) cách gửi dữ liệu tới Analytics Service (A5).

## Base URL

```
http://26.52.94.169:8000/api/v1
```

## Endpoint: POST /analytics/camera

### Mục đích
Gửi camera event từ Camera Service (A2) tới Analytics Service (A5) để lưu trữ và phân tích.

### Request

**Header:**
```
Content-Type: application/json
```

**Method:** `POST`

**URL:** `http://26.52.94.169:8000/api/v1/analytics/camera`

**Request Body:**
```json
{
  "event_id": "camera-event-9ae287cb8912",
  "event_type": "camera.vision.processed",
  "source_service": "team-camera",
  "camera_id": "cam-gate-a",
  "timestamp": "2026-06-17T08:32:12.450123",
  "location": "Main Gate A",
  "motion_detected": true,
  "motion_score": 99.9,
  "detections": [
    {
      "label": "person",
      "confidence": 0.92
    },
    {
      "label": "chair",
      "confidence": 0.75
    }
  ],
  "unknown_person": false,
  "risk_level": "medium"
}
```

### Request Fields

| Trường | Kiểu | Bắt buộc | Mô tả |
|--------|------|----------|-------|
| `event_id` | String | **Có** | ID duy nhất (để chống trùng lặp) |
| `event_type` | String | **Có** | Loại event (ví dụ: `camera.vision.processed`) |
| `source_service` | String | **Có** | Tên dịch vụ gửi (ví dụ: `team-camera`) |
| `camera_id` | String | **Có** | Mã camera |
| `timestamp` | String (ISO 8601) | **Có** | Thời gian event |
| `location` | String | **Có** | Vị trí camera |
| `motion_detected` | Boolean | **Có** | Có phát hiện chuyển động |
| `motion_score` | Float | **Có** | Điểm số chuyển động (0-100) |
| `detections` | Array | **Có** | Danh sách vật thể phát hiện |
| `detections[].label` | String | **Có** | Tên vật thể (ví dụ: `person`, `car`) |
| `detections[].confidence` | Float | **Có** | Độ tin cậy (0.0-1.0) |
| `unknown_person` | Boolean | **Có** | Có phát hiện người lạ |
| `risk_level` | String | **Có** | Mức độ rủi ro: `high`, `medium`, `info` |

### Response Success (HTTP 201)

```json
{
  "status": "success",
  "message": "Camera event logged successfully",
  "logged_id": "log-event-123"
}
```

### Response Error (HTTP 400)

**Thiếu required field:**
```json
{
  "detail": {
    "status": "error",
    "message": "Missing required field: event_id"
  }
}
```

**Invalid risk_level:**
```json
{
  "detail": {
    "status": "error",
    "message": "Invalid risk_level. Must be: high, medium, info"
  }
}
```

**Invalid timestamp:**
```json
{
  "detail": {
    "status": "error",
    "message": "Invalid timestamp format. Use ISO 8601"
  }
}
```

**Duplicate event_id:**
```json
{
  "detail": {
    "status": "error",
    "message": "Duplicate event_id: camera-event-9ae287cb8912"
  }
}
```

## Endpoint: GET /analytics/camera

### Mục đích
Lấy danh sách camera events đã lưu (cho testing/debugging).

### Request

**Method:** `GET`

**URL:** `http://26.52.94.169:8000/api/v1/analytics/camera`

### Query Parameters

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---------|------|----------|-------|
| `camera_id` | String | Không | Lọc theo camera_id |
| `risk_level` | String | Không | Lọc theo risk_level |
| `limit` | Integer | Không | Số lượng kết quả (mặc định 100) |
| `offset` | Integer | Không | Offset (mặc định 0) |

### Ví dụ Request

```bash
# Lấy 10 events đầu tiên
GET http://26.52.94.169:8000/api/v1/analytics/camera?limit=10

# Lấy events từ camera "cam-gate-a"
GET http://26.52.94.169:8000/api/v1/analytics/camera?camera_id=cam-gate-a

# Lấy events có risk_level="high"
GET http://26.52.94.169:8000/api/v1/analytics/camera?risk_level=high

# Lọc kết hợp
GET http://26.52.94.169:8000/api/v1/analytics/camera?camera_id=cam-gate-a&risk_level=high&limit=20&offset=0
```

### Response (HTTP 200)

```json
{
  "status": "success",
  "count": 1,
  "total_count": 50,
  "offset": 0,
  "limit": 10,
  "events": [
    {
      "id": 1,
      "event_id": "camera-event-9ae287cb8912",
      "event_type": "camera.vision.processed",
      "source_service": "team-camera",
      "camera_id": "cam-gate-a",
      "timestamp": "2026-06-17T08:32:12.450123",
      "location": "Main Gate A",
      "motion_detected": true,
      "motion_score": 99.9,
      "detections": [
        {"label": "person", "confidence": 0.92}
      ],
      "unknown_person": false,
      "risk_level": "medium",
      "created_at": "2026-06-17T10:25:41.123456"
    }
  ]
}
```

## Test với cURL

### Test POST event

```bash
curl -X POST http://26.52.94.169:8000/api/v1/analytics/camera \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "camera-event-test-001",
    "event_type": "camera.vision.processed",
    "source_service": "team-camera",
    "camera_id": "cam-gate-a",
    "timestamp": "2026-06-17T08:32:12.450123",
    "location": "Main Gate A",
    "motion_detected": true,
    "motion_score": 99.9,
    "detections": [
      {
        "label": "person",
        "confidence": 0.92
      }
    ],
    "unknown_person": false,
    "risk_level": "medium"
  }'
```

### Test GET events

```bash
# Lấy tất cả
curl http://26.52.94.169:8000/api/v1/analytics/camera

# Lọc theo camera
curl http://26.52.94.169:8000/api/v1/analytics/camera?camera_id=cam-gate-a

# Lọc theo risk_level
curl http://26.52.94.169:8000/api/v1/analytics/camera?risk_level=high
```

## Lỗi thường gặp

### 1. Connection Refused
**Lỗi:** `Connection refused`
**Nguyên nhân:** Analytics Service chưa chạy
**Giải pháp:** Chạy: `python -m uvicorn app.main:app --reload --host 26.52.94.169 --port 8000`

### 2. Invalid timestamp format
**Lỗi:** `Invalid timestamp format. Use ISO 8601`
**Nguyên nhân:** Timestamp không đúng format
**Giải pháp:** Sử dụng ISO 8601: `2026-06-17T08:32:12.450123` hoặc `2026-06-17T08:32:12+07:00`

### 3. Duplicate event_id
**Lỗi:** `Duplicate event_id`
**Nguyên nhân:** event_id đã tồn tại trong database
**Giải pháp:** Tạo event_id mới (dùng UUID)

### 4. Invalid risk_level
**Lỗi:** `Invalid risk_level. Must be: high, medium, info`
**Nguyên nhân:** risk_level không trong enum
**Giải pháp:** Sử dụng: `high`, `medium`, hoặc `info`

## Cơ chế gửi dữ liệu

Camera Service (A2) nên:
1. Tạo `event_id` duy nhất (sử dụng UUID)
2. Gửi event đến Analytics với POST request
3. Nếu gửi thất bại, sử dụng retry mechanism
4. Gửi ở chế độ asynchronous (background thread)

## Database Schema

Dữ liệu được lưu trữ tại bảng `camera_events`:

```sql
CREATE TABLE camera_events (
    id INTEGER PRIMARY KEY,
    event_id VARCHAR UNIQUE,
    event_type VARCHAR,
    source_service VARCHAR,
    camera_id VARCHAR,
    timestamp DATETIME,
    location VARCHAR,
    motion_detected INTEGER,  -- 0 or 1
    motion_score FLOAT,
    detections JSON,
    unknown_person INTEGER,  -- 0 or 1
    risk_level VARCHAR,
    created_at DATETIME,
    date VARCHAR
)
```
