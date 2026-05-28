"""
Forex Factory calendar scraper
Fetches upcoming economic events with impact ratings
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup


CACHE_DIR = Path(__file__).resolve().parent.parent / "memory" / "cache" / "forex_factory"
CACHE_TTL_SECONDS = 600  # 10 minutes
REQUEST_INTERVAL = 60  # seconds between requests


class ForexFactoryScraper:
    """Scrapes Forex Factory economic calendar"""

    BASE_URL = "https://www.forexfactory.com"

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.last_request_time = None
        os.makedirs(CACHE_DIR, exist_ok=True)

    async def fetch_calendar(self, date_range: str = "week") -> List[Dict]:
        """Fetch economic calendar for the given range.

        date_range: 'week' (this week), 'next_week', or date string '2026-06-05'
        """
        url = f"{self.BASE_URL}/calendar"
        if date_range == "next_week":
            url += "?range=nextWeek"
        elif date_range != "week":
            url += f"?date={date_range}"

        html = await self._fetch(url)
        if not html:
            return []

        return self._parse_calendar(html)

    async def fetch_this_week(self) -> List[Dict]:
        return await self.fetch_calendar("week")

    async def fetch_next_week(self) -> List[Dict]:
        return await self.fetch_calendar("next_week")

    async def fetch_range(self, from_date: str, to_date: str) -> List[Dict]:
        """Fetch events across a date range."""
        all_events = []
        current = datetime.strptime(from_date, "%Y-%m-%d")
        end = datetime.strptime(to_date, "%Y-%m-%d")
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            events = await self.fetch_calendar(date_str)
            all_events.extend(events)
            current += timedelta(days=7)
        return all_events

    async def get_historical_event(self, event_url: str) -> Optional[Dict]:
        """Fetch historical data for a specific event."""
        if not event_url.startswith("http"):
            event_url = f"{self.BASE_URL}{event_url}"

        html = await self._fetch(event_url)
        if not html:
            return None

        return self._parse_event_history(html)

    async def _fetch(self, url: str) -> Optional[str]:
        """Fetch HTML with rate limiting and caching."""
        cache_key = hashlib.md5(url.encode()).hexdigest()
        cache_path = CACHE_DIR / f"{cache_key}.json"

        cached = self._load_cache(cache_path)
        if cached:
            return cached

        # Rate limiting
        now = datetime.now()
        if self.last_request_time:
            elapsed = (now - self.last_request_time).total_seconds()
            if elapsed < REQUEST_INTERVAL:
                wait = REQUEST_INTERVAL - elapsed
                self.logger.info(f"Rate limit: waiting {wait:.0f}s")
                import asyncio
                await asyncio.sleep(wait)

        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        self.logger.error(f"HTTP {response.status} for {url}")
                        return None
                    html = await response.text()

            self.last_request_time = datetime.now()
            self._save_cache(cache_path, html)
            return html

        except Exception as e:
            self.logger.error(f"Fetch failed: {e}")
            return None

    def _parse_calendar(self, html: str) -> List[Dict]:
        """Parse Forex Factory calendar HTML into event dicts."""
        events = []
        soup = BeautifulSoup(html, "html.parser")

        calendar_rows = soup.select("tr.calendar__row")
        if not calendar_rows:
            calendar_rows = soup.select("tr[data-event-id]")

        current_date = None
        current_time = None

        for row in calendar_rows:
            date_cell = row.select_one("td.calendar__date")
            if date_cell:
                date_text = date_cell.get_text(strip=True)
                if date_text:
                    current_date = self._parse_ff_date(date_text)

            time_cell = row.select_one("td.calendar__time")
            if time_cell:
                time_text = time_cell.get_text(strip=True)
                current_time = time_text if time_text and time_text != "All Day" else None

            currency_cell = row.select_one("td.calendar__currency")
            event_cell = row.select_one("td.calendar__event")
            impact_cell = row.select_one("td.calendar__impact")
            actual_cell = row.select_one("td.calendar__actual")
            forecast_cell = row.select_one("td.calendar__forecast")
            previous_cell = row.select_one("td.calendar__previous")

            if not currency_cell or not event_cell:
                continue

            currency = currency_cell.get_text(strip=True)
            event_name = event_cell.get_text(strip=True)
            if not currency or not event_name:
                continue

            impact = 0
            if impact_cell:
                impact_spans = impact_cell.select("span")
                impact = len(impact_spans)

            event = {
                "source": "forex_factory",
                "currency": currency,
                "event": event_name,
                "impact": impact,
                "date": current_date,
                "time": current_time,
                "actual": self._parse_value(actual_cell),
                "forecast": self._parse_value(forecast_cell),
                "previous": self._parse_value(previous_cell),
            }

            event_link = event_cell.select_one("a")
            if event_link and event_link.get("href"):
                event["url"] = event_link["href"]

            events.append(event)

        return events

    def _parse_event_history(self, html: str) -> Optional[Dict]:
        """Parse historical event data page."""
        soup = BeautifulSoup(html, "html.parser")
        result = {"title": None, "history": []}

        title = soup.select_one("h1")
        if title:
            result["title"] = title.get_text(strip=True)

        history_rows = soup.select("tr.calendar__history-row")
        for row in history_rows:
            cells = row.select("td")
            if len(cells) >= 4:
                result["history"].append({
                    "date": cells[0].get_text(strip=True) if cells[0] else None,
                    "actual": cells[1].get_text(strip=True) if cells[1] else None,
                    "forecast": cells[2].get_text(strip=True) if cells[2] else None,
                    "previous": cells[3].get_text(strip=True) if cells[3] else None,
                })

        return result if result["title"] or result["history"] else None

    def _parse_ff_date(self, text: str) -> Optional[str]:
        """Parse Forex Factory date format like 'Jun5' or 'Jun05'."""
        import re
        match = re.match(r"([A-Za-z]+)(\d+)", text.strip())
        if match:
            month = match.group(1)
            day = match.group(2).zfill(2)
            year = datetime.now().year
            try:
                dt = datetime.strptime(f"{month}{day}{year}", "%b%d%Y")
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
        return None

    def _parse_value(self, cell) -> Optional[str]:
        """Extract text from a table cell."""
        if cell:
            text = cell.get_text(strip=True)
            return text if text and text != "-" else None
        return None

    def _load_cache(self, path: Path) -> Optional[str]:
        """Load cached HTML if not expired."""
        if not path.exists():
            return None
        try:
            with open(path) as f:
                data = json.load(f)
            age = (datetime.now() - datetime.fromisoformat(data["cached_at"])).total_seconds()
            if age < CACHE_TTL_SECONDS:
                return data["html"]
        except (json.JSONDecodeError, KeyError):
            pass
        return None

    def _save_cache(self, path: Path, html: str):
        """Save HTML to cache."""
        try:
            with open(path, "w") as f:
                json.dump({"cached_at": datetime.now().isoformat(), "html": html}, f)
        except Exception as e:
            self.logger.warning(f"Cache save failed: {e}")
