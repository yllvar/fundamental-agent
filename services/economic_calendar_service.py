"""
Economic Calendar Service
Checks for upcoming high-impact events and sends alerts
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from config.forex_config import EVENT_TO_CURRENCY, FOREX_PAIRS
from data_monitoring.data_collector import EconomicDataCollector
from data_monitoring.forex_factory import ForexFactoryScraper

logger = logging.getLogger(__name__)

CURRENCY_TO_SYMBOLS: Optional[Dict[str, List[str]]] = None


def _build_currency_map():
    """Build currency → forex symbol lookup"""
    global CURRENCY_TO_SYMBOLS
    if CURRENCY_TO_SYMBOLS is not None:
        return
    CURRENCY_TO_SYMBOLS = {}
    for sym, config in FOREX_PAIRS.items():
        name = config.get("name", "")
        for currency in ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "NZD", "CHF"]:
            if currency in name and "X" not in name.split("/")[0]:
                pass
        base, quote = name.split("/") if "/" in name else ("", "")
        for c in [base, quote]:
            if c not in CURRENCY_TO_SYMBOLS:
                CURRENCY_TO_SYMBOLS[c] = []
            CURRENCY_TO_SYMBOLS[c].append(sym)


def _get_affected_pairs(event_name: str, currency: str) -> List[str]:
    """Get forex pairs affected by an economic event"""
    _build_currency_map()
    pairs = CURRENCY_TO_SYMBOLS.get(currency, [])

    event_lower = event_name.lower()
    for known_event, ev_currency in EVENT_TO_CURRENCY.items():
        if known_event.lower() in event_lower or event_lower in known_event.lower():
            return CURRENCY_TO_SYMBOLS.get(ev_currency, pairs)

    return pairs


def _get_pair_snapshot(symbols: List[str]) -> Dict[str, Dict]:
    """Fetch current price snapshot for affected pairs"""
    collector = EconomicDataCollector()
    snapshot = {}
    for sym in symbols:
        try:
            data = collector.collect_forex_data(sym)
            if data:
                snapshot[sym] = data
        except Exception:
            continue
    return snapshot


def _is_within_48h(event: Dict) -> bool:
    """Check if event is within the next 48 hours"""
    dt_str = event.get("datetime") or event.get("date")
    if not dt_str:
        return False
    try:
        event_dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        now = datetime.now(event_dt.tzinfo) if event_dt.tzinfo else datetime.now()
        return 0 <= (event_dt - now).total_seconds() <= 172800
    except (ValueError, TypeError):
        return False


async def check_upcoming_events(tg) -> int:
    """Fetch calendar, filter for high-impact events within 48h, send alerts"""
    logger.info("Checking upcoming economic events...")

    try:
        scraper = ForexFactoryScraper()
        events = await scraper.fetch_this_week()
    except Exception as e:
        logger.warning(f"Forex Factory fetch failed: {e} — trying range fetch")
        scraper = ForexFactoryScraper()
        today = datetime.now().strftime("%Y-%m-%d")
        two_days = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        events = await scraper.fetch_range(today, two_days)

    if not events:
        logger.info("No upcoming events found")
        return 0

    from services.notification_templates import format_economic_event_alert

    count = 0
    for event in events:
        impact = event.get("impact", 0)
        if impact < 3:
            continue
        if not _is_within_48h(event):
            continue

        currency = event.get("currency", "")
        event_name = event.get("event", event.get("name", "Unknown"))
        affected = _get_affected_pairs(event_name, currency)
        snapshot = _get_pair_snapshot(affected) if affected else {}

        alert = format_economic_event_alert(event, affected, snapshot)
        await tg.send_message(alert)
        count += 1
        logger.info(f"⚠️ Event alert sent: {event_name} ({currency})")
        await asyncio.sleep(1)

    if count == 0:
        logger.info("No high-impact events within 48h")

    return count
