"""
Forex Query Router
Classifies intent and extracts entities from natural language forex queries
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agents.deepseek_provider import DeepSeekProvider

SUPPORTED_INTENTS = [
    "outlook",
    "event_analysis",
    "risk_assessment",
    "comparison",
    "what_changed",
    "confidence",
    "historical"
]

ALL_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD",
    "USD/CAD", "NZD/USD", "USD/CHF",
    "EUR/JPY", "GBP/JPY", "EUR/GBP"
]

INTENT_SYSTEM_PROMPT = """You are a forex intent classifier. Given a user query about forex/currencies, return JSON with:
  "intent": one of ["outlook", "event_analysis", "risk_assessment", "comparison", "what_changed", "confidence", "historical"]
  "pairs": list of detected currency pairs (use EUR/USD format), empty list if none
  "events": list of detected event types (e.g. "NFP", "CPI", "rate decision"), empty list if none
  "timeframe": one of ["1h", "4h", "1d", "1w", "1mo", "today", "this week", "this month"] or null
  "confidence": float 0-1

Intent definitions:
- outlook: asking for future direction or forecast
- event_analysis: asking about economic event impact
- risk_assessment: asking about risk, volatility, stop loss
- comparison: comparing two or more pairs
- what_changed: asking what moved or why
- confidence: asking about trade confidence or probability
- historical: asking about past performance or patterns

Respond with ONLY valid JSON, no other text."""


async def route_query(query: str, user_id: str, context: Optional[Dict] = None) -> Dict:
    """
    Classify intent and extract entities from a forex query.
    
    Returns:
        {"intent": "...", "pairs": [...], "events": [...], "timeframe": ..., "confidence": 0.0}
    """
    logger = logging.getLogger("forex_query_router")

    try:
        llm = DeepSeekProvider(model="deepseek-v4-flash", temperature=0.1, max_tokens=200)
        response = await llm.ainvoke(INTENT_SYSTEM_PROMPT, query)
        response = response.strip()

        if response.startswith("```"):
            response = response.split("\n", 1)[1] if "\n" in response else response
            response = response.rsplit("\n", 1)[0] if response.endswith("```") else response

        result = json.loads(response)

        if result.get("intent") not in SUPPORTED_INTENTS:
            result["intent"] = "outlook"

        pair_str_to_symbol = {
            "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "USDJPY=X",
            "AUD/USD": "AUDUSD=X", "USD/CAD": "USDCAD=X", "NZD/USD": "NZDUSD=X",
            "USD/CHF": "USDCHF=X", "EUR/JPY": "EURJPY=X", "GBP/JPY": "GBPJPY=X",
            "EUR/GBP": "EURGBP=X"
        }
        result["symbols"] = [pair_str_to_symbol.get(p) for p in result.get("pairs", []) if p in pair_str_to_symbol]

        return result

    except Exception as e:
        logger.error(f"Query routing failed: {e}")
        return {
            "intent": "outlook",
            "pairs": [],
            "symbols": [],
            "events": [],
            "timeframe": None,
            "confidence": 0.0,
            "error": str(e)
        }
