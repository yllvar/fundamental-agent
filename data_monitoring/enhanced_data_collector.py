"""
향상된 글로벌 경제 데이터 수집 모듈
미국, 아시아, 거시지표, 뉴스, SNS 분석 포함
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
import pandas as pd
import numpy as np
import requests
import feedparser
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

# 필요한 모듈들 import
from data_monitoring.integrated_alphavantage_collector import IntegratedAlphaVantageCollector
from data_monitoring.alphavantage_intelligence_complete import AlphaVantageIntelligenceComplete
from data_monitoring.fred_data_collector import FREDDataCollector
from data_monitoring.news_social_collector import EnhancedNewsCollector
import json

@dataclass
class MarketData:
    symbol: str
    name: str
    timestamp: datetime
    current_price: float
    previous_close: float
    change_percent: float
    volume: int
    high_24h: float
    low_24h: float
    market_cap: Optional[float] = None
    region: str = "US"

@dataclass
class NewsData:
    title: str
    summary: str
    url: str
    published: datetime
    source: str
    sentiment_score: float = 0.0
    keywords: List[str] = None

@dataclass
class EconomicIndicator:
    name: str
    value: float
    previous_value: float
    change_percent: float
    timestamp: datetime
    unit: str
    importance: str  # high, medium, low

class EnhancedGlobalDataCollector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = None
        
        # Alpha Vantage 통합
        try:
            self.alphavantage_collector = IntegratedAlphaVantageCollector()
            self.alphavantage_intelligence = AlphaVantageIntelligenceComplete()
            self.use_alphavantage = True
            self.logger.info("✅ Alpha Vantage 통합 활성화 (데이터 + Intelligence)")
        except Exception as e:
            self.logger.warning(f"Alpha Vantage 통합 실패: {e}")
            self.use_alphavantage = False
        
        # FRED 데이터 수집기 초기화
        try:
            self.fred_collector = FREDDataCollector()
            self.use_fred = True
            self.logger.info("✅ FRED 데이터 수집기 활성화")
        except Exception as e:
            self.logger.warning(f"⚠️ FRED 수집기 비활성화: {e}")
            self.use_fred = False
        
        # 강화된 뉴스 수집기 초기화
        try:
            self.news_collector = EnhancedNewsCollector()
            self.use_enhanced_news = True
            self.logger.info("✅ 강화된 뉴스 수집기 활성화")
        except Exception as e:
            self.logger.warning(f"⚠️ 강화된 뉴스 수집기 비활성화: {e}")
            self.use_enhanced_news = False
        
        # 글로벌 시장 심볼 정의
        self.market_symbols = {
            # 미국 주요 지수
            "US_INDICES": {
                "^GSPC": "S&P 500",
                "^DJI": "Dow Jones",
                "^IXIC": "NASDAQ",
                "^RUT": "Russell 2000",
                "^VIX": "VIX"
            },
            
            # 미국 주요 주식
            "US_STOCKS": {
                "AAPL": "Apple Inc",
                "MSFT": "Microsoft",
                "GOOGL": "Alphabet",
                "AMZN": "Amazon",
                "TSLA": "Tesla",
                "NVDA": "NVIDIA",
                "META": "Meta",
                "NFLX": "Netflix"
            },
            
            # 아시아 주요 지수
            "ASIA_INDICES": {
                "^KS11": "KOSPI (한국)",
                "^N225": "Nikkei 225 (일본)",
                "000001.SS": "Shanghai Composite (중국)",
                "^HSI": "Hang Seng (홍콩)",
                "^TWII": "Taiwan Weighted (대만)",
                "^STI": "Straits Times (싱가포르)"
            },
            
            # 통화
            "CURRENCIES": {
                "USDKRW=X": "USD/KRW",
                "USDJPY=X": "USD/JPY",
                "USDCNY=X": "USD/CNY",
                "EURUSD=X": "EUR/USD",
                "GBPUSD=X": "GBP/USD",
                "DX-Y.NYB": "Dollar Index (DXY)"  # DXY 대체 심볼
            },
            
            # 원자재
            "COMMODITIES": {
                "GC=F": "Gold",
                "CL=F": "Crude Oil",
                "BTC-USD": "Bitcoin",
                "ETH-USD": "Ethereum"
            },
            
            # 채권
            "BONDS": {
                "^TNX": "10-Year Treasury",
                "^TYX": "30-Year Treasury",
                "^FVX": "5-Year Treasury"
            }
        }
        
        # 뉴스 소스 정의
        self.news_sources = {
            "FINANCIAL": [
                "https://feeds.bloomberg.com/markets/news.rss",
                "https://feeds.reuters.com/reuters/businessNews",
                "https://rss.cnn.com/rss/money_latest.rss",
                "https://feeds.marketwatch.com/marketwatch/topstories/",
                "https://feeds.finance.yahoo.com/rss/2.0/headline"
            ],
            "ECONOMIC": [
                "https://www.federalreserve.gov/feeds/press_all.xml",
                "https://feeds.reuters.com/reuters/economicNews"
            ],
            "ASIA": [
                "https://feeds.reuters.com/reuters/asiaNews",
                "https://english.yonhapnews.co.kr/RSS/news.xml"
            ]
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def collect_market_data_safe(self, symbol: str, region: str = "US") -> Optional[MarketData]:
        """안전한 시장 데이터 수집 (오류 처리 강화)"""
        try:
            # DXY 특별 처리
            if symbol in ["DXY", "$DXY"]:
                symbol = "DX-Y.NYB"  # Yahoo Finance의 올바른 DXY 심볼
            
            ticker = yf.Ticker(symbol)
            
            # 여러 기간으로 시도
            hist = None
            for period in ["2d", "5d", "1mo"]:
                try:
                    hist = ticker.history(period=period)
                    if not hist.empty and len(hist) >= 2:
                        break
                except:
                    continue
            
            if hist is None or hist.empty:
                self.logger.warning(f"No data found for symbol: {symbol}")
                return None
            
            # 정보 가져오기 (실패해도 계속 진행)
            info = {}
            try:
                info = ticker.info
            except:
                self.logger.debug(f"Could not get info for {symbol}, using defaults")
            
            current_data = hist.iloc[-1]
            previous_data = hist.iloc[-2] if len(hist) > 1 else current_data
            
            # 변화율 계산
            change_percent = 0.0
            if previous_data['Close'] != 0:
                change_percent = ((current_data['Close'] - previous_data['Close']) / previous_data['Close']) * 100
            
            return MarketData(
                symbol=symbol,
                name=info.get('longName', self._get_symbol_name(symbol)),
                timestamp=datetime.now(),
                current_price=float(current_data['Close']),
                previous_close=float(previous_data['Close']),
                change_percent=float(change_percent),
                volume=int(current_data.get('Volume', 0)),
                high_24h=float(current_data['High']),
                low_24h=float(current_data['Low']),
                market_cap=info.get('marketCap'),
                region=region
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting data for {symbol}: {str(e)}")
            return None
    
    def _get_symbol_name(self, symbol: str) -> str:
        """심볼에서 이름 추출"""
        for category, symbols in self.market_symbols.items():
            if symbol in symbols:
                return symbols[symbol]
        return symbol
    
    async def collect_all_market_data(self) -> Dict[str, Dict[str, MarketData]]:
        """모든 시장 데이터 수집"""
        results = {}
        
        for category, symbols in self.market_symbols.items():
            self.logger.info(f"Collecting {category} data...")
            category_data = {}
            
            for symbol, name in symbols.items():
                region = "ASIA" if "ASIA" in category else "US"
                data = await asyncio.to_thread(self.collect_market_data_safe, symbol, region)
                if data:
                    category_data[symbol] = data
                    self.logger.debug(f"✅ {symbol}: {data.current_price}")
                else:
                    self.logger.warning(f"❌ Failed to collect data for {symbol}")
            
            results[category] = category_data
        
        return results
    
    def collect_news_data(self, max_articles: int = 50) -> List[NewsData]:
        """뉴스 데이터 수집"""
        all_news = []
        
        for category, sources in self.news_sources.items():
            self.logger.info(f"Collecting {category} news...")
            
            for source_url in sources:
                try:
                    feed = feedparser.parse(source_url)
                    
                    for entry in feed.entries[:10]:  # 각 소스에서 최대 10개
                        try:
                            published = datetime.now()
                            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                published = datetime(*entry.published_parsed[:6])
                            
                            # 간단한 감정 분석 (키워드 기반)
                            sentiment_score = self._analyze_sentiment(entry.title + " " + entry.get('summary', ''))
                            
                            # 키워드 추출
                            keywords = self._extract_keywords(entry.title + " " + entry.get('summary', ''))
                            
                            news_item = NewsData(
                                title=entry.title,
                                summary=entry.get('summary', '')[:500],  # 500자 제한
                                url=entry.link,
                                published=published,
                                source=feed.feed.get('title', 'Unknown'),
                                sentiment_score=sentiment_score,
                                keywords=keywords
                            )
                            
                            all_news.append(news_item)
                            
                        except Exception as e:
                            self.logger.debug(f"Error processing news entry: {e}")
                            continue
                
                except Exception as e:
                    self.logger.warning(f"Error fetching news from {source_url}: {e}")
                    continue
        
        # 최신 뉴스 순으로 정렬하고 제한
        all_news.sort(key=lambda x: x.published, reverse=True)
        return all_news[:max_articles]
    
    def _analyze_sentiment(self, text: str) -> float:
        """간단한 감정 분석 (키워드 기반)"""
        positive_words = [
            'gain', 'rise', 'up', 'surge', 'rally', 'boost', 'strong', 'growth', 
            'positive', 'bullish', 'optimistic', 'recovery', 'improve', 'advance'
        ]
        
        negative_words = [
            'fall', 'drop', 'down', 'decline', 'crash', 'weak', 'loss', 'negative',
            'bearish', 'pessimistic', 'recession', 'crisis', 'concern', 'worry'
        ]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.0
        
        # -1 (매우 부정) ~ 1 (매우 긍정)
        sentiment = (positive_count - negative_count) / max(total_words / 10, 1)
        return max(-1.0, min(1.0, sentiment))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        # 경제/금융 관련 키워드
        economic_keywords = [
            'inflation', 'interest rate', 'fed', 'gdp', 'unemployment', 'earnings',
            'revenue', 'profit', 'stock', 'market', 'trading', 'investment',
            'economy', 'financial', 'monetary', 'fiscal', 'policy', 'bank',
            'cryptocurrency', 'bitcoin', 'ethereum', 'oil', 'gold', 'dollar'
        ]
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in economic_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords[:5]  # 최대 5개 키워드
    
    def collect_economic_indicators(self) -> List[EconomicIndicator]:
        """경제 지표 수집 (시뮬레이션)"""
        # 실제로는 FRED API, 경제 데이터 API 등을 사용
        indicators = []
        
        try:
            # VIX를 변동성 지표로 사용
            vix_data = self.collect_market_data_safe("^VIX")
            if vix_data:
                indicators.append(EconomicIndicator(
                    name="Market Volatility (VIX)",
                    value=vix_data.current_price,
                    previous_value=vix_data.previous_close,
                    change_percent=vix_data.change_percent,
                    timestamp=datetime.now(),
                    unit="Index",
                    importance="high"
                ))
            
            # 10년 국채 수익률
            treasury_data = self.collect_market_data_safe("^TNX")
            if treasury_data:
                indicators.append(EconomicIndicator(
                    name="10-Year Treasury Yield",
                    value=treasury_data.current_price,
                    previous_value=treasury_data.previous_close,
                    change_percent=treasury_data.change_percent,
                    timestamp=datetime.now(),
                    unit="Percent",
                    importance="high"
                ))
            
        except Exception as e:
            self.logger.error(f"Error collecting economic indicators: {e}")
        
        return indicators
    
    def analyze_market_sentiment(self, news_data: List[NewsData]) -> Dict[str, Any]:
        """시장 감정 분석"""
        if not news_data:
            return {"overall_sentiment": 0.0, "sentiment_distribution": {}}
        
        sentiments = [news.sentiment_score for news in news_data]
        
        overall_sentiment = np.mean(sentiments)
        
        # 감정 분포
        positive_count = sum(1 for s in sentiments if s > 0.1)
        negative_count = sum(1 for s in sentiments if s < -0.1)
        neutral_count = len(sentiments) - positive_count - negative_count
        
        # 키워드 빈도 분석
        all_keywords = []
        for news in news_data:
            if news.keywords:
                all_keywords.extend(news.keywords)
        
        keyword_freq = {}
        for keyword in all_keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        # 상위 키워드
        top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "overall_sentiment": float(overall_sentiment),
            "sentiment_distribution": {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count
            },
            "top_keywords": top_keywords,
            "total_articles": len(news_data)
        }
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """종합 시장 리포트 생성"""
        self.logger.info("Generating comprehensive market report...")
        
        # 시장 데이터 수집 (동기 방식으로 변경)
        market_data = self._collect_market_data_sync()
        
        # 뉴스 데이터 수집
        news_data = self.collect_news_data()
        
        # 경제 지표 수집
        economic_indicators = self.collect_economic_indicators()
        
        # 감정 분석
        sentiment_analysis = self.analyze_market_sentiment(news_data)
        
        # 리포트 생성
        report = {
            "timestamp": datetime.now().isoformat(),
            "market_data": self._serialize_market_data(market_data),
            "news_summary": {
                "total_articles": len(news_data),
                "latest_articles": [
                    {
                        "title": news.title,
                        "source": news.source,
                        "sentiment": news.sentiment_score,
                        "published": news.published.isoformat()
                    }
                    for news in news_data[:5]
                ]
            },
            "economic_indicators": [
                {
                    "name": indicator.name,
                    "value": indicator.value,
                    "change_percent": indicator.change_percent,
                    "importance": indicator.importance
                }
                for indicator in economic_indicators
            ],
            "sentiment_analysis": sentiment_analysis,
            "market_summary": self._generate_market_summary(market_data)
        }
        
        return report
    
    def _collect_market_data_sync(self) -> Dict[str, Dict[str, MarketData]]:
        """동기 방식으로 시장 데이터 수집 (Alpha Vantage 우선)"""
        results = {}
        
        # Alpha Vantage 데이터 우선 수집
        if self.use_alphavantage:
            try:
                self.logger.info("🚀 Alpha Vantage 고품질 데이터 수집 중...")
                av_data = self.alphavantage_collector.collect_priority_data()
                
                # Alpha Vantage 데이터를 기존 형식으로 변환
                if av_data.get("stocks"):
                    results["ALPHAVANTAGE_STOCKS"] = {}
                    for stock_data in av_data["stocks"]:
                        market_data = MarketData(
                            symbol=stock_data.symbol,
                            name=stock_data.name,
                            timestamp=stock_data.timestamp,
                            current_price=stock_data.current_price,
                            previous_close=stock_data.previous_close,
                            change_percent=stock_data.change_percent,
                            volume=stock_data.volume,
                            high_24h=stock_data.high_24h,
                            low_24h=stock_data.low_24h,
                            market_cap=None,
                            region="US"
                        )
                        results["ALPHAVANTAGE_STOCKS"][stock_data.symbol] = market_data
                
                if av_data.get("indices"):
                    results["ALPHAVANTAGE_INDICES"] = {}
                    for index_data in av_data["indices"]:
                        market_data = MarketData(
                            symbol=index_data.symbol,
                            name=index_data.name,
                            timestamp=index_data.timestamp,
                            current_price=index_data.current_price,
                            previous_close=index_data.previous_close,
                            change_percent=index_data.change_percent,
                            volume=index_data.volume,
                            high_24h=index_data.high_24h,
                            low_24h=index_data.low_24h,
                            market_cap=None,
                            region="US"
                        )
                        results["ALPHAVANTAGE_INDICES"][index_data.symbol] = market_data
                
                if av_data.get("forex"):
                    results["ALPHAVANTAGE_FOREX"] = {}
                    for forex_data in av_data["forex"]:
                        market_data = MarketData(
                            symbol=forex_data.symbol,
                            name=forex_data.name,
                            timestamp=forex_data.timestamp,
                            current_price=forex_data.current_price,
                            previous_close=forex_data.previous_close,
                            change_percent=forex_data.change_percent,
                            volume=forex_data.volume,
                            high_24h=forex_data.high_24h,
                            low_24h=forex_data.low_24h,
                            market_cap=None,
                            region="GLOBAL"
                        )
                        results["ALPHAVANTAGE_FOREX"][forex_data.symbol] = market_data
                
                self.logger.info(f"✅ Alpha Vantage 데이터 수집 완료: {sum(len(v) for v in results.values())}개")
                
            except Exception as e:
                self.logger.error(f"Alpha Vantage 데이터 수집 오류: {e}")
        
        # 기존 Yahoo Finance 데이터로 보완
        for category, symbols in self.market_symbols.items():
            # Alpha Vantage에서 이미 수집한 카테고리는 건너뛰기
            if f"ALPHAVANTAGE_{category}" in results:
                continue
                
            self.logger.info(f"Collecting {category} data (Yahoo Finance)...")
            category_data = {}
            
            for symbol, name in symbols.items():
                region = "ASIA" if "ASIA" in category else "US"
                data = self.collect_market_data_safe(symbol, region)
                if data:
                    category_data[symbol] = data
                    self.logger.debug(f"✅ {symbol}: {data.current_price}")
                else:
                    self.logger.warning(f"❌ Failed to collect data for {symbol}")
            
            results[category] = category_data
        
        return results
    
    async def _collect_market_data_async(self):
        """비동기 시장 데이터 수집"""
        return await asyncio.to_thread(self.collect_all_market_data)
    
    def _serialize_market_data(self, market_data: Dict[str, Dict[str, MarketData]]) -> Dict:
        """시장 데이터 직렬화"""
        serialized = {}
        for category, data_dict in market_data.items():
            serialized[category] = {}
            for symbol, data in data_dict.items():
                serialized[category][symbol] = {
                    "name": data.name,
                    "current_price": data.current_price,
                    "change_percent": data.change_percent,
                    "volume": data.volume,
                    "region": data.region
                }
        return serialized
    
    def _generate_market_summary(self, market_data: Dict[str, Dict[str, MarketData]]) -> Dict[str, Any]:
        """시장 요약 생성"""
        summary = {
            "us_market_status": "neutral",
            "asia_market_status": "neutral",
            "major_movers": [],
            "risk_indicators": {}
        }
        
        try:
            # 미국 시장 상태
            us_indices = market_data.get("US_INDICES", {})
            if us_indices:
                us_changes = [data.change_percent for data in us_indices.values()]
                avg_change = np.mean(us_changes)
                summary["us_market_status"] = "bullish" if avg_change > 1 else "bearish" if avg_change < -1 else "neutral"
            
            # 아시아 시장 상태
            asia_indices = market_data.get("ASIA_INDICES", {})
            if asia_indices:
                asia_changes = [data.change_percent for data in asia_indices.values()]
                avg_change = np.mean(asia_changes)
                summary["asia_market_status"] = "bullish" if avg_change > 1 else "bearish" if avg_change < -1 else "neutral"
            
            # 주요 변동 종목
            all_data = []
            for category_data in market_data.values():
                all_data.extend(category_data.values())
            
            # 변동률 기준 정렬
            sorted_by_change = sorted(all_data, key=lambda x: abs(x.change_percent), reverse=True)
            summary["major_movers"] = [
                {
                    "symbol": data.symbol,
                    "name": data.name,
                    "change_percent": data.change_percent
                }
                for data in sorted_by_change[:5]
            ]
            
            # 리스크 지표
            vix_data = None
            for category_data in market_data.values():
                for symbol, data in category_data.items():
                    if symbol == "^VIX":
                        vix_data = data
                        break
            
            if vix_data:
                summary["risk_indicators"]["vix"] = {
                    "value": vix_data.current_price,
                    "level": "high" if vix_data.current_price > 25 else "medium" if vix_data.current_price > 15 else "low"
                }
        
        except Exception as e:
            self.logger.error(f"Error generating market summary: {e}")
        
        return summary
    
    def collect_intelligence_data(self) -> Dict[str, Any]:
        """Alpha Vantage Intelligence API 데이터 수집 (최적화된 버전)"""
        if not self.use_alphavantage:
            return {}
        
        try:
            self.logger.info("🧠 Intelligence 데이터 수집 시작...")
            intelligence_data = self.alphavantage_intelligence.collect_comprehensive_intelligence()
            
            # 데이터 요약 (최적화된 구조)
            summary = intelligence_data.get('summary', {})
            data_counts = summary.get('data_counts', {})
            market_analysis = summary.get('market_analysis', {})
            
            optimized_summary = {
                'market_status_count': data_counts.get('market_status', 0),
                'top_gainers_count': data_counts.get('top_gainers', 0),
                'top_losers_count': data_counts.get('top_losers', 0),
                'most_active_count': data_counts.get('most_active', 0),
                'open_markets_count': market_analysis.get('open_markets', 0),
                'market_volatility': 'unknown'  # 추후 계산 로직 추가
            }
            
            self.logger.info(f"✅ Intelligence 데이터 수집 완료: {optimized_summary}")
            
            return {
                'data': intelligence_data,
                'summary': optimized_summary,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Intelligence 데이터 수집 오류: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'status': 'failed'
            }
    
    def collect_fred_data(self) -> Dict[str, Any]:
        """FRED 경제 데이터 수집"""
        if not hasattr(self, 'use_fred') or not self.use_fred:
            return {}
        
        try:
            self.logger.info("📊 FRED 경제 데이터 수집 시작...")
            fred_data = self.fred_collector.collect_key_indicators()
            
            summary = fred_data.get('summary', {})
            self.logger.info(f"✅ FRED 데이터 수집 완료: {summary.get('collected_indicators', 0)}개 지표")
            
            return {
                'data': fred_data,
                'summary': summary,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"FRED 데이터 수집 오류: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'status': 'failed'
            }
    
    def collect_enhanced_news_data(self) -> Dict[str, Any]:
        """강화된 뉴스 및 소셜미디어 데이터 수집"""
        if not hasattr(self, 'use_enhanced_news') or not self.use_enhanced_news:
            return {}
        
        try:
            self.logger.info("📰 강화된 뉴스 데이터 수집 시작...")
            
            # 뉴스 데이터 수집
            news_data = self.news_collector.collect_news_by_category(max_items_per_source=8)
            
            # 소셜미디어 데이터 수집
            social_data = self.news_collector.get_social_media_mentions()
            
            # 통합 데이터 구성
            enhanced_news = {
                'news_data': news_data,
                'social_data': social_data,
                'combined_summary': self._generate_combined_news_summary(news_data, social_data)
            }
            
            news_summary = news_data.get('summary', {})
            self.logger.info(f"✅ 강화된 뉴스 수집 완료: {news_summary.get('total_articles', 0)}개 기사")
            
            return {
                'data': enhanced_news,
                'summary': enhanced_news['combined_summary'],
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"강화된 뉴스 수집 오류: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'status': 'failed'
            }
    
    def _generate_combined_news_summary(self, news_data: Dict, social_data: Dict) -> Dict[str, Any]:
        """뉴스와 소셜미디어 데이터 통합 요약"""
        try:
            news_summary = news_data.get('summary', {})
            news_sentiment = news_summary.get('sentiment_analysis', {})
            social_sentiment = social_data.get('overall_sentiment', {})
            
            combined_summary = {
                'total_articles': news_summary.get('total_articles', 0),
                'news_sentiment': {
                    'positive_ratio': news_sentiment.get('positive_ratio', 0),
                    'negative_ratio': news_sentiment.get('negative_ratio', 0)
                },
                'social_sentiment': {
                    'score': social_sentiment.get('score', 0),
                    'label': social_sentiment.get('label', 'neutral')
                },
                'trending_topics': news_summary.get('trending_topics', {}),
                'social_mentions': {
                    'twitter': social_data.get('platforms', {}).get('twitter', {}).get('mentions', 0),
                    'reddit_posts': social_data.get('platforms', {}).get('reddit', {}).get('posts', 0)
                },
                'overall_market_sentiment': self._calculate_overall_sentiment(news_sentiment, social_sentiment)
            }
            
            return combined_summary
            
        except Exception as e:
            self.logger.error(f"통합 요약 생성 오류: {e}")
            return {}
    
    def _calculate_overall_sentiment(self, news_sentiment: Dict, social_sentiment: Dict) -> Dict[str, Any]:
        """전체 시장 감정 계산"""
        try:
            # 뉴스 감정 점수 (0-1 범위로 정규화)
            news_positive = news_sentiment.get('positive_ratio', 0) / 100
            news_negative = news_sentiment.get('negative_ratio', 0) / 100
            news_score = news_positive - news_negative
            
            # 소셜미디어 감정 점수 (-1 to 1)
            social_score = social_sentiment.get('score', 0)
            
            # 가중 평균 (뉴스 70%, 소셜미디어 30%)
            overall_score = (news_score * 0.7) + (social_score * 0.3)
            
            # 라벨링
            if overall_score > 0.2:
                label = "매우 긍정적"
            elif overall_score > 0.05:
                label = "긍정적"
            elif overall_score > -0.05:
                label = "중립"
            elif overall_score > -0.2:
                label = "부정적"
            else:
                label = "매우 부정적"
            
            return {
                'score': round(overall_score, 3),
                'label': label,
                'news_weight': 0.7,
                'social_weight': 0.3
            }
            
        except Exception as e:
            self.logger.error(f"전체 감정 계산 오류: {e}")
            return {'score': 0, 'label': '중립', 'news_weight': 0.7, 'social_weight': 0.3}
        
        try:
            self.logger.info("🧠 Intelligence 데이터 수집 시작...")
            intelligence_data = self.alphavantage_intelligence.collect_comprehensive_intelligence()
            
            # 데이터 요약 (최적화된 구조)
            summary = {
                'market_status_count': len(intelligence_data.get('market_status', [])),
                'top_gainers_count': len(intelligence_data.get('top_gainers_losers', {}).get('top_gainers', [])),
                'top_losers_count': len(intelligence_data.get('top_gainers_losers', {}).get('top_losers', [])),
                'most_active_count': len(intelligence_data.get('top_gainers_losers', {}).get('most_actively_traded', [])),
                'open_markets_count': 0,
                'market_volatility': 'unknown'
            }
            
            # 추가 분석
            if 'summary' in intelligence_data:
                intel_summary = intelligence_data['summary']
                if 'market_analysis' in intel_summary:
                    summary['open_markets_count'] = intel_summary['market_analysis'].get('open_markets', 0)
                if 'risk_indicators' in intel_summary:
                    summary['market_volatility'] = intel_summary['risk_indicators'].get('volatility_level', 'unknown')
            
            self.logger.info(f"✅ Intelligence 데이터 수집 완료: {summary}")
            
            return {
                'data': intelligence_data,
                'summary': summary,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Intelligence 데이터 수집 오류: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'status': 'failed'
            }
    
    async def generate_comprehensive_report_async(self) -> Dict[str, Any]:
        """종합 리포트 생성 (비동기 버전)"""
        try:
            # 기존 데이터 수집
            market_data = await self.collect_all_market_data()
            news_data = self.collect_news_data(max_articles=10)
            intelligence_data = self.collect_intelligence_data()
            
            # 시장 요약
            market_summary = self._generate_market_summary(market_data)
            
            # 감정 분석
            sentiment_scores = [news.sentiment_score for news in news_data if news.sentiment_score is not None]
            overall_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0.0
            
            # Intelligence 인사이트
            intelligence_insights = {}
            if intelligence_data and 'data' in intelligence_data:
                intel_data = intelligence_data['data']
                
                # 시장 상태 분석
                if 'market_status' in intel_data:
                    open_markets = [m for m in intel_data['market_status'] if m.get('current_status') == 'open']
                    intelligence_insights['open_markets_count'] = len(open_markets)
                
                # 주요 변동 종목
                if 'top_gainers_losers' in intel_data:
                    movers = intel_data['top_gainers_losers']
                    if 'top_gainers' in movers and movers['top_gainers']:
                        top_gainer = movers['top_gainers'][0]
                        intelligence_insights['top_gainer'] = {
                            'ticker': top_gainer.get('ticker'),
                            'change_percentage': top_gainer.get('change_percentage')
                        }
                    
                    if 'top_losers' in movers and movers['top_losers']:
                        top_loser = movers['top_losers'][0]
                        intelligence_insights['top_loser'] = {
                            'ticker': top_loser.get('ticker'),
                            'change_percentage': top_loser.get('change_percentage')
                        }
            
            return {
                'timestamp': datetime.now().isoformat(),
                'market_data': self._serialize_market_data(market_data),
                'market_summary': market_summary,
                'news_data': [
                    {
                        'title': news.title,
                        'source': news.source,
                        'sentiment_score': news.sentiment_score,
                        'published_date': news.published.isoformat() if news.published else None
                    }
                    for news in news_data
                ],
                'sentiment_analysis': {
                    'overall_sentiment': overall_sentiment,
                    'sentiment_distribution': {
                        'positive': len([s for s in sentiment_scores if s > 0.1]),
                        'neutral': len([s for s in sentiment_scores if -0.1 <= s <= 0.1]),
                        'negative': len([s for s in sentiment_scores if s < -0.1])
                    }
                },
                'intelligence_data': intelligence_data,
                'intelligence_insights': intelligence_insights,
                'data_sources': {
                    'market_data_sources': list(market_data.keys()),
                    'news_sources_count': len(self.news_sources),
                    'alphavantage_enabled': self.use_alphavantage,
                    'intelligence_enabled': bool(intelligence_data)
                }
            }
            
        except Exception as e:
            self.logger.error(f"종합 리포트 생성 오류: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'status': 'failed'
            }
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """종합 리포트 생성 (동기 버전)"""
        try:
            # 기존 데이터 수집 (동기 방식)
            market_data = {}
            news_data = self.collect_news_data(max_articles=10)
            intelligence_data = self.collect_intelligence_data()
            
            # 시장 요약
            market_summary = {}
            
            # 감정 분석
            sentiment_scores = [news.sentiment_score for news in news_data if news.sentiment_score is not None]
            overall_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0.0
            
            # Intelligence 인사이트
            intelligence_insights = {}
            if intelligence_data and 'data' in intelligence_data:
                intel_data = intelligence_data['data']
                
                # 시장 상태 분석
                if 'market_status' in intel_data:
                    open_markets = [m for m in intel_data['market_status'] if m.get('current_status') == 'open']
                    intelligence_insights['open_markets_count'] = len(open_markets)
                
                # 주요 변동 종목
                if 'top_gainers_losers' in intel_data:
                    movers = intel_data['top_gainers_losers']
                    if 'top_gainers' in movers and movers['top_gainers']:
                        top_gainer = movers['top_gainers'][0]
                        intelligence_insights['top_gainer'] = {
                            'ticker': top_gainer.get('ticker'),
                            'change_percentage': top_gainer.get('change_percentage')
                        }
                    
                    if 'top_losers' in movers and movers['top_losers']:
                        top_loser = movers['top_losers'][0]
                        intelligence_insights['top_loser'] = {
                            'ticker': top_loser.get('ticker'),
                            'change_percentage': top_loser.get('change_percentage')
                        }
            
            return {
                'timestamp': datetime.now().isoformat(),
                'market_data': market_data,
                'market_summary': market_summary,
                'news_data': [
                    {
                        'title': news.title,
                        'source': news.source,
                        'sentiment_score': news.sentiment_score,
                        'published_date': news.published.isoformat() if news.published else None
                    }
                    for news in news_data
                ],
                'sentiment_analysis': {
                    'overall_sentiment': overall_sentiment,
                    'sentiment_distribution': {
                        'positive': len([s for s in sentiment_scores if s > 0.1]),
                        'neutral': len([s for s in sentiment_scores if -0.1 <= s <= 0.1]),
                        'negative': len([s for s in sentiment_scores if s < -0.1])
                    }
                },
                'intelligence_data': intelligence_data,
                'intelligence_insights': intelligence_insights,
                'data_sources': {
                    'market_data_sources': [],
                    'news_sources_count': len(self.news_sources),
                    'alphavantage_enabled': self.use_alphavantage,
                    'intelligence_enabled': bool(intelligence_data)
                }
            }
            
        except Exception as e:
            self.logger.error(f"종합 리포트 생성 오류: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'status': 'failed'
            }

# 테스트 함수
async def test_enhanced_collector():
    collector = EnhancedGlobalDataCollector()
    
    print("🔍 Enhanced Global Data Collector Test")
    print("=" * 50)
    
    # 1. 시장 데이터 테스트
    print("\n📊 Market Data Collection:")
    market_data = await collector.collect_all_market_data()
    
    for category, data_dict in market_data.items():
        print(f"\n{category}:")
        for symbol, data in data_dict.items():
            print(f"  {symbol}: {data.current_price:.2f} ({data.change_percent:+.2f}%)")
    
    # 2. 뉴스 데이터 테스트
    print("\n📰 News Data Collection:")
    news_data = collector.collect_news_data(max_articles=5)
    for news in news_data:
        print(f"  📄 {news.title[:60]}... (Sentiment: {news.sentiment_score:.2f})")
    
    # 3. Intelligence 데이터 테스트
    print("\n🧠 Intelligence Data Collection:")
    intelligence_data = collector.collect_intelligence_data()
    if intelligence_data and 'summary' in intelligence_data:
        summary = intelligence_data['summary']
        print(f"  📊 Market Status: {summary['market_status_count']}개")
        print(f"  📰 News Articles: {summary['news_articles_count']}개")
        print(f"  📈 Top Movers: {summary['top_movers_categories']}개 카테고리")
        print(f"  🔍 Analytics: {summary['analytics_symbols_count']}개 심볼")
    else:
        print("  ❌ Intelligence 데이터 수집 실패")
    
    # 4. 종합 리포트 테스트 (비동기 버전)
    print("\n📋 Comprehensive Report (Async):")
    report = await collector.generate_comprehensive_report_async()
    print(f"  Market Summary: {report.get('market_summary', {})}")
    print(f"  Sentiment: {report.get('sentiment_analysis', {}).get('overall_sentiment', 0):.2f}")
    
    if 'intelligence_insights' in report:
        insights = report['intelligence_insights']
        print(f"  Intelligence Insights:")
        if 'open_markets_count' in insights:
            print(f"    - 개장 시장: {insights['open_markets_count']}개")
        if 'top_gainer' in insights:
            gainer = insights['top_gainer']
            print(f"    - 최고 상승: {gainer['ticker']} ({gainer['change_percentage']}%)")
        if 'top_loser' in insights:
            loser = insights['top_loser']
            print(f"    - 최고 하락: {loser['ticker']} ({loser['change_percentage']}%)")

if __name__ == "__main__":
    asyncio.run(test_enhanced_collector())
