"""
Response Formatter
Converts structured JSON output from DeepSeek into Telegram HTML messages
Zero LLM tokens — pure string manipulation
"""

from datetime import datetime
from typing import Dict, List, Optional, Any


def format_analysis_response(intent: str, analysis: Dict, pairs: List[str]) -> str:
    """Format analysis JSON into Telegram HTML"""
    formatters = {
        "outlook": _format_outlook,
        "event_analysis": _format_event_analysis,
        "risk_assessment": _format_risk_assessment,
        "comparison": _format_comparison,
        "what_changed": _format_what_changed,
        "confidence": _format_confidence,
        "historical": _format_historical,
    }

    formatter = formatters.get(intent, _format_outlook)
    return formatter(analysis, pairs)


def format_error_message(query: str, error: str) -> str:
    """Format error message for Telegram"""
    return (
        f"<b>Query Error</b>\n\n"
        f"Could not process: <code>{query[:100]}</code>\n"
        f"Reason: {error}\n\n"
        f"Try rephrasing or use a more specific question."
    )


def format_help_message() -> str:
    """Format help message with example queries"""
    return (
        "<b>Forex Assistant — Help</b>\n\n"
        "Try these queries:\n"
        "• <i>EUR/USD outlook this week</i>\n"
        "• <i>What moved GBP/USD today?</i>\n"
        "• <i>Compare EUR/USD and GBP/USD</i>\n"
        "• <i>Risk assessment for USD/JPY</i>\n"
        "• <i>NFP impact on dollar pairs</i>\n"
        "• <i>Historical performance of USD this month</i>\n"
        "• <i>Trade confidence on forex pairs</i>"
    )


def _format_outlook(analysis: Dict, pairs: List[str]) -> str:
    direction = analysis.get('direction', 'neutral').upper()
    conf = analysis.get('confidence', 0)
    levels = analysis.get('key_levels', {})
    reasoning = analysis.get('reasoning', '')

    lines = [f"<b>Outlook — {', '.join(pairs)}</b>\n"]
    lines.append(f"Direction: <b>{direction}</b>")
    lines.append(f"Confidence: {conf * 100:.0f}%" if conf else "")
    if levels:
        lines.append(f"Support: {_fmt(levels.get('support'))} | Resistance: {_fmt(levels.get('resistance'))}")
    if reasoning:
        lines.append(f"\n{reasoning}")
    return "\n".join(l for l in lines if l)


def _format_event_analysis(analysis: Dict, pairs: List[str]) -> str:
    impact = analysis.get('event_impact', {})
    vol = analysis.get('expected_volatility', 'medium')

    lines = [f"<b>Event Impact — {', '.join(pairs)}</b>\n"]
    if isinstance(impact, dict):
        for pair, imp in impact.items():
            lines.append(f"{pair}: <b>{imp}</b>")
    lines.append(f"Volatility: {vol}")
    r = analysis.get('reasoning', '')
    if r:
        lines.append(f"\n{r}")
    return "\n".join(l for l in lines if l)


def _format_risk_assessment(analysis: Dict, pairs: List[str]) -> str:
    lines = [f"<b>Risk Assessment — {', '.join(pairs)}</b>\n"]
    lines.append(f"Risk: <b>{analysis.get('risk_level', 'medium').upper()}</b>")
    lines.append(f"ATR: {analysis.get('atr_pips', '?')} pips")
    lines.append(f"Suggested Stop: {analysis.get('suggested_stop_pips', '?')} pips")
    levels = analysis.get('key_levels', {})
    if levels:
        lines.append(f"Support: {_fmt(levels.get('support'))} | Resistance: {_fmt(levels.get('resistance'))}")
    note = analysis.get('volatility_note', '')
    if note:
        lines.append(f"\n{note}")
    return "\n".join(l for l in lines if l)


def _format_comparison(analysis: Dict, pairs: List[str]) -> str:
    lines = [f"<b>Pair Comparison</b>\n"]
    lines.append(f"Strongest: <b>{analysis.get('strongest', '?')}</b>")
    lines.append(f"Weakest: <b>{analysis.get('weakest', '?')}</b>")
    comp = analysis.get('comparison', {})
    if isinstance(comp, dict):
        for pair, bias in comp.items():
            lines.append(f"{pair}: {bias}")
    r = analysis.get('reasoning', '')
    if r:
        lines.append(f"\n{r}")
    db = analysis.get('dollar_bias', '')
    if db:
        lines.append(f"\nDollar bias: {db}")
    return "\n".join(l for l in lines if l)


def _format_what_changed(analysis: Dict, pairs: List[str]) -> str:
    lines = [f"<b>Market Movers</b>\n"]
    lines.append(f"Biggest mover: <b>{analysis.get('biggest_mover', '?')}</b>")
    lines.append(f"Move: {analysis.get('change_pips', '?')} pips")
    driver = analysis.get('driver', '')
    if driver:
        lines.append(f"\nDriver: {driver}")
    summary = analysis.get('summary', '')
    if summary:
        lines.append(f"\n{summary}")
    return "\n".join(l for l in lines if l)


def _format_confidence(analysis: Dict, pairs: List[str]) -> str:
    lines = [f"<b>Trade Confidence — {', '.join(pairs) if pairs else 'Forex'}</b>\n"]
    lines.append(f"Overall: <b>{analysis.get('overall_confidence', 0) * 100:.0f}%</b>")
    lines.append(f"Technical: {analysis.get('technical_score', 0) * 100:.0f}%")
    lines.append(f"Fundamental: {analysis.get('fundamental_score', 0) * 100:.0f}%")
    concerns = analysis.get('concerns', [])
    if concerns:
        lines.append(f"\nConcerns: {'; '.join(concerns[:3])}")
    fav = analysis.get('favorable_pairs', [])
    if fav:
        lines.append(f"Favorable: {', '.join(fav)}")
    return "\n".join(l for l in lines if l)


def _format_historical(analysis: Dict, pairs: List[str]) -> str:
    lines = [f"<b>Historical Performance</b>\n"]
    lines.append(f"Top: <b>{analysis.get('top_performer', '?')}</b>")
    lines.append(f"Worst: <b>{analysis.get('worst_performer', '?')}</b>")
    pattern = analysis.get('pattern', '')
    if pattern:
        lines.append(f"\nPattern: {pattern}")
    summary = analysis.get('summary', '')
    if summary:
        lines.append(f"\n{summary}")
    return "\n".join(l for l in lines if l)


def _fmt(val: Any) -> str:
    """Format a value for display"""
    if val is None:
        return "?"
    if isinstance(val, float):
        return f"{val:.5f}"
    return str(val)
