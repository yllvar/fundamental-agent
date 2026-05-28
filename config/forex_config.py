"""Forex pair configurations and event mappings"""

FOREX_PAIRS = {
    "EURUSD=X": {"name": "EUR/USD", "pip": 0.0001, "digits": 5, "spread_avg": 1.2, "session": "london_ny", "central_bank": "ECB"},
    "GBPUSD=X": {"name": "GBP/USD", "pip": 0.0001, "digits": 5, "spread_avg": 1.5, "session": "london", "central_bank": "BOE"},
    "USDJPY=X": {"name": "USD/JPY", "pip": 0.01, "digits": 3, "spread_avg": 1.0, "session": "tokyo_london", "central_bank": "BOJ"},
    "AUDUSD=X": {"name": "AUD/USD", "pip": 0.0001, "digits": 5, "spread_avg": 1.8, "session": "sydney", "central_bank": "RBA"},
    "USDCAD=X": {"name": "USD/CAD", "pip": 0.0001, "digits": 5, "spread_avg": 1.6, "session": "ny", "central_bank": "BOC"},
    "NZDUSD=X": {"name": "NZD/USD", "pip": 0.0001, "digits": 5, "spread_avg": 2.0, "session": "sydney", "central_bank": "RBNZ"},
    "USDCHF=X": {"name": "USD/CHF", "pip": 0.0001, "digits": 5, "spread_avg": 1.3, "session": "london", "central_bank": "SNB"},
    "EURJPY=X": {"name": "EUR/JPY", "pip": 0.01, "digits": 3, "spread_avg": 1.8, "session": "tokyo_london", "central_bank": "ECB"},
    "GBPJPY=X": {"name": "GBP/JPY", "pip": 0.01, "digits": 3, "spread_avg": 2.5, "session": "london", "central_bank": "BOE"},
    "EURGBP=X": {"name": "EUR/GBP", "pip": 0.0001, "digits": 5, "spread_avg": 1.0, "session": "london", "central_bank": "ECB"},
}

MAJOR_PAIRS = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "USDCHF=X"]
CROSS_PAIRS = ["EURJPY=X", "GBPJPY=X", "EURGBP=X"]

EVENT_TO_CURRENCY = {
    "Non-Farm Employment Change": "USD",
    "Unemployment Rate": "USD",
    "CPI": "USD",
    "Core CPI": "USD",
    "GDP": "USD",
    "Retail Sales": "USD",
    "Industrial Production": "USD",
    "Consumer Confidence": "USD",
    "ISM Manufacturing PMI": "USD",
    "ISM Services PMI": "USD",
    "Federal Funds Rate": "USD",
    "FOMC Statement": "USD",
    "ECB Interest Rate Decision": "EUR",
    "ECB Press Conference": "EUR",
    "Eurozone CPI": "EUR",
    "Eurozone GDP": "EUR",
    "Eurozone PMI": "EUR",
    "BOE Interest Rate Decision": "GBP",
    "BOE Monetary Policy Report": "GBP",
    "UK CPI": "GBP",
    "UK GDP": "GBP",
    "BOJ Interest Rate Decision": "JPY",
    "BOJ Press Conference": "JPY",
    "Japan CPI": "JPY",
    "RBA Interest Rate Decision": "AUD",
    "Australia CPI": "AUD",
    "RBNZ Interest Rate Decision": "NZD",
    "BOC Interest Rate Decision": "CAD",
    "Canada CPI": "CAD",
    "SNB Interest Rate Decision": "CHF",
    "NFP": "USD",
}

CENTRAL_BANK_RATES = {
    "ECB": {"name": "European Central Bank", "currency": "EUR", "current_rate": None},
    "BOE": {"name": "Bank of England", "currency": "GBP", "current_rate": None},
    "BOJ": {"name": "Bank of Japan", "currency": "JPY", "current_rate": None},
    "RBA": {"name": "Reserve Bank of Australia", "currency": "AUD", "current_rate": None},
    "BOC": {"name": "Bank of Canada", "currency": "CAD", "current_rate": None},
    "RBNZ": {"name": "Reserve Bank of New Zealand", "currency": "NZD", "current_rate": None},
    "SNB": {"name": "Swiss National Bank", "currency": "CHF", "current_rate": None},
    "FED": {"name": "Federal Reserve", "currency": "USD", "current_rate": None},
}

# Event impact thresholds (pips move expected)
EVENT_IMPACT = {
    3: {"label": "high", "expected_pips": "20-50+"},
    2: {"label": "medium", "expected_pips": "10-20"},
    1: {"label": "low", "expected_pips": "5-10"},
}

FOREX_SYMBOLS = list(FOREX_PAIRS.keys())

# Market session definitions — opening times in UTC, relevant pairs
MARKET_SESSIONS = {
    "tokyo": {
        "open_utc": "00:00",
        "close_utc": "09:00",
        "pairs": ["USDJPY=X", "EURJPY=X", "GBPJPY=X", "AUDUSD=X", "NZDUSD=X"],
        "name": "Tokyo / Asia-Pacific",
        "emoji": "🌏",
    },
    "london": {
        "open_utc": "08:00",
        "close_utc": "17:00",
        "pairs": ["EURUSD=X", "GBPUSD=X", "EURGBP=X", "USDCHF=X", "EURJPY=X", "GBPJPY=X"],
        "name": "London / European",
        "emoji": "🇪🇺",
    },
    "new_york": {
        "open_utc": "13:00",
        "close_utc": "22:00",
        "pairs": ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCAD=X", "USDCHF=X", "AUDUSD=X", "NZDUSD=X"],
        "name": "New York / Americas",
        "emoji": "🗽",
    },
}

SESSION_ORDER = ["tokyo", "london", "new_york"]

def get_previous_session(session_name: str) -> str:
    """Get the session that precedes the given session."""
    idx = SESSION_ORDER.index(session_name)
    return SESSION_ORDER[idx - 1] if idx > 0 else SESSION_ORDER[-1]
