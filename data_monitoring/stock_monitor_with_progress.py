#!/usr/bin/env python3
"""
진행률 표시 기능이 있는 개별 주식 모니터링 시스템
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Callable
import logging
import requests
import json
import time
from dataclasses import dataclass

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

class ProgressCallback:
    """진행률 콜백 클래스"""
    def __init__(self, progress_bar=None, status_text=None, log_container=None):
        self.progress_bar = progress_bar
        self.status_text = status_text
        self.log_container = log_container
        self.logs = []
    
    def update_progress(self, current: int, total: int, message: str = ""):
        """진행률 업데이트"""
        if self.progress_bar:
            progress = current / total if total > 0 else 0
            self.progress_bar.progress(progress)
        
        if self.status_text:
            status_msg = f"진행률: {current}/{total} ({progress*100:.1f}%)"
            if message:
                status_msg += f" - {message}"
            self.status_text.text(status_msg)
    
    def add_log(self, message: str, level: str = "INFO"):
        """로그 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.logs.append(log_entry)
        
        if self.log_container:
            # 최근 10개 로그만 표시
            recent_logs = self.logs[-10:]
            self.log_container.text("\n".join(recent_logs))

class StockMonitorWithProgress:
    """진행률 표시 기능이 있는 주식 모니터링 클래스"""
    
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
        
        # Alpha Vantage API
        self.alpha_vantage_key = self._get_alpha_vantage_key()
    
    def _get_alpha_vantage_key(self) -> str:
        """Alpha Vantage API 키 가져오기"""
        try:
            import os
            if 'ALPHA_VANTAGE_API_KEY' in os.environ:
                return os.environ['ALPHA_VANTAGE_API_KEY']
            
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('ALPHA_VANTAGE_API_KEY='):
                            return line.split('=', 1)[1].strip()
            
            return 'demo'
            
        except Exception as e:
            self.logger.warning(f"API 키 로드 실패, 데모 키 사용: {e}")
            return 'demo'
    
    def get_top_gainers_losers(self, callback: Optional[ProgressCallback] = None) -> Dict:
        """Alpha Vantage에서 상위/하위 종목 가져오기"""
        if callback:
            callback.add_log("Alpha Vantage 상위/하위 종목 데이터 요청 중...")
            callback.update_progress(0, 1, "Alpha Vantage API 호출")
        
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'TOP_GAINERS_LOSERS',
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if callback:
                callback.update_progress(1, 1, "Alpha Vantage 데이터 처리 완료")
            
            if 'top_gainers' in data:
                result = {
                    'top_gainers': data.get('top_gainers', [])[:10],
                    'top_losers': data.get('top_losers', [])[:10],
                    'most_actively_traded': data.get('most_actively_traded', [])[:10]
                }
                if callback:
                    callback.add_log(f"Alpha Vantage 데이터 수집 완료: 상승 {len(result['top_gainers'])}개, 하락 {len(result['top_losers'])}개")
                return result
            else:
                if callback:
                    callback.add_log("Alpha Vantage 데이터 형식 오류", "WARNING")
                return {}
                
        except Exception as e:
            if callback:
                callback.add_log(f"Alpha Vantage 데이터 수집 실패: {str(e)}", "ERROR")
            return {}
    
    def get_market_stocks(self, market: str, limit: int = 20, 
                         callback: Optional[ProgressCallback] = None) -> List[StockData]:
        """특정 시장의 주식 데이터 수집"""
        if market not in self.market_symbols:
            return []
        
        symbols = self.market_symbols[market]['symbols'][:limit]
        stocks_data = []
        market_name = self.market_symbols[market]['name']
        
        if callback:
            callback.add_log(f"{market_name} 데이터 수집 시작 ({len(symbols)}개 종목)")
        
        try:
            # 배치로 데이터 수집
            if callback:
                callback.update_progress(0, len(symbols), f"{market_name} 데이터 요청 중...")
            
            tickers = yf.Tickers(' '.join(symbols))
            
            for i, symbol in enumerate(symbols):
                try:
                    if callback:
                        callback.update_progress(i, len(symbols), f"{symbol} 처리 중...")
                    
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
                            market=market_name,
                            currency=info.get('currency', 'USD')
                        )
                        stocks_data.append(stock_data)
                        
                        if callback:
                            callback.add_log(f"{symbol}: {change_percent:+.2f}% (${current_price:.2f})")
                    
                    # 짧은 지연으로 API 제한 방지
                    time.sleep(0.1)
                        
                except Exception as e:
                    if callback:
                        callback.add_log(f"{symbol} 데이터 수집 실패: {str(e)}", "WARNING")
                    continue
            
            if callback:
                callback.update_progress(len(symbols), len(symbols), f"{market_name} 완료")
                callback.add_log(f"{market_name} 수집 완료: {len(stocks_data)}/{len(symbols)}개 성공")
            
            return stocks_data
            
        except Exception as e:
            if callback:
                callback.add_log(f"{market_name} 데이터 수집 실패: {str(e)}", "ERROR")
            return []
    
    def get_all_markets_data(self, callback: Optional[ProgressCallback] = None) -> Dict[str, List[StockData]]:
        """모든 시장의 주식 데이터 수집"""
        all_data = {}
        markets = list(self.market_symbols.keys())
        
        if callback:
            callback.add_log("전체 시장 데이터 수집 시작")
        
        for i, market_code in enumerate(markets):
            if callback:
                callback.update_progress(i, len(markets), f"{self.market_symbols[market_code]['name']} 수집 중...")
            
            all_data[market_code] = self.get_market_stocks(market_code, callback=callback)
            
            # 시장간 짧은 지연
            time.sleep(0.5)
        
        if callback:
            callback.update_progress(len(markets), len(markets), "전체 시장 데이터 수집 완료")
            total_stocks = sum(len(stocks) for stocks in all_data.values())
            callback.add_log(f"전체 수집 완료: {total_stocks}개 종목")
        
        return all_data
    
    def get_top_stocks_by_criteria(self, stocks_data: List[StockData], 
                                 criteria: str = 'change_percent', 
                                 ascending: bool = False, 
                                 limit: int = 10) -> List[StockData]:
        """기준에 따른 상위 주식 반환"""
        if not stocks_data:
            return []
        
        try:
            sorted_stocks = sorted(stocks_data, 
                                 key=lambda x: getattr(x, criteria), 
                                 reverse=not ascending)
            return sorted_stocks[:limit]
            
        except Exception as e:
            self.logger.error(f"주식 정렬 실패: {e}")
            return stocks_data[:limit]
    
    def analyze_market_trends(self, market_data: Dict[str, List[StockData]], 
                            callback: Optional[ProgressCallback] = None) -> Dict:
        """시장 트렌드 분석"""
        if callback:
            callback.add_log("시장 트렌드 분석 시작")
        
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
            
            if callback:
                sentiment = analysis[market]['market_sentiment']
                callback.add_log(f"{self.market_symbols[market]['name']}: {sentiment} (평균 {avg_change:.2f}%)")
        
        if callback:
            callback.add_log("시장 트렌드 분석 완료")
        
        return analysis

def main():
    """테스트 실행"""
    logging.basicConfig(level=logging.INFO)
    
    monitor = StockMonitorWithProgress()
    
    # 콘솔용 간단한 콜백
    class ConsoleCallback(ProgressCallback):
        def update_progress(self, current: int, total: int, message: str = ""):
            progress = current / total if total > 0 else 0
            print(f"진행률: {current}/{total} ({progress*100:.1f}%) - {message}")
        
        def add_log(self, message: str, level: str = "INFO"):
            print(f"[{level}] {message}")
    
    callback = ConsoleCallback()
    
    print("=== 진행률 표시 주식 모니터링 테스트 ===")
    
    # Alpha Vantage 데이터
    av_data = monitor.get_top_gainers_losers(callback)
    
    # 시장별 데이터
    all_data = monitor.get_all_markets_data(callback)
    
    # 트렌드 분석
    trends = monitor.analyze_market_trends(all_data, callback)
    
    print("\n=== 수집 완료 ===")

if __name__ == "__main__":
    main()
