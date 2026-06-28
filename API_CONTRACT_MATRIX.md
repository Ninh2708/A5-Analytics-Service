# API Contract Matrix

Tài liệu này gom tất cả API của các nhóm và đối chiếu với `analytics-service`.

## Quy ước trạng thái

- `Implemented`: có trong code của `analytics-service`
- `Implemented (proxy)`: có trong code của `analytics-service` dưới dạng proxy sang service khác
- `External service`: thuộc service khác, không phải `analytics-service`
- `Missing`: được contract nhắc tới nhưng chưa thấy trong code hiện tại

## 1. A1 IoT -> A5 Analytics

| Endpoint | Trạng thái | Ghi chú |
|---|---|---|
| `POST /api/v1/analytics/sensor` | Implemented | Có trong `app/routes/analytics.py` |

## 2. A2 Camera -> A5 Analytics

| Endpoint | Trạng thái | Ghi chú |
|---|---|---|
| `POST /api/v1/analytics/camera` | Implemented | Có trong `app/routes/analytics.py` |
| `GET /api/v1/analytics/camera` | Implemented | Có trong `app/routes/analytics.py` |

## 3. A4 AI Vision -> A5 Analytics

| Endpoint | Trạng thái | Ghi chú |
|---|---|---|
| `POST /api/v1/analytics/vision-detections` | Implemented | Có trong `app/routes/analytics.py` |

## 4. A3 Access Gate

| Endpoint | Trạng thái | Ghi chú |
|---|---|---|
| `POST /api/v1/events/access` | External service | Thuộc Access Gate service |
| `GET /api/v1/logs?limit=N` | External service | Thuộc Access Gate service |
| `GET /api/v1/analytics` | External service | Thuộc Access Gate service |

## 5. A6 Core Business

| Endpoint | Trạng thái | Ghi chú |
|---|---|---|
| `GET /health` | External service | Health của Core Business |
| `POST /api/v1/events/sensor` | External service | Thuộc Core Business |
| `POST /api/v1/events/access` | External service | Thuộc Core Business |
| `POST /api/v1/events/camera` | External service | Thuộc Core Business |
| `GET /api/v1/events` | External service | Thuộc Core Business |
| `GET /api/v1/events/sensor` | External service | Thuộc Core Business |
| `GET /api/v1/events/access` | External service | Thuộc Core Business |
| `GET /api/v1/events/camera` | External service | Thuộc Core Business |
| `GET /api/v1/alerts` | External service | Thuộc Core Business |
| `GET /api/v1/analytics/summary` | External service | Thuộc Core Business |

## 6. A7 Notification

| Endpoint | Trạng thái | Ghi chú |
|---|---|---|
| `POST /notifications` | External service | Thuộc Notification service |
| `GET /notifications` | External service | Thuộc Notification service |

## 7. API của analytics-service

| Endpoint | Trạng thái | Ghi chú |
|---|---|---|
| `GET /api/v1/analytics/health` | Implemented | Health của analytics-service |
| `GET /api/v1/analytics/metrics/daily` | Implemented | Summary metrics theo ngày |
| `GET /api/v1/analytics/report/daily` | Implemented | Daily report đầy đủ |
| `GET /api/v1/analytics/metrics/summary` | Implemented | Summary metrics dạng JSON |
| `GET /api/v1/analytics/metrics/range` | Implemented | Metrics theo khoảng ngày |
| `POST /api/v1/analytics/webhook/access` | Implemented | Webhook từ Access Gate |
| `POST /api/v1/analytics/webhook/iot` | Implemented | Webhook từ IoT |
| `POST /api/v1/analytics/webhook/camera` | Implemented | Webhook từ Camera |
| `POST /api/v1/analytics/webhook/alerts` | Implemented | Webhook từ Core Business |
| `GET /api/v1/analytics/core/health` | Implemented (proxy) | Proxy tới Core Business |
| `GET /api/v1/analytics/core/events` | Implemented (proxy) | Proxy tới Core Business |
| `GET /api/v1/analytics/core/events/sensor` | Implemented (proxy) | Proxy tới Core Business |
| `GET /api/v1/analytics/core/events/access` | Implemented (proxy) | Proxy tới Core Business |
| `GET /api/v1/analytics/core/events/camera` | Implemented (proxy) | Proxy tới Core Business |
| `GET /api/v1/analytics/core/events/anomaly` | Implemented (proxy) | Proxy tới Core Business |
| `GET /api/v1/analytics/core/alerts` | Implemented (proxy) | Proxy tới Core Business |
| `GET /api/v1/analytics/core/summary` | Implemented (proxy) | Proxy tới Core Business |
| `GET /api/v1/analytics/dashboard` | Implemented | Dashboard tổng hợp |

## 8. Kết luận nhanh

- Docs cũ đang dùng prefix `/api/analytics/...`, nhưng code thật đang dùng `/api/v1/analytics/...`
- Các API thuộc A3, A6, A7 là của service khác, `analytics-service` chỉ gọi qua proxy hoặc không sở hữu chúng
