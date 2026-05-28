#!/usr/bin/env python3
"""
개별 주식 모니터링 시스템
각 시장별 상승/하락/거래량 상위 주식 모니터링
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import asyncio
import aiohttp
from dataclasses import dataclass
import requests
import json

@dataclass
class StockData:
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float]
    sector: Optional[str]
    market: str
    currency: str

class StockMonitor:
    """개별 주식 모니터링 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 시장별 주요 주식 심볼
        self.market_symbols = {
            'US': {
                'name': '미국 시장',
                'symbols': [
                    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
                    'JPM', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'MA', 'DIS', 'PYPL', 'ADBE',
                    'CRM', 'INTC', 'VZ', 'KO', 'PFE', 'T', 'XOM', 'CVX', 'WMT', 'BAC',
                    'ABBV', 'TMO', 'COST', 'AVGO', 'ACN', 'DHR', 'TXN', 'NEE', 'LIN',
                    'HON', 'QCOM', 'UPS', 'LOW', 'AMD', 'SBUX', 'MDT', 'IBM', 'AMGN'
                ]
            },
            'KR': {
                'name': '한국 시장',
                'symbols': [
                    '005930.KS', '000660.KS', '035420.KS', '005380.KS', '051910.KS',
                    '035720.KS', '006400.KS', '207940.KS', '005490.KS', '068270.KS',
                    '028260.KS', '066570.KS', '003670.KS', '096770.KS', '000270.KS',
                    '323410.KS', '017670.KS', '030200.KS', '036570.KS', '003550.KS',
                    '034730.KS', '018260.KS', '015760.KS', '138040.KS', '402340.KS'
                ]
            },
            'JP': {
                'name': '일본 시장',
                'symbols': [
                    '7203.T', '6758.T', '9984.T', '8306.T', '9432.T', '6861.T',
                    '8316.T', '7974.T', '6954.T', '4063.T', '9983.T', '4502.T',
                    '8035.T', '6098.T', '4568.T', '7267.T', '6367.T', '4543.T',
                    '7751.T', '6902.T', '8058.T', '9020.T', '2914.T', '4755.T'
                ]
            },
            'CN': {
                'name': '중국 시장',
                'symbols': [
                    '000001.SS', '000002.SS', '600036.SS', '600519.SS', '000858.SS',
                    '600000.SS', '601318.SS', '000002.SZ', '002415.SZ', '300059.SZ',
                    '600276.SS', '601166.SS', '000725.SZ', '002594.SZ', '600887.SS',
                    '601012.SS', '600104.SS', '000063.SZ', '002304.SZ', '600309.SS'
                ]
            }
        }
        
        # Alpha Vantage API (상위/하위 종목용)
        self.alpha_vantage_key = self._get_alpha_vantage_key()
    
    def _get_alpha_vantage_key(self) -> str:
        """Alpha Vantage API 키 가져오기"""
        try:
            # 환경 변수에서 먼저 시도
            import os
            if 'ALPHA_VANTAGE_API_KEY' in os.environ:
                return os.environ['ALPHA_VANTAGE_API_KEY']
            
            # .env 파일에서 시도
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('ALPHA_VANTAGE_API_KEY='):
                            return line.split('=', 1)[1].strip()
            
            # 기본 데모 키 사용
            return 'demo'
            
        except Exception as e:
            self.logger.warning(f"API 키 로드 실패, 데모 키 사용: {e}")
            return 'demo'
    
    def get_top_gainers_losers(self) -> Dict:
        """Alpha Vantage에서 상위/하위 종목 가져오기"""
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'TOP_GAINERS_LOSERS',
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'top_gainers' in data:
                return {
                    'top_gainers': data.get('top_gainers', [])[:10],
                    'top_losers': data.get('top_losers', [])[:10],
                    'most_actively_traded': data.get('most_actively_traded', [])[:10]
                }
            else:
                self.logger.warning("Alpha Vantage 데이터 형식 오류")
                return {}
                
        except Exception as e:
            self.logger.error(f"Alpha Vantage 데이터 수집 실패: {e}")
            return {}
    
    def get_market_stocks(self, market: str, limit: int = 20) -> List[StockData]:
        """특정 시장의 주식 데이터 수집"""
        if market not in self.market_symbols:
            return []
        
        symbols = self.market_symbols[market]['symbols'][:limit]
        stocks_data = []
        
        try:
            # 배치로 데이터 수집
            tickers = yf.Tickers(' '.join(symbols))
            
            for symbol in symbols:
                try:
                    ticker = tickers.tickers[symbol]
                    info = ticker.info
                    hist = ticker.history(period='2d')
                    
                    if len(hist) >= 2:
                        current_price = hist['Close'].iloc[-1]
                        prev_price = hist['Close'].iloc[-2]
                        change = current_price - prev_price
                        change_percent = (change / prev_price) * 100
                        volume = int(hist['Volume'].iloc[-1])
                        
                        stock_data = StockData(
                            symbol=symbol,
                            name=info.get('longName', symbol),
                            price=float(current_price),
                            change=float(change),
                            change_percent=float(change_percent),
                            volume=volume,
                            market_cap=info.get('marketCap'),
                            sector=info.get('sector'),
                            market=self.market_symbols[market]['name'],
                            currency=info.get('currency', 'USD')
                        )
                        stocks_data.append(stock_data)
                        
                except Exception as e:
                    self.logger.warning(f"주식 {symbol} 데이터 수집 실패: {e}")
                    continue
            
            self.logger.info(f"{market} 시장: {len(stocks_data)}개 주식 데이터 수집 완료")
            return stocks_data
            
        except Exception as e:
            self.logger.error(f"{market} 시장 데이터 수집 실패: {e}")
            return []
    
    def get_all_markets_data(self) -> Dict[str, List[StockData]]:
        """모든 시장의 주식 데이터 수집"""
        all_data = {}
        
        for market_code in self.market_symbols.keys():
            self.logger.info(f"{market_code} 시장 데이터 수집 중...")
            all_data[market_code] = self.get_market_stocks(market_code)
        
        return all_data
    
    def get_top_stocks_by_criteria(self, stocks_data: List[StockData], 
                                 criteria: str = 'change_percent', 
                                 ascending: bool = False, 
                                 limit: int = 10) -> List[StockData]:
        """기준에 따른 상위 주식 반환"""
        if not stocks_data:
            return []
        
        try:
            # 정렬
            sorted_stocks = sorted(stocks_data, 
                                 key=lambda x: getattr(x, criteria), 
                                 reverse=not ascending)
            return sorted_stocks[:limit]
            
        except Exception as e:
            self.logger.error(f"주식 정렬 실패: {e}")
            return stocks_data[:limit]
    
    def analyze_market_trends(self, market_data: Dict[str, List[StockData]]) -> Dict:
        """시장 트렌드 분석"""
        analysis = {}
        
        for market, stocks in market_data.items():
            if not stocks:
                continue
            
            # 상승/하락 주식 수
            gainers = [s for s in stocks if s.change_percent > 0]
            losers = [s for s in stocks if s.change_percent < 0]
            unchanged = [s for s in stocks if s.change_percent == 0]
            
            # 평균 변화율
            avg_change = np.mean([s.change_percent for s in stocks])
            
            # 거래량 분석
            total_volume = sum([s.volume for s in stocks])
            avg_volume = np.mean([s.volume for s in stocks])
            
            analysis[market] = {
                'total_stocks': len(stocks),
                'gainers': len(gainers),
                'losers': len(losers),
                'unchanged': len(unchanged),
                'avg_change_percent': float(avg_change),
                'total_volume': int(total_volume),
                'avg_volume': int(avg_volume),
                'market_sentiment': 'bullish' if avg_change > 1 else 'bearish' if avg_change < -1 else 'neutral'
            }
        
        return analysis

def main():
    """테스트 실행"""
    logging.basicConfig(level=logging.INFO)
    
    monitor = StockMonitor()
    
    print("=== 개별 주식 모니터링 테스트 ===")
    
    # Alpha Vantage 상위/하위 종목
    print("\n📈 Alpha Vantage 상위/하위 종목:")
    av_data = monitor.get_top_gainers_losers()
    if av_data:
        print(f"상위 종목: {len(av_data.get('top_gainers', []))}개")
        print(f"하위 종목: {len(av_data.get('top_losers', []))}개")
        print(f"거래량 상위: {len(av_data.get('most_actively_traded', []))}개")
    
    # 시장별 데이터
    print("\n🌍 시장별 주식 데이터:")
    all_data = monitor.get_all_markets_data()
    
    for market, stocks in all_data.items():
        if stocks:
            print(f"\n{monitor.market_symbols[market]['name']}: {len(stocks)}개")
            
            # 상위 상승 주식
            top_gainers = monitor.get_top_stocks_by_criteria(stocks, 'change_percent', False, 3)
            print("  상위 상승:")
            for stock in top_gainers:
                print(f"    {stock.symbol}: {stock.change_percent:.2f}%")
    
    # 트렌드 분석
    print("\n📊 시장 트렌드 분석:")
    trends = monitor.analyze_market_trends(all_data)
    for market, trend in trends.items():
        print(f"{monitor.market_symbols[market]['name']}: {trend['market_sentiment']} "
              f"(평균 {trend['avg_change_percent']:.2f}%)")

if __name__ == "__main__":
    main()
