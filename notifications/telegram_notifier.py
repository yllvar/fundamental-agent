"""
Telegram Notification System
Sends event detection results to Telegram
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass

from enum import Enum


class AlertPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TelegramAlert:
    title: str
    message: str
    priority: AlertPriority
    symbol: str
    severity: float
    timestamp: datetime
    details: Optional[Dict] = None
    chart_url: Optional[str] = None


class TelegramNotifier:
    """Telegram notification sending class"""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self.logger = logging.getLogger(__name__)

        self.alert_settings = {
            "enabled": True,
            "min_severity": 0.3,
            "cooldown_minutes": 15,
            "max_alerts_per_hour": 20,
        }

        self.last_alerts = {}
        self.hourly_count = 0
        self.last_hour_reset = datetime.now().hour

        self.priority_emojis = {
            AlertPriority.LOW: "\U0001f7e2",
            AlertPriority.MEDIUM: "\U0001f7e1",
            AlertPriority.HIGH: "\U0001f7e0",
            AlertPriority.CRITICAL: "\U0001f534"
        }

        self.event_emojis = {
            "surge": "\U0001f4c8",
            "drop": "\U0001f4c9",
            "volatility": "\u26a1",
            "volume_spike": "\U0001f4ca",
            "technical_breakout": "\U0001f680",
            "sentiment_shift": "\U0001f4ad",
            "momentum_divergence": "\U0001f504",
            "sector_rotation": "\U0001f500",
            "market_regime_change": "\U0001f30a",
            "liquidity_crisis": "\U0001f4a7",
            "risk_off": "\U0001f6e1\ufe0f",
            "risk_on": "\u2694\ufe0f",
            "correlation_break": "\U0001f517"
        }

    async def send_market_summary(self, monitoring_result: Dict) -> bool:
        try:
            risk_level = monitoring_result['risk_assessment']['overall_risk_level']
            total_events = monitoring_result['total_events']

            text = (
                f"\U0001f4ca <b>Market Analysis Summary</b> - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"{self._get_risk_emoji(risk_level)} Risk Assessment: <b>{risk_level.upper().replace('_', ' ')}</b>\n"
                f"\U0001f4ca Detected Events: {total_events}\n"
                f"\U0001f3af Risk Score: {monitoring_result['risk_assessment']['risk_score']:.2f}/1.00"
            )

            if monitoring_result.get('priority_alerts'):
                text += "\n\n\U0001f6a8 <b>Priority Alerts:</b>\n"
                for i, alert in enumerate(monitoring_result['priority_alerts'][:3], 1):
                    emoji = self.event_emojis.get(alert.get('type', '').split('_')[-1], "\u26a0\ufe0f")
                    text += f"{i}. {emoji} <code>{alert['symbol']}</code> {alert['message']}\n"

            insights = monitoring_result.get('advanced_analysis', {}).get('analysis_summary', {}).get('key_insights', [])
            if insights:
                text += "\n\U0001f4a1 <b>Key Insights:</b>\n"
                for insight in insights[:3]:
                    text += f"\u2022 {insight}\n"

            return await self._send_telegram(text)

        except Exception as e:
            self.logger.error(f"Failed to send market summary: {str(e)}")
            return False

    async def send_critical_alert(self, alert: TelegramAlert) -> bool:
        try:
            if not self._check_cooldown(alert.symbol, alert.priority):
                self.logger.info(f"Skipping {alert.symbol} alert due to cooldown")
                return False

            if not self._check_hourly_limit():
                self.logger.warning("Hourly alert limit exceeded")
                return False

            priority_emoji = self.priority_emojis[alert.priority]
            event_emoji = self.event_emojis.get(alert.symbol.lower(), "\U0001f4ca")

            text = (
                f"{priority_emoji} <b>{alert.priority.value.upper()} ALERT</b> {event_emoji}\n"
                f"<b>{alert.title}</b>\n"
                f"{alert.message}\n"
                f"\U0001f4cb Symbol: <code>{alert.symbol}</code>\n"
                f"\U0001f4a5 Severity: {alert.severity:.2f}\n"
                f"\U0001f552 Time: {alert.timestamp.strftime('%H:%M:%S')}"
            )

            if alert.details:
                text += "\n\n\U0001f4cb <b>Details:</b>\n"
                for key, value in alert.details.items():
                    if isinstance(value, (int, float)):
                        text += f"\u2022 {key}: {value:.2f}\n"
                    else:
                        text += f"\u2022 {key}: {value}\n"

            if alert.chart_url:
                text += f"\n\U0001f5bc <a href=\"{alert.chart_url}\">View Chart</a>"

            success = await self._send_telegram(text)

            if success:
                self._update_cooldown(alert.symbol, alert.priority)
                self._increment_hourly_count()

            return success

        except Exception as e:
            self.logger.error(f"Failed to send critical alert: {str(e)}")
            return False

    async def send_news_notification(self, article_data: Dict) -> bool:
        try:
            headline = "Fundamental Agent Update"
            if isinstance(article_data.get('article'), dict):
                headline = article_data['article'].get('headline', headline)

            text = f"\U0001f4f0 <b>New Fundamental Agent Article Generated</b>\n<b>{headline}</b>\n\U0001f552 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            if isinstance(article_data.get('article'), dict):
                key_points = article_data['article'].get('key_points', [])
                if key_points:
                    text += "\n\n\U0001f4cb <b>Key Points:</b>\n"
                    for point in key_points[:3]:
                        text += f"\u2022 {point}\n"

            return await self._send_telegram(text)

        except Exception as e:
            self.logger.error(f"Failed to send news notification: {str(e)}")
            return False

    async def send_system_status(self, status: Dict) -> bool:
        try:
            is_running = status.get('is_running', False)
            status_emoji = "\U0001f7e2" if is_running else "\U0001f534"
            status_text = "Running" if is_running else "Stopped"

            text = (
                f"\U0001f527 <b>System Status Report</b>\n"
                f"{status_emoji} System Status: <b>{status_text}</b>\n"
                f"\U0001f4ca Monitoring Symbols: {status.get('monitoring_symbols_count', 0)}\n"
                f"\U0001f6a8 Latest Risk Level: {status.get('latest_risk_level', 'unknown').upper()}"
            )

            if status.get('last_analysis'):
                text += f"\n\U0001f552 Last Analysis: {status['last_analysis']}"

            return await self._send_telegram(text)

        except Exception as e:
            self.logger.error(f"Failed to send system status: {str(e)}")
            return False

    async def get_updates(self, offset: int = 0) -> list:
        """Poll Telegram for new messages"""
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        params = {"offset": offset, "timeout": 30, "allowed_updates": ["message"]}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=35)) as resp:
                    body = await resp.json()
                    if body.get("ok"):
                        return body.get("result", [])
                    self.logger.warning(f"getUpdates error: {body}")
                    return []
        except Exception as e:
            self.logger.error(f"getUpdates failed: {e}")
            return []

    async def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Public method to send a message to the configured chat"""
        return await self._send_telegram(text, parse_mode)

    async def _send_telegram(self, text: str, parse_mode: str = "HTML") -> bool:
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        self.logger.info("Telegram notification sent successfully")
                        return True
                    else:
                        body = await response.text()
                        self.logger.error(f"Telegram API error {response.status}: {body}")
                        return False

        except Exception as e:
            self.logger.error(f"Telegram send error: {str(e)}")
            return False

    def _get_risk_emoji(self, risk_level: str) -> str:
        emoji_map = {
            "low": "\U0001f7e2",
            "medium": "\U0001f7e1",
            "high": "\U0001f7e0",
            "very_high": "\U0001f534"
        }
        return emoji_map.get(risk_level, "\u26aa")

    def _check_cooldown(self, symbol: str, priority: AlertPriority) -> bool:
        if not self.alert_settings["enabled"]:
            return False

        now = datetime.now()
        cooldown_key = f"{symbol}_{priority.value}"

        if cooldown_key in self.last_alerts:
            last_time = self.last_alerts[cooldown_key]
            minutes_passed = (now - last_time).total_seconds() / 60

            cooldown_minutes = self.alert_settings["cooldown_minutes"]
            if priority == AlertPriority.CRITICAL:
                cooldown_minutes = 5
            elif priority == AlertPriority.HIGH:
                cooldown_minutes = 10

            if minutes_passed < cooldown_minutes:
                return False

        return True

    def _update_cooldown(self, symbol: str, priority: AlertPriority):
        cooldown_key = f"{symbol}_{priority.value}"
        self.last_alerts[cooldown_key] = datetime.now()

    def _check_hourly_limit(self) -> bool:
        current_hour = datetime.now().hour

        if current_hour != self.last_hour_reset:
            self.hourly_count = 0
            self.last_hour_reset = current_hour

        return self.hourly_count < self.alert_settings["max_alerts_per_hour"]

    def _increment_hourly_count(self):
        self.hourly_count += 1

    def update_settings(self, settings: Dict):
        self.alert_settings.update(settings)
        self.logger.info(f"Alert settings updated: {settings}")


def create_alert_from_event(event_data: Dict) -> TelegramAlert:
    severity = event_data.get('severity', 0.5)

    if severity >= 0.9:
        priority = AlertPriority.CRITICAL
    elif severity >= 0.7:
        priority = AlertPriority.HIGH
    elif severity >= 0.5:
        priority = AlertPriority.MEDIUM
    else:
        priority = AlertPriority.LOW

    return TelegramAlert(
        title=f"{event_data.get('symbol', 'UNKNOWN')} - {event_data.get('event_type', 'Event')}",
        message=event_data.get('description', 'Event detected.'),
        priority=priority,
        symbol=event_data.get('symbol', 'UNKNOWN'),
        severity=severity,
        timestamp=datetime.fromisoformat(event_data.get('timestamp', datetime.now().isoformat())),
        details={
            'change_percent': event_data.get('change_percent'),
            'current_price': event_data.get('current_price'),
            'volume': event_data.get('volume'),
            'confidence': event_data.get('confidence')
        }
    )


async def test_telegram_notifier():
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

    if not bot_token or not chat_id:
        print("\u274c Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars")
        return

    notifier = TelegramNotifier(bot_token, chat_id)

    test_alert = TelegramAlert(
        title="Test Alert",
        message="This is a test of the Telegram notification system.",
        priority=AlertPriority.MEDIUM,
        symbol="TEST",
        severity=0.6,
        timestamp=datetime.now(),
        details={"test_value": 123.45}
    )

    print("\U0001f4e4 Sending test notification...")
    success = await notifier.send_critical_alert(test_alert)

    if success:
        print("\u2705 Test notification sent successfully!")
    else:
        print("\u274c Failed to send test notification")


if __name__ == "__main__":
    import os
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_telegram_notifier())
