from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any


class AccessData(BaseModel):
    """Data from Access Gate Service"""
    timestamp: datetime
    person_id: str
    access_type: str  # "entry" or "exit"
    gate_id: str
    location: str
    

class TemperatureData(BaseModel):
    """Data from IoT Sensors"""
    timestamp: datetime
    sensor_id: str
    temperature: float
    room_id: str
    room_name: str
    humidity: Optional[float] = None


class MotionDetectionData(BaseModel):
    """Data from Camera Stream / AI Vision"""
    timestamp: datetime
    camera_id: str
    detected: bool
    location: str
    confidence: float
    frame_id: Optional[str] = None


class DetectionObject(BaseModel):
    """Detection object from Camera AI"""
    label: str
    confidence: float


class CameraEventData(BaseModel):
    """Camera event from Camera Stream Service (A2) - API Contract"""
    event_id: str
    event_type: str
    source_service: str
    camera_id: str
    timestamp: str  # ISO 8601 format
    location: str
    motion_detected: bool
    motion_score: float
    detections: List[DetectionObject]
    unknown_person: bool
    risk_level: str  # "high", "medium", "info"


class CameraEventResponse(BaseModel):
    """Response when camera event is logged"""
    status: str
    message: str
    logged_id: str


class VisionFinding(BaseModel):
    """Detection finding details from AI Vision"""
    finding_type: str  # "person" | "object"
    object_name: Optional[str] = None
    risk_level: str  # "low" | "medium" | "high"
    description: Optional[str] = None


class VisionDetectionData(BaseModel):
    """Vision detection log from A4 AI Vision"""
    model_config = ConfigDict(protected_namespaces=())
    detection_id: str
    camera_id: str
    frame_url: str
    timestamp: str  # ISO 8601 format
    anomaly_detected: bool
    confidence_score: Optional[float] = None
    finding: VisionFinding
    model_mode: str  # "yolo" | "mock-ai"
    notes: Optional[str] = None


class VisionDetectionResponse(BaseModel):
    """Response when vision detection is logged"""
    status: str
    message: str
    detection_id: str


class SensorEventData(BaseModel):
    """Sensor event from IoT Service (A1) - API Contract"""
    event_id: str
    event_type: str
    source_service: str
    raw_event_id: str
    device_id: str
    timestamp: str  # ISO 8601 format
    location: str
    temperature_c: Optional[float] = None  # Can be null if sensor fails
    humidity_percent: Optional[float] = None  # Can be null if sensor fails
    motion_detected: bool
    light_lux: Optional[float] = None
    co2_ppm: Optional[float] = None
    smoke_ppm: Optional[float] = None
    battery_percent: Optional[float] = None
    status: str  # "normal", "warning", "danger", "sensor_error", "invalid_device"
    alert_level: str  # "none", "medium", "high"
    reason: str  # e.g., "environment_normal", "temperature_critical"


class SensorEventResponse(BaseModel):
    """Response when sensor event is logged"""
    status: str
    message: str
    logged_id: str


class AlertData(BaseModel):
    """Data from Core Business Service"""
    timestamp: datetime
    alert_id: str
    alert_type: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    source: str


class AnomalyEventData(BaseModel):
    """Anomaly detection data — used for parsing Core Business API responses"""
    timestamp: datetime
    event_type: str
    description: str
    severity: str
    source: str


class AnomalyEventResponse(BaseModel):
    """Wrapper returned by /core/events/anomaly route"""
    status: str
    count: int
    data: List[AnomalyEventData]


class MetricResponse(BaseModel):
    """Response format for analytics metrics"""
    date: str
    total_access: int
    total_access_in: int
    total_access_out: int
    access_by_hour: Dict[str, int]  # hour: count
    avg_temperature: float
    temperature_by_room: Dict[str, float]  # room_name: avg_temp
    total_alerts: int
    alerts_by_type: Dict[str, int]
    total_motion_detections: int
    total_anomaly_events: int


class DailyReport(BaseModel):
    """Daily analytics report"""
    date: str
    summary: MetricResponse
    hourly_breakdown: Dict[str, Any]
    status: str  # "success", "partial", "failed"
    generated_at: datetime
