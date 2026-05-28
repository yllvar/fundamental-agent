"""
Notification templates for market open briefings and economic alerts
Zero LLM tokens — pure Telegram HTML formatting
"""

from datetime import datetime
from typing import Dict, List, Optional, Any


def format_session_briefing(
    session_name: str,
    session_config: Dict,
    pairs_data: Dict[str, Dict],
    prev_close_data: Optional[Dict[str, float]] = None,
) -> str:
    """Format a market session open briefing"""
    emoji = session_config.get("emoji", "")
    label = session_config.get("name", session_name.title())
    now = datetime.utcnow().strftime("%H:%M UTC")

    lines = [
        f"{emoji} <b>Market Open — {label}</b>",
        f"🕐 {now}\n",
    ]

    for symbol in session_config.get("pairs", []):
        data = pairs_data.get(symbol)
        if not data:
            continue

        name = data.get("name", symbol)
        price = data.get("current_price", 0)
        pips = data.get("change_pips", 0)
        pct = data.get("change_percent", 0)
        atr = data.get("atr", None)

        arrow = "🟢" if pips > 0 else ("🔴" if pips < 0 else "⚪")

        line = f"{arrow} <b>{name}</b>: {price:.5f}  ({pips:+.1f}p / {pct:+.2f}%)"
        if atr:
            line += f"  ATR {atr:.1f}p"

        if prev_close_data and symbol in prev_close_data:
            prev = prev_close_data[symbol]
            vs_prev = (price - prev) / (data.get("pip_value", 0.0001)) if data.get("pip_value") else 0
            line += f"\n   └ from previous session: {vs_prev:+.1f}p"

        lines.append(line)

    lines.append(f"\n#forex #{session_name}_session")
    return "\n".join(lines)


def format_economic_event_alert(
    event: Dict[str, Any],
    affected_pairs: List[str],
    pair_snapshot: Optional[Dict[str, Dict]] = None,
) -> str:
    """Format an economic event alert"""
    name = event.get("event", event.get("name", "Unknown"))
    currency = event.get("currency", "")
    impact = event.get("impact", 0)
    dt_str = event.get("datetime", event.get("date", ""))
    forecast = event.get("forecast", "—")
    previous = event.get("previous", "—")

    stars = "⭐" * impact
    impact_labels = {3: "HIGH", 2: "MEDIUM", 1: "LOW"}
    impact_label = impact_labels.get(impact, "UNKNOWN")

    lines = [
        f"⚠️ <b>Economic Event Alert</b>",
        f"{stars} <b>{name}</b> ({currency})",
        f"Impact: <b>{impact_label}</b>",
        f"Time: {dt_str}\n",
        f"Forecast: <code>{forecast}</code> | Previous: <code>{previous}</code>",
    ]

    if affected_pairs:
        lines.append(f"\nAffected: {', '.join(affected_pairs)}")

    if pair_snapshot:
        lines.append("")
        for sym, data in pair_snapshot.items():
            pips = data.get("change_pips", 0)
            lines.append(f"   {data.get('name', sym)}: {data.get('current_price', 0):.5f} ({pips:+.1f}p)")

    lines.append(f"\n⏱ Alert issued: {datetime.utcnow().strftime('%H:%M UTC')}")
    lines.append("#economic_calendar #forex")
    return "\n".join(lines)


def format_health_briefing(health: Dict[str, Any]) -> str:
    """Format health check for Telegram"""
    status_emoji = "🟢" if health.get("all_ok") else "🔴"
    return (
        f"{status_emoji} <b>System Health</b>\n"
        f"DeepSeek: {health['deepseek_api']['status']} | "
        f"Yahoo: {health['yahoo_finance']['status']} | "
        f"Cache: {health['cache']['entries']} entries"
    )
