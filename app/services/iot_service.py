import httpx
from typing import List, Dict, Any
import logging
from app.models.schemas import TemperatureData
from app.config import settings

logger = logging.getLogger(__name__)


class IoTService:
    """Service để lấy dữ liệu từ IoT Ingestion"""
    
    def __init__(self):
        self.base_url = settings.IOT_SERVICE_URL
        self.timeout = 10.0
    
    async def get_temperature_data(self, date: str) -> List[TemperatureData]:
        """
        Lấy dữ liệu nhiệt độ từ IoT Service
        
        Args:
            date: Định dạng YYYY-MM-DD
            
        Returns:
            List of TemperatureData
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/iot/sensors/temperature",
                    params={"date": date},
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                return [TemperatureData(**item) for item in data.get("data", [])]
        except Exception as e:
            logger.error(f"Error fetching temperature data from IoT: {e}")
            return []
    
    async def get_average_temperature(self, date: str) -> float:
        """Lấy nhiệt độ trung bình cho ngày"""
        try:
            data = await self.get_temperature_data(date)
            if not data:
                return 0.0
            
            temperatures = [d.temperature for d in data]
            return round(sum(temperatures) / len(temperatures), 2)
        except Exception as e:
            logger.error(f"Error calculating average temperature: {e}")
            return 0.0
    
    async def get_temperature_by_room(self, date: str) -> Dict[str, float]:
        """Lấy nhiệt độ trung bình theo phòng/khu vực"""
        try:
            data = await self.get_temperature_data(date)
            room_temps = {}
            
            for temp_data in data:
                room = temp_data.room_name
                if room not in room_temps:
                    room_temps[room] = []
                room_temps[room].append(temp_data.temperature)
            
            # Tính trung bình cho mỗi phòng
            result = {}
            for room, temps in room_temps.items():
                result[room] = round(sum(temps) / len(temps), 2)
            
            return result
        except Exception as e:
            logger.error(f"Error calculating temperature by room: {e}")
            return {}
    
    async def get_iot_summary(self, date: str) -> Dict[str, Any]:
        """Lấy tóm tắt dữ liệu IoT — chỉ fetch temperature data 1 lần"""
        try:
            data = await self.get_temperature_data(date)

            if not data:
                return {"avg_temperature": 0.0, "by_room": {}}

            temperatures = [d.temperature for d in data]
            avg_temp = round(sum(temperatures) / len(temperatures), 2)

            room_temps: Dict[str, list] = {}
            for temp_data in data:
                room = temp_data.room_name
                room_temps.setdefault(room, []).append(temp_data.temperature)

            temp_by_room = {room: round(sum(temps) / len(temps), 2) for room, temps in room_temps.items()}

            return {
                "avg_temperature": avg_temp,
                "by_room": temp_by_room,
            }
        except Exception as e:
            logger.error(f"Error getting IoT summary: {e}")
            return {"avg_temperature": 0.0, "by_room": {}}
