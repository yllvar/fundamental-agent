"""
System Health Checks
Single function that reports status of all data sources and agents
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_monitoring.data_collector import EconomicDataCollector
from config.forex_config import FOREX_PAIRS
from memory.analysis_cache import stats as cache_stats


async def check_health() -> Dict[str, Any]:
    """Return status of all data sources and agents"""
    logger = logging.getLogger(__name__)
    checks = {}

    checks["timestamp"] = datetime.now().isoformat()

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    checks["deepseek_api"] = {
        "status": "ok" if api_key else "missing",
        "configured": bool(api_key),
    }

    tg_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    tg_chat = os.environ.get("TELEGRAM_CHAT_ID", "")
    checks["telegram"] = {
        "status": "ok" if (tg_token and tg_chat) else "missing",
        "bot_configured": bool(tg_token),
        "chat_configured": bool(tg_chat),
    }

    checks["forex_config"] = {
        "status": "ok",
        "pairs_configured": len(FOREX_PAIRS),
    }

    cache_info = cache_stats()
    checks["cache"] = {
        "status": "ok",
        "entries": cache_info.get("entries", 0),
        "size_bytes": cache_info.get("size_bytes", 0),
    }

    try:
        collector = EconomicDataCollector()
        eurusd = collector.collect_yahoo_finance_data("EURUSD=X")
        checks["yahoo_finance"] = {
            "status": "ok" if eurusd else "error",
            "test_pair": "EUR/USD",
            "test_price": eurusd.current_price if eurusd else None,
        }
    except Exception as e:
        checks["yahoo_finance"] = {
            "status": "error",
            "error": str(e),
        }

    checks["all_ok"] = all(
        v.get("status") == "ok"
        for k, v in checks.items()
        if isinstance(v, dict) and "status" in v
    )

    return checks
