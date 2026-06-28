import httpx
from typing import List, Dict, Any
import logging
from app.models.schemas import MotionDetectionData
from app.config import settings

logger = logging.getLogger(__name__)


class CameraService:
    """Service để lấy dữ liệu từ Camera Stream / AI Vision"""
    
    def __init__(self):
        self.base_url = settings.CAMERA_SERVICE_URL
        self.timeout = 10.0
    
    async def get_motion_detections(self, date: str) -> List[MotionDetectionData]:
        """
        Lấy dữ liệu phát hiện chuyển động từ Camera Service
        
        Args:
            date: Định dạng YYYY-MM-DD
            
        Returns:
            List of MotionDetectionData
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/camera/detections/motion",
                    params={"date": date},
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                return [MotionDetectionData(**item) for item in data.get("data", [])]
        except Exception as e:
            logger.error(f"Error fetching motion detection data from Camera: {e}")
            return []
    
    async def get_motion_count(self, date: str) -> int:
        """Lấy tổng số lần phát hiện chuyển động"""
        try:
            detections = await self.get_motion_detections(date)
            return len([d for d in detections if d.detected])
        except Exception as e:
            logger.error(f"Error calculating motion detection count: {e}")
            return 0
    
    async def get_motion_by_location(self, date: str) -> Dict[str, int]:
        """Lấy số lần phát hiện chuyển động theo vị trí"""
        try:
            detections = await self.get_motion_detections(date)
            location_counts = {}
            
            for detection in detections:
                if detection.detected:
                    location = detection.location
                    location_counts[location] = location_counts.get(location, 0) + 1
            
            return location_counts
        except Exception as e:
            logger.error(f"Error calculating motion by location: {e}")
            return {}
    
    async def get_camera_summary(self, date: str) -> Dict[str, Any]:
        """Lấy tóm tắt dữ liệu Camera — chỉ fetch detections 1 lần"""
        try:
            detections = await self.get_motion_detections(date)

            motion_count = len([d for d in detections if d.detected])

            location_counts: Dict[str, int] = {}
            for detection in detections:
                if detection.detected:
                    location_counts[detection.location] = location_counts.get(detection.location, 0) + 1

            return {
                "total_motion_detections": motion_count,
                "by_location": location_counts,
            }
        except Exception as e:
            logger.error(f"Error getting camera summary: {e}")
            return {"total_motion_detections": 0, "by_location": {}}
