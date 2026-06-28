"""
HTTP Client để gọi Core Business Service (A6)
"""
import logging
import httpx
from typing import Optional, Dict, Any, List
from app.config import settings

logger = logging.getLogger(__name__)


class CoreBusinessClient:
    """Client để tương tác với Core Business Service (A6)"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.CORE_BUSINESS_URL
        self.timeout = 5.0  # 5 seconds timeout
    
    async def health_check(self) -> Optional[Dict[str, Any]]:
        """Kiểm tra Core Business Service đang chạy"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"Core health check failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error checking Core Business health: {e}")
            return None
    
    async def get_all_events(self, event_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Lấy toàn bộ events từ Core Business"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {}
                if event_type:
                    params["event_type"] = event_type
                
                response = await client.get(
                    f"{self.base_url}/api/v1/events",
                    params=params
                )
                
                if response.status_code == 200:
                    return response.json()
                
                logger.warning(f"Get events failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting events from Core Business: {e}")
            return None
    
    async def get_sensor_events(self) -> Optional[Dict[str, Any]]:
        """Lấy sensor events từ Core Business"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/events/sensor")
                
                if response.status_code == 200:
                    return response.json()
                
                logger.warning(f"Get sensor events failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting sensor events from Core Business: {e}")
            return None
    
    async def get_access_events(self) -> Optional[Dict[str, Any]]:
        """Lấy access events từ Core Business"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/events/access")
                
                if response.status_code == 200:
                    return response.json()
                
                logger.warning(f"Get access events failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting access events from Core Business: {e}")
            return None
    
    async def get_camera_events(self) -> Optional[Dict[str, Any]]:
        """Lấy camera events từ Core Business"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/events/camera")
                
                if response.status_code == 200:
                    return response.json()
                
                logger.warning(f"Get camera events failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting camera events from Core Business: {e}")
            return None

    async def get_anomaly_events(self, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Lấy anomaly events từ Core Business"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {}
                if date:
                    params["date"] = date

                response = await client.get(
                    f"{self.base_url}/api/anomaly-events",
                    params=params
                )

                if response.status_code == 200:
                    return response.json()

                logger.warning(f"Get anomaly events failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting anomaly events from Core Business: {e}")
            return None

    async def get_alerts(self, severity: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Lấy alerts từ Core Business"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {}
                if severity:
                    params["severity"] = severity
                
                response = await client.get(
                    f"{self.base_url}/api/v1/alerts",
                    params=params
                )
                
                if response.status_code == 200:
                    return response.json()
                
                logger.warning(f"Get alerts failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting alerts from Core Business: {e}")
            return None
    
    async def get_analytics_summary(self) -> Optional[Dict[str, Any]]:
        """Lấy analytics summary từ Core Business"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/analytics/summary")
                
                if response.status_code == 200:
                    return response.json()
                
                logger.warning(f"Get analytics summary failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting analytics summary from Core Business: {e}")
            return None


# Create global client instance
core_client = CoreBusinessClient()
