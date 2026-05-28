"""
Economic Event Detection Module
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from .data_collector import MarketData, EconomicDataCollector
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.monitoring_config import ECONOMIC_INDICATORS, SEVERITY_WEIGHTS

class EventType(Enum):
    SURGE = "surge"  # Sharp rise
    DROP = "drop"    # Sharp drop
    VOLATILITY = "volatility"  # High volatility
    VOLUME_SPIKE = "volume_spike"  # Volume spike
    CORRELATION_BREAK = "correlation_break"  # Correlation break

    # Forex-specific event types
    FOREX_SURGE = "forex_surge"            # Forex pair sharp move up
    FOREX_DROP = "forex_drop"              # Forex pair sharp move down
    FOREX_VOLATILITY = "forex_volatility"  # Elevated volatility in pips
    DOLLAR_STRENGTH = "dollar_strength"    # Broad USD strength
    DOLLAR_WEAKNESS = "dollar_weakness"    # Broad USD weakness
    CARRY_TRADE = "carry_trade"            # Yield differential shift
    FOREX_CORRELATION_BREAK = "forex_correlation_break"  # Pair correlation break

@dataclass
class EconomicEvent:
    event_id: str
    symbol: str
    name: str
    event_type: EventType
    severity: float  # 0-1 scale
    timestamp: datetime
    current_price: float
    change_percent: float
    volume: int
    description: str
    technical_indicators: Dict[str, float]
    market_context: Dict[str, any]

class EventDetector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_collector = EconomicDataCollector()
        self.event_history = []  # Recent event history
        self.alert_cooldown = {}  # Alert cooldown management
    
    def detect_events(self, market_data: Dict[str, MarketData]) -> List[EconomicEvent]:
        """Detect events in market data"""
        events = []
        
        for symbol, data in market_data.items():
            # Check thresholds per indicator
            indicator_config = self._get_indicator_config(symbol)
            if not indicator_config:
                continue
            
            # 1. Price change event detection
            price_events = self._detect_price_events(data, indicator_config)
            events.extend(price_events)
            
            # 2. Volume event detection
            volume_events = self._detect_volume_events(data, symbol)
            events.extend(volume_events)
            
            # 3. Volatility event detection
            volatility_events = self._detect_volatility_events(data, indicator_config, symbol)
            events.extend(volatility_events)
        
        # 4. Forex-specific event detection
        for symbol, data in market_data.items():
            if self._is_forex_symbol(symbol):
                forex_events = self._detect_forex_events(data)
                events.extend(forex_events)
        
        # 5. Broad dollar strength/weakness detection
        dollar_events = self._detect_dollar_strength(market_data)
        events.extend(dollar_events)
        
        # 6. Forex correlation break detection
        fx_corr_events = self._detect_forex_correlation_events(market_data)
        events.extend(fx_corr_events)
        
        # 7. Cross-market correlation event detection
        correlation_events = self._detect_correlation_events(market_data)
        events.extend(correlation_events)
        
        # 8. Event filtering and prioritization
        filtered_events = self._filter_and_prioritize_events(events)
        
        return filtered_events
    
    def _get_indicator_config(self, symbol: str) -> Optional[Dict]:
        """Find config for symbol"""
        for category, indicators in ECONOMIC_INDICATORS.items():
            for key, config in indicators.items():
                if config['symbol'] == symbol:
                    return config
        return None
    
    def _detect_price_events(self, data: MarketData, config: Dict) -> List[EconomicEvent]:
        """Detect price change events"""
        events = []
        change_percent = data.change_percent
        
        # Surge detection
        if change_percent >= config['threshold_surge']:
            severity = min(abs(change_percent) / 10.0, 1.0)  # Normalize to max 10% change
            
            event = EconomicEvent(
                event_id=f"{data.symbol}_SURGE_{int(datetime.now().timestamp())}",
                symbol=data.symbol,
                name=data.name,
                event_type=EventType.SURGE,
                severity=severity,
                timestamp=data.timestamp,
                current_price=data.current_price,
                change_percent=change_percent,
                volume=data.volume,
                description=f"{data.name} surged {change_percent:.2f}%.",
                technical_indicators=self._get_technical_indicators(data.symbol),
                market_context=self._get_market_context(data)
            )
            events.append(event)
        
        # Drop detection
        elif change_percent <= config['threshold_drop']:
            severity = min(abs(change_percent) / 10.0, 1.0)
            
            event = EconomicEvent(
                event_id=f"{data.symbol}_DROP_{int(datetime.now().timestamp())}",
                symbol=data.symbol,
                name=data.name,
                event_type=EventType.DROP,
                severity=severity,
                timestamp=data.timestamp,
                current_price=data.current_price,
                change_percent=change_percent,
                volume=data.volume,
                description=f"{data.name} dropped {change_percent:.2f}%.",
                technical_indicators=self._get_technical_indicators(data.symbol),
                market_context=self._get_market_context(data)
            )
            events.append(event)
        
        return events
    
    def _detect_volume_events(self, data: MarketData, symbol: str) -> List[EconomicEvent]:
        """Detect volume spike events"""
        events = []
        
        try:
            # Compare with 20-day average volume
            historical_data = self.data_collector.get_historical_data(symbol, "1mo")
            if historical_data.empty or len(historical_data) < 20:
                return events
            
            avg_volume = historical_data['Volume'].rolling(window=20).mean().iloc[-2]  # Average up to yesterday
            volume_ratio = data.volume / avg_volume if avg_volume > 0 else 0
            
            # If volume is 3x the average
            if volume_ratio >= 3.0:
                severity = min(volume_ratio / 10.0, 1.0)  # Normalize to max 10x
                
                event = EconomicEvent(
                    event_id=f"{data.symbol}_VOLUME_{int(datetime.now().timestamp())}",
                    symbol=data.symbol,
                    name=data.name,
                    event_type=EventType.VOLUME_SPIKE,
                    severity=severity,
                    timestamp=data.timestamp,
                    current_price=data.current_price,
                    change_percent=data.change_percent,
                    volume=data.volume,
                    description=f"{data.name} volume surged {volume_ratio:.1f}x above average.",
                    technical_indicators=self._get_technical_indicators(symbol),
                    market_context={'volume_ratio': volume_ratio, 'avg_volume': avg_volume}
                )
                events.append(event)
        
        except Exception as e:
            self.logger.error(f"Error detecting volume events for {symbol}: {str(e)}")
        
        return events
    
    def _detect_volatility_events(self, data: MarketData, config: Dict, symbol: str) -> List[EconomicEvent]:
        """Detect volatility events"""
        events = []
        
        try:
            # Calculate intraday volatility (high-low)/close
            intraday_volatility = ((data.high_24h - data.low_24h) / data.current_price) * 100
            
            if intraday_volatility >= config['volatility_threshold']:
                severity = min(intraday_volatility / 20.0, 1.0)  # Normalize to max 20% volatility
                
                event = EconomicEvent(
                    event_id=f"{data.symbol}_VOLATILITY_{int(datetime.now().timestamp())}",
                    symbol=data.symbol,
                    name=data.name,
                    event_type=EventType.VOLATILITY,
                    severity=severity,
                    timestamp=data.timestamp,
                    current_price=data.current_price,
                    change_percent=data.change_percent,
                    volume=data.volume,
                    description=f"{data.name} volatility is high at {intraday_volatility:.2f}%.",
                    technical_indicators=self._get_technical_indicators(symbol),
                    market_context={'intraday_volatility': intraday_volatility}
                )
                events.append(event)
        
        except Exception as e:
            self.logger.error(f"Error detecting volatility events for {symbol}: {str(e)}")
        
        return events
    
    def _detect_correlation_events(self, market_data: Dict[str, MarketData]) -> List[EconomicEvent]:
        """Detect cross-market correlation break events"""
        events = []
        
        # Check correlation among major indices (KOSPI, S&P500, NASDAQ)
        major_indices = {}
        for symbol, data in market_data.items():
            if symbol in ['^KS11', '^GSPC', '^IXIC']:
                major_indices[symbol] = data
        
        if len(major_indices) >= 2:
            # Check change direction
            changes = {symbol: data.change_percent for symbol, data in major_indices.items()}
            
            # Detect when indices move in opposite directions
            positive_changes = sum(1 for change in changes.values() if change > 1.0)
            negative_changes = sum(1 for change in changes.values() if change < -1.0)
            
            # If strong opposing movement exists
            if positive_changes > 0 and negative_changes > 0:
                max_change = max(abs(change) for change in changes.values())
                severity = min(max_change / 5.0, 1.0)
                
                event = EconomicEvent(
                    event_id=f"CORRELATION_BREAK_{int(datetime.now().timestamp())}",
                    symbol="MARKET_CORRELATION",
                    name="Market Correlation",
                    event_type=EventType.CORRELATION_BREAK,
                    severity=severity,
                    timestamp=datetime.now(),
                    current_price=0,
                    change_percent=0,
                    volume=0,
                    description="A correlation break among major indices has occurred.",
                    technical_indicators={},
                    market_context={'market_changes': changes}
                )
                events.append(event)
        
        return events
    
    def _get_technical_indicators(self, symbol: str) -> Dict[str, float]:
        """Calculate technical indicators"""
        try:
            historical_data = self.data_collector.get_historical_data(symbol, "3mo")
            return self.data_collector.calculate_technical_indicators(historical_data)
        except Exception as e:
            self.logger.error(f"Error getting technical indicators for {symbol}: {str(e)}")
            return {}
    
    def _get_market_context(self, data: MarketData) -> Dict[str, any]:
        """Market context information"""
        return {
            'market_cap': data.market_cap,
            'price_range_24h': {
                'high': data.high_24h,
                'low': data.low_24h,
                'range_percent': ((data.high_24h - data.low_24h) / data.current_price) * 100
            },
            'previous_close': data.previous_close
        }
    
    def _is_forex_symbol(self, symbol: str) -> bool:
        """Check if symbol is a forex pair"""
        return symbol.endswith("=X") and not symbol.startswith("^")

    def _get_forex_config(self, symbol: str) -> Optional[Dict]:
        """Get forex config for a symbol"""
        for key, config in ECONOMIC_INDICATORS.get('forex_pairs', {}).items():
            if config['symbol'] == symbol:
                return config
        return None

    def _calculate_pips(self, symbol: str, price_change: float) -> float:
        """Convert price change to pips"""
        config = self._get_forex_config(symbol)
        pip_value = config.get('pip_value', 0.0001) if config else 0.0001
        return price_change / pip_value

    def _detect_forex_events(self, data: MarketData) -> List[EconomicEvent]:
        """Detect forex-specific events using pips thresholds"""
        events = []
        config = self._get_forex_config(data.symbol)
        if not config:
            return events

        change_pips = self._calculate_pips(data.symbol, data.change_percent / 100 * data.current_price if data.current_price else 0)
        pip_threshold = config.get('pip_threshold', 50)

        if abs(change_pips) >= pip_threshold:
            event_type = EventType.FOREX_SURGE if change_pips > 0 else EventType.FOREX_DROP
            severity = min(abs(change_pips) / (pip_threshold * 3), 1.0)
            direction = "surged" if change_pips > 0 else "dropped"

            event = EconomicEvent(
                event_id=f"{data.symbol}_FX_{int(datetime.now().timestamp())}",
                symbol=data.symbol,
                name=f"{config['name']} Forex",
                event_type=event_type,
                severity=severity,
                timestamp=data.timestamp,
                current_price=data.current_price,
                change_percent=data.change_percent,
                volume=data.volume,
                description=f"{config['name']} {direction} {abs(change_pips):.1f} pips ({data.change_percent:.2f}%).",
                technical_indicators={'change_pips': change_pips, 'pip_threshold': pip_threshold},
                market_context={
                    'pip_value': config.get('pip_value'),
                    'pip_threshold': pip_threshold,
                    'change_pips': change_pips
                }
            )
            events.append(event)

        # Volatility check in pips
        if data.high_24h and data.low_24h:
            range_pips = self._calculate_pips(data.symbol, data.high_24h - data.low_24h)
            if range_pips >= pip_threshold * 2:
                severity = min(range_pips / (pip_threshold * 5), 1.0)
                event = EconomicEvent(
                    event_id=f"{data.symbol}_FXVOL_{int(datetime.now().timestamp())}",
                    symbol=data.symbol,
                    name=f"{config['name']} Volatility",
                    event_type=EventType.FOREX_VOLATILITY,
                    severity=severity,
                    timestamp=data.timestamp,
                    current_price=data.current_price,
                    change_percent=data.change_percent,
                    volume=data.volume,
                    description=f"{config['name']} range is {range_pips:.1f} pips — elevated volatility.",
                    technical_indicators={'range_pips': range_pips, 'pip_threshold': pip_threshold},
                    market_context={'range_pips': range_pips, 'pip_threshold': pip_threshold}
                )
                events.append(event)

        return events

    def _detect_dollar_strength(self, market_data: Dict[str, MarketData]) -> List[EconomicEvent]:
        """Detect broad USD strength or weakness across multiple pairs"""
        events = []
        usd_pairs = {}
        for symbol, data in market_data.items():
            config = self._get_forex_config(symbol)
            if config and ('USD' in symbol.split('=')[0]):
                usd_pairs[symbol] = data

        if len(usd_pairs) < 3:
            return events

        # Count directional moves for USD
        usd_strength_count = 0
        usd_weakness_count = 0
        for symbol, data in usd_pairs.items():
            base = symbol.split('=')[0]
            change = data.change_percent
            # If USD is base (USDXXX), negative change = USD strength
            if base.startswith('USD'):
                if change < -0.3:
                    usd_strength_count += 1
                elif change > 0.3:
                    usd_weakness_count += 1
            # If USD is quote (XXXUSD), positive change = USD strength
            else:
                if change > 0.3:
                    usd_strength_count += 1
                elif change < -0.3:
                    usd_weakness_count += 1

        total = len(usd_pairs)
        if usd_strength_count >= total * 0.6:
            severity = min(usd_strength_count / total, 1.0)
            event = EconomicEvent(
                event_id=f"DOLLAR_STRENGTH_{int(datetime.now().timestamp())}",
                symbol="DX-Y.NYB",
                name="Dollar Index",
                event_type=EventType.DOLLAR_STRENGTH,
                severity=severity,
                timestamp=datetime.now(),
                current_price=0,
                change_percent=0,
                volume=0,
                description=f"Broad USD strength detected ({usd_strength_count}/{total} pairs moving in USD favor).",
                technical_indicators={'usd_strength_count': usd_strength_count, 'total_pairs': total},
                market_context={'usd_strength_count': usd_strength_count, 'usd_weakness_count': usd_weakness_count}
            )
            events.append(event)
        elif usd_weakness_count >= total * 0.6:
            severity = min(usd_weakness_count / total, 1.0)
            event = EconomicEvent(
                event_id=f"DOLLAR_WEAKNESS_{int(datetime.now().timestamp())}",
                symbol="DX-Y.NYB",
                name="Dollar Index",
                event_type=EventType.DOLLAR_WEAKNESS,
                severity=severity,
                timestamp=datetime.now(),
                current_price=0,
                change_percent=0,
                volume=0,
                description=f"Broad USD weakness detected ({usd_weakness_count}/{total} pairs moving against USD).",
                technical_indicators={'usd_weakness_count': usd_weakness_count, 'total_pairs': total},
                market_context={'usd_strength_count': usd_strength_count, 'usd_weakness_count': usd_weakness_count}
            )
            events.append(event)

        return events

    def _detect_forex_correlation_events(self, market_data: Dict[str, MarketData]) -> List[EconomicEvent]:
        """Detect correlation breaks between related forex pairs"""
        events = []

        # EUR/USD and USD/CHF are typically inversely correlated
        eurusd = market_data.get('EURUSD=X')
        usdchf = market_data.get('USDCHF=X')
        if eurusd and usdchf:
            eurusd_change = eurusd.change_percent
            usdchf_change = usdchf.change_percent
            # Normally they move in opposite directions
            if (eurusd_change > 0.5 and usdchf_change > 0.5) or \
               (eurusd_change < -0.5 and usdchf_change < -0.5):
                severity = min(abs(eurusd_change) / 2.0, 1.0)
                event = EconomicEvent(
                    event_id=f"FX_CORR_BREAK_{int(datetime.now().timestamp())}",
                    symbol="EURUSD=X",
                    name="EUR/USD vs USD/CHF",
                    event_type=EventType.FOREX_CORRELATION_BREAK,
                    severity=severity,
                    timestamp=datetime.now(),
                    current_price=eurusd.current_price,
                    change_percent=eurusd.change_percent,
                    volume=eurusd.volume,
                    description="EUR/USD and USD/CHF correlation break detected — they are moving in the same direction.",
                    technical_indicators={'eurusd_change': eurusd_change, 'usdchf_change': usdchf_change},
                    market_context={'pairs': ['EURUSD=X', 'USDCHF=X']}
                )
                events.append(event)

        return events

    def _filter_and_prioritize_events(self, events: List[EconomicEvent]) -> List[EconomicEvent]:
        """Filter and prioritize events"""
        # Cooldown filtering
        filtered_events = []
        current_time = datetime.now()
        
        for event in events:
            cooldown_key = f"{event.symbol}_{event.event_type.value}"
            
            # Cooldown check
            if cooldown_key in self.alert_cooldown:
                last_alert = self.alert_cooldown[cooldown_key]
                if (current_time - last_alert).seconds < 300:  # 5 minute cooldown
                    continue
            
            self.alert_cooldown[cooldown_key] = current_time
            filtered_events.append(event)
        
        # Sort by severity
        filtered_events.sort(key=lambda x: x.severity, reverse=True)
        
        return filtered_events

# Test function
async def test_event_detector():
    detector = EventDetector()
    
    # Test with sample data
    async with EconomicDataCollector() as collector:
        symbols = ["^KS11", "^GSPC", "USDKRW=X"]
        market_data = await collector.collect_multiple_symbols(symbols)
        
        events = detector.detect_events(market_data)
        
        print(f"Number of detected events: {len(events)}")
        for event in events:
            print(f"- {event.name}: {event.event_type.value}, severity: {event.severity:.2f}")
            print(f"  {event.description}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_event_detector())
