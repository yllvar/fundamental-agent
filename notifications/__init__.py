"""
Notification system module
Telegram notifications and integrated monitoring
"""

from .telegram_notifier import TelegramNotifier, TelegramAlert, AlertPriority
from .integrated_slack_monitor import IntegratedMonitor

SlackIntegratedMonitor = IntegratedMonitor

__all__ = [
    'TelegramNotifier',
    'TelegramAlert',
    'AlertPriority',
    'IntegratedMonitor',
    'SlackIntegratedMonitor',
]
