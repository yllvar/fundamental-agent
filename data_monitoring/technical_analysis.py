"""
Technical Analysis Indicators Module
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import yfinance as yf
from datetime import datetime, timedelta

class TechnicalSignal(Enum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    NEUTRAL = "neutral"
    SELL = "sell"
    STRONG_SELL = "strong_sell"

@dataclass
class TechnicalIndicators:
    symbol: str
    timestamp: datetime
    
    # Trend indicators
    sma_20: float  # 20-day Simple Moving Average
    sma_50: float  # 50-day Simple Moving Average
    ema_12: float  # 12-day Exponential Moving Average
    ema_26: float  # 26-day Exponential Moving Average
    
    # Momentum indicators
    rsi: float  # Relative Strength Index (0-100)
    macd: float  # MACD
    macd_signal: float  # MACD signal line
    macd_histogram: float  # MACD histogram
    
    # Volatility indicators
    bollinger_upper: float  # Bollinger Band upper
    bollinger_middle: float  # Bollinger Band middle (20-day SMA)
    bollinger_lower: float  # Bollinger Band lower
    bollinger_width: float  # Bollinger Band width
    
    # Volume indicators
    volume_sma: float  # Volume moving average
    volume_ratio: float  # Current volume / average volume
    
    # Support/Resistance levels
    support_level: float
    resistance_level: float
    
    # Overall signal
    overall_signal: TechnicalSignal
    signal_strength: float  # 0-1 scale

class TechnicalAnalyzer:
    """Technical analysis indicator calculation class"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_symbol(self, symbol: str, period: str = "6mo") -> Optional[TechnicalIndicators]:
        """Perform technical analysis for a symbol"""
        try:
            # Data collection
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty or len(hist) < 50:
                self.logger.warning(f"Insufficient data for {symbol}")
                return None
            
            # Calculate each indicator
            indicators = self._calculate_all_indicators(hist)
            
            # Calculate overall signal
            overall_signal, signal_strength = self._calculate_overall_signal(indicators)
            
            return TechnicalIndicators(
                symbol=symbol,
                timestamp=datetime.now(),
                **indicators,
                overall_signal=overall_signal,
                signal_strength=signal_strength
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {str(e)}")
            return None
    
    def _calculate_all_indicators(self, data: pd.DataFrame) -> Dict:
        """Calculate all technical indicators"""
        close = data['Close']
        high = data['High']
        low = data['Low']
        volume = data['Volume']
        
        indicators = {}
        
        # Moving averages
        indicators['sma_20'] = close.rolling(window=20).mean().iloc[-1]
        indicators['sma_50'] = close.rolling(window=50).mean().iloc[-1]
        indicators['ema_12'] = close.ewm(span=12).mean().iloc[-1]
        indicators['ema_26'] = close.ewm(span=26).mean().iloc[-1]
        
        # Calculate RSI
        indicators['rsi'] = self._calculate_rsi(close)
        
        # Calculate MACD
        macd_data = self._calculate_macd(close)
        indicators.update(macd_data)
        
        # Calculate Bollinger Bands
        bollinger_data = self._calculate_bollinger_bands(close)
        indicators.update(bollinger_data)
        
        # Volume indicators
        indicators['volume_sma'] = volume.rolling(window=20).mean().iloc[-1]
        indicators['volume_ratio'] = volume.iloc[-1] / indicators['volume_sma'] if indicators['volume_sma'] > 0 else 1.0
        
        # Support/Resistance levels
        support_resistance = self._calculate_support_resistance(high, low, close)
        indicators.update(support_resistance)
        
        return indicators
    
    def _calculate_rsi(self, close: pd.Series, period: int = 14) -> float:
        """Calculate RSI"""
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
    
    def _calculate_macd(self, close: pd.Series) -> Dict:
        """Calculate MACD"""
        ema_12 = close.ewm(span=12).mean()
        ema_26 = close.ewm(span=26).mean()
        
        macd = ema_12 - ema_26
        macd_signal = macd.ewm(span=9).mean()
        macd_histogram = macd - macd_signal
        
        return {
            'macd': macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else 0.0,
            'macd_signal': macd_signal.iloc[-1] if not pd.isna(macd_signal.iloc[-1]) else 0.0,
            'macd_histogram': macd_histogram.iloc[-1] if not pd.isna(macd_histogram.iloc[-1]) else 0.0
        }
    
    def _calculate_bollinger_bands(self, close: pd.Series, period: int = 20, std_dev: int = 2) -> Dict:
        """Calculate Bollinger Bands"""
        sma = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        width = ((upper - lower) / sma) * 100
        
        return {
            'bollinger_upper': upper.iloc[-1] if not pd.isna(upper.iloc[-1]) else close.iloc[-1] * 1.02,
            'bollinger_middle': sma.iloc[-1] if not pd.isna(sma.iloc[-1]) else close.iloc[-1],
            'bollinger_lower': lower.iloc[-1] if not pd.isna(lower.iloc[-1]) else close.iloc[-1] * 0.98,
            'bollinger_width': width.iloc[-1] if not pd.isna(width.iloc[-1]) else 4.0
        }
    
    def _calculate_support_resistance(self, high: pd.Series, low: pd.Series, close: pd.Series) -> Dict:
        """Calculate support/resistance levels"""
        # Analyze recent 20-day highs/lows
        recent_high = high.rolling(window=20).max().iloc[-1]
        recent_low = low.rolling(window=20).min().iloc[-1]
        
        # Calculate pivot point
        pivot = (recent_high + recent_low + close.iloc[-1]) / 3
        
        # Support/resistance levels (simplified)
        resistance = pivot + (recent_high - recent_low) * 0.618  # Apply Fibonacci ratio
        support = pivot - (recent_high - recent_low) * 0.618
        
        return {
            'support_level': max(support, recent_low),
            'resistance_level': min(resistance, recent_high)
        }
    
    def _calculate_overall_signal(self, indicators: Dict) -> Tuple[TechnicalSignal, float]:
        """Calculate overall trading signal"""
        signals = []
        weights = []
        
        current_price = indicators.get('bollinger_middle', 0)  # Approximate SMA20 as current price
        
        # RSI signal (weight: 0.25)
        rsi = indicators.get('rsi', 50)
        if rsi > 70:
            signals.append(-2)  # Overbought
        elif rsi > 60:
            signals.append(-1)
        elif rsi < 30:
            signals.append(2)   # Oversold
        elif rsi < 40:
            signals.append(1)
        else:
            signals.append(0)
        weights.append(0.25)
        
        # MACD signal (weight: 0.25)
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        macd_histogram = indicators.get('macd_histogram', 0)
        
        if macd > macd_signal and macd_histogram > 0:
            signals.append(2)   # Strong buy
        elif macd > macd_signal:
            signals.append(1)   # Buy
        elif macd < macd_signal and macd_histogram < 0:
            signals.append(-2)  # Strong sell
        elif macd < macd_signal:
            signals.append(-1)  # Sell
        else:
            signals.append(0)
        weights.append(0.25)
        
        # Moving average signal (weight: 0.2)
        sma_20 = indicators.get('sma_20', current_price)
        sma_50 = indicators.get('sma_50', current_price)
        
        if sma_20 > sma_50 * 1.02:  # Golden cross
            signals.append(2)
        elif sma_20 > sma_50:
            signals.append(1)
        elif sma_20 < sma_50 * 0.98:  # Dead cross
            signals.append(-2)
        elif sma_20 < sma_50:
            signals.append(-1)
        else:
            signals.append(0)
        weights.append(0.2)
        
        # Bollinger Bands signal (weight: 0.15)
        bollinger_upper = indicators.get('bollinger_upper', current_price * 1.02)
        bollinger_lower = indicators.get('bollinger_lower', current_price * 0.98)
        
        if current_price >= bollinger_upper:
            signals.append(-1)  # Overbought zone
        elif current_price <= bollinger_lower:
            signals.append(1)   # Oversold zone
        else:
            signals.append(0)
        weights.append(0.15)
        
        # Volume signal (weight: 0.15)
        volume_ratio = indicators.get('volume_ratio', 1.0)
        if volume_ratio > 2.0:
            signals.append(1)   # Volume surge is positive
        elif volume_ratio < 0.5:
            signals.append(-1)  # Volume drop is negative
        else:
            signals.append(0)
        weights.append(0.15)
        
        # Calculate weighted average
        weighted_signal = sum(s * w for s, w in zip(signals, weights))
        signal_strength = abs(weighted_signal) / 2.0  # 0-1 normalization
        
        # Signal classification
        if weighted_signal >= 1.5:
            return TechnicalSignal.STRONG_BUY, signal_strength
        elif weighted_signal >= 0.5:
            return TechnicalSignal.BUY, signal_strength
        elif weighted_signal <= -1.5:
            return TechnicalSignal.STRONG_SELL, signal_strength
        elif weighted_signal <= -0.5:
            return TechnicalSignal.SELL, signal_strength
        else:
            return TechnicalSignal.NEUTRAL, signal_strength
    
    def get_signal_description(self, indicators: TechnicalIndicators) -> str:
        """Generate technical analysis description"""
        desc_parts = []
        
        # RSI analysis
        if indicators.rsi > 70:
            desc_parts.append(f"RSI {indicators.rsi:.1f} indicates overbought")
        elif indicators.rsi < 30:
            desc_parts.append(f"RSI {indicators.rsi:.1f} indicates oversold")
        
        # MACD analysis
        if indicators.macd > indicators.macd_signal:
            desc_parts.append("MACD uptrend")
        else:
            desc_parts.append("MACD downtrend")
        
        # Bollinger Bands analysis
        current_price = indicators.bollinger_middle
        if current_price >= indicators.bollinger_upper:
            desc_parts.append("Bollinger Band upper breakout")
        elif current_price <= indicators.bollinger_lower:
            desc_parts.append("Bollinger Band lower touch")
        
        # Volume analysis
        if indicators.volume_ratio > 2.0:
            desc_parts.append(f"Volume surged {indicators.volume_ratio:.1f}x")
        
        return ", ".join(desc_parts) if desc_parts else "Neutral technical indicators"

# Test function
def test_technical_analyzer():
    analyzer = TechnicalAnalyzer()
    
    symbols = ["AAPL", "GOOGL", "MSFT", "^GSPC"]
    
    for symbol in symbols:
        print(f"\n=== {symbol} Technical Analysis ===")
        indicators = analyzer.analyze_symbol(symbol)
        
        if indicators:
            print(f"RSI: {indicators.rsi:.2f}")
            print(f"MACD: {indicators.macd:.4f}")
            print(f"Bollinger Bands: {indicators.bollinger_lower:.2f} - {indicators.bollinger_upper:.2f}")
            print(f"Overall Signal: {indicators.overall_signal.value} (Strength: {indicators.signal_strength:.2f})")
            print(f"Description: {analyzer.get_signal_description(indicators)}")
        else:
            print("Analysis failed")

if __name__ == "__main__":
    test_technical_analyzer()
