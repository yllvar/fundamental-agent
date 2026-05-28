"""
Economic Data Monitoring Main System
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from dataclasses import asdict

from .data_collector import EconomicDataCollector, MarketData
from .event_detector import EventDetector, EconomicEvent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.monitoring_config import ECONOMIC_INDICATORS, MONITORING_CONFIG

class EconomicMonitor:
    def __init__(self):
        self.logger = self._setup_logging()
        self.data_collector = EconomicDataCollector()
        self.event_detector = EventDetector()
        self.is_running = False
        self.monitoring_symbols = self._get_monitoring_symbols()
        
    def _setup_logging(self) -> logging.Logger:
        """Logging setup"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/home/ec2-user/projects/ABP/fundamental_agent/logs/monitor.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _get_monitoring_symbols(self) -> List[str]:
        """Create list of symbols to monitor"""
        symbols = []
        for category, indicators in ECONOMIC_INDICATORS.items():
            for key, config in indicators.items():
                symbols.append(config['symbol'])
        return symbols
    
    async def start_monitoring(self):
        """Start monitoring"""
        self.is_running = True
        self.logger.info("Starting economic data monitoring.")
        self.logger.info(f"Monitoring targets: {len(self.monitoring_symbols)} indicators")
        
        while self.is_running:
            try:
                await self._monitoring_cycle()
                await asyncio.sleep(MONITORING_CONFIG['check_interval'])
                
            except KeyboardInterrupt:
                self.logger.info("Monitoring interrupted by user.")
                break
            except Exception as e:
                self.logger.error(f"Error during monitoring: {str(e)}")
                await asyncio.sleep(30)  # Wait 30 seconds on error
    
    async def _monitoring_cycle(self):
        """One monitoring cycle"""
        cycle_start = datetime.now()
        self.logger.info(f"Monitoring cycle started: {cycle_start}")
        
        # 1. Data collection
        market_data = await self._collect_market_data()
        if not market_data:
            self.logger.warning("No collected market data.")
            return
        
        self.logger.info(f"Collected data: {len(market_data)} indicators")
        
        # 2. Event detection
        events = self.event_detector.detect_events(market_data)
        
        if events:
            self.logger.info(f"Detected events: {len(events)}")
            await self._process_events(events)
        else:
            self.logger.info("No events detected.")
        
        # 3. Market summary
        await self._log_market_summary(market_data)
        
        cycle_end = datetime.now()
        cycle_duration = (cycle_end - cycle_start).total_seconds()
        self.logger.info(f"Monitoring cycle completed: {cycle_duration:.2f}s taken")
    
    async def _collect_market_data(self) -> Dict[str, MarketData]:
        """Collect market data"""
        try:
            async with EconomicDataCollector() as collector:
                market_data = await collector.collect_multiple_symbols(self.monitoring_symbols)
                return market_data
        except Exception as e:
            self.logger.error(f"Error collecting data: {str(e)}")
            return {}
    
    async def _process_events(self, events: List[EconomicEvent]):
        """Process detected events"""
        for event in events:
            # Event logging
            self.logger.warning(f"\U0001f6a8 {event.event_type.value.upper()} event detected!")
            self.logger.warning(f"   Target: {event.name} ({event.symbol})")
            self.logger.warning(f"   Severity: {event.severity:.2f}")
            self.logger.warning(f"   Description: {event.description}")
            
            # Save event
            await self._save_event(event)
            
            # Immediate alert for high severity events
            if event.severity >= 0.7:
                await self._send_high_priority_alert(event)
    
    async def _save_event(self, event: EconomicEvent):
        """Save event to file"""
        try:
            event_data = {
                'event_id': event.event_id,
                'symbol': event.symbol,
                'name': event.name,
                'event_type': event.event_type.value,
                'severity': event.severity,
                'timestamp': event.timestamp.isoformat(),
                'current_price': event.current_price,
                'change_percent': event.change_percent,
                'volume': event.volume,
                'description': event.description,
                'technical_indicators': event.technical_indicators,
                'market_context': event.market_context
            }
            
            # Save to date-based file
            date_str = event.timestamp.strftime('%Y-%m-%d')
            filename = f"/home/ec2-user/projects/ABP/fundamental_agent/logs/events_{date_str}.json"
            
            # Append to file
            try:
                with open(filename, 'r') as f:
                    events_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                events_data = []
            
            events_data.append(event_data)
            
            with open(filename, 'w') as f:
                json.dump(events_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Error saving event: {str(e)}")
    
    async def _send_high_priority_alert(self, event: EconomicEvent):
        """High priority event alert"""
        # Integrate actual notification system here (email, Slack, AWS SNS, etc.)
        alert_message = f"""
\U0001f6a8 Emergency Economic Event Alert \U0001f6a8

Target: {event.name} ({event.symbol})
Event: {event.event_type.value.upper()}
Severity: {event.severity:.2f}/1.0
Time: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

Current Price: {event.current_price:,.2f}
Change: {event.change_percent:+.2f}%
Volume: {event.volume:,}

Description: {event.description}
        """
        
        self.logger.critical(alert_message)
        
        # TODO: Integrate actual notification system
        # await self._send_slack_notification(alert_message)
        # await self._send_email_notification(alert_message)
    
    async def _log_market_summary(self, market_data: Dict[str, MarketData]):
        """Log market summary"""
        summary_lines = ["\U0001f4ca Market Summary:"]
        
        # Summary by category
        categories = {
            'stock_indices': 'Stock Indices',
            'currencies': 'Currencies',
            'commodities': 'Commodities'
        }
        
        for category, category_name in categories.items():
            category_data = []
            
            if category in ECONOMIC_INDICATORS:
                for key, config in ECONOMIC_INDICATORS[category].items():
                    symbol = config['symbol']
                    if symbol in market_data:
                        data = market_data[symbol]
                        category_data.append(f"  {config['name']}: {data.change_percent:+.2f}%")
            
            if category_data:
                summary_lines.append(f"{category_name}:")
                summary_lines.extend(category_data)
        
        self.logger.info('\n'.join(summary_lines))
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_running = False
        self.logger.info("Monitoring stop requested")
    
    async def get_recent_events(self, hours: int = 24) -> List[Dict]:
        """Get recent events"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_events = []
            
            # Check event files from recent days
            for i in range(3):  # Recent 3 days
                date = datetime.now() - timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                filename = f"/home/ec2-user/projects/ABP/fundamental_agent/logs/events_{date_str}.json"
                
                try:
                    with open(filename, 'r') as f:
                        events_data = json.load(f)
                        
                    for event_data in events_data:
                        event_time = datetime.fromisoformat(event_data['timestamp'])
                        if event_time >= cutoff_time:
                            recent_events.append(event_data)
                            
                except (FileNotFoundError, json.JSONDecodeError):
                    continue
            
            # Sort by time
            recent_events.sort(key=lambda x: x['timestamp'], reverse=True)
            return recent_events
            
        except Exception as e:
            self.logger.error(f"Error querying recent events: {str(e)}")
            return []

# CLI interface
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Economic Data Monitoring System')
    parser.add_argument('--mode', choices=['monitor', 'events'], default='monitor',
                       help='Run mode: monitor, events (recent events query)')
    parser.add_argument('--hours', type=int, default=24,
                       help='Recent events query time (hours)')
    
    args = parser.parse_args()
    
    monitor = EconomicMonitor()
    
    if args.mode == 'monitor':
        try:
            await monitor.start_monitoring()
        except KeyboardInterrupt:
            monitor.stop_monitoring()
            print("\nMonitoring stopped.")
    
    elif args.mode == 'events':
        events = await monitor.get_recent_events(args.hours)
        print(f"\nEvents in the last {args.hours} hours: {len(events)}")
        
        for event in events[:10]:  # Show up to 10 most recent
            print(f"- {event['timestamp']}: {event['name']} ({event['event_type']}) - {event['description']}")

if __name__ == "__main__":
    asyncio.run(main())
