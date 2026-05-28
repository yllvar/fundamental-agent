"""
Market Open Service
One-shot functions: fetch session snapshot, format briefing, send
"""

import logging
from datetime import datetime
from typing import Dict, Optional

from data_monitoring.data_collector import EconomicDataCollector
from config.forex_config import MARKET_SESSIONS, get_previous_session

logger = logging.getLogger(__name__)


def _get_pip_value(symbol: str) -> float:
    """Get pip value for a symbol"""
    from config.forex_config import FOREX_PAIRS
    pair = FOREX_PAIRS.get(symbol, {})
    return pair.get("pip", 0.0001)


def get_session_snapshot(session_name: str) -> Dict[str, Dict]:
    """Fetch current price data for session-relevant pairs"""
    session = MARKET_SESSIONS.get(session_name)
    if not session:
        logger.warning(f"Unknown session: {session_name}")
        return {}

    collector = EconomicDataCollector()
    result = {}

    for symbol in session.get("pairs", []):
        try:
            data = collector.collect_forex_data(symbol)
            if data:
                hist = collector.get_historical_data(symbol, "1mo")
                atr = None
                if not hist.empty and len(hist) >= 15:
                    high, low, close = hist["High"], hist["Low"], hist["Close"]
                    tr = (high - low).combine(
                        (high - close.shift()).abs(), max
                    ).combine(
                        (low - close.shift()).abs(), max
                    )
                    atr = round(float(tr.rolling(14).mean().iloc[-1]) / _get_pip_value(symbol), 1)

                result[symbol] = {
                    **data,
                    "atr": atr,
                    "pip_value": _get_pip_value(symbol),
                }
        except Exception as e:
            logger.warning(f"Failed to fetch {symbol} for {session_name}: {e}")

    return result


def get_previous_session_close(prev_session_name: str) -> Dict[str, float]:
    """Fetch close prices from the previous session's pairs"""
    prev_session = MARKET_SESSIONS.get(prev_session_name)
    if not prev_session:
        return {}

    collector = EconomicDataCollector()
    closes = {}

    for symbol in prev_session.get("pairs", []):
        try:
            hist = collector.get_historical_data(symbol, "5d")
            if not hist.empty and len(hist) >= 2:
                closes[symbol] = float(hist["Close"].iloc[-2])
        except Exception:
            continue

    return closes


async def handle_market_open(tg, session_name: str, session_config: Dict):
    """Fetch data, build briefing, and send via Telegram"""
    from services.notification_templates import format_session_briefing

    logger.info(f"🌅 {session_name.title()} session opening — fetching data...")

    prev_name = get_previous_session(session_name)
    prev_close = get_previous_session_close(prev_name)
    snapshot = get_session_snapshot(session_name)

    if not snapshot:
        logger.warning(f"No data for {session_name} — skipping briefing")
        return

    briefing = format_session_briefing(session_name, session_config, snapshot, prev_close)
    await tg.send_message(briefing)
    logger.info(f"✅ {session_name.title()} briefing sent ({len(snapshot)} pairs)")
