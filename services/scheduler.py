"""
Scheduler — event-driven loop checking time-based conditions every 30s
No continuous yfinance polling
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Set

from config.forex_config import MARKET_SESSIONS, SESSION_ORDER
from services.market_open_service import handle_market_open
from services.economic_calendar_service import check_upcoming_events
from system.health_checks import check_health as run_health_check
from services.notification_templates import format_health_briefing

logger = logging.getLogger(__name__)


def _parse_utc_time(time_str: str) -> int:
    """Parse 'HH:MM' UTC string to total minutes"""
    parts = time_str.split(":")
    return int(parts[0]) * 60 + int(parts[1])


def _current_utc_minutes() -> int:
    """Current UTC time in minutes since midnight"""
    now = datetime.utcnow()
    return now.hour * 60 + now.minute


def _check_session_open(session_name: str) -> bool:
    """Check if a session opened in the last 30 seconds"""
    session = MARKET_SESSIONS.get(session_name)
    if not session:
        return False
    open_time = _parse_utc_time(session["open_utc"])
    now = _current_utc_minutes()
    return now == open_time


async def run_scheduler(tg) -> None:
    """
    Main scheduler — checks conditions every 30 seconds.
    Fires: market open briefings, economic calendar checks, health checks.
    """
    logger.info("🚀 Scheduler started — checking every 30s")

    last_calendar_check: datetime = datetime.min
    last_health_check: datetime = datetime.min
    last_notified: Set[str] = set()

    CALENDAR_INTERVAL = timedelta(hours=6)
    HEALTH_INTERVAL = timedelta(hours=1)

    while True:
        now = datetime.now()

        # 1. Check each market session for opening time
        for session_name in SESSION_ORDER:
            if _check_session_open(session_name) and session_name not in last_notified:
                session_config = MARKET_SESSIONS[session_name]
                logger.info(f"⏰ {session_name.title()} session opening")
                await handle_market_open(tg, session_name, session_config)
                last_notified.add(session_name)

        # Reset notification flags at midnight UTC
        if now.hour == 0 and now.minute == 0:
            last_notified.clear()

        # 2. Economic calendar check (every 6h)
        if (now - last_calendar_check) >= CALENDAR_INTERVAL:
            logger.info("📅 Checking economic calendar...")
            await check_upcoming_events(tg)
            last_calendar_check = now

        # 3. Health check every hour
        if (now - last_health_check) >= HEALTH_INTERVAL:
            health = await run_health_check()
            logger.info(f"🩺 Health: all_ok={health.get('all_ok')}")
            if tg:
                await tg.send_message(format_health_briefing(health))
            last_health_check = now

        await asyncio.sleep(30)
