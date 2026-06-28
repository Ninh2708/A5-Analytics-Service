import httpx
from typing import List, Dict, Any
from datetime import datetime
import logging
from app.models.schemas import AccessData
from app.config import settings

logger = logging.getLogger(__name__)


class AccessGateService:
    """Service để lấy dữ liệu từ Access Gate"""
    
    def __init__(self):
        self.base_url = settings.ACCESS_GATE_URL
        self.timeout = 10.0
    
    async def get_access_logs(self, date: str) -> List[AccessData]:
        """
        Lấy dữ liệu ra/vào từ Access Gate Service
        
        Args:
            date: Định dạng YYYY-MM-DD
            
        Returns:
            List of AccessData
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/access/logs",
                    params={"date": date},
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                return [AccessData(**item) for item in data.get("data", [])]
        except Exception as e:
            logger.error(f"Error fetching access logs from Access Gate: {e}")
            return []
    
    async def get_hourly_access_count(self, date: str) -> Dict[int, int]:
        """Lấy số lượt ra/vào theo giờ"""
        try:
            logs = await self.get_access_logs(date)
            hourly_count = {hour: 0 for hour in range(24)}
            
            for log in logs:
                hour = log.timestamp.hour
                hourly_count[hour] += 1
            
            return hourly_count
        except Exception as e:
            logger.error(f"Error calculating hourly access count: {e}")
            return {hour: 0 for hour in range(24)}
    
    async def get_access_summary(self, date: str) -> Dict[str, Any]:
        """Lấy tóm tắt dữ liệu ra/vào — chỉ fetch logs 1 lần"""
        try:
            logs = await self.get_access_logs(date)

            total_access = len(logs)
            total_in = sum(1 for log in logs if log.access_type.lower() == "entry")
            total_out = sum(1 for log in logs if log.access_type.lower() == "exit")

            hourly_count: Dict[int, int] = {hour: 0 for hour in range(24)}
            for log in logs:
                hourly_count[log.timestamp.hour] += 1

            return {
                "total_access": total_access,
                "total_in": total_in,
                "total_out": total_out,
                "by_hour": hourly_count,
            }
        except Exception as e:
            logger.error(f"Error getting access summary: {e}")
            return {"total_access": 0, "total_in": 0, "total_out": 0, "by_hour": {}}
