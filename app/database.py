"""
Database models for Analytics Service (optional - for storing historical data)
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()


class DailyMetrics(Base):
    """Table để lưu metrics hàng ngày"""
    __tablename__ = "daily_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, unique=True, index=True)
    total_access = Column(Integer, default=0)
    total_access_in = Column(Integer, default=0)
    total_access_out = Column(Integer, default=0)
    access_by_hour = Column(JSON)
    avg_temperature = Column(Float, default=0.0)
    temperature_by_room = Column(JSON)
    total_alerts = Column(Integer, default=0)
    alerts_by_type = Column(JSON)
    total_motion_detections = Column(Integer, default=0)
    total_anomaly_events = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AccessEvent(Base):
    """Table để lưu access events"""
    __tablename__ = "access_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    person_id = Column(String, index=True)
    access_type = Column(String)  # entry or exit
    gate_id = Column(String)
    location = Column(String)
    date = Column(String, index=True)
    hour = Column(Integer)


class TemperatureReading(Base):
    """Table để lưu temperature readings"""
    __tablename__ = "temperature_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    sensor_id = Column(String, index=True)
    temperature = Column(Float)
    room_id = Column(String, index=True)
    room_name = Column(String)
    humidity = Column(Float, nullable=True)
    date = Column(String, index=True)


class AlertEvent(Base):
    """Table để lưu alert events"""
    __tablename__ = "alert_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    alert_id = Column(String, unique=True)
    alert_type = Column(String, index=True)
    severity = Column(String)
    description = Column(String)
    source = Column(String)
    date = Column(String, index=True)


class MotionDetectionEvent(Base):
    """Table để lưu motion detection events"""
    __tablename__ = "motion_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    camera_id = Column(String, index=True)
    detected = Column(Integer)  # 1 for true, 0 for false
    location = Column(String)
    confidence = Column(Float)
    date = Column(String, index=True)


class AnomalyEvent(Base):
    """Table để lưu anomaly events"""
    __tablename__ = "anomaly_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    event_type = Column(String)
    description = Column(String)
    severity = Column(String)
    source = Column(String)
    date = Column(String, index=True)


class CameraEvent(Base):
    """Table để lưu camera events từ Camera Service (A2)"""
    __tablename__ = "camera_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)  # chống trùng lặp
    event_type = Column(String, index=True)
    source_service = Column(String)
    camera_id = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    location = Column(String)
    motion_detected = Column(Integer)  # 1 for true, 0 for false
    motion_score = Column(Float)
    detections = Column(JSON)  # lưu danh sách detection objects
    unknown_person = Column(Integer)  # 1 for true, 0 for false
    risk_level = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    date = Column(String, index=True)


class VisionDetectionEvent(Base):
    """Table để lưu vision detection logs từ AI Vision (A4)"""
    __tablename__ = "vision_detection_events"

    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(String, unique=True, index=True)
    camera_id = Column(String, index=True)
    frame_url = Column(String)
    timestamp = Column(DateTime, index=True)
    anomaly_detected = Column(Integer)
    confidence_score = Column(Float, nullable=True)
    finding = Column(JSON)
    model_mode = Column(String)
    notes = Column(String, nullable=True)
    date = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class SensorEvent(Base):
    """Table để lưu sensor events từ IoT Service (A1)"""
    __tablename__ = "sensor_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)  # chống trùng lặp
    event_type = Column(String, index=True)
    source_service = Column(String)
    raw_event_id = Column(String, index=True)  # truy vết từ Pi Simulator
    device_id = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    location = Column(String)
    temperature_c = Column(Float, nullable=True)
    humidity_percent = Column(Float, nullable=True)
    motion_detected = Column(Integer)  # 1 for true, 0 for false
    light_lux = Column(Float, nullable=True)
    co2_ppm = Column(Float, nullable=True)
    smoke_ppm = Column(Float, nullable=True)
    battery_percent = Column(Float, nullable=True)
    status = Column(String)  # normal, warning, danger, sensor_error, invalid_device
    alert_level = Column(String)  # none, medium, high
    reason = Column(String)  # e.g., environment_normal, temperature_critical
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    date = Column(String, index=True)
