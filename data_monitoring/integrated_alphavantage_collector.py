"""
통합 Alpha Vantage 데이터 수집기
기존 모니터링 시스템과 통합하여 고품질 실시간 데이터 제공
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
import asyncio

@dataclass
class AlphaVantageMarketData:
    symbol: str
    name: str
    timestamp: datetime
    current_price: float
    previous_close: float
    change_percent: float
    volume: int
    high_24h: float
    low_24h: float
    data_source: str = "AlphaVantage"
    data_quality: str = "high"

class IntegratedAlphaVantageCollector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = self._load_api_key()
        self.base_url = "https://www.alphavantage.co/query"
        
        # API 호출 제한 (5 calls per minute for free tier)
        self.call_interval = 12  # seconds between calls
        self.last_call_time = 0
        
        # 우선순위 심볼 (API 제한 고려)
        self.priority_symbols = {
            "US_STOCKS": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META"],
            "INDICES": ["SPY", "QQQ", "IWM"],  # ETF로 지수 대체
            "FOREX": [("USD", "KRW"), ("USD", "JPY"), ("EUR", "USD")],
            "CRYPTO": ["BTC", "ETH"]
        }
        
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
            
            self.logger.info("✅ Alpha Vantage API 키 로드 완료")
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
    
    def get_stock_data(self, symbol: str) -> Optional[AlphaVantageMarketData]:
        """주식 데이터 수집 (Alpha Vantage)"""
        self._wait_for_rate_limit()
        
        try:
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": "5min",
                "outputsize": "compact",
                "apikey": self.api_key,
                "datatype": "json"
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # 오류 체크
            if "Error Message" in data:
                self.logger.error(f"API Error for {symbol}: {data['Error Message']}")
                return None
            
            if "Note" in data:
                self.logger.warning(f"API Rate limit for {symbol}: {data['Note']}")
                return None
            
            # 데이터 파싱
            time_series_key = "Time Series (5min)"
            if time_series_key not in data:
                self.logger.warning(f"No time series data for {symbol}")
                return None
            
            time_series = data[time_series_key]
            if not time_series:
                return None
            
            # 최신 데이터와 이전 데이터 추출
            sorted_times = sorted(time_series.keys(), reverse=True)
            latest_time = sorted_times[0]
            latest_data = time_series[latest_time]
            
            # 이전 데이터 (변화율 계산용)
            previous_data = time_series[sorted_times[1]] if len(sorted_times) > 1 else latest_data
            
            current_price = float(latest_data["4. close"])
            previous_price = float(previous_data["4. close"])
            
            # 변화율 계산
            change_percent = 0.0
            if previous_price != 0:
                change_percent = ((current_price - previous_price) / previous_price) * 100
            
            # 24시간 고가/저가 계산 (최근 데이터에서)
            prices = [float(time_series[t]["2. high"]) for t in sorted_times[:20]]  # 최근 20개 포인트
            low_prices = [float(time_series[t]["3. low"]) for t in sorted_times[:20]]
            
            high_24h = max(prices) if prices else current_price
            low_24h = min(low_prices) if low_prices else current_price
            
            market_data = AlphaVantageMarketData(
                symbol=symbol,
                name=self._get_company_name(symbol),
                timestamp=datetime.strptime(latest_time, "%Y-%m-%d %H:%M:%S"),
                current_price=current_price,
                previous_close=previous_price,
                change_percent=change_percent,
                volume=int(latest_data["5. volume"]),
                high_24h=high_24h,
                low_24h=low_24h
            )
            
            self.logger.info(f"✅ {symbol}: ${current_price:.2f} ({change_percent:+.2f}%)")
            return market_data
            
        except Exception as e:
            self.logger.error(f"Error getting stock data for {symbol}: {e}")
            return None
    
    def get_forex_data(self, from_currency: str, to_currency: str) -> Optional[AlphaVantageMarketData]:
        """외환 데이터 수집"""
        self._wait_for_rate_limit()
        
        try:
            params = {
                "function": "FX_INTRADAY",
                "from_symbol": from_currency,
                "to_symbol": to_currency,
                "interval": "5min",
                "outputsize": "compact",
                "apikey": self.api_key,
                "datatype": "json"
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "Error Message" in data or "Note" in data:
                return None
            
            time_series_key = "Time Series FX (5min)"
            if time_series_key not in data:
                return None
            
            time_series = data[time_series_key]
            if not time_series:
                return None
            
            # 최신 데이터 추출
            sorted_times = sorted(time_series.keys(), reverse=True)
            latest_time = sorted_times[0]
            latest_data = time_series[latest_time]
            
            previous_data = time_series[sorted_times[1]] if len(sorted_times) > 1 else latest_data
            
            current_price = float(latest_data["4. close"])
            previous_price = float(previous_data["4. close"])
            
            change_percent = 0.0
            if previous_price != 0:
                change_percent = ((current_price - previous_price) / previous_price) * 100
            
            # 고가/저가
            prices = [float(time_series[t]["2. high"]) for t in sorted_times[:20]]
            low_prices = [float(time_series[t]["3. low"]) for t in sorted_times[:20]]
            
            forex_data = AlphaVantageMarketData(
                symbol=f"{from_currency}{to_currency}=X",
                name=f"{from_currency}/{to_currency}",
                timestamp=datetime.strptime(latest_time, "%Y-%m-%d %H:%M:%S"),
                current_price=current_price,
                previous_close=previous_price,
                change_percent=change_percent,
                volume=0,  # FX doesn't have volume
                high_24h=max(prices) if prices else current_price,
                low_24h=min(low_prices) if low_prices else current_price
            )
            
            self.logger.info(f"✅ {from_currency}/{to_currency}: {current_price:.4f} ({change_percent:+.2f}%)")
            return forex_data
            
        except Exception as e:
            self.logger.error(f"Error getting forex data for {from_currency}/{to_currency}: {e}")
            return None
    
    def get_crypto_data(self, symbol: str, market: str = "USD") -> Optional[AlphaVantageMarketData]:
        """암호화폐 데이터 수집"""
        self._wait_for_rate_limit()
        
        try:
            params = {
                "function": "CRYPTO_INTRADAY",
                "symbol": symbol,
                "market": market,
                "interval": "5min",
                "outputsize": "compact",
                "apikey": self.api_key,
                "datatype": "json"
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "Error Message" in data or "Note" in data:
                return None
            
            time_series_key = "Time Series (Crypto)"
            if time_series_key not in data:
                return None
            
            time_series = data[time_series_key]
            if not time_series:
                return None
            
            # 최신 데이터 추출
            sorted_times = sorted(time_series.keys(), reverse=True)
            latest_time = sorted_times[0]
            latest_data = time_series[latest_time]
            
            previous_data = time_series[sorted_times[1]] if len(sorted_times) > 1 else latest_data
            
            current_price = float(latest_data["4a. close (USD)"])
            previous_price = float(previous_data["4a. close (USD)"])
            
            change_percent = 0.0
            if previous_price != 0:
                change_percent = ((current_price - previous_price) / previous_price) * 100
            
            crypto_data = AlphaVantageMarketData(
                symbol=f"{symbol}-{market}",
                name=f"{symbol}/{market}",
                timestamp=datetime.strptime(latest_time, "%Y-%m-%d %H:%M:%S"),
                current_price=current_price,
                previous_close=previous_price,
                change_percent=change_percent,
                volume=int(float(latest_data["5. volume"])),
                high_24h=float(latest_data["2a. high (USD)"]),
                low_24h=float(latest_data["3a. low (USD)"])
            )
            
            self.logger.info(f"✅ {symbol}/{market}: ${current_price:.2f} ({change_percent:+.2f}%)")
            return crypto_data
            
        except Exception as e:
            self.logger.error(f"Error getting crypto data for {symbol}: {e}")
            return None
    
    def _get_company_name(self, symbol: str) -> str:
        """심볼에서 회사명 추출 (간단한 매핑)"""
        company_names = {
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corporation",
            "GOOGL": "Alphabet Inc.",
            "AMZN": "Amazon.com Inc.",
            "TSLA": "Tesla Inc.",
            "NVDA": "NVIDIA Corporation",
            "META": "Meta Platforms Inc.",
            "SPY": "SPDR S&P 500 ETF",
            "QQQ": "Invesco QQQ ETF",
            "IWM": "iShares Russell 2000 ETF"
        }
        return company_names.get(symbol, symbol)
    
    def collect_priority_data(self) -> Dict[str, List[AlphaVantageMarketData]]:
        """우선순위 데이터 수집 (API 제한 고려)"""
        self.logger.info("🚀 Alpha Vantage 우선순위 데이터 수집 시작")
        
        results = {
            "stocks": [],
            "indices": [],
            "forex": [],
            "crypto": []
        }
        
        # 1. 주요 주식 (3개만)
        self.logger.info("📈 주요 주식 데이터 수집 중...")
        for symbol in self.priority_symbols["US_STOCKS"][:3]:
            stock_data = self.get_stock_data(symbol)
            if stock_data:
                results["stocks"].append(stock_data)
        
        # 2. 지수 ETF (2개만)
        self.logger.info("📊 지수 ETF 데이터 수집 중...")
        for symbol in self.priority_symbols["INDICES"][:2]:
            index_data = self.get_stock_data(symbol)
            if index_data:
                results["indices"].append(index_data)
        
        # 3. 주요 외환 (1개만)
        self.logger.info("💱 외환 데이터 수집 중...")
        for from_curr, to_curr in self.priority_symbols["FOREX"][:1]:
            forex_data = self.get_forex_data(from_curr, to_curr)
            if forex_data:
                results["forex"].append(forex_data)
        
        # 4. 암호화폐 (1개만)
        self.logger.info("₿ 암호화폐 데이터 수집 중...")
        for symbol in self.priority_symbols["CRYPTO"][:1]:
            crypto_data = self.get_crypto_data(symbol, "USD")
            if crypto_data:
                results["crypto"].append(crypto_data)
        
        total_collected = sum(len(data_list) for data_list in results.values())
        self.logger.info(f"✅ Alpha Vantage 데이터 수집 완료: {total_collected}개 항목")
        
        return results
    
    def get_market_summary(self, collected_data: Dict[str, List[AlphaVantageMarketData]]) -> Dict[str, Any]:
        """수집된 데이터 기반 시장 요약"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "data_source": "Alpha Vantage",
            "total_symbols": sum(len(data_list) for data_list in collected_data.values()),
            "market_status": {},
            "top_movers": [],
            "data_quality": "high"
        }
        
        # 모든 데이터 통합
        all_data = []
        for category, data_list in collected_data.items():
            all_data.extend(data_list)
        
        if not all_data:
            return summary
        
        # 시장 상태 분석
        stock_changes = [data.change_percent for data in collected_data.get("stocks", [])]
        if stock_changes:
            avg_change = np.mean(stock_changes)
            summary["market_status"]["us_stocks"] = {
                "average_change": avg_change,
                "status": "bullish" if avg_change > 1 else "bearish" if avg_change < -1 else "neutral"
            }
        
        # 주요 변동 종목
        sorted_by_change = sorted(all_data, key=lambda x: abs(x.change_percent), reverse=True)
        summary["top_movers"] = [
            {
                "symbol": data.symbol,
                "name": data.name,
                "current_price": data.current_price,
                "change_percent": data.change_percent,
                "data_source": data.data_source
            }
            for data in sorted_by_change[:5]
        ]
        
        return summary
    
    def save_collected_data(self, collected_data: Dict[str, List[AlphaVantageMarketData]], 
                           filename: str = None):
        """수집된 데이터를 파일로 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alphavantage_collected_{timestamp}.json"
        
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # 데이터 직렬화
        serialized_data = {}
        for category, data_list in collected_data.items():
            serialized_data[category] = [
                {
                    "symbol": data.symbol,
                    "name": data.name,
                    "timestamp": data.timestamp.isoformat(),
                    "current_price": data.current_price,
                    "change_percent": data.change_percent,
                    "volume": data.volume,
                    "high_24h": data.high_24h,
                    "low_24h": data.low_24h,
                    "data_source": data.data_source,
                    "data_quality": data.data_quality
                }
                for data in data_list
            ]
        
        # 시장 요약 추가
        serialized_data["market_summary"] = self.get_market_summary(collected_data)
        
        filepath = output_dir / filename
        
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serialized_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📁 Alpha Vantage 데이터 저장 완료: {filepath}")

# 테스트 함수
def test_integrated_alphavantage():
    collector = IntegratedAlphaVantageCollector()
    
    print("🔍 통합 Alpha Vantage 수집기 테스트")
    print("=" * 50)
    
    # 우선순위 데이터 수집
    collected_data = collector.collect_priority_data()
    
    # 결과 출력
    for category, data_list in collected_data.items():
        print(f"\n📊 {category.upper()}:")
        for data in data_list:
            print(f"  {data.symbol}: ${data.current_price:.2f} ({data.change_percent:+.2f}%)")
    
    # 시장 요약
    market_summary = collector.get_market_summary(collected_data)
    print(f"\n📋 시장 요약:")
    print(f"  총 심볼: {market_summary['total_symbols']}개")
    print(f"  데이터 품질: {market_summary['data_quality']}")
    
    if market_summary.get('top_movers'):
        print(f"  주요 변동:")
        for mover in market_summary['top_movers'][:3]:
            print(f"    {mover['symbol']}: {mover['change_percent']:+.2f}%")
    
    # 데이터 저장
    collector.save_collected_data(collected_data)

if __name__ == "__main__":
    test_integrated_alphavantage()
