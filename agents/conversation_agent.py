"""
Forex Conversation Strand Agent
Handles user queries — routes intent, fetches data, generates responses
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .strands_framework import BaseStrandAgent, StrandContext, StrandMessage, MessageType
from forex_query_router import route_query, ALL_PAIRS
from data_monitoring.data_collector import EconomicDataCollector
from config.forex_config import FOREX_PAIRS
from memory.analysis_cache import get as cache_get, set as cache_set

ANALYSIS_PROMPTS = {
    "outlook": """You are a forex analyst. Given price data and technical indicators for {pairs}, provide a concise outlook.
Return JSON with:
  "direction": "bullish" | "bearish" | "neutral"
  "key_levels": {"support": X, "resistance": Y}
  "reasoning": "2-3 sentence explanation"
  "confidence": 0-1""",

    "event_analysis": """You are a forex analyst. Given economic event data for {events}, analyze the impact on {pairs}.
Return JSON with:
  "event_impact": "positive" | "negative" | "neutral" for each pair
  "expected_volatility": "low" | "medium" | "high"
  "key_levels": {"support": X, "resistance": Y}
  "reasoning": "2-3 sentence explanation"
  "confidence": 0-1""",

    "risk_assessment": """You are a forex risk analyst. Given price and volatility data for {pairs}, assess current risk.
Return JSON with:
  "risk_level": "low" | "medium" | "high"
  "atr_pips": X
  "volatility_note": "brief note"
  "suggested_stop_pips": X
  "key_levels": {"support": X, "resistance": Y}""",

    "comparison": """You are a forex analyst. Compare the following pairs: {pairs}.
Return JSON with:
  "strongest": "pair name"
  "weakest": "pair name"
  "comparison": {"pair1": "bullish/bearish/neutral", "pair2": "..."}
  "reasoning": "2-3 sentence explanation"
  "dollar_bias": "USD strength/weakness/neutral"
""",

    "what_changed": """You are a forex analyst. Given recent price data for {pairs}, explain what moved.
Return JSON with:
  "biggest_mover": "pair name"
  "change_pips": X
  "driver": "brief explanation of likely cause"
  "summary": "1-2 sentence summary"
  "key_levels": {"support": X, "resistance": Y}""",

    "confidence": """You are a forex analyst. Given technical data for {pairs}, assess trade confidence.
Return JSON with:
  "overall_confidence": 0-1
  "technical_score": 0-1
  "fundamental_score": 0-1
  "concerns": ["concern1", "concern2"]
  "favorable_pairs": ["pair1", "pair2"]""",

    "historical": """You are a forex analyst. Given historical data for {pairs}, summarize recent performance.
Return JSON with:
  "period": "last X days/weeks"
  "top_performer": "pair name with change"
  "worst_performer": "pair name with change"
  "pattern": "brief description of the pattern"
  "summary": "2-3 sentence summary"""
}


class ConversationStrand(BaseStrandAgent):
    """Forex Conversation Strand Agent"""

    def __init__(self):
        super().__init__(
            agent_id="conversation_agent",
            name="Conversation Agent"
        )
        self.capabilities = [
            "forex_query_handling",
            "intent_classification",
            "forex_analysis",
            "response_formatting"
        ]
    def get_capabilities(self) -> List[str]:
        return self.capabilities

    async def process(self, context: StrandContext, message: Optional[StrandMessage] = None) -> Dict[str, Any]:
        query = context.input_data.get("query", "")
        user_id = context.input_data.get("user_id", "default")

        if not query:
            raise Exception("No query provided")

        self.logger.info(f" Processing query: {query[:50]}...")

        try:
            routed = await route_query(query, user_id)

            pair_str = "_".join(routed.get("pairs", ["unknown"]))
            intent = routed.get("intent", "outlook")
            cached = cache_get(pair_str, intent)
            if cached:
                self.logger.info(f"Cache hit for {pair_str}/{intent}")
                return cached
            self.logger.info(f"Intent: {routed.get('intent')}, pairs: {routed.get('pairs')}")

            symbols = routed.get("symbols", [])
            if not symbols:
                routed["pairs"] = ["EUR/USD"]
                routed["symbols"] = ["EURUSD=X"]

            forex_data = await self._fetch_forex_data(symbols)

            analysis = await self._generate_analysis(routed, forex_data, query)

            result = {
                "status": "success",
                "query": query,
                "intent": routed.get("intent"),
                "pairs": routed.get("pairs"),
                "forex_data": forex_data,
                "analysis": analysis,
                "response_text": analysis.get("analysis_text", ""),
                "timestamp": datetime.now().isoformat()
            }

            cache_set(pair_str, intent, result)
            return result

        except Exception as e:
            self.logger.error(f" Query processing failed: {e}")
            return {
                "status": "error",
                "query": query,
                "error": str(e),
                "response_text": "Sorry, I couldn't process that query. Please try again."
            }

    async def _fetch_forex_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Fetch forex data for the given symbols"""
        collector = EconomicDataCollector()
        data = {}

        for symbol in symbols:
            try:
                pair_data = collector.collect_forex_data(symbol)
                if pair_data:
                    hist = collector.get_historical_data(symbol, "1mo")
                    sma_20 = float(hist["Close"].tail(20).mean()) if not hist.empty and len(hist) >= 20 else None

                    data[symbol] = {
                        **pair_data,
                        "sma_20": sma_20,
                    }
            except Exception as e:
                self.logger.warning(f"Failed to fetch {symbol}: {e}")

        return data

    async def _generate_analysis(self, routed: Dict, forex_data: Dict, query: str) -> Dict:
        """Generate analysis based on routed intent"""
        intent = routed.get("intent", "outlook")
        pairs_str = ", ".join(routed.get("pairs", ["EUR/USD"]))
        events_str = ", ".join(routed.get("events", [])) or "general"

        prompt_template = ANALYSIS_PROMPTS.get(intent, ANALYSIS_PROMPTS["outlook"])
        system_prompt = prompt_template.format(pairs=pairs_str, events=events_str)

        user_prompt = f"Query: {query}\n\nData: {json.dumps(forex_data, indent=2, default=str)}"

        try:
            response = await self.call_llm(system_prompt, user_prompt)
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1]) if len(lines) > 2 else lines[-1]

            analysis_json = json.loads(response)
            analysis_json = {k: v for k, v in analysis_json.items() if v is not None}

            lines_str = json.dumps(analysis_json, indent=2)
            analysis_json["analysis_text"] = self._format_response_text(intent, analysis_json, routed)

            return analysis_json

        except Exception as e:
            self.logger.error(f"Analysis generation failed: {e}")
            return {
                "direction": "neutral",
                "reasoning": f"Analysis unavailable for: {pairs_str}",
                "confidence": 0.0,
                "analysis_text": f"Could not analyze {pairs_str}. Please try a more specific query.",
                "error": str(e)
            }

    def _format_response_text(self, intent: str, analysis: Dict, routed: Dict) -> str:
        """Format analysis JSON into readable text"""
        pairs = routed.get("pairs", ["EUR/USD"])
        lines = [f"<b>Forex Analysis — {', '.join(pairs)}</b>\n"]

        if intent == "outlook":
            lines.append(f"Direction: <b>{analysis.get('direction', 'neutral').upper()}</b>")
            k = analysis.get("key_levels", {})
            if k:
                lines.append(f"Support: {k.get('support', '?')} | Resistance: {k.get('resistance', '?')}")
            lines.append(f"\n{analysis.get('reasoning', '')}")
            lines.append(f"Confidence: {analysis.get('confidence', 0) * 100:.0f}%")

        elif intent == "event_analysis":
            impact = analysis.get("event_impact", {})
            if isinstance(impact, dict):
                for pair, imp in impact.items():
                    lines.append(f"{pair}: <b>{imp}</b>")
            lines.append(f"\nExpected volatility: {analysis.get('expected_volatility', 'medium')}")
            lines.append(f"\n{analysis.get('reasoning', '')}")

        elif intent == "risk_assessment":
            lines.append(f"Risk Level: <b>{analysis.get('risk_level', 'medium').upper()}</b>")
            lines.append(f"ATR: {analysis.get('atr_pips', '?')} pips")
            lines.append(f"Suggested Stop: {analysis.get('suggested_stop_pips', '?')} pips")
            k = analysis.get("key_levels", {})
            if k:
                lines.append(f"Support: {k.get('support', '?')} | Resistance: {k.get('resistance', '?')}")
            lines.append(f"\n{analysis.get('volatility_note', '')}")

        elif intent == "comparison":
            lines.append(f"Strongest: <b>{analysis.get('strongest', '?')}</b>")
            lines.append(f"Weakest: <b>{analysis.get('weakest', '?')}</b>")
            comp = analysis.get("comparison", {})
            if isinstance(comp, dict):
                for pair, bias in comp.items():
                    lines.append(f"{pair}: {bias}")
            lines.append(f"\n{analysis.get('reasoning', '')}")
            lines.append(f"Dollar bias: {analysis.get('dollar_bias', 'neutral')}")

        elif intent == "what_changed":
            lines.append(f"Biggest mover: <b>{analysis.get('biggest_mover', '?')}</b>")
            lines.append(f"Move: {analysis.get('change_pips', '?')} pips")
            lines.append(f"\nDriver: {analysis.get('driver', 'Unknown')}")
            lines.append(f"\n{analysis.get('summary', '')}")

        elif intent == "confidence":
            lines.append(f"Overall: <b>{analysis.get('overall_confidence', 0) * 100:.0f}%</b>")
            lines.append(f"Technical: {analysis.get('technical_score', 0) * 100:.0f}%")
            lines.append(f"Fundamental: {analysis.get('fundamental_score', 0) * 100:.0f}%")
            concerns = analysis.get("concerns", [])
            if concerns:
                lines.append(f"\nConcerns: {'; '.join(concerns[:3])}")
            fav = analysis.get("favorable_pairs", [])
            if fav:
                lines.append(f"Favorable: {', '.join(fav)}")

        elif intent == "historical":
            lines.append(f"Top: <b>{analysis.get('top_performer', '?')}</b>")
            lines.append(f"Worst: <b>{analysis.get('worst_performer', '?')}</b>")
            lines.append(f"\nPattern: {analysis.get('pattern', '')}")
            lines.append(f"\n{analysis.get('summary', '')}")

        return "\n".join(lines)

    # Cache replaced by memory/analysis_cache.py file-based cache
