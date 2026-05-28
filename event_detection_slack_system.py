#!/usr/bin/env python3
"""
Integrated Event Detection and Slack Notification System
Real-time economic event detection and Slack alert delivery
"""

import os
import sys
import json
import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd
import numpy as np

# Load .env file
load_dotenv()

# Path setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class EventSeverity(Enum):
    """Event severity"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class EconomicEvent:
    """Economic event data class"""
    symbol: str
    event_type: str
    severity: EventSeverity
    title: str
    description: str
    current_value: float
    previous_value: float
    change_percent: float
    timestamp: datetime
    details: Dict[str, Any] = None

class EventDetector:
    """Economic event detector"""
    
    def __init__(self):
        """Initialization"""
        self.logger = logging.getLogger(__name__)
        
        # Monitoring target symbols
        self.symbols = [
            # Major indices
            "^GSPC",  # S&P 500
            "^IXIC",  # NASDAQ
            "^DJI",   # Dow Jones
            "^VIX",   # VIX

            # Major stocks
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA",

            # Currencies
            "USDKRW=X", "USDJPY=X", "EURUSD=X",
            "GBPUSD=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "USDCHF=X",
            "EURJPY=X", "GBPJPY=X", "EURGBP=X",

            # Commodities
            "GC=F",   # Gold
            "CL=F",   # Oil
            "BTC-USD", # Bitcoin
            "DX-Y.NYB", # Dollar Index
        ]
        
        # Event detection thresholds
        self.thresholds = {
            'price_change': {
                'medium': 2.0,    # 2% change
                'high': 5.0,      # 5% change
                'critical': 10.0  # 10% change
            },
            'volume_spike': {
                'medium': 1.5,    # 1.5x average
                'high': 2.0,      # 2x average
                'critical': 3.0   # 3x average
            },
            'volatility': {
                'medium': 15.0,   # 15% volatility
                'high': 25.0,     # 25% volatility
                'critical': 40.0  # 40% volatility
            }
        }
        
        self.logger.info("✅ Event detector initialized")
    
    def detect_events(self) -> List[EconomicEvent]:
        """Run event detection"""
        
        self.logger.info("🔍 Starting economic event detection")
        events = []
        
        for symbol in self.symbols:
            try:
                # Data collection
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d", interval="1d")
                
                if len(hist) < 2:
                    continue
                
                # Current and previous values
                current_price = hist['Close'].iloc[-1]
                previous_price = hist['Close'].iloc[-2]
                current_volume = hist['Volume'].iloc[-1]
                
                # Calculate change percentage
                price_change = ((current_price - previous_price) / previous_price) * 100
                
                # Calculate average volume
                avg_volume = hist['Volume'].mean()
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                
                # Calculate volatility (5-day)
                volatility = hist['Close'].pct_change().std() * 100
                
                # Detect events
                detected_events = self._analyze_metrics(
                    symbol, current_price, previous_price, price_change,
                    volume_ratio, volatility, current_volume
                )
                
                events.extend(detected_events)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to collect data for {symbol}: {e}")
                continue
        
        # Sort by severity
        events.sort(key=lambda x: self._get_severity_score(x.severity), reverse=True)
        
        self.logger.info(f"✅ Event detection complete: {len(events)} events found")
        return events
    
    def _analyze_metrics(self, symbol: str, current_price: float, previous_price: float,
                        price_change: float, volume_ratio: float, volatility: float,
                        current_volume: float) -> List[EconomicEvent]:
        """Analyze metrics and generate events"""
        
        events = []
        
        # 1. Price change event
        price_severity = self._get_price_change_severity(abs(price_change))
        if price_severity != EventSeverity.LOW:
            direction = "surged" if price_change > 0 else "dropped"
            events.append(EconomicEvent(
                symbol=symbol,
                event_type="price_change",
                severity=price_severity,
                title=f"{symbol} {direction} detected",
                description=f"{symbol} has {direction} by {price_change:.2f}%.",
                current_value=current_price,
                previous_value=previous_price,
                change_percent=price_change,
                timestamp=datetime.now(),
                details={
                    'direction': direction,
                    'volume': current_volume,
                    'volume_ratio': volume_ratio
                }
            ))
        
        # 2. Volume spike event
        volume_severity = self._get_volume_spike_severity(volume_ratio)
        if volume_severity != EventSeverity.LOW:
            events.append(EconomicEvent(
                symbol=symbol,
                event_type="volume_spike",
                severity=volume_severity,
                title=f"{symbol} volume spike",
                description=f"{symbol} volume increased {volume_ratio:.1f}x above average.",
                current_value=current_volume,
                previous_value=current_volume / volume_ratio,
                change_percent=(volume_ratio - 1) * 100,
                timestamp=datetime.now(),
                details={
                    'volume_ratio': volume_ratio,
                    'price_change': price_change
                }
            ))
        
        # 3. Volatility event
        volatility_severity = self._get_volatility_severity(volatility)
        if volatility_severity != EventSeverity.LOW:
            events.append(EconomicEvent(
                symbol=symbol,
                event_type="high_volatility",
                severity=volatility_severity,
                title=f"{symbol} high volatility",
                description=f"{symbol} volatility increased to {volatility:.1f}%.",
                current_value=volatility,
                previous_value=0,
                change_percent=volatility,
                timestamp=datetime.now(),
                details={
                    'volatility': volatility,
                    'price_change': price_change
                }
            ))
        
        return events
    
    def _get_price_change_severity(self, abs_change: float) -> EventSeverity:
        """Determine price change severity"""
        if abs_change >= self.thresholds['price_change']['critical']:
            return EventSeverity.CRITICAL
        elif abs_change >= self.thresholds['price_change']['high']:
            return EventSeverity.HIGH
        elif abs_change >= self.thresholds['price_change']['medium']:
            return EventSeverity.MEDIUM
        else:
            return EventSeverity.LOW
    
    def _get_volume_spike_severity(self, volume_ratio: float) -> EventSeverity:
        """Determine volume spike severity"""
        if volume_ratio >= self.thresholds['volume_spike']['critical']:
            return EventSeverity.CRITICAL
        elif volume_ratio >= self.thresholds['volume_spike']['high']:
            return EventSeverity.HIGH
        elif volume_ratio >= self.thresholds['volume_spike']['medium']:
            return EventSeverity.MEDIUM
        else:
            return EventSeverity.LOW
    
    def _get_volatility_severity(self, volatility: float) -> EventSeverity:
        """Determine volatility severity"""
        if volatility >= self.thresholds['volatility']['critical']:
            return EventSeverity.CRITICAL
        elif volatility >= self.thresholds['volatility']['high']:
            return EventSeverity.HIGH
        elif volatility >= self.thresholds['volatility']['medium']:
            return EventSeverity.MEDIUM
        else:
            return EventSeverity.LOW
    
    def _get_severity_score(self, severity: EventSeverity) -> int:
        """Return severity score"""
        scores = {
            EventSeverity.LOW: 1,
            EventSeverity.MEDIUM: 2,
            EventSeverity.HIGH: 3,
            EventSeverity.CRITICAL: 4
        }
        return scores.get(severity, 1)


class EventMonitoringSystem:
    """Integrated event monitoring system"""
    
    def __init__(self):
        """Initialization"""
        self.logger = logging.getLogger(__name__)
        self.detector = EventDetector()
        self.logger.info("\u2705 Integrated event monitoring system initialized")
    
    def run_single_scan(self) -> Dict[str, Any]:
        """Run single scan"""
        
        self.logger.info("\U0001f50d Starting event scan")
        
        try:
            # Detect events
            events = self.detector.detect_events()
            
            # Compile results
            result = {
                'timestamp': datetime.now().isoformat(),
                'total_events': len(events),
                'events_by_severity': {
                    'critical': len([e for e in events if e.severity == EventSeverity.CRITICAL]),
                    'high': len([e for e in events if e.severity == EventSeverity.HIGH]),
                    'medium': len([e for e in events if e.severity == EventSeverity.MEDIUM]),
                    'low': len([e for e in events if e.severity == EventSeverity.LOW])
                },
                'events': []
            }
            
            # Add event info
            for event in events:
                result['events'].append({
                    'symbol': event.symbol,
                    'type': event.event_type,
                    'severity': event.severity.value,
                    'title': event.title,
                    'description': event.description,
                    'change_percent': event.change_percent,
                    'timestamp': event.timestamp.isoformat()
                })
            
            # Send Telegram notification with scan results
            if events:
                asyncio.create_task(self._send_telegram_scan_result(events))
            
            self.logger.info(f"\u2705 Event scan complete: {len(events)} events")
            return result
            
        except Exception as e:
            self.logger.error(f"\u274c Event scan failed: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'total_events': 0
            }
    
    def run_continuous_monitoring(self, interval_minutes: int = 15):
        """Run continuous monitoring"""
        
        self.logger.info(f"\U0001f504 Starting continuous monitoring (interval: {interval_minutes}min)")
        
        try:
            while True:
                # Run scan
                result = self.run_single_scan()
                
                # Log results
                if result.get('total_events', 0) > 0:
                    self.logger.info(f"\U0001f4ca Events found: {result['total_events']}")
                else:
                    self.logger.info("\U0001f634 No events")
                
                # Wait
                import time
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            self.logger.info("\u23f9\ufe0f Monitoring stopped")
        except Exception as e:
            self.logger.error(f"\u274c Continuous monitoring error: {e}")

    async def _send_telegram_scan_result(self, events):
        import aiohttp
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if not bot_token or not chat_id:
            return
        text = f"Event scan complete: {len(events)} event(s) detected"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10))


def main():
    """Main function"""
    
    # Logging setup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\U0001f680 Economic Event Detection and Slack Alert System")
    print("=" * 60)
    
    # Initialize system
    monitor = EventMonitoringSystem()
    
    # Run single scan
    print("\n1\ufe0f\u20e3 Running single scan test...")
    result = monitor.run_single_scan()
    
    print(f"\n\U0001f4ca Scan Results:")
    print(f"   Total Events: {result.get('total_events', 0)}")
    
    if result.get('events_by_severity'):
        sc = result['events_by_severity']
        print(f"   \U0001f525 Critical: {sc.get('critical', 0)}")
        print(f"   \U0001f6a8 High: {sc.get('high', 0)}")
        print(f"   \u26a0\ufe0f Medium: {sc.get('medium', 0)}")
        print(f"   \u2139\ufe0f Low: {sc.get('low', 0)}")
    
    if result.get('events'):
        print(f"\n\U0001f4cb Key Events:")
        for event in result['events'][:5]:
            print(f"   \u2022 {event['symbol']}: {event['title']} ({event['change_percent']:+.1f}%)")
    
    # Continuous monitoring option
    print(f"\n2\ufe0f\u20e3 Continuous Monitoring Option:")
    print("   Enter 'y' to start continuous monitoring (Ctrl+C to stop)")
    
    try:
        choice = input("   Choice: ").strip().lower()
        if choice == 'y':
            monitor.run_continuous_monitoring(interval_minutes=5)  # 5 minute interval
    except KeyboardInterrupt:
        print("\n\U0001f44b Program terminated")

if __name__ == "__main__":
    main()
