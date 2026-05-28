"""
Analysis Cache
File-based JSON cache with TTL — not Redis, not SQLite
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")


def _ensure_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def _hash_key(pair: str, intent: str, granularity: str) -> str:
    raw = f"{pair}:{intent}:{granularity}"
    return hashlib.md5(raw.encode()).hexdigest()


def _cache_path(key: str) -> str:
    _ensure_dir()
    return os.path.join(CACHE_DIR, f"{key}.json")


def get(pair: str, intent: str) -> Optional[Dict[str, Any]]:
    """Get cached analysis — try minute-level first, fall back to day-level"""
    now = datetime.now()
    hour_key = _hash_key(pair, intent, now.strftime("%Y%m%d_%H"))
    day_key = _hash_key(pair, intent, now.strftime("%Y%m%d"))

    for key, ttl_minutes in [(hour_key, 60), (day_key, 1440)]:
        path = _cache_path(key)
        try:
            if os.path.exists(path):
                mtime = datetime.fromtimestamp(os.path.getmtime(path))
                if (now - mtime) < timedelta(minutes=ttl_minutes):
                    with open(path, "r") as f:
                        return json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

    return None


def set(pair: str, intent: str, data: Dict[str, Any]):
    """Cache analysis result"""
    now = datetime.now()
    key = _hash_key(pair, intent, now.strftime("%Y%m%d_%H"))
    path = _cache_path(key)
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except OSError as e:
        logging.getLogger(__name__).warning(f"Cache write failed: {e}")


def clear(pair: Optional[str] = None, intent: Optional[str] = None):
    """Clear cache entries — all or filtered by pair/intent"""
    _ensure_dir()
    for fname in os.listdir(CACHE_DIR):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(CACHE_DIR, fname)
        try:
            os.remove(path)
        except OSError:
            continue


def stats() -> Dict[str, Any]:
    """Get cache statistics"""
    _ensure_dir()
    files = [f for f in os.listdir(CACHE_DIR) if f.endswith(".json")]
    total_bytes = sum(os.path.getsize(os.path.join(CACHE_DIR, f)) for f in files)
    return {
        "entries": len(files),
        "size_bytes": total_bytes,
        "cache_dir": CACHE_DIR,
    }
