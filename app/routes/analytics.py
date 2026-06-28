from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import asyncio
import logging
from typing import Optional, List

from app.services.analytics_engine import AnalyticsEngine
from app.services.core_business_client import core_client
from app.models.schemas import (
    MetricResponse, DailyReport,
    CameraEventData, CameraEventResponse,
    SensorEventData, SensorEventResponse,
    AnomalyEventData, AnomalyEventResponse,
    VisionDetectionData, VisionDetectionResponse,
)
from app.database import CameraEvent, SensorEvent, VisionDetectionEvent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

# Initialize analytics engine
analytics_engine = AnalyticsEngine()

# Database setup — engine is exported so main.py can call create_all on it
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Max allowed days for /metrics/range to prevent DoS
_MAX_RANGE_DAYS = 90


# ── helpers ──────────────────────────────────────────────────────────────────

def _serialize_camera_event(event: CameraEvent) -> dict:
    return {
        "kind": "camera",
        "id": event.id,
        "event_id": event.event_id,
        "timestamp": event.timestamp.isoformat() if event.timestamp else None,
        "camera_id": event.camera_id,
        "location": event.location,
        "risk_level": event.risk_level,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


def _serialize_sensor_event(event: SensorEvent) -> dict:
    return {
        "kind": "sensor",
        "id": event.id,
        "event_id": event.event_id,
        "timestamp": event.timestamp.isoformat() if event.timestamp else None,
        "device_id": event.device_id,
        "location": event.location,
        "status": event.status,
        "alert_level": event.alert_level,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


def _serialize_vision_event(event: VisionDetectionEvent) -> dict:
    return {
        "kind": "vision",
        "id": event.id,
        "detection_id": event.detection_id,
        "timestamp": event.timestamp.isoformat() if event.timestamp else None,
        "camera_id": event.camera_id,
        "finding": event.finding,
        "model_mode": event.model_mode,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


# ── health ────────────────────────────────────────────────────────────────────

@router.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ── metrics ───────────────────────────────────────────────────────────────────

@router.get("/metrics/daily", response_model=MetricResponse)
async def get_daily_metrics(date: str = None):
    """Lấy metrics hàng ngày. date: YYYY-MM-DD (mặc định hôm nay)"""
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        datetime.strptime(date, "%Y-%m-%d")
        report = await analytics_engine.generate_daily_report(date)
        return report.summary
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Error in get_daily_metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/report/daily", response_model=DailyReport)
async def get_daily_report(date: str = None):
    """Lấy báo cáo hàng ngày chi tiết. date: YYYY-MM-DD (mặc định hôm nay)"""
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        datetime.strptime(date, "%Y-%m-%d")
        return await analytics_engine.generate_daily_report(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Error in get_daily_report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/metrics/summary")
async def get_metrics_summary(date: str = None):
    """Lấy tóm tắt metrics. date: YYYY-MM-DD (mặc định hôm nay)"""
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        datetime.strptime(date, "%Y-%m-%d")
        return await analytics_engine.get_metrics_summary(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Error in get_metrics_summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/metrics/range")
async def get_metrics_range(start_date: str, end_date: str):
    """
    Lấy metrics cho khoảng thời gian. start_date/end_date: YYYY-MM-DD.
    Tối đa 90 ngày mỗi request.
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        if start > end:
            raise HTTPException(status_code=400, detail="start_date must be before end_date")

        if (end - start).days > _MAX_RANGE_DAYS:
            raise HTTPException(
                status_code=400,
                detail=f"Date range too large. Maximum is {_MAX_RANGE_DAYS} days.",
            )

        dates = [
            (start + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range((end - start).days + 1)
        ]
        # Fetch all dates in parallel
        results = await asyncio.gather(*[analytics_engine.get_metrics_summary(d) for d in dates])

        return {
            "start_date": start_date,
            "end_date": end_date,
            "data": list(results),
            "count": len(results),
        }
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Error in get_metrics_range: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ── webhooks ──────────────────────────────────────────────────────────────────

@router.post("/webhook/access")
async def webhook_access(data: dict):
    """Webhook nhận dữ liệu từ Access Gate Service"""
    logger.info(f"Received access webhook data: {data}")
    return {"status": "received", "message": "Access data received successfully"}


@router.post("/webhook/iot")
async def webhook_iot(data: dict):
    """Webhook nhận dữ liệu từ IoT Service"""
    logger.info(f"Received IoT webhook data: {data}")
    return {"status": "received", "message": "IoT data received successfully"}


@router.post("/webhook/camera")
async def webhook_camera(data: dict):
    """Webhook nhận dữ liệu từ Camera Service"""
    logger.info(f"Received camera webhook data: {data}")
    return {"status": "received", "message": "Camera data received successfully"}


@router.post("/webhook/alerts")
async def webhook_alerts(data: dict):
    """Webhook nhận dữ liệu từ Core Business Service"""
    logger.info(f"Received alert webhook data: {data}")
    return {"status": "received", "message": "Alert data received successfully"}


# ── camera events ─────────────────────────────────────────────────────────────

@router.post("/camera", response_model=CameraEventResponse, status_code=201)
async def log_camera_event(event: CameraEventData):
    """Nhận camera event từ Camera Stream Service (A2), lưu vào DB."""
    if not event.event_id:
        raise HTTPException(status_code=400, detail={"status": "error", "message": "Missing required field: event_id"})
    if not event.camera_id:
        raise HTTPException(status_code=400, detail={"status": "error", "message": "Missing required field: camera_id"})
    if event.risk_level not in ["high", "medium", "info"]:
        raise HTTPException(status_code=400, detail={"status": "error", "message": "Invalid risk_level. Must be: high, medium, info"})

    try:
        timestamp = datetime.fromisoformat(event.timestamp.replace("Z", "+00:00"))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(status_code=400, detail={"status": "error", "message": "Invalid timestamp format. Use ISO 8601"})

    db = SessionLocal()
    try:
        existing = db.query(CameraEvent).filter(CameraEvent.event_id == event.event_id).first()
        if existing:
            raise HTTPException(status_code=400, detail={"status": "error", "message": f"Duplicate event_id: {event.event_id}"})

        detections_list = [{"label": d.label, "confidence": d.confidence} for d in event.detections]
        camera_event = CameraEvent(
            event_id=event.event_id,
            event_type=event.event_type,
            source_service=event.source_service,
            camera_id=event.camera_id,
            timestamp=timestamp,
            location=event.location,
            motion_detected=1 if event.motion_detected else 0,
            motion_score=event.motion_score,
            detections=detections_list,
            unknown_person=1 if event.unknown_person else 0,
            risk_level=event.risk_level,
            date=timestamp.strftime("%Y-%m-%d"),
        )
        db.add(camera_event)
        db.commit()
        db.refresh(camera_event)
        logged_id = f"log-event-{camera_event.id}"
        logger.info(f"Camera event logged: event_id={event.event_id}, logged_id={logged_id}")
        return CameraEventResponse(status="success", message="Camera event logged successfully", logged_id=logged_id)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving camera event: {e}")
        raise HTTPException(status_code=500, detail={"status": "error", "message": f"Failed to log camera event: {str(e)}"})
    finally:
        db.close()


@router.get("/camera")
async def get_camera_events(
    camera_id: Optional[str] = None,
    risk_level: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """Lấy danh sách camera events. Lọc theo camera_id, risk_level."""
    if risk_level and risk_level not in ["high", "medium", "info"]:
        raise HTTPException(status_code=400, detail="Invalid risk_level. Must be: high, medium, info")

    db = SessionLocal()
    try:
        query = db.query(CameraEvent)
        if camera_id:
            query = query.filter(CameraEvent.camera_id == camera_id)
        if risk_level:
            query = query.filter(CameraEvent.risk_level == risk_level)

        total_count = query.count()
        events = query.order_by(CameraEvent.timestamp.desc()).offset(offset).limit(limit).all()

        events_list = [
            {
                "id": e.id, "event_id": e.event_id, "event_type": e.event_type,
                "source_service": e.source_service, "camera_id": e.camera_id,
                "timestamp": e.timestamp.isoformat(), "location": e.location,
                "motion_detected": bool(e.motion_detected), "motion_score": e.motion_score,
                "detections": e.detections, "unknown_person": bool(e.unknown_person),
                "risk_level": e.risk_level, "created_at": e.created_at.isoformat(),
            }
            for e in events
        ]
        return {"status": "success", "count": len(events_list), "total_count": total_count,
                "offset": offset, "limit": limit, "events": events_list}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching camera events: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        db.close()


# ── sensor events ─────────────────────────────────────────────────────────────

@router.post("/sensor", response_model=SensorEventResponse, status_code=201)
async def log_sensor_event(event: SensorEventData):
    """Nhận sensor event từ IoT Service (A1), lưu vào DB."""
    if not event.event_id:
        raise HTTPException(status_code=400, detail={"status": "error", "message": "Missing required field: event_id"})
    if not event.device_id:
        raise HTTPException(status_code=400, detail={"status": "error", "message": "Missing required field: device_id"})
    if event.status not in ["normal", "warning", "danger", "sensor_error", "invalid_device"]:
        raise HTTPException(status_code=400, detail={"status": "error", "message": "Invalid status."})
    if event.alert_level not in ["none", "medium", "high"]:
        raise HTTPException(status_code=400, detail={"status": "error", "message": "Invalid alert_level. Must be: none, medium, high"})

    try:
        timestamp = datetime.fromisoformat(event.timestamp.replace("Z", "+00:00"))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(status_code=400, detail={"status": "error", "message": "Invalid timestamp format. Use ISO 8601"})

    db = SessionLocal()
    try:
        existing = db.query(SensorEvent).filter(SensorEvent.event_id == event.event_id).first()
        if existing:
            raise HTTPException(status_code=400, detail={"status": "error", "message": f"Duplicate event_id: {event.event_id}"})

        sensor_event = SensorEvent(
            event_id=event.event_id, event_type=event.event_type,
            source_service=event.source_service, raw_event_id=event.raw_event_id,
            device_id=event.device_id, timestamp=timestamp, location=event.location,
            temperature_c=event.temperature_c, humidity_percent=event.humidity_percent,
            motion_detected=1 if event.motion_detected else 0,
            light_lux=event.light_lux, co2_ppm=event.co2_ppm,
            smoke_ppm=event.smoke_ppm, battery_percent=event.battery_percent,
            status=event.status, alert_level=event.alert_level,
            reason=event.reason, date=timestamp.strftime("%Y-%m-%d"),
        )
        db.add(sensor_event)
        db.commit()
        db.refresh(sensor_event)
        logged_id = f"log-sensor-{sensor_event.id}"
        logger.info(f"Sensor event logged: event_id={event.event_id}, logged_id={logged_id}")
        return SensorEventResponse(status="success", message="Sensor event logged successfully", logged_id=logged_id)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error logging sensor event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        db.close()


@router.get("/sensor")
async def get_sensor_events(
    device_id: Optional[str] = None,
    status: Optional[str] = None,
    alert_level: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """Lấy danh sách sensor events. Lọc theo device_id, status, alert_level."""
    if status and status not in ["normal", "warning", "danger", "sensor_error", "invalid_device"]:
        raise HTTPException(status_code=400, detail="Invalid status.")
    if alert_level and alert_level not in ["none", "medium", "high"]:
        raise HTTPException(status_code=400, detail="Invalid alert_level. Must be: none, medium, high")

    db = SessionLocal()
    try:
        query = db.query(SensorEvent)
        if device_id:
            query = query.filter(SensorEvent.device_id == device_id)
        if status:
            query = query.filter(SensorEvent.status == status)
        if alert_level:
            query = query.filter(SensorEvent.alert_level == alert_level)

        total_count = query.count()
        events = query.order_by(SensorEvent.timestamp.desc()).offset(offset).limit(limit).all()

        events_list = [
            {
                "id": e.id, "event_id": e.event_id, "event_type": e.event_type,
                "source_service": e.source_service, "raw_event_id": e.raw_event_id,
                "device_id": e.device_id, "timestamp": e.timestamp.isoformat(),
                "location": e.location, "temperature_c": e.temperature_c,
                "humidity_percent": e.humidity_percent, "motion_detected": bool(e.motion_detected),
                "light_lux": e.light_lux, "co2_ppm": e.co2_ppm, "smoke_ppm": e.smoke_ppm,
                "battery_percent": e.battery_percent, "status": e.status,
                "alert_level": e.alert_level, "reason": e.reason,
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ]
        return {"status": "success", "count": len(events_list), "total_count": total_count,
                "offset": offset, "limit": limit, "events": events_list}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching sensor events: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        db.close()


# ── vision detections ─────────────────────────────────────────────────────────

@router.post("/vision-detections", response_model=VisionDetectionResponse, status_code=201)
async def log_vision_detection(event: VisionDetectionData):
    """Nhận detection log từ A4 AI Vision, lưu vào DB."""
    if not event.detection_id:
        raise HTTPException(status_code=400, detail={"status": "error", "message": "Missing required field: detection_id"})
    if not event.camera_id:
        raise HTTPException(status_code=400, detail={"status": "error", "message": "Missing required field: camera_id"})
    if event.model_mode not in ["yolo", "mock-ai"]:
        raise HTTPException(status_code=400, detail={"status": "error", "message": "Invalid model_mode. Must be: yolo, mock-ai"})
    if event.finding.finding_type not in ["person", "object"]:
        raise HTTPException(status_code=400, detail={"status": "error", "message": "Invalid finding.finding_type. Must be: person, object"})
    if event.finding.risk_level not in ["low", "medium", "high"]:
        raise HTTPException(status_code=400, detail={"status": "error", "message": "Invalid finding.risk_level. Must be: low, medium, high"})

    try:
        timestamp = datetime.fromisoformat(event.timestamp.replace("Z", "+00:00"))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(status_code=400, detail={"status": "error", "message": "Invalid timestamp format. Use ISO 8601"})

    db = SessionLocal()
    try:
        existing = db.query(VisionDetectionEvent).filter(VisionDetectionEvent.detection_id == event.detection_id).first()
        if existing:
            raise HTTPException(status_code=400, detail={"status": "error", "message": f"Duplicate detection_id: {event.detection_id}"})

        vision_event = VisionDetectionEvent(
            detection_id=event.detection_id, camera_id=event.camera_id,
            frame_url=event.frame_url, timestamp=timestamp,
            anomaly_detected=1 if event.anomaly_detected else 0,
            confidence_score=event.confidence_score,
            finding={"finding_type": event.finding.finding_type, "object_name": event.finding.object_name,
                     "risk_level": event.finding.risk_level, "description": event.finding.description},
            model_mode=event.model_mode, notes=event.notes,
            date=timestamp.strftime("%Y-%m-%d"),
        )
        db.add(vision_event)
        db.commit()
        db.refresh(vision_event)
        logger.info(f"Vision detection logged: detection_id={event.detection_id}")
        return VisionDetectionResponse(status="received", message="Detection log stored successfully", detection_id=event.detection_id)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving vision detection: {e}")
        raise HTTPException(status_code=500, detail={"status": "error", "message": f"Failed to log vision detection: {str(e)}"})
    finally:
        db.close()


# ── sample data ───────────────────────────────────────────────────────────────

@router.get("/sample-data/recent")
async def get_recent_sample_data(limit: int = 5, kind: Optional[str] = None):
    """Trả về các sample event gần nhất để hiển thị trong UI."""
    kind_value = (kind or "all").strip().lower()
    if kind_value not in {"all", "camera", "sensor", "vision"}:
        raise HTTPException(status_code=400, detail="Invalid kind filter. Use camera, sensor, vision, or all.")

    db = SessionLocal()
    try:
        items = []
        if kind_value in {"all", "camera"}:
            rows = db.query(CameraEvent).filter(CameraEvent.event_id.like("camera-sample-%")) \
                      .order_by(CameraEvent.timestamp.desc()).limit(limit).all()
            items.extend(_serialize_camera_event(e) for e in rows)
        if kind_value in {"all", "sensor"}:
            rows = db.query(SensorEvent).filter(SensorEvent.event_id.like("sensor-sample-%")) \
                      .order_by(SensorEvent.timestamp.desc()).limit(limit).all()
            items.extend(_serialize_sensor_event(e) for e in rows)
        if kind_value in {"all", "vision"}:
            rows = db.query(VisionDetectionEvent).filter(VisionDetectionEvent.detection_id.like("vision-sample-%")) \
                      .order_by(VisionDetectionEvent.timestamp.desc()).limit(limit).all()
            items.extend(_serialize_vision_event(e) for e in rows)

        items.sort(key=lambda x: x.get("created_at") or "", reverse=True)
        return {"status": "success", "count": len(items[:limit]), "items": items[:limit]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching recent sample data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        db.close()


@router.delete("/sample-data")
async def clear_sample_data():
    """Xóa toàn bộ sample data đã seed từ UI."""
    db = SessionLocal()
    try:
        cam = db.query(CameraEvent).filter(CameraEvent.event_id.like("camera-sample-%")).delete(synchronize_session=False)
        sen = db.query(SensorEvent).filter(SensorEvent.event_id.like("sensor-sample-%")).delete(synchronize_session=False)
        vis = db.query(VisionDetectionEvent).filter(VisionDetectionEvent.detection_id.like("vision-sample-%")).delete(synchronize_session=False)
        db.commit()
        return {"status": "success", "message": "Sample data cleared successfully",
                "deleted": {"camera": cam, "sensor": sen, "vision": vis}}
    except Exception as e:
        db.rollback()
        logger.error(f"Error clearing sample data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        db.close()


# ── Core Business Service (A6) ────────────────────────────────────────────────

@router.get("/core/health")
async def get_core_business_health():
    """Kiểm tra Core Business Service (A6)"""
    result = await core_client.health_check()
    if result:
        return result
    raise HTTPException(status_code=503, detail="Core Business Service is unavailable")


@router.get("/core/events")
async def get_core_events(event_type: Optional[str] = None):
    """Lấy toàn bộ events từ Core Business Service (A6)"""
    result = await core_client.get_all_events(event_type)
    if result:
        return result
    raise HTTPException(status_code=503, detail="Cannot fetch events from Core Business Service")


@router.get("/core/events/sensor")
async def get_core_sensor_events():
    """Lấy sensor events từ Core Business Service (A6)"""
    result = await core_client.get_sensor_events()
    if result:
        return result
    raise HTTPException(status_code=503, detail="Cannot fetch sensor events from Core Business Service")


@router.get("/core/events/access")
async def get_core_access_events():
    """Lấy access events từ Core Business Service (A6)"""
    result = await core_client.get_access_events()
    if result:
        return result
    raise HTTPException(status_code=503, detail="Cannot fetch access events from Core Business Service")


@router.get("/core/events/camera")
async def get_core_camera_events():
    """Lấy camera events từ Core Business Service (A6)"""
    result = await core_client.get_camera_events()
    if result:
        return result
    raise HTTPException(status_code=503, detail="Cannot fetch camera events from Core Business Service")


@router.get("/core/events/anomaly", response_model=AnomalyEventResponse)
async def get_core_anomaly_events(date: Optional[str] = None):
    """
    Lấy anomaly events từ Core Business Service (A6).
    date: YYYY-MM-DD (mặc định hôm nay)
    """
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    raw = await core_client.get_anomaly_events(date)
    if raw is None:
        raise HTTPException(status_code=503, detail="Cannot fetch anomaly events from Core Business Service")

    # raw is Optional[Dict] from core_client; parse into typed response
    data_items = raw.get("data", []) if isinstance(raw, dict) else []
    try:
        parsed = [AnomalyEventData(**item) for item in data_items]
    except Exception as e:
        logger.error(f"Error parsing anomaly events: {e}")
        parsed = []

    return AnomalyEventResponse(status="success", count=len(parsed), data=parsed)


@router.get("/core/alerts")
async def get_core_alerts(severity: Optional[str] = None):
    """Lấy alerts từ Core Business Service (A6)"""
    result = await core_client.get_alerts(severity)
    if result:
        return result
    raise HTTPException(status_code=503, detail="Cannot fetch alerts from Core Business Service")


@router.get("/core/summary")
async def get_core_analytics_summary():
    """Lấy analytics summary từ Core Business Service (A6)"""
    result = await core_client.get_analytics_summary()
    if result:
        return result
    raise HTTPException(status_code=503, detail="Cannot fetch analytics summary from Core Business Service")


# ── dashboard ─────────────────────────────────────────────────────────────────

@router.get("/dashboard")
async def get_analytics_dashboard():
    """
    Tổng hợp dashboard metrics từ tất cả sources.
    Fetch Core Business calls song song để giảm latency.
    """
    try:
        # Fetch Core Business data in parallel
        core_health, core_events, core_alerts, core_summary = await asyncio.gather(
            core_client.health_check(),
            core_client.get_all_events(),
            core_client.get_alerts(),
            core_client.get_analytics_summary(),
        )

        db = SessionLocal()
        try:
            total_camera_events = db.query(CameraEvent).count()
            high_risk_camera = db.query(CameraEvent).filter(CameraEvent.risk_level == "high").count()
            total_sensor_events = db.query(SensorEvent).count()
            danger_sensors = db.query(SensorEvent).filter(SensorEvent.status == "danger").count()
            warning_sensors = db.query(SensorEvent).filter(SensorEvent.status == "warning").count()
            high_alert_sensors = db.query(SensorEvent).filter(SensorEvent.alert_level == "high").count()

            sensor_status_count = {}
            for s in ["normal", "warning", "danger", "sensor_error", "invalid_device"]:
                c = db.query(SensorEvent).filter(SensorEvent.status == s).count()
                if c > 0:
                    sensor_status_count[s] = c
        except Exception as e:
            logger.error(f"Error fetching DB analytics data: {e}")
            total_camera_events = high_risk_camera = 0
            total_sensor_events = danger_sensors = warning_sensors = high_alert_sensors = 0
            sensor_status_count = {}
        finally:
            db.close()

        return {
            "timestamp": datetime.now().isoformat(),
            "core_business": {
                "status": "online" if core_health else "offline",
                "health": core_health,
                "total_events": core_events.get("count", 0) if core_events else 0,
                "total_alerts": core_alerts.get("count", 0) if core_alerts else 0,
                "summary": core_summary,
            },
            "camera_analytics": {
                "total_events": total_camera_events,
                "high_risk_events": high_risk_camera,
            },
            "sensor_analytics": {
                "total_events": total_sensor_events,
                "danger_status": danger_sensors,
                "warning_status": warning_sensors,
                "high_alert_level": high_alert_sensors,
                "status_breakdown": sensor_status_count,
            },
            "integration_status": {
                "camera_a2": "ready",
                "sensor_iot_a1": "ready",
                "core_business_a6": "online" if core_health else "offline",
                "notification_a7": "configured",
            },
        }
    except Exception as e:
        logger.error(f"Error building analytics dashboard: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
