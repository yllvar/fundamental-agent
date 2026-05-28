"""
Integrated monitoring system
Sends event detection results via Telegram
"""

import asyncio
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notifications.telegram_notifier import TelegramNotifier, TelegramAlert, AlertPriority, create_alert_from_event
from data_monitoring.enhanced_monitor import EnhancedEconomicMonitor


class IntegratedMonitor:
    """Integrated monitoring system with Telegram alerts"""

    def __init__(self, telegram_token: str = "", telegram_chat_id: str = ""):
        self.logger = logging.getLogger(__name__)

        self.enhanced_monitor = EnhancedEconomicMonitor()

        self.telegram_notifier = TelegramNotifier(telegram_token, telegram_chat_id) if telegram_token and telegram_chat_id else None

        self.notification_settings = {
            "send_summary": True,
            "send_critical_alerts": True,
            "send_news_updates": True,
            "send_system_status": True,
            "summary_interval_minutes": 60,
            "min_alert_severity": 0.6,
        }

        self.last_summary_time = None
        self.monitoring_active = False
        self.alert_history = []

    async def start_monitoring_with_alerts(self, interval_minutes: int = 30):
        """Start monitoring with alerts"""
        self.monitoring_active = True
        self.logger.info("Telegram monitoring started")

        await self._send_startup_notification()

        try:
            while self.monitoring_active:
                monitoring_result = await self.enhanced_monitor.run_enhanced_monitoring_cycle()

                if "error" not in monitoring_result:
                    await self._process_monitoring_result(monitoring_result)
                else:
                    await self._send_error_notification(monitoring_result["error"])

                await asyncio.sleep(interval_minutes * 60)

        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Monitoring error: {str(e)}")
            await self._send_error_notification(str(e))
        finally:
            self.monitoring_active = False
            await self._send_shutdown_notification()

    async def run_single_analysis_with_alerts(self):
        """Run single analysis with alerts"""
        self.logger.info("Running single analysis with alerts")

        try:
            monitoring_result = await self.enhanced_monitor.run_enhanced_monitoring_cycle()

            if "error" not in monitoring_result:
                await self._process_monitoring_result(monitoring_result)
                return monitoring_result
            else:
                await self._send_error_notification(monitoring_result["error"])
                return monitoring_result

        except Exception as e:
            self.logger.error(f"Analysis error: {str(e)}")
            await self._send_error_notification(str(e))
            return {"error": str(e)}

    async def _process_monitoring_result(self, monitoring_result: Dict):
        """Process monitoring results and send alerts"""
        try:
            if self.notification_settings["send_critical_alerts"]:
                await self._send_critical_alerts(monitoring_result)

            if self.notification_settings["send_summary"]:
                await self._send_summary_if_needed(monitoring_result)

            if (self.notification_settings["send_news_updates"] and
                monitoring_result.get('news_generated')):
                if self.telegram_notifier:
                    await self.telegram_notifier.send_news_notification(monitoring_result)

            self._update_alert_history(monitoring_result)

        except Exception as e:
            self.logger.error(f"Alert processing error: {str(e)}")

    async def _send_critical_alerts(self, monitoring_result: Dict):
        """Send critical alerts"""
        try:
            priority_alerts = monitoring_result.get('priority_alerts', [])

            for alert_data in priority_alerts:
                severity = alert_data.get('severity', 0.5)

                if severity < self.notification_settings["min_alert_severity"]:
                    continue

                alert = create_alert_from_event(alert_data)

                if self.telegram_notifier:
                    tg_alert = TelegramAlert(
                        title=alert.title, message=alert.message, priority=alert.priority,
                        symbol=alert.symbol, severity=alert.severity, timestamp=alert.timestamp,
                        details=alert.details, chart_url=alert.chart_url
                    )
                    await self.telegram_notifier.send_critical_alert(tg_alert)

            risk_level = monitoring_result['risk_assessment']['overall_risk_level']
            if risk_level == "very_high":
                await self._send_high_risk_alert(monitoring_result)

        except Exception as e:
            self.logger.error(f"Critical alert error: {str(e)}")

    async def _send_high_risk_alert(self, monitoring_result: Dict):
        """Send high risk alert"""
        try:
            risk_assessment = monitoring_result['risk_assessment']

            message = (f"Market risk reached very high level.\n"
                       f"Risk Score: {risk_assessment['risk_score']:.2f}/1.00\n"
                       f"Total Events: {monitoring_result['total_events']}")

            if self.telegram_notifier:
                await self.telegram_notifier.send_critical_alert(TelegramAlert(
                    title="HIGH RISK MARKET CONDITION",
                    message=message,
                    priority=AlertPriority.CRITICAL,
                    symbol="MARKET",
                    severity=risk_assessment['risk_score'],
                    timestamp=datetime.now(),
                    details={
                        "risk_factors": risk_assessment.get('risk_factors', []),
                        "high_severity_events": monitoring_result.get('advanced_events_count', 0)
                    }
                ))

        except Exception as e:
            self.logger.error(f"High risk alert error: {str(e)}")

    async def _send_summary_if_needed(self, monitoring_result: Dict):
        """Send summary if interval has passed"""
        try:
            now = datetime.now()

            if (self.last_summary_time is None or
                (now - self.last_summary_time).total_seconds() >=
                self.notification_settings["summary_interval_minutes"] * 60):

                if self.telegram_notifier:
                    await self.telegram_notifier.send_market_summary(monitoring_result)
                    self.last_summary_time = now
                    self.logger.info("Market summary sent")

        except Exception as e:
            self.logger.error(f"Summary alert error: {str(e)}")

    async def _send_startup_notification(self):
        """Send startup notification"""
        try:
            status = self.enhanced_monitor.get_monitoring_status()
            status['is_running'] = True
            status['startup_time'] = datetime.now().isoformat()

            if self.telegram_notifier:
                await self.telegram_notifier.send_system_status(status)
            self.logger.info("Startup notification sent")

        except Exception as e:
            self.logger.error(f"Startup notification failed: {str(e)}")

    async def _send_shutdown_notification(self):
        """Send shutdown notification"""
        try:
            status = {
                'is_running': False,
                'shutdown_time': datetime.now().isoformat(),
                'total_alerts_sent': len(self.alert_history)
            }

            if self.telegram_notifier:
                await self.telegram_notifier.send_system_status(status)
            self.logger.info("Shutdown notification sent")

        except Exception as e:
            self.logger.error(f"Shutdown notification failed: {str(e)}")

    async def _send_error_notification(self, error_message: str):
        """Send error notification"""
        try:
            if self.telegram_notifier:
                await self.telegram_notifier.send_critical_alert(TelegramAlert(
                    title="System Error",
                    message=f"Monitoring system error:\n```{error_message}```",
                    priority=AlertPriority.HIGH,
                    symbol="SYSTEM",
                    severity=0.8,
                    timestamp=datetime.now()
                ))

        except Exception as e:
            self.logger.error(f"Error notification failed: {str(e)}")

    def _update_alert_history(self, monitoring_result: Dict):
        """Update alert history"""
        try:
            history_entry = {
                "timestamp": monitoring_result["timestamp"],
                "total_events": monitoring_result["total_events"],
                "risk_level": monitoring_result["risk_assessment"]["overall_risk_level"],
                "alerts_sent": len(monitoring_result.get("priority_alerts", []))
            }

            self.alert_history.append(history_entry)

            cutoff_time = datetime.now() - timedelta(hours=24)
            self.alert_history = [
                entry for entry in self.alert_history
                if datetime.fromisoformat(entry["timestamp"]) > cutoff_time
            ]

        except Exception as e:
            self.logger.error(f"History update error: {str(e)}")

    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        self.logger.info("Monitoring stop requested")

    def update_notification_settings(self, settings: Dict):
        """Update notification settings"""
        self.notification_settings.update(settings)
        if self.telegram_notifier:
            self.telegram_notifier.update_settings(settings)
        self.logger.info(f"Notification settings updated: {settings}")

    def get_alert_statistics(self) -> Dict:
        """Get alert statistics"""
        if not self.alert_history:
            return {"message": "No alert history available."}

        total_alerts = sum(entry["alerts_sent"] for entry in self.alert_history)
        avg_events = sum(entry["total_events"] for entry in self.alert_history) / len(self.alert_history)

        risk_levels = [entry["risk_level"] for entry in self.alert_history]
        high_risk_count = sum(1 for level in risk_levels if level in ["high", "very_high"])

        return {
            "total_monitoring_cycles": len(self.alert_history),
            "total_alerts_sent": total_alerts,
            "average_events_per_cycle": round(avg_events, 2),
            "high_risk_cycles": high_risk_count,
            "high_risk_percentage": round(high_risk_count / len(self.alert_history) * 100, 1)
        }


def load_telegram_config(config_file: str = "config/telegram_config.json") -> Dict:
    """Load Telegram configuration"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "telegram_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
            "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
            "notification_settings": {
                "send_summary": True,
                "send_critical_alerts": True,
                "send_news_updates": True,
                "summary_interval_minutes": 60,
                "min_alert_severity": 0.6
            }
        }


async def main():
    """Main function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/monitor.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    config = load_telegram_config()

    if not config["telegram_token"]:
        print("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
        return

    monitor = IntegratedMonitor(
        telegram_token=config["telegram_token"],
        telegram_chat_id=config["telegram_chat_id"]
    )

    if "notification_settings" in config:
        monitor.update_notification_settings(config["notification_settings"])

    print("Telegram Integrated Monitoring System")
    print("=" * 50)
    print("1. Start continuous monitoring")
    print("2. Run single analysis")
    print("3. View alert statistics")
    print("4. Exit")

    while True:
        try:
            choice = input("\nSelect (1-4): ").strip()

            if choice == "1":
                interval = input("Monitoring interval (min, default 30): ").strip()
                interval = int(interval) if interval.isdigit() else 30
                print(f"Starting continuous monitoring every {interval} minutes...")
                print("Press Ctrl+C to stop")
                await monitor.start_monitoring_with_alerts(interval)
                break

            elif choice == "2":
                print("Running single analysis...")
                result = await monitor.run_single_analysis_with_alerts()
                if "error" not in result:
                    print(f"Analysis complete: {result['total_events']} events detected")
                    print(f"Risk Level: {result['risk_assessment']['overall_risk_level']}")
                else:
                    print(f"Analysis failed: {result['error']}")

            elif choice == "3":
                stats = monitor.get_alert_statistics()
                print("\nAlert Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")

            elif choice == "4":
                print("Shutting down.")
                break

            else:
                print("Invalid choice.")

        except KeyboardInterrupt:
            print("\nUser shutdown")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
