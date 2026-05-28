"""
Alpha Vantage API를 사용한 고급 데이터 수집기
실시간 및 과거 데이터, 기술적 지표, 경제 지표 수집
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
import aiohttp

@dataclass
class IntradayData:
    symbol: str
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    interval: str

@dataclass
class TechnicalIndicator:
    symbol: str
    indicator_name: str
    timestamp: datetime
    value: float
    signal: str  # BUY, SELL, HOLD

@dataclass
class EconomicIndicatorData:
    name: str
    value: float
    date: datetime
    unit: str
    importance: str

class AlphaVantageCollector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = self._load_api_key()
        self.base_url = "https://www.alphavantage.co/query"
        self.session = None
        
        # API 호출 제한 (5 calls per minute for free tier)
        self.call_interval = 12  # seconds between calls
        self.last_call_time = 0
        
        # 주요 모니터링 심볼
        self.us_stocks = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", 
            "NVDA", "META", "NFLX", "IBM", "JPM"
        ]
        
        self.forex_pairs = [
            "USDKRW", "USDJPY", "USDCNY", "EURUSD", 
            "GBPUSD", "AUDUSD", "USDCAD"
        ]
        
        self.crypto_symbols = [
            "BTC", "ETH", "ADA", "DOT", "LINK"
        ]
    
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
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _wait_for_rate_limit(self):
        """API 호출 제한 준수"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.call_interval:
            wait_time = self.call_interval - time_since_last_call
            self.logger.debug(f"Rate limit wait: {wait_time:.1f}s")
            time.sleep(wait_time)
        
        self.last_call_time = time.time()
    
    def get_intraday_data(self, symbol: str, interval: str = "5min", 
                         outputsize: str = "compact") -> List[IntradayData]:
        """실시간 인트라데이 데이터 수집"""
        self._wait_for_rate_limit()
        
        try:
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": interval,
                "outputsize": outputsize,
                "apikey": self.api_key,
                "datatype": "json"
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # 오류 체크
            if "Error Message" in data:
                self.logger.error(f"API Error for {symbol}: {data['Error Message']}")
                return []
            
            if "Note" in data:
                self.logger.warning(f"API Note for {symbol}: {data['Note']}")
                return []
            
            # 데이터 파싱
            time_series_key = f"Time Series ({interval})"
            if time_series_key not in data:
                self.logger.warning(f"No time series data for {symbol}")
                return []
            
            time_series = data[time_series_key]
            intraday_data = []
            
            for timestamp_str, ohlcv in time_series.items():
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    
                    intraday_point = IntradayData(
                        symbol=symbol,
                        timestamp=timestamp,
                        open_price=float(ohlcv["1. open"]),
                        high_price=float(ohlcv["2. high"]),
                        low_price=float(ohlcv["3. low"]),
                        close_price=float(ohlcv["4. close"]),
                        volume=int(ohlcv["5. volume"]),
                        interval=interval
                    )
                    
                    intraday_data.append(intraday_point)
                    
                except (ValueError, KeyError) as e:
                    self.logger.debug(f"Error parsing data point for {symbol}: {e}")
                    continue
            
            # 시간순 정렬 (최신 데이터 먼저)
            intraday_data.sort(key=lambda x: x.timestamp, reverse=True)
            
            self.logger.info(f"✅ {symbol}: {len(intraday_data)}개 인트라데이 데이터 수집")
            return intraday_data
            
        except Exception as e:
            self.logger.error(f"Error getting intraday data for {symbol}: {e}")
            return []
    
    def get_technical_indicator(self, symbol: str, indicator: str, 
                              interval: str = "daily", **kwargs) -> List[TechnicalIndicator]:
        """기술적 지표 데이터 수집"""
        self._wait_for_rate_limit()
        
        try:
            params = {
                "function": indicator,
                "symbol": symbol,
                "interval": interval,
                "apikey": self.api_key,
                "datatype": "json"
            }
            
            # 추가 파라미터 병합
            params.update(kwargs)
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # 오류 체크
            if "Error Message" in data:
                self.logger.error(f"API Error for {symbol} {indicator}: {data['Error Message']}")
                return []
            
            # 기술적 지표 데이터 파싱
            technical_data = []
            
            # 다양한 기술적 지표의 키 패턴 처리
            data_key = None
            for key in data.keys():
                if "Technical Analysis" in key or indicator.upper() in key:
                    data_key = key
                    break
            
            if not data_key:
                self.logger.warning(f"No technical data found for {symbol} {indicator}")
                return []
            
            indicator_series = data[data_key]
            
            for timestamp_str, values in indicator_series.items():
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d")
                    
                    # 지표 값 추출 (첫 번째 값 사용)
                    indicator_value = None
                    for value_key, value in values.items():
                        if indicator.upper() in value_key.upper():
                            indicator_value = float(value)
                            break
                    
                    if indicator_value is None:
                        # 첫 번째 값 사용
                        indicator_value = float(list(values.values())[0])
                    
                    # 간단한 신호 생성
                    signal = self._generate_signal(indicator, indicator_value)
                    
                    tech_indicator = TechnicalIndicator(
                        symbol=symbol,
                        indicator_name=indicator,
                        timestamp=timestamp,
                        value=indicator_value,
                        signal=signal
                    )
                    
                    technical_data.append(tech_indicator)
                    
                except (ValueError, KeyError, IndexError) as e:
                    self.logger.debug(f"Error parsing technical data for {symbol}: {e}")
                    continue
            
            # 시간순 정렬
            technical_data.sort(key=lambda x: x.timestamp, reverse=True)
            
            self.logger.info(f"✅ {symbol} {indicator}: {len(technical_data)}개 기술적 지표 수집")
            return technical_data
            
        except Exception as e:
            self.logger.error(f"Error getting technical indicator for {symbol} {indicator}: {e}")
            return []
    
    def _generate_signal(self, indicator: str, value: float) -> str:
        """기술적 지표 기반 간단한 신호 생성"""
        indicator_upper = indicator.upper()
        
        if "RSI" in indicator_upper:
            if value > 70:
                return "SELL"
            elif value < 30:
                return "BUY"
            else:
                return "HOLD"
        
        elif "MACD" in indicator_upper:
            if value > 0:
                return "BUY"
            elif value < 0:
                return "SELL"
            else:
                return "HOLD"
        
        else:
            return "HOLD"
    
    def get_forex_data(self, from_currency: str, to_currency: str) -> Optional[Dict[str, Any]]:
        """외환 데이터 수집"""
        self._wait_for_rate_limit()
        
        try:
            params = {
                "function": "FX_INTRADAY",
                "from_symbol": from_currency,
                "to_symbol": to_currency,
                "interval": "5min",
                "apikey": self.api_key,
                "datatype": "json"
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "Error Message" in data:
                self.logger.error(f"Forex API Error: {data['Error Message']}")
                return None
            
            # 최신 데이터 추출
            time_series_key = "Time Series FX (5min)"
            if time_series_key not in data:
                return None
            
            time_series = data[time_series_key]
            latest_timestamp = max(time_series.keys())
            latest_data = time_series[latest_timestamp]
            
            forex_data = {
                "pair": f"{from_currency}/{to_currency}",
                "timestamp": datetime.strptime(latest_timestamp, "%Y-%m-%d %H:%M:%S"),
                "open": float(latest_data["1. open"]),
                "high": float(latest_data["2. high"]),
                "low": float(latest_data["3. low"]),
                "close": float(latest_data["4. close"])
            }
            
            self.logger.info(f"✅ {from_currency}/{to_currency}: {forex_data['close']}")
            return forex_data
            
        except Exception as e:
            self.logger.error(f"Error getting forex data for {from_currency}/{to_currency}: {e}")
            return None
    
    def get_crypto_data(self, symbol: str, market: str = "USD") -> Optional[Dict[str, Any]]:
        """암호화폐 데이터 수집"""
        self._wait_for_rate_limit()
        
        try:
            params = {
                "function": "CRYPTO_INTRADAY",
                "symbol": symbol,
                "market": market,
                "interval": "5min",
                "apikey": self.api_key,
                "datatype": "json"
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "Error Message" in data:
                self.logger.error(f"Crypto API Error: {data['Error Message']}")
                return None
            
            # 최신 데이터 추출
            time_series_key = "Time Series (Crypto)"
            if time_series_key not in data:
                return None
            
            time_series = data[time_series_key]
            latest_timestamp = max(time_series.keys())
            latest_data = time_series[latest_timestamp]
            
            crypto_data = {
                "symbol": f"{symbol}/{market}",
                "timestamp": datetime.strptime(latest_timestamp, "%Y-%m-%d %H:%M:%S"),
                "open": float(latest_data["1a. open (USD)"]),
                "high": float(latest_data["2a. high (USD)"]),
                "low": float(latest_data["3a. low (USD)"]),
                "close": float(latest_data["4a. close (USD)"]),
                "volume": float(latest_data["5. volume"])
            }
            
            self.logger.info(f"✅ {symbol}/{market}: {crypto_data['close']}")
            return crypto_data
            
        except Exception as e:
            self.logger.error(f"Error getting crypto data for {symbol}: {e}")
            return None
    
    def get_economic_indicators(self) -> List[EconomicIndicatorData]:
        """경제 지표 수집"""
        indicators = []
        
        # GDP 데이터
        gdp_data = self._get_economic_indicator("REAL_GDP", "quarterly")
        if gdp_data:
            indicators.append(gdp_data)
        
        # 실업률
        unemployment_data = self._get_economic_indicator("UNEMPLOYMENT", "monthly")
        if unemployment_data:
            indicators.append(unemployment_data)
        
        # 인플레이션
        inflation_data = self._get_economic_indicator("INFLATION", "monthly")
        if inflation_data:
            indicators.append(inflation_data)
        
        return indicators
    
    def _get_economic_indicator(self, indicator: str, interval: str) -> Optional[EconomicIndicatorData]:
        """개별 경제 지표 수집"""
        self._wait_for_rate_limit()
        
        try:
            params = {
                "function": indicator,
                "interval": interval,
                "apikey": self.api_key,
                "datatype": "json"
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "Error Message" in data:
                return None
            
            # 데이터 파싱 (구조는 지표마다 다를 수 있음)
            data_key = "data"
            if data_key not in data:
                return None
            
            indicator_data = data[data_key]
            if not indicator_data:
                return None
            
            # 최신 데이터 사용
            latest_data = indicator_data[0]
            
            return EconomicIndicatorData(
                name=indicator,
                value=float(latest_data["value"]),
                date=datetime.strptime(latest_data["date"], "%Y-%m-%d"),
                unit=latest_data.get("unit", ""),
                importance="high"
            )
            
        except Exception as e:
            self.logger.debug(f"Error getting economic indicator {indicator}: {e}")
            return None
    
    async def collect_comprehensive_data(self) -> Dict[str, Any]:
        """종합 데이터 수집"""
        self.logger.info("🚀 Alpha Vantage 종합 데이터 수집 시작")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "intraday_data": {},
            "technical_indicators": {},
            "forex_data": {},
            "crypto_data": {},
            "economic_indicators": []
        }
        
        # 1. 주요 주식 인트라데이 데이터
        self.logger.info("📈 주식 인트라데이 데이터 수집 중...")
        for symbol in self.us_stocks[:3]:  # API 제한으로 3개만
            intraday_data = self.get_intraday_data(symbol, "5min", "compact")
            if intraday_data:
                results["intraday_data"][symbol] = {
                    "latest_price": intraday_data[0].close_price,
                    "latest_volume": intraday_data[0].volume,
                    "data_points": len(intraday_data),
                    "last_update": intraday_data[0].timestamp.isoformat()
                }
        
        # 2. 기술적 지표
        self.logger.info("📊 기술적 지표 수집 중...")
        for symbol in ["AAPL", "MSFT"]:  # 2개 종목만
            rsi_data = self.get_technical_indicator(symbol, "RSI", "daily", time_period=14)
            if rsi_data:
                results["technical_indicators"][f"{symbol}_RSI"] = {
                    "latest_value": rsi_data[0].value,
                    "signal": rsi_data[0].signal,
                    "timestamp": rsi_data[0].timestamp.isoformat()
                }
        
        # 3. 외환 데이터
        self.logger.info("💱 외환 데이터 수집 중...")
        forex_data = self.get_forex_data("USD", "KRW")
        if forex_data:
            results["forex_data"]["USDKRW"] = forex_data
        
        # 4. 암호화폐 데이터
        self.logger.info("₿ 암호화폐 데이터 수집 중...")
        crypto_data = self.get_crypto_data("BTC", "USD")
        if crypto_data:
            results["crypto_data"]["BTCUSD"] = crypto_data
        
        # 5. 경제 지표
        self.logger.info("🏛️ 경제 지표 수집 중...")
        economic_indicators = self.get_economic_indicators()
        results["economic_indicators"] = [
            {
                "name": indicator.name,
                "value": indicator.value,
                "date": indicator.date.isoformat(),
                "importance": indicator.importance
            }
            for indicator in economic_indicators
        ]
        
        self.logger.info("✅ Alpha Vantage 데이터 수집 완료")
        return results
    
    def save_data_to_file(self, data: Dict[str, Any], filename: str = None):
        """데이터를 파일로 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alphavantage_data_{timestamp}.json"
        
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📁 데이터 저장 완료: {filepath}")

# 테스트 함수
async def test_alphavantage_collector():
    collector = AlphaVantageCollector()
    
    print("🔍 Alpha Vantage Collector Test")
    print("=" * 50)
    
    # 1. 인트라데이 데이터 테스트
    print("\n📈 Intraday Data Test:")
    intraday_data = collector.get_intraday_data("AAPL", "5min", "compact")
    if intraday_data:
        latest = intraday_data[0]
        print(f"  AAPL 최신 데이터: ${latest.close_price:.2f} at {latest.timestamp}")
        print(f"  데이터 포인트: {len(intraday_data)}개")
    
    # 2. 기술적 지표 테스트
    print("\n📊 Technical Indicator Test:")
    rsi_data = collector.get_technical_indicator("AAPL", "RSI", "daily", time_period=14)
    if rsi_data:
        latest_rsi = rsi_data[0]
        print(f"  AAPL RSI: {latest_rsi.value:.2f} ({latest_rsi.signal})")
    
    # 3. 외환 데이터 테스트
    print("\n💱 Forex Data Test:")
    forex_data = collector.get_forex_data("USD", "KRW")
    if forex_data:
        print(f"  USD/KRW: {forex_data['close']:.2f}")
    
    # 4. 종합 데이터 수집 테스트
    print("\n🚀 Comprehensive Data Collection:")
    comprehensive_data = await collector.collect_comprehensive_data()
    
    print(f"  인트라데이 데이터: {len(comprehensive_data['intraday_data'])}개 종목")
    print(f"  기술적 지표: {len(comprehensive_data['technical_indicators'])}개")
    print(f"  외환 데이터: {len(comprehensive_data['forex_data'])}개")
    print(f"  암호화폐 데이터: {len(comprehensive_data['crypto_data'])}개")
    print(f"  경제 지표: {len(comprehensive_data['economic_indicators'])}개")
    
    # 데이터 저장
    collector.save_data_to_file(comprehensive_data)

if __name__ == "__main__":
    asyncio.run(test_alphavantage_collector())
