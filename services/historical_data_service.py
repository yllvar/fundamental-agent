"""
Historical Data Service
Downloads and caches OHLCV parquet files from Hugging Face on demand.
Provides statistics for enriching market open briefings.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

import pandas as pd
import requests

from config.forex_config import FOREX_PAIRS

logger = logging.getLogger(__name__)

HF_BASE = "https://huggingface.co/datasets/Yllvar/fx-historical-data/resolve/main"
CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "historical"

SYMBOL_MAP = {
    "EURUSD=X": "EURUSD", "GBPUSD=X": "GBPUSD", "USDJPY=X": "USDJPY",
    "AUDUSD=X": "AUDUSD", "USDCAD=X": "USDCAD", "NZDUSD=X": "NZDUSD",
    "USDCHF=X": "USDCHF", "EURJPY=X": "EURJPY", "GBPJPY=X": "GBPJPY",
    "EURGBP=X": "EURGBP",
}

TF_MAP = {
    "1m": "M1", "5m": "M5", "15m": "M15", "30m": "M30",
    "1h": "H1", "4h": "H4", "1d": "D1",
}

WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _yahoo_to_hf(symbol: str) -> Optional[str]:
    return SYMBOL_MAP.get(symbol)


def _tf_to_hf(timeframe: str) -> Optional[str]:
    return TF_MAP.get(timeframe)


def _pip_value(symbol: str) -> float:
    return FOREX_PAIRS.get(symbol, {}).get("pip", 0.0001)


def _ensure_download(symbol: str, timeframe: str = "1d") -> Optional[Path]:
    hf_sym = _yahoo_to_hf(symbol)
    hf_tf = _tf_to_hf(timeframe)
    if not hf_sym or not hf_tf:
        logger.warning(f"No HF mapping for {symbol} / {timeframe}")
        return None

    cache_path = CACHE_DIR / hf_sym / f"{hf_sym}_{hf_tf}.parquet"
    if cache_path.exists():
        return cache_path

    url = f"{HF_BASE}/{hf_sym}/{hf_sym}_{hf_tf}.parquet"
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        logger.info(f"Downloading {url}...")
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        cache_path.write_bytes(resp.content)
        logger.info(f"Cached to {cache_path} ({len(resp.content) / 1024:.0f} KB)")
        return cache_path
    except Exception as e:
        logger.warning(f"Failed to download {url}: {e}")
        return None


def get_historical_df(symbol: str, timeframe: str = "1d") -> Optional[pd.DataFrame]:
    path = _ensure_download(symbol, timeframe)
    if not path:
        return None
    try:
        df = pd.read_parquet(path)
        if "Time" in df.columns:
            df["Time"] = pd.to_datetime(df["Time"])
            df = df.sort_values("Time")
        return df
    except Exception as e:
        logger.warning(f"Failed to read {path}: {e}")
        return None


def get_percentile_rank(symbol: str, current_price: float, timeframe: str = "1d") -> Optional[int]:
    df = get_historical_df(symbol, timeframe)
    if df is None or df.empty or "Close" not in df.columns:
        return None
    try:
        rank = (df["Close"] < current_price).mean() * 100
        return int(round(rank))
    except Exception as e:
        logger.warning(f"Percentile calc failed for {symbol}: {e}")
        return None


def get_day_of_week_bias(symbol: str, timeframe: str = "1d") -> Optional[Dict[str, float]]:
    df = get_historical_df(symbol, timeframe)
    if df is None or df.empty:
        return None
    try:
        if "Time" not in df.columns or "Open" not in df.columns or "Close" not in df.columns:
            return None
        daily = df.copy()
        daily["weekday"] = daily["Time"].dt.weekday
        daily["return_pct"] = (daily["Close"] - daily["Open"]) / daily["Open"] * 100
        bias = daily.groupby("weekday")["return_pct"].mean()
        return {WEEKDAY_NAMES[d]: round(bias.get(d, 0), 2) for d in range(5)}
    except Exception as e:
        logger.warning(f"DOW bias calc failed for {symbol}: {e}")
        return None


def get_range_stats(symbol: str, timeframe: str = "1d") -> Optional[Dict[str, float]]:
    df = get_historical_df(symbol, timeframe)
    if df is None or df.empty:
        return None
    try:
        pip = _pip_value(symbol)
        ranges = (df["High"] - df["Low"]) / pip
        return {
            "avg_pips": round(float(ranges.mean()), 1),
            "median_pips": round(float(ranges.median()), 1),
            "p95_pips": round(float(ranges.quantile(0.95)), 1),
        }
    except Exception as e:
        logger.warning(f"Range stats failed for {symbol}: {e}")
        return None
