"""
Finnhub economic calendar API client
Backup source for economic events when Forex Factory is unavailable
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import aiohttp


FINNHUB_BASE = "https://finnhub.io/api/v1"


class FinnhubCalendar:
    """Fetches economic calendar from Finnhub API"""

    def __init__(self, api_key: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key or os.getenv("FINNHUB_API_KEY", "")

    async def fetch_economic_calendar(
        self, from_date: Optional[str] = None, to_date: Optional[str] = None
    ) -> List[Dict]:
        """Fetch economic calendar events within a date range."""
        if not self.api_key:
            self.logger.warning("No Finnhub API key configured")
            return []

        if not from_date:
            from_date = datetime.now().strftime("%Y-%m-%d")
        if not to_date:
            to_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        url = f"{FINNHUB_BASE}/calendar/economic"
        params = {"token": self.api_key, "from": from_date, "to": to_date}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, params=params, timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status != 200:
                        self.logger.error(f"Finnhub API error: {response.status}")
                        return []
                    data = await response.json()

            events = []
            for item in data.get("economicCalendar", []):
                event = self._to_common_schema(item)
                if event:
                    events.append(event)

            self.logger.info(f"Finnhub: {len(events)} events fetched")
            return events

        except Exception as e:
            self.logger.error(f"Finnhub fetch failed: {e}")
            return []

    def _to_common_schema(self, item: Dict) -> Optional[Dict]:
        """Convert Finnhub event to common schema."""
        try:
            # Finnhub impact: 0-3 scale
            impact_raw = item.get("impact", "").lower()
            impact_map = {"low": 1, "medium": 2, "high": 3}
            impact = impact_map.get(impact_raw, 0)

            event = {
                "source": "finnhub",
                "currency": self._country_to_currency(item.get("country", "")),
                "event": item.get("event", ""),
                "impact": impact,
                "date": item.get("date"),
                "time": None,
                "actual": item.get("actual"),
                "forecast": item.get("estimate"),
                "previous": item.get("prev"),
                "unit": item.get("unit"),
            }
            return event if event["event"] else None
        except Exception as e:
            self.logger.warning(f"Finnhub parse error: {e}")
            return None

    def _country_to_currency(self, country: str) -> str:
        """Map country code to currency code."""
        mapping = {
            "US": "USD", "EU": "EUR", "GB": "GBP", "JP": "JPY",
            "AU": "AUD", "CA": "CAD", "NZ": "NZD", "CH": "CHF",
            "CN": "CNY", "IN": "INR",
        }
        return mapping.get(country.upper(), country.upper())

    async def fetch_this_week(self) -> List[Dict]:
        return await self.fetch_economic_calendar()

    async def fetch_single_day(self, date: str) -> List[Dict]:
        return await self.fetch_economic_calendar(from_date=date, to_date=date)
