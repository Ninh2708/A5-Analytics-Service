import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
from app.services.access_gate_service import AccessGateService
from app.services.iot_service import IoTService
from app.services.camera_service import CameraService
from app.services.core_business_service import CoreBusinessService
from app.models.schemas import MetricResponse, DailyReport

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Engine chính để tổng hợp các metric từ các service khác nhau"""
    
    def __init__(self):
        self.access_service = AccessGateService()
        self.iot_service = IoTService()
        self.camera_service = CameraService()
        self.business_service = CoreBusinessService()
    
    async def generate_daily_report(self, date: str) -> DailyReport:
        """
        Tạo báo cáo hàng ngày bằng cách tổng hợp dữ liệu từ tất cả các service
        
        Args:
            date: Định dạng YYYY-MM-DD
            
        Returns:
            DailyReport object
        """
        try:
            # Lấy dữ liệu từ tất cả các service song song
            access_summary, iot_summary, camera_summary, business_summary = await asyncio.gather(
                self.access_service.get_access_summary(date),
                self.iot_service.get_iot_summary(date),
                self.camera_service.get_camera_summary(date),
                self.business_service.get_business_summary(date),
            )
            
            # Tạo metric response
            metrics = MetricResponse(
                date=date,
                total_access=access_summary.get("total_access", 0),
                total_access_in=access_summary.get("total_in", 0),
                total_access_out=access_summary.get("total_out", 0),
                access_by_hour=access_summary.get("by_hour", {}),
                avg_temperature=iot_summary.get("avg_temperature", 0.0),
                temperature_by_room=iot_summary.get("by_room", {}),
                total_alerts=business_summary.get("total_alerts", 0),
                alerts_by_type=business_summary.get("alerts_by_type", {}),
                total_motion_detections=camera_summary.get("total_motion_detections", 0),
                total_anomaly_events=business_summary.get("total_anomaly_events", 0),
            )
            
            # Tạo hourly breakdown
            hourly_breakdown = self._create_hourly_breakdown(
                access_summary.get("by_hour", {}),
                date
            )
            
            # Tạo DailyReport
            report = DailyReport(
                date=date,
                summary=metrics,
                hourly_breakdown=hourly_breakdown,
                status="success",
                generated_at=datetime.now()
            )
            
            logger.info(f"Successfully generated daily report for {date}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
            # Return empty report with failed status
            return DailyReport(
                date=date,
                summary=MetricResponse(
                    date=date,
                    total_access=0,
                    total_access_in=0,
                    total_access_out=0,
                    access_by_hour={},
                    avg_temperature=0.0,
                    temperature_by_room={},
                    total_alerts=0,
                    alerts_by_type={},
                    total_motion_detections=0,
                    total_anomaly_events=0,
                ),
                hourly_breakdown={},
                status="failed",
                generated_at=datetime.now()
            )
    
    def _create_hourly_breakdown(self, access_by_hour: Dict[int, int], date: str) -> Dict[int, Any]:
        """Tạo chi tiết từng giờ"""
        breakdown = {}
        for hour, count in access_by_hour.items():
            breakdown[hour] = {
                "access_count": count,
                "hour": f"{hour:02d}:00"
            }
        return breakdown
    
    async def get_metrics_summary(self, date: str) -> Dict[str, Any]:
        """
        Lấy tóm tắt metrics dưới dạng JSON
        
        Args:
            date: Định dạng YYYY-MM-DD
            
        Returns:
            Dictionary chứa các metrics
        """
        try:
            report = await self.generate_daily_report(date)
            return {
                "date": report.date,
                "total_access": report.summary.total_access,
                "total_alerts": report.summary.total_alerts,
                "avg_temperature": report.summary.avg_temperature,
                "total_motion_detections": report.summary.total_motion_detections,
                "total_anomaly_events": report.summary.total_anomaly_events,
            }
        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}")
            return {
                "date": date,
                "total_access": 0,
                "total_alerts": 0,
                "avg_temperature": 0.0,
                "total_motion_detections": 0,
                "total_anomaly_events": 0,
            }
