"""
Forex Analyst Strand Agent
Analyzes forex-specific events, pips movement, and fundamental factors
"""

import os
import sys
import json
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.forex_config import FOREX_PAIRS
from .strands_framework import BaseStrandAgent, StrandContext, StrandMessage, MessageType


class ForexAnalystStrand(BaseStrandAgent):
    """Forex Analysis Strand Agent"""

    def __init__(self):
        super().__init__(
            agent_id="forex_analyst",
            name="Forex Analyst Agent"
        )

        self.capabilities = [
            "forex_pips_analysis",
            "forex_correlation",
            "forex_technical_indicators",
            "dollar_index_analysis",
            "carry_trade_analysis"
        ]

    def get_capabilities(self) -> List[str]:
        return self.capabilities

    async def process(self, context: StrandContext, message: Optional[StrandMessage] = None) -> Dict[str, Any]:
        event_data = context.input_data.get('event')
        if not event_data:
            raise Exception("No event data")

        symbol = event_data.get('symbol')
        if not symbol:
            raise Exception("No symbol information")

        self.logger.info(f" Forex {symbol} analysis started")

        try:
            pair_config = FOREX_PAIRS.get(symbol)
            pip_value = pair_config["pip"] if pair_config else 0.0001

            analysis_result = {
                "symbol": symbol,
                "pair_name": pair_config["name"] if pair_config else symbol,
                "pip_value": pip_value,
                "analysis_timestamp": datetime.now().isoformat(),
            }

            pips_analysis = self._analyze_pips_movement(symbol, pip_value)
            analysis_result["pips_analysis"] = pips_analysis

            technical = self._calculate_forex_indicators(symbol, pip_value)
            analysis_result["technical_indicators"] = technical

            correlation = self._analyze_correlation(symbol)
            analysis_result["correlation"] = correlation

            fundamental = self._analyze_fundamental(symbol)
            analysis_result["fundamental"] = fundamental

            analysis_result["dollar_index"] = self._get_dollar_index_data()

            event_impact = self._analyze_event_impact(event_data, analysis_result)
            analysis_result["event_impact"] = event_impact

            await self.set_shared_data(context, "forex_analysis", analysis_result)

            self.logger.info(f" {symbol} forex analysis completed")
            return analysis_result

        except Exception as e:
            self.logger.error(f" Forex analysis failed: {e}")
            raise

    def _analyze_pips_movement(self, symbol: str, pip_value: float) -> Dict[str, Any]:
        """Analyze price movement in pips"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")

            if hist.empty or len(hist) < 2:
                return {"error": "Insufficient data"}

            current = float(hist["Close"].iloc[-1])
            prev = float(hist["Close"].iloc[-2])
            change_pips = (current - prev) / pip_value

            high_pips = float(hist["High"].max() - hist["Low"].min()) / pip_value if len(hist) > 1 else 0

            return {
                "current_price": current,
                "change_pips": round(change_pips, 1),
                "change_percent": round((current / prev - 1) * 100, 2),
                "week_high_pips": round(high_pips, 1),
                "daily_high": float(hist["High"].iloc[-1]) if not hist.empty else None,
                "daily_low": float(hist["Low"].iloc[-1]) if not hist.empty else None,
                "direction": "bullish" if change_pips > 0 else ("bearish" if change_pips < 0 else "neutral")
            }
        except Exception as e:
            self.logger.error(f"Pips analysis failed: {e}")
            return {}

    def _calculate_forex_indicators(self, symbol: str, pip_value: float) -> Dict[str, Any]:
        """Forex-specific technical indicators"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="3mo")

            if len(hist) < 20:
                return {}

            current = float(hist["Close"].iloc[-1])
            sma_20 = float(hist["Close"].tail(20).mean())
            sma_50 = float(hist["Close"].tail(50).mean()) if len(hist) >= 50 else None

            sma_20_pips = (current - sma_20) / pip_value

            delta = hist["Close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = float((100 - (100 / (1 + rs))).iloc[-1]) if not rs.empty and rs.iloc[-1] is not None else 50

            high, low = hist["High"], hist["Low"]
            tr = pd.concat([high - low, abs(high - hist["Close"].shift()), abs(low - hist["Close"].shift())], axis=1).max(axis=1)
            atr_pips = float(tr.rolling(14).mean().iloc[-1]) / pip_value if not tr.empty else 0

            return {
                "current_price": current,
                "sma_20": round(sma_20, 5),
                "sma_50": round(sma_50, 5) if sma_50 else None,
                "distance_from_sma20_pips": round(sma_20_pips, 1),
                "rsi_14": round(rsi, 1),
                "rsi_signal": "overbought" if rsi > 70 else ("oversold" if rsi < 30 else "neutral"),
                "atr_14_pips": round(atr_pips, 1),
                "above_sma_20": current > sma_20
            }
        except Exception as e:
            self.logger.error(f"Forex indicators failed: {e}")
            return {}

    def _analyze_correlation(self, symbol: str) -> Dict[str, Any]:
        """Analyze correlation with related pairs"""
        try:
            base_currency = symbol.split("=")[0] if "=" in symbol else symbol

            correlated_pairs = []
            for pair_sym, config in FOREX_PAIRS.items():
                if pair_sym != symbol:
                    related = False
                    for c in base_currency:
                        if c in pair_sym:
                            related = True
                            break
                    if related:
                        correlated_pairs.append(pair_sym)

            correlations = {}
            hist_base = yf.Ticker(symbol).history(period="1mo")
            if hist_base.empty:
                return {}

            for pair in correlated_pairs[:3]:
                try:
                    hist_pair = yf.Ticker(pair).history(period="1mo")
                    if not hist_pair.empty:
                        common = hist_base.index.intersection(hist_pair.index)
                        if len(common) > 5:
                            corr = hist_base.loc[common, "Close"].corr(hist_pair.loc[common, "Close"])
                            correlations[pair] = round(float(corr), 3)
                except:
                    continue

            return {
                "correlated_pairs": correlations,
                "note": "Strong correlation > 0.7, Inverse < -0.3"
            }
        except Exception as e:
            self.logger.error(f"Correlation analysis failed: {e}")
            return {}

    def _analyze_fundamental(self, symbol: str) -> Dict[str, Any]:
        """Analyze fundamental factors from config"""
        pair_config = FOREX_PAIRS.get(symbol)
        if not pair_config:
            return {}

        central_bank = pair_config.get("central_bank", "")
        session = pair_config.get("session", "")

        return {
            "central_bank": central_bank,
            "primary_session": session,
            "pair_type": pair_config.get("name", symbol).split("/")[0],
            "note": f"Driven by {central_bank} policy and {session} session liquidity"
        }

    def _get_dollar_index_data(self) -> Dict[str, Any]:
        """Get Dollar Index (DXY) data"""
        try:
            dxy = yf.Ticker("DX-Y.NYB")
            hist = dxy.history(period="5d")
            if hist.empty:
                return {}

            current = float(hist["Close"].iloc[-1])
            change = float(hist["Close"].iloc[-2] / hist["Close"].iloc[-1] - 1) * 100 if len(hist) > 1 else 0

            return {
                "dxy_price": current,
                "dxy_change_percent": round(change, 2),
                "dxy_direction": "USD strengthening" if change > 0 else ("USD weakening" if change < 0 else "flat"),
                "dxy_week_high": float(hist["High"].max()),
                "dxy_week_low": float(hist["Low"].min())
            }
        except Exception as e:
            self.logger.error(f"DXY data failed: {e}")
            return {}

    def _analyze_event_impact(self, event_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how the detected event impacts forex"""
        event_type = event_data.get("event_type", "unknown")
        pips = analysis.get("pips_analysis", {})
        indicators = analysis.get("technical_indicators", {})

        impact = {
            "event_type": event_type,
            "severity": event_data.get("severity", "low"),
        }

        change_pips = pips.get("change_pips", 0)
        if abs(change_pips) > 100:
            impact["market_impact"] = "significant"
            impact["volatility_outlook"] = "high"
        elif abs(change_pips) > 50:
            impact["market_impact"] = "moderate"
            impact["volatility_outlook"] = "elevated"
        else:
            impact["market_impact"] = "low"
            impact["volatility_outlook"] = "normal"

        rsi = indicators.get("rsi_14", 50)
        if rsi > 70:
            impact["technical_bias"] = "overbought — caution on longs"
        elif rsi < 30:
            impact["technical_bias"] = "oversold — caution on shorts"
        else:
            impact["technical_bias"] = "neutral"

        atr = indicators.get("atr_14_pips", 0)
        impact["expected_range_pips"] = round(atr, 1) if atr else "unknown"

        return impact
