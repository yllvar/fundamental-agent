"""
Forex Report Generator
Lightweight templates that convert forex data → Telegram HTML
Zero LLM tokens — pure string formatting
"""

from datetime import datetime
from typing import Dict, List, Optional


def generate_snapshot_report(forex_data: Dict[str, Dict]) -> str:
    """Generate a snapshot report of multiple forex pairs"""
    if not forex_data:
        return "<b>No forex data available.</b>"

    lines = [f"<b>Forex Market Snapshot</b>\n"]
    lines.append(f"Updated: {datetime.now().strftime('%H:%M UTC')}\n")

    for symbol, data in sorted(forex_data.items(), key=lambda x: abs(x[1].get('change_pips', 0)), reverse=True):
        name = data.get('name', symbol)
        price = data.get('current_price', 0)
        pips = data.get('change_pips', 0)
        pct = data.get('change_percent', 0)
        arrow = "🟢" if pips > 0 else ("🔴" if pips < 0 else "⚪")
        lines.append(f"{arrow} <b>{name}</b>: {price:.5f}")
        lines.append(f"   {pips:+.1f} pips ({pct:+.2f}%)")

    return "\n".join(lines)


def generate_event_alert(event: Dict, pairs: List[str]) -> str:
    """Generate an alert for an upcoming economic event"""
    name = event.get('event', event.get('name', 'Unknown'))
    currency = event.get('currency', '')
    impact = event.get('impact', 0)
    dt_str = event.get('datetime', event.get('date', ''))
    forecast = event.get('forecast', '?')
    previous = event.get('previous', '?')

    stars = "⭐" * impact
    lines = [
        f"<b>Economic Event Alert</b>\n",
        f"{stars} <b>{name}</b> ({currency})",
        f"Time: {dt_str}",
        f"Forecast: {forecast} | Previous: {previous}",
    ]

    if pairs:
        lines.append(f"\nAffected pairs: {', '.join(pairs)}")

    lines.append("\n#forex #economic_calendar")
    return "\n".join(lines)


def generate_pips_movement_alert(symbol: str, name: str, price: float, pips: float, pct: float) -> str:
    """Generate an alert for a significant pips movement"""
    direction = "surged" if pips > 0 else ("dropped" if pips < 0 else "flat")
    arrow = "🟢" if pips > 0 else ("🔴" if pips < 0 else "⚪")

    return (
        f"{arrow} <b>{name}</b> {direction} <b>{abs(pips):.1f} pips</b> ({pct:+.2f}%)\n"
        f"Price: {price:.5f}\n"
        f"#forex #{symbol.split('=')[0] if '=' in symbol else symbol}"
    )


def generate_summary_report(data: Dict) -> str:
    """Generate a brief forex summary from analysis data"""
    analysis = data.get('analysis', data)
    pairs = data.get('pairs', [])
    intent = data.get('intent', 'outlook')

    if intent == "outlook":
        direction = analysis.get('direction', 'neutral').upper()
        confidence = analysis.get('confidence', 0)
        reasoning = analysis.get('reasoning', '')
        return (
            f"<b>Outlook — {', '.join(pairs)}</b>\n"
            f"Direction: <b>{direction}</b>\n"
            f"Confidence: {confidence * 100:.0f}%\n\n"
            f"{reasoning}"
        )

    return analysis.get('analysis_text', '')
