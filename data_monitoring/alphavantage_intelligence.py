"""
Alpha Vantage Intelligence API 통합
Market Intelligence, News & Sentiment, Earnings, Top Movers 등 고급 데이터 수집
"""

import requests
import pandas as pd
import numpy as np
import configparser
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import json

@dataclass
class MarketStatus:
    market: str
    region: str
    primary_exchanges: str
    local_open: str
    local_close: str
    current_status: str
    notes: str

@dataclass
class MarketNews:
    title: str
    url: str
    time_published: datetime
    authors: List[str]
    summary: str
    banner_image: str
    source: str
    category_within_source: str
    source_domain: str
    topics: List[Dict[str, str]]
    overall_sentiment_score: float
    overall_sentiment_label: str
    ticker_sentiment: List[Dict[str, Any]]

@dataclass
class TopMover:
    ticker: str
    price: float
    change_amount: float
    change_percentage: str
    volume: int

@dataclass
class InsiderTransaction:
    symbol: str
    name: str
    link: str
    summary: str
    transaction_type: str
    acquisition_or_disposition: str

@dataclass
class AnalyticsData:
    symbol: str
    metric: str
    value: float
    timestamp: datetime

class AlphaVantageIntelligence:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = self._load_api_key()
        self.base_url = "https://www.alphavantage.co/query"
        
        # API 호출 제한
        self.call_interval = 12  # seconds between calls
        self.last_call_time = 0
        
    def _load_api_key(self) -> str:
        """configure 파일에서 Alpha Vantage API 키 로드"""
        try:
            config_file = Path(__file__).parent.parent / "configure"
            if not config_file.exists():
                raise FileNotFoundError("configure 파일을 찾을 수 없습니다")
            
            config = configparser.ConfigParser()
            config.read(config_file)
            
            if 'alphavantage' not in config:
                raise KeyError("configure 파일에 [alphavantage] 섹션이 없습니다")
            
            api_key = config['alphavantage'].get('api_key')
            if not api_key:
                raise ValueError("Alpha Vantage API 키가 설정되지 않았습니다")
            
            self.logger.info("✅ Alpha Vantage Intelligence API 키 로드 완료")
            return api_key
            
        except Exception as e:
            self.logger.error(f"API 키 로드 실패: {e}")
            raise
    
    def _wait_for_rate_limit(self):
        """API 호출 제한 준수"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.call_interval:
            wait_time = self.call_interval - time_since_last_call
            self.logger.debug(f"Rate limit wait: {wait_time:.1f}s")
            time.sleep(wait_time)
        
        self.last_call_time = time.time()
    
    def get_market_status(self) -> List[MarketStatus]:
        """글로벌 시장 개장/폐장 상태 조회"""
        self._wait_for_rate_limit()
        
        try:
            params = {
                "function": "MARKET_STATUS",
                "apikey": self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "Error Message" in data or "Note" in data:
                self.logger.warning(f"Market status API issue: {data}")
                return []
            
            markets = data.get("markets", [])
            market_statuses = []
            
            self.logger.debug(f"Processing {len(markets)} markets from API response")
            
            for i, market_data in enumerate(markets):
                try:
                    market_status = MarketStatus(
                        market=market_data.get("market_type", ""),
                        region=market_data.get("region", ""),
                        primary_exchanges=market_data.get("primary_exchanges", ""),
                        local_open=market_data.get("local_open", ""),
                        local_close=market_data.get("local_close", ""),
                        current_status=market_data.get("current_status", ""),
                        notes=market_data.get("notes", "")
                    )
                    market_statuses.append(market_status)
                    self.logger.debug(f"Successfully parsed market {i+1}: {market_status.region}")
                except Exception as e:
                    self.logger.error(f"Error parsing market status {i+1}: {e}")
                    self.logger.error(f"Market data: {market_data}")
                    continue
            
            self.logger.info(f"✅ 글로벌 시장 상태 수집: {len(market_statuses)}개 시장")
            return market_statuses
            
        except Exception as e:
            self.logger.error(f"Error getting market status: {e}")
            return []
    
    def get_market_news_sentiment(self, tickers: str = None, topics: str = None, 
                                 time_from: str = None, time_to: str = None,
                                 sort: str = "LATEST", limit: int = 50) -> List[MarketNews]:
        """시장 뉴스 및 감정 분석 데이터 수집"""
        self._wait_for_rate_limit()
        
        try:
            params = {
                "function": "NEWS_SENTIMENT",
                "apikey": self.api_key,
                "sort": sort,
                "limit": limit
            }
            
            if tickers:
                params["tickers"] = tickers
            if topics:
                params["topics"] = topics
            if time_from:
                params["time_from"] = time_from
            if time_to:
                params["time_to"] = time_to
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "Error Message" in data or "Note" in data:
                self.logger.warning(f"News sentiment API issue: {data}")
                return []
            
            feed = data.get("feed", [])
            news_items = []
            
            for news_data in feed:
                try:
                    # 시간 파싱
                    time_published = datetime.strptime(
                        news_data.get("time_published", ""), 
                        "%Y%m%dT%H%M%S"
                    )
                    
                    # 감정 분석 데이터 파싱
                    overall_sentiment = news_data.get("overall_sentiment_score", 0.0)
                    overall_label = news_data.get("overall_sentiment_label", "Neutral")
                    
                    # 티커별 감정 분석
                    ticker_sentiment = news_data.get("ticker_sentiment", [])
                    
                    news_item = MarketNews(
                        title=news_data.get("title", ""),
                        url=news_data.get("url", ""),
                        time_published=time_published,
                        authors=news_data.get("authors", []),
                        summary=news_data.get("summary", ""),
                        banner_image=news_data.get("banner_image", ""),
                        source=news_data.get("source", ""),
                        category_within_source=news_data.get("category_within_source", ""),
                        source_domain=news_data.get("source_domain", ""),
                        topics=news_data.get("topics", []),
                        overall_sentiment_score=float(overall_sentiment),
                        overall_sentiment_label=overall_label,
                        ticker_sentiment=ticker_sentiment
                    )
                    
                    news_items.append(news_item)
                    
                except Exception as e:
                    self.logger.debug(f"Error parsing news item: {e}")
                    continue
            
            self.logger.info(f"✅ 시장 뉴스 및 감정 분석: {len(news_items)}개 기사")
            return news_items
            
        except Exception as e:
            self.logger.error(f"Error getting news sentiment: {e}")
            return []
    
    def get_top_gainers_losers(self) -> Dict[str, List[TopMover]]:
        """상승/하락/거래량 상위 종목 조회"""
        self._wait_for_rate_limit()
        
        try:
            params = {
                "function": "TOP_GAINERS_LOSERS",
                "apikey": self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "Error Message" in data or "Note" in data:
                self.logger.warning(f"Top movers API issue: {data}")
                return {"top_gainers": [], "top_losers": [], "most_actively_traded": []}
            
            result = {
                "top_gainers": [],
                "top_losers": [],
                "most_actively_traded": []
            }
            
            # 상승 종목
            gainers_data = data.get("top_gainers", [])
            self.logger.debug(f"Processing {len(gainers_data)} gainers")
            for i, gainer in enumerate(gainers_data):
                try:
                    top_mover = TopMover(
                        ticker=gainer.get("ticker", ""),
                        price=float(gainer.get("price", 0)),
                        change_amount=float(gainer.get("change_amount", 0)),
                        change_percentage=gainer.get("change_percentage", "0%"),
                        volume=int(gainer.get("volume", 0))
                    )
                    result["top_gainers"].append(top_mover)
                    self.logger.debug(f"Successfully parsed gainer {i+1}: {top_mover.ticker}")
                except Exception as e:
                    self.logger.error(f"Error parsing gainer {i+1}: {e}")
                    self.logger.error(f"Gainer data: {gainer}")
                    continue
            
            # 하락 종목
            losers_data = data.get("top_losers", [])
            self.logger.debug(f"Processing {len(losers_data)} losers")
            for i, loser in enumerate(losers_data):
                try:
                    top_mover = TopMover(
                        ticker=loser.get("ticker", ""),
                        price=float(loser.get("price", 0)),
                        change_amount=float(loser.get("change_amount", 0)),
                        change_percentage=loser.get("change_percentage", "0%"),
                        volume=int(loser.get("volume", 0))
                    )
                    result["top_losers"].append(top_mover)
                    self.logger.debug(f"Successfully parsed loser {i+1}: {top_mover.ticker}")
                except Exception as e:
                    self.logger.error(f"Error parsing loser {i+1}: {e}")
                    self.logger.error(f"Loser data: {loser}")
                    continue
            
            # 거래량 상위 종목
            active_data = data.get("most_actively_traded", [])
            self.logger.debug(f"Processing {len(active_data)} most active")
            for i, active in enumerate(active_data):
                try:
                    top_mover = TopMover(
                        ticker=active.get("ticker", ""),
                        price=float(active.get("price", 0)),
                        change_amount=float(active.get("change_amount", 0)),
                        change_percentage=active.get("change_percentage", "0%"),
                        volume=int(active.get("volume", 0))
                    )
                    result["most_actively_traded"].append(top_mover)
                    self.logger.debug(f"Successfully parsed active {i+1}: {top_mover.ticker}")
                except Exception as e:
                    self.logger.error(f"Error parsing active {i+1}: {e}")
                    self.logger.error(f"Active data: {active}")
                    continue
            
            total_items = sum(len(movers) for movers in result.values())
            self.logger.info(f"✅ 상위 종목 데이터: {total_items}개 종목")
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting top gainers/losers: {e}")
            return {"top_gainers": [], "top_losers": [], "most_actively_traded": []}
                try:
                    top_mover = TopMover(
                        ticker=loser.get("ticker", ""),
                        price=float(loser.get("price", 0)),
                        change_amount=float(loser.get("change_amount", 0)),
                        change_percentage=loser.get("change_percentage", "0%"),
                        volume=int(loser.get("volume", 0))
                    )
                    result["top_losers"].append(top_mover)
                except Exception as e:
                    self.logger.debug(f"Error parsing loser: {e}")
                    continue
            
            # 거래량 상위 종목
            for active in data.get("most_actively_traded", []):
                try:
                    top_mover = TopMover(
                        ticker=active.get("ticker", ""),
                        price=float(active.get("price", 0)),
                        change_amount=float(active.get("change_amount", 0)),
                        change_percentage=active.get("change_percentage", "0%"),
                        volume=int(active.get("volume", 0))
                    )
                    result["most_actively_traded"].append(top_mover)
                except Exception as e:
                    self.logger.debug(f"Error parsing active stock: {e}")
                    continue
            
            total_count = sum(len(movers) for movers in result.values())
            self.logger.info(f"✅ 상위 종목 데이터: {total_count}개 종목")
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting top movers: {e}")
            return {}
    
    def get_insider_transactions(self, symbol: str = None) -> List[InsiderTransaction]:
        """내부자 거래 정보 조회"""
        self._wait_for_rate_limit()
        
        try:
            params = {
                "function": "INSIDER_TRANSACTIONS",
                "apikey": self.api_key
            }
            
            if symbol:
                params["symbol"] = symbol
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "Error Message" in data or "Note" in data:
                self.logger.warning(f"Insider transactions API issue: {data}")
                return []
            
            transactions = []
            feed = data.get("feed", [])
            
            for transaction_data in feed:
                try:
                    transaction = InsiderTransaction(
                        symbol=transaction_data.get("symbol", ""),
                        name=transaction_data.get("name", ""),
                        link=transaction_data.get("link", ""),
                        summary=transaction_data.get("summary", ""),
                        transaction_type=transaction_data.get("transaction_type", ""),
                        acquisition_or_disposition=transaction_data.get("acquisition_or_disposition", "")
                    )
                    transactions.append(transaction)
                except Exception as e:
                    self.logger.debug(f"Error parsing insider transaction: {e}")
                    continue
            
            self.logger.info(f"✅ 내부자 거래 정보: {len(transactions)}개")
            return transactions
            
        except Exception as e:
            self.logger.error(f"Error getting insider transactions: {e}")
            return []
    
    def get_analytics_sliding_window(self, symbols: List[str], range_: str = "1month",
                                   interval: str = "daily", ohlc: str = "close",
                                   window_size: int = 10, 
                                   calculations: str = "MEAN,STDDEV") -> Dict[str, List[AnalyticsData]]:
        """고급 분석 데이터 (슬라이딩 윈도우)"""
        results = {}
        
        for symbol in symbols:
            self._wait_for_rate_limit()
            
            try:
                params = {
                    "function": "ANALYTICS_SLIDING_WINDOW",
                    "SYMBOLS": symbol,
                    "RANGE": range_,
                    "INTERVAL": interval,
                    "OHLC": ohlc,
                    "WINDOW_SIZE": window_size,
                    "CALCULATIONS": calculations,
                    "apikey": self.api_key
                }
                
                response = requests.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if "Error Message" in data or "Note" in data:
                    self.logger.warning(f"Analytics API issue for {symbol}: {data}")
                    continue
                
                analytics_data = []
                payload = data.get("payload", {})
                
                for date_str, metrics in payload.items():
                    try:
                        timestamp = datetime.strptime(date_str, "%Y-%m-%d")
                        
                        for metric_name, value in metrics.items():
                            if value and value != "null":
                                analytics_point = AnalyticsData(
                                    symbol=symbol,
                                    metric=metric_name,
                                    value=float(value),
                                    timestamp=timestamp
                                )
                                analytics_data.append(analytics_point)
                    except Exception as e:
                        self.logger.debug(f"Error parsing analytics data: {e}")
                        continue
                
                results[symbol] = analytics_data
                self.logger.info(f"✅ {symbol} 고급 분석: {len(analytics_data)}개 데이터 포인트")
                
            except Exception as e:
                self.logger.error(f"Error getting analytics for {symbol}: {e}")
                continue
        
        return results
    
    def collect_comprehensive_intelligence(self) -> Dict[str, Any]:
        """종합 Intelligence 데이터 수집 (작동하는 엔드포인트만)"""
        self.logger.info("🧠 Alpha Vantage Intelligence 데이터 수집 시작")
        
        intelligence_data = {
            "timestamp": datetime.now().isoformat(),
            "market_status": [],
            "top_gainers_losers": {},
            "summary": {}
        }
        
        try:
            # 1. 글로벌 시장 상태 (✅ 작동)
            self.logger.info("🌍 글로벌 시장 상태 수집 중...")
            market_status = self.get_market_status()
            intelligence_data["market_status"] = [
                {
                    "market": status.market,
                    "region": status.region,
                    "primary_exchanges": status.primary_exchanges,
                    "current_status": status.current_status,
                    "local_open": status.local_open,
                    "local_close": status.local_close,
                    "notes": status.notes
                }
                for status in market_status
            ]
            
            # 2. 상위 종목 (상승/하락/거래량) (✅ 작동)
            self.logger.info("📈 상위 종목 데이터 수집 중...")
            top_movers = self.get_top_gainers_losers()
            
            for category, movers in top_movers.items():
                intelligence_data["top_gainers_losers"][category] = [
                    {
                        "ticker": mover.ticker,
                        "price": float(mover.price),
                        "change_amount": float(mover.change_amount),
                        "change_percentage": mover.change_percentage.replace('%', ''),
                        "volume": int(mover.volume)
                    }
                    for mover in movers
                ]
            
            # 3. 요약 통계 생성
            intelligence_data["summary"] = self._generate_intelligence_summary(intelligence_data)
            
        except Exception as e:
            self.logger.error(f"Intelligence 데이터 수집 중 오류: {e}")
        
        # 수집 완료 로그
        total_items = (
            len(intelligence_data["market_status"]) +
            sum(len(movers) for movers in intelligence_data["top_gainers_losers"].values())
        )
        
        self.logger.info(f"✅ Intelligence 데이터 수집 완료: {total_items}개 항목")
        return intelligence_data
    
    def _generate_intelligence_summary(self, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligence 데이터 요약 생성"""
        summary = {
            "collection_time": datetime.now().isoformat(),
            "market_analysis": {},
            "top_movers_analysis": {},
            "risk_indicators": {}
        }
        
        try:
            # 시장 상태 분석
            market_status = intelligence_data.get("market_status", [])
            open_markets = [m for m in market_status if m["current_status"] == "open"]
            closed_markets = [m for m in market_status if m["current_status"] == "closed"]
            
            summary["market_analysis"] = {
                "total_markets": len(market_status),
                "open_markets": len(open_markets),
                "closed_markets": len(closed_markets),
                "open_market_regions": list(set(m["region"] for m in open_markets)),
                "market_status_distribution": {
                    "open": len(open_markets),
                    "closed": len(closed_markets)
                }
            }
            
            # 상위 종목 분석
            top_movers = intelligence_data.get("top_gainers_losers", {})
            
            if "top_gainers" in top_movers and top_movers["top_gainers"]:
                gainers = top_movers["top_gainers"]
                top_gainer = gainers[0]
                avg_gain = sum(float(g["change_percentage"]) for g in gainers) / len(gainers)
                
                summary["top_movers_analysis"]["gainers"] = {
                    "count": len(gainers),
                    "top_performer": {
                        "ticker": top_gainer["ticker"],
                        "change_percentage": float(top_gainer["change_percentage"]),
                        "volume": top_gainer["volume"]
                    },
                    "average_gain": round(avg_gain, 2)
                }
            
            if "top_losers" in top_movers and top_movers["top_losers"]:
                losers = top_movers["top_losers"]
                top_loser = losers[0]
                avg_loss = sum(float(l["change_percentage"]) for l in losers) / len(losers)
                
                summary["top_movers_analysis"]["losers"] = {
                    "count": len(losers),
                    "worst_performer": {
                        "ticker": top_loser["ticker"],
                        "change_percentage": float(top_loser["change_percentage"]),
                        "volume": top_loser["volume"]
                    },
                    "average_loss": round(avg_loss, 2)
                }
            
            if "most_actively_traded" in top_movers and top_movers["most_actively_traded"]:
                most_active = top_movers["most_actively_traded"]
                top_volume = most_active[0]
                total_volume = sum(m["volume"] for m in most_active)
                
                summary["top_movers_analysis"]["most_active"] = {
                    "count": len(most_active),
                    "highest_volume": {
                        "ticker": top_volume["ticker"],
                        "volume": top_volume["volume"],
                        "change_percentage": float(top_volume["change_percentage"])
                    },
                    "total_volume": total_volume
                }
            
            # 리스크 지표 계산
            if "top_gainers" in top_movers and "top_losers" in top_movers:
                gainers = top_movers["top_gainers"]
                losers = top_movers["top_losers"]
                
                if gainers and losers:
                    max_gain = max(float(g["change_percentage"]) for g in gainers)
                    max_loss = min(float(l["change_percentage"]) for l in losers)
                    volatility = max_gain - max_loss
                    
                    summary["risk_indicators"] = {
                        "max_gain_percentage": round(max_gain, 2),
                        "max_loss_percentage": round(max_loss, 2),
                        "market_volatility": round(volatility, 2),
                        "volatility_level": "high" if volatility > 100 else "medium" if volatility > 50 else "low"
                    }
        
        except Exception as e:
            self.logger.error(f"Intelligence 요약 생성 오류: {e}")
            summary["error"] = str(e)
        
        return summary
    
    def save_intelligence_data(self, intelligence_data: Dict[str, Any], filename: str = None):
        """Intelligence 데이터를 파일로 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alphavantage_intelligence_{timestamp}.json"
        
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(intelligence_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📁 Intelligence 데이터 저장 완료: {filepath}")
    
    def get_intelligence_summary(self, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligence 데이터 요약"""
        summary = {
            "timestamp": intelligence_data.get("timestamp"),
            "data_overview": {
                "market_status_count": len(intelligence_data.get("market_status", [])),
                "news_articles_count": len(intelligence_data.get("market_news", [])),
                "top_movers_categories": len(intelligence_data.get("top_movers", {})),
                "insider_transactions_count": len(intelligence_data.get("insider_transactions", [])),
                "analytics_symbols_count": len(intelligence_data.get("analytics", {}))
            },
            "market_insights": {},
            "sentiment_analysis": {},
            "key_highlights": []
        }
        
        # 시장 상태 요약
        market_status = intelligence_data.get("market_status", [])
        open_markets = [m for m in market_status if m.get("current_status") == "open"]
        closed_markets = [m for m in market_status if m.get("current_status") == "closed"]
        
        summary["market_insights"] = {
            "open_markets": len(open_markets),
            "closed_markets": len(closed_markets),
            "total_markets": len(market_status)
        }
        
        # 감정 분석 요약
        market_news = intelligence_data.get("market_news", [])
        if market_news:
            sentiment_scores = [news.get("overall_sentiment_score", 0) for news in market_news]
            avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0
            
            summary["sentiment_analysis"] = {
                "average_sentiment": avg_sentiment,
                "sentiment_label": "Bullish" if avg_sentiment > 0.1 else "Bearish" if avg_sentiment < -0.1 else "Neutral",
                "total_articles": len(market_news)
            }
        
        # 주요 하이라이트
        highlights = []
        
        # 상위 상승/하락 종목
        top_movers = intelligence_data.get("top_movers", {})
        if top_movers.get("top_gainers"):
            top_gainer = top_movers["top_gainers"][0]
            highlights.append(f"📈 최고 상승: {top_gainer['ticker']} ({top_gainer['change_percentage']})")
        
        if top_movers.get("top_losers"):
            top_loser = top_movers["top_losers"][0]
            highlights.append(f"📉 최고 하락: {top_loser['ticker']} ({top_loser['change_percentage']})")
        
        # 주요 뉴스
        if market_news:
            latest_news = market_news[0]
            highlights.append(f"📰 최신 뉴스: {latest_news['title'][:50]}...")
        
        summary["key_highlights"] = highlights
        
        return summary

# 테스트 함수
def test_alphavantage_intelligence():
    intelligence = AlphaVantageIntelligence()
    
    print("🧠 Alpha Vantage Intelligence API 테스트")
    print("=" * 60)
    
    # 종합 Intelligence 데이터 수집
    intelligence_data = intelligence.collect_comprehensive_intelligence()
    
    # 요약 정보 출력
    summary = intelligence.get_intelligence_summary(intelligence_data)
    
    print(f"\n📊 데이터 개요:")
    for key, value in summary["data_overview"].items():
        print(f"  {key}: {value}")
    
    print(f"\n🌍 시장 현황:")
    market_insights = summary["market_insights"]
    print(f"  개장 시장: {market_insights.get('open_markets', 0)}개")
    print(f"  폐장 시장: {market_insights.get('closed_markets', 0)}개")
    
    print(f"\n💭 감정 분석:")
    sentiment = summary["sentiment_analysis"]
    if sentiment:
        print(f"  평균 감정: {sentiment.get('average_sentiment', 0):.3f}")
        print(f"  감정 라벨: {sentiment.get('sentiment_label', 'N/A')}")
        print(f"  분석 기사: {sentiment.get('total_articles', 0)}개")
    
    print(f"\n🔥 주요 하이라이트:")
    for highlight in summary["key_highlights"]:
        print(f"  {highlight}")
    
    # 데이터 저장
    intelligence.save_intelligence_data(intelligence_data)
    
    print(f"\n✅ Intelligence 데이터 수집 및 저장 완료!")

if __name__ == "__main__":
    test_alphavantage_intelligence()
