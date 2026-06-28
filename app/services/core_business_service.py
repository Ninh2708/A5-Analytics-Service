import asyncio
import httpx
from typing import List, Dict, Any
import logging
from app.models.schemas import AlertData, AnomalyEventData
from app.config import settings

logger = logging.getLogger(__name__)


class CoreBusinessService:
    """Service để lấy dữ liệu từ Core Business"""

    def __init__(self):
        self.base_url = settings.CORE_BUSINESS_URL
        self.timeout = 10.0

    async def get_alerts(self, date: str) -> List[AlertData]:
        """
        Lấy dữ liệu cảnh báo từ Core Business Service

        Args:
            date: Định dạng YYYY-MM-DD

        Returns:
            List of AlertData
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/alerts",  # fixed: was /api/alerts
                    params={"date": date},
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()
                return [AlertData(**item) for item in data.get("data", [])]
        except Exception as e:
            logger.error(f"Error fetching alerts from Core Business: {e}")
            return []

    async def get_anomaly_events(self, date: str) -> List[AnomalyEventData]:
        """
        Lấy dữ liệu event bất thường từ Core Business

        Args:
            date: Định dạng YYYY-MM-DD

        Returns:
            List of AnomalyEventData
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/anomaly-events",
                    params={"date": date},
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()
                return [AnomalyEventData(**item) for item in data.get("data", [])]
        except Exception as e:
            logger.error(f"Error fetching anomaly events from Core Business: {e}")
            return []

    async def get_business_summary(self, date: str) -> Dict[str, Any]:
        """
        Lấy tóm tắt dữ liệu Core Business.
        Fetch alerts và anomaly events song song, tính toán từ kết quả — chỉ 2 HTTP calls.
        """
        try:
            alerts, anomaly_events = await asyncio.gather(
                self.get_alerts(date),
                self.get_anomaly_events(date),
            )

            alert_types: Dict[str, int] = {}
            for alert in alerts:
                alert_types[alert.alert_type] = alert_types.get(alert.alert_type, 0) + 1

            return {
                "total_alerts": len(alerts),
                "alerts_by_type": alert_types,
                "total_anomaly_events": len(anomaly_events),
            }
        except Exception as e:
            logger.error(f"Error getting business summary: {e}")
            return {
                "total_alerts": 0,
                "alerts_by_type": {},
                "total_anomaly_events": 0,
            }
