#!/usr/bin/env python3
"""
아시아 시장 데이터 수집기
한국, 중국, 일본, 대만, 싱가포르, 인도 등의 주요 주식 및 지수
"""

import yfinance as yf
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import time
import requests

class AsianMarketsCollector:
    """아시아 시장 데이터 수집기"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 아시아 주요 시장 지수 (한국 시간 기준)
        self.market_indices = {
            'korea': {
                'name': '한국',
                'index_symbol': '^KS11',  # KOSPI
                'index_name': 'KOSPI',
                'currency': 'KRW',
                'timezone': 'Asia/Seoul',
                'market_hours': '09:00-15:30 KST'
            },
            'japan': {
                'name': '일본',
                'index_symbol': '^N225',  # Nikkei 225
                'index_name': 'Nikkei 225',
                'currency': 'JPY',
                'timezone': 'Asia/Tokyo',
                'market_hours': '09:00-15:00 JST (한국시간 동일)'
            },
            'china': {
                'name': '중국',
                'index_symbol': '000001.SS',  # Shanghai Composite
                'index_name': 'Shanghai Composite',
                'currency': 'CNY',
                'timezone': 'Asia/Shanghai',
                'market_hours': '09:30-15:00 CST (한국시간 10:30-16:00)'
            },
            'hongkong': {
                'name': '홍콩',
                'index_symbol': '^HSI',  # Hang Seng
                'index_name': 'Hang Seng',
                'currency': 'HKD',
                'timezone': 'Asia/Hong_Kong',
                'market_hours': '09:30-16:00 HKT (한국시간 10:30-17:00)'
            },
            'taiwan': {
                'name': '대만',
                'index_symbol': '^TWII',  # Taiwan Weighted
                'index_name': 'Taiwan Weighted',
                'currency': 'TWD',
                'timezone': 'Asia/Taipei',
                'market_hours': '09:00-13:30 CST (한국시간 10:00-14:30)'
            },
            'singapore': {
                'name': '싱가포르',
                'index_symbol': '^STI',  # Straits Times
                'index_name': 'Straits Times',
                'currency': 'SGD',
                'timezone': 'Asia/Singapore',
                'market_hours': '09:00-17:00 SGT (한국시간 10:00-18:00)'
            },
            'india': {
                'name': '인도',
                'index_symbol': '^BSESN',  # BSE Sensex
                'index_name': 'BSE Sensex',
                'currency': 'INR',
                'timezone': 'Asia/Kolkata',
                'market_hours': '09:15-15:30 IST (한국시간 12:45-19:00)'
            }
        }
        
        # 각 시장의 주요 주식 (시가총액 기준 상위 종목들)
        self.major_stocks = {
            'korea': [
                {'symbol': '005930.KS', 'name': 'Samsung Electronics', 'sector': 'Technology'},
                {'symbol': '000660.KS', 'name': 'SK Hynix', 'sector': 'Technology'},
                {'symbol': '207940.KS', 'name': 'Samsung Biologics', 'sector': 'Healthcare'},
                {'symbol': '005380.KS', 'name': 'Hyundai Motor', 'sector': 'Automotive'},
                {'symbol': '051910.KS', 'name': 'LG Chem', 'sector': 'Chemicals'},
                {'symbol': '006400.KS', 'name': 'Samsung SDI', 'sector': 'Technology'},
                {'symbol': '035420.KS', 'name': 'NAVER', 'sector': 'Technology'},
                {'symbol': '028260.KS', 'name': 'Samsung C&T', 'sector': 'Construction'},
                {'symbol': '066570.KS', 'name': 'LG Electronics', 'sector': 'Technology'},
                {'symbol': '003670.KS', 'name': 'Posco Holdings', 'sector': 'Steel'}
            ],
            'japan': [
                {'symbol': '7203.T', 'name': 'Toyota Motor', 'sector': 'Automotive'},
                {'symbol': '6758.T', 'name': 'Sony Group', 'sector': 'Technology'},
                {'symbol': '6861.T', 'name': 'Keyence', 'sector': 'Technology'},
                {'symbol': '8306.T', 'name': 'Mitsubishi UFJ', 'sector': 'Financial'},
                {'symbol': '9984.T', 'name': 'SoftBank Group', 'sector': 'Technology'},
                {'symbol': '6098.T', 'name': 'Recruit Holdings', 'sector': 'Services'},
                {'symbol': '4519.T', 'name': 'Chugai Pharma', 'sector': 'Healthcare'},
                {'symbol': '8035.T', 'name': 'Tokyo Electron', 'sector': 'Technology'},
                {'symbol': '9432.T', 'name': 'NTT', 'sector': 'Telecom'},
                {'symbol': '7974.T', 'name': 'Nintendo', 'sector': 'Gaming'}
            ],
            'china': [
                {'symbol': '600519.SS', 'name': 'Kweichow Moutai', 'sector': 'Consumer'},
                {'symbol': '000858.SZ', 'name': 'Wuliangye', 'sector': 'Consumer'},
                {'symbol': '300750.SZ', 'name': 'Contemporary Amperex', 'sector': 'Technology'},
                {'symbol': '002594.SZ', 'name': 'BYD', 'sector': 'Automotive'},
                {'symbol': '000001.SZ', 'name': 'Ping An Insurance', 'sector': 'Financial'},
                {'symbol': '600036.SS', 'name': 'China Merchants Bank', 'sector': 'Financial'},
                {'symbol': '600887.SS', 'name': 'Inner Mongolia Yili', 'sector': 'Consumer'},
                {'symbol': '002415.SZ', 'name': 'Hangzhou Hikvision', 'sector': 'Technology'},
                {'symbol': '000002.SZ', 'name': 'China Vanke', 'sector': 'Real Estate'},
                {'symbol': '600276.SS', 'name': 'Jiangsu Hengrui', 'sector': 'Healthcare'}
            ],
            'hongkong': [
                {'symbol': '0700.HK', 'name': 'Tencent Holdings', 'sector': 'Technology'},
                {'symbol': '9988.HK', 'name': 'Alibaba Group', 'sector': 'Technology'},
                {'symbol': '1299.HK', 'name': 'AIA Group', 'sector': 'Financial'},
                {'symbol': '0939.HK', 'name': 'China Construction Bank', 'sector': 'Financial'},
                {'symbol': '1398.HK', 'name': 'ICBC', 'sector': 'Financial'},
                {'symbol': '2318.HK', 'name': 'Ping An Insurance', 'sector': 'Financial'},
                {'symbol': '0005.HK', 'name': 'HSBC Holdings', 'sector': 'Financial'},
                {'symbol': '9618.HK', 'name': 'JD.com', 'sector': 'Technology'},
                {'symbol': '1810.HK', 'name': 'Xiaomi', 'sector': 'Technology'},
                {'symbol': '2020.HK', 'name': 'ANTA Sports', 'sector': 'Consumer'}
            ],
            'taiwan': [
                {'symbol': '2330.TW', 'name': 'Taiwan Semiconductor', 'sector': 'Technology'},
                {'symbol': '2454.TW', 'name': 'MediaTek', 'sector': 'Technology'},
                {'symbol': '2317.TW', 'name': 'Hon Hai Precision', 'sector': 'Technology'},
                {'symbol': '1303.TW', 'name': 'Nan Ya Plastics', 'sector': 'Chemicals'},
                {'symbol': '1301.TW', 'name': 'Formosa Plastics', 'sector': 'Chemicals'},
                {'symbol': '2881.TW', 'name': 'Fubon Financial', 'sector': 'Financial'},
                {'symbol': '2882.TW', 'name': 'Cathay Financial', 'sector': 'Financial'},
                {'symbol': '2412.TW', 'name': 'Chunghwa Telecom', 'sector': 'Telecom'},
                {'symbol': '2308.TW', 'name': 'Delta Electronics', 'sector': 'Technology'},
                {'symbol': '2303.TW', 'name': 'United Microelectronics', 'sector': 'Technology'}
            ],
            'singapore': [
                {'symbol': 'D05.SI', 'name': 'DBS Group', 'sector': 'Financial'},
                {'symbol': 'O39.SI', 'name': 'OCBC Bank', 'sector': 'Financial'},
                {'symbol': 'U11.SI', 'name': 'UOB', 'sector': 'Financial'},
                {'symbol': 'Z74.SI', 'name': 'Singapore Telecom', 'sector': 'Telecom'},
                {'symbol': 'C6L.SI', 'name': 'Singapore Airlines', 'sector': 'Airlines'},
                {'symbol': 'G13.SI', 'name': 'Genting Singapore', 'sector': 'Gaming'},
                {'symbol': 'Y92.SI', 'name': 'Thai Beverage', 'sector': 'Consumer'},
                {'symbol': 'S68.SI', 'name': 'Singapore Exchange', 'sector': 'Financial'},
                {'symbol': 'C52.SI', 'name': 'ComfortDelGro', 'sector': 'Transportation'},
                {'symbol': 'BN4.SI', 'name': 'Keppel Corp', 'sector': 'Conglomerate'}
            ],
            'india': [
                {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries', 'sector': 'Energy'},
                {'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services', 'sector': 'Technology'},
                {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank', 'sector': 'Financial'},
                {'symbol': 'INFY.NS', 'name': 'Infosys', 'sector': 'Technology'},
                {'symbol': 'HINDUNILVR.NS', 'name': 'Hindustan Unilever', 'sector': 'Consumer'},
                {'symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank', 'sector': 'Financial'},
                {'symbol': 'SBIN.NS', 'name': 'State Bank of India', 'sector': 'Financial'},
                {'symbol': 'BHARTIARTL.NS', 'name': 'Bharti Airtel', 'sector': 'Telecom'},
                {'symbol': 'ITC.NS', 'name': 'ITC', 'sector': 'Consumer'},
                {'symbol': 'LT.NS', 'name': 'Larsen & Toubro', 'sector': 'Construction'}
            ]
        }
        
        self.logger.info("✅ 아시아 시장 수집기 초기화 완료")
    
    def get_market_indices_data(self) -> Dict[str, Any]:
        """아시아 시장 지수 데이터 수집"""
        self.logger.info("📊 아시아 시장 지수 데이터 수집 시작")
        
        indices_data = {}
        
        for market_key, market_info in self.market_indices.items():
            try:
                symbol = market_info['index_symbol']
                ticker = yf.Ticker(symbol)
                
                # 현재 데이터 및 기본 정보
                info = ticker.info
                hist = ticker.history(period="5d")
                
                if not hist.empty:
                    latest_data = hist.iloc[-1]
                    previous_data = hist.iloc[-2] if len(hist) > 1 else latest_data
                    
                    current_price = latest_data['Close']
                    previous_close = previous_data['Close']
                    change = current_price - previous_close
                    change_percent = (change / previous_close) * 100
                    
                    # 시장 상태 판단 (간단한 로직)
                    market_status = self._get_market_status(market_key)
                    
                    indices_data[market_key] = {
                        'market_name': market_info['name'],
                        'index_name': market_info['index_name'],
                        'symbol': symbol,
                        'current_price': round(current_price, 2),
                        'previous_close': round(previous_close, 2),
                        'change': round(change, 2),
                        'change_percent': round(change_percent, 2),
                        'volume': int(latest_data.get('Volume', 0)),
                        'market_cap': info.get('marketCap', 'N/A'),
                        'currency': market_info['currency'],
                        'market_hours': market_info['market_hours'],
                        'market_status': market_status,
                        'last_updated': datetime.now().isoformat()
                    }
                    
                    self.logger.info(f"✅ {market_info['name']} 지수 데이터 수집 완료")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                self.logger.error(f"❌ {market_info['name']} 지수 데이터 수집 실패: {e}")
                indices_data[market_key] = {
                    'market_name': market_info['name'],
                    'error': str(e),
                    'status': 'failed'
                }
        
        return indices_data
    
    def get_major_stocks_data(self, market_key: str, limit: int = 10) -> List[Dict[str, Any]]:
        """특정 시장의 주요 주식 데이터 수집"""
        if market_key not in self.major_stocks:
            return []
        
        self.logger.info(f"📈 {self.market_indices[market_key]['name']} 주요 주식 데이터 수집 시작")
        
        stocks_data = []
        stocks_list = self.major_stocks[market_key][:limit]
        
        for stock_info in stocks_list:
            try:
                symbol = stock_info['symbol']
                ticker = yf.Ticker(symbol)
                
                # 현재 데이터
                info = ticker.info
                hist = ticker.history(period="5d")
                
                if not hist.empty:
                    latest_data = hist.iloc[-1]
                    previous_data = hist.iloc[-2] if len(hist) > 1 else latest_data
                    
                    current_price = latest_data['Close']
                    previous_close = previous_data['Close']
                    change = current_price - previous_close
                    change_percent = (change / previous_close) * 100
                    
                    stocks_data.append({
                        'symbol': symbol,
                        'name': stock_info['name'],
                        'sector': stock_info['sector'],
                        'current_price': round(current_price, 2),
                        'previous_close': round(previous_close, 2),
                        'change': round(change, 2),
                        'change_percent': round(change_percent, 2),
                        'volume': int(latest_data.get('Volume', 0)),
                        'market_cap': info.get('marketCap', 0),
                        'pe_ratio': info.get('trailingPE', 'N/A'),
                        'dividend_yield': info.get('dividendYield', 0),
                        'currency': self.market_indices[market_key]['currency'],
                        'yahoo_finance_url': f"https://finance.yahoo.com/quote/{symbol}",
                        'last_updated': datetime.now().isoformat()
                    })
                
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                self.logger.error(f"❌ {stock_info['name']} 데이터 수집 실패: {e}")
                continue
        
        # 시가총액 기준 정렬
        stocks_data.sort(key=lambda x: x.get('market_cap', 0) if isinstance(x.get('market_cap'), (int, float)) else 0, reverse=True)
        
        self.logger.info(f"✅ {self.market_indices[market_key]['name']} 주식 {len(stocks_data)}개 수집 완료")
        return stocks_data
    
    def get_comprehensive_asian_data(self) -> Dict[str, Any]:
        """아시아 시장 종합 데이터 수집"""
        self.logger.info("🌏 아시아 시장 종합 데이터 수집 시작")
        
        comprehensive_data = {
            'timestamp': datetime.now().isoformat(),
            'market_indices': {},
            'major_stocks': {},
            'market_summary': {},
            'open_markets': []
        }
        
        # 시장 지수 데이터 수집
        indices_data = self.get_market_indices_data()
        comprehensive_data['market_indices'] = indices_data
        
        # 각 시장의 주요 주식 데이터 수집
        for market_key in self.market_indices.keys():
            stocks_data = self.get_major_stocks_data(market_key, limit=10)
            comprehensive_data['major_stocks'][market_key] = stocks_data
        
        # 요약 정보 생성
        comprehensive_data['market_summary'] = self._generate_market_summary(indices_data)
        comprehensive_data['open_markets'] = self._get_open_markets(indices_data)
        
        self.logger.info("✅ 아시아 시장 종합 데이터 수집 완료")
        return comprehensive_data
    
    def _get_market_status(self, market_key: str) -> str:
        """시장 개장/폐장 상태 판단 (한국 시간 기준)"""
        from datetime import datetime
        import pytz
        
        # 한국 시간 기준으로 현재 시간 가져오기
        korea_tz = pytz.timezone('Asia/Seoul')
        korea_now = datetime.now(korea_tz)
        korea_hour = korea_now.hour
        korea_minute = korea_now.minute
        korea_weekday = korea_now.weekday()  # 0=월요일, 6=일요일
        
        # 주말 체크 (토요일=5, 일요일=6)
        if korea_weekday >= 5:
            return "closed"
        
        # 각 시장별 개장 시간 (한국 시간 기준)
        market_hours = {
            'korea': {
                'open_hour': 9, 'open_minute': 0,
                'close_hour': 15, 'close_minute': 30
            },
            'japan': {
                'open_hour': 9, 'open_minute': 0,  # 일본은 한국과 같은 시간대
                'close_hour': 15, 'close_minute': 0
            },
            'china': {
                'open_hour': 10, 'open_minute': 30,  # 중국은 한국보다 1시간 늦음
                'close_hour': 16, 'close_minute': 0
            },
            'hongkong': {
                'open_hour': 10, 'open_minute': 30,  # 홍콩은 한국보다 1시간 늦음
                'close_hour': 17, 'close_minute': 0
            },
            'taiwan': {
                'open_hour': 10, 'open_minute': 0,  # 대만은 한국보다 1시간 늦음
                'close_hour': 14, 'close_minute': 30
            },
            'singapore': {
                'open_hour': 10, 'open_minute': 0,  # 싱가포르는 한국보다 1시간 늦음
                'close_hour': 18, 'close_minute': 0
            },
            'india': {
                'open_hour': 12, 'open_minute': 45,  # 인도는 한국보다 3.5시간 늦음
                'close_hour': 19, 'close_minute': 0
            }
        }
        
        if market_key not in market_hours:
            return "unknown"
        
        hours = market_hours[market_key]
        
        # 현재 시간을 분 단위로 변환
        current_minutes = korea_hour * 60 + korea_minute
        open_minutes = hours['open_hour'] * 60 + hours['open_minute']
        close_minutes = hours['close_hour'] * 60 + hours['close_minute']
        
        # 개장 시간 체크
        if open_minutes <= current_minutes <= close_minutes:
            return "open"
        else:
            return "closed"
    
    def _generate_market_summary(self, indices_data: Dict) -> Dict[str, Any]:
        """시장 요약 정보 생성"""
        summary = {
            'total_markets': len(indices_data),
            'positive_markets': 0,
            'negative_markets': 0,
            'neutral_markets': 0,
            'best_performer': None,
            'worst_performer': None,
            'average_change': 0
        }
        
        changes = []
        best_change = float('-inf')
        worst_change = float('inf')
        
        for market_key, data in indices_data.items():
            if 'change_percent' in data:
                change_pct = data['change_percent']
                changes.append(change_pct)
                
                if change_pct > 0:
                    summary['positive_markets'] += 1
                elif change_pct < 0:
                    summary['negative_markets'] += 1
                else:
                    summary['neutral_markets'] += 1
                
                if change_pct > best_change:
                    best_change = change_pct
                    summary['best_performer'] = {
                        'market': data['market_name'],
                        'change_percent': change_pct
                    }
                
                if change_pct < worst_change:
                    worst_change = change_pct
                    summary['worst_performer'] = {
                        'market': data['market_name'],
                        'change_percent': change_pct
                    }
        
        if changes:
            summary['average_change'] = round(sum(changes) / len(changes), 2)
        
        return summary
    
    def _get_open_markets(self, indices_data: Dict) -> List[str]:
        """현재 개장 중인 시장 목록"""
        open_markets = []
        
        for market_key, data in indices_data.items():
            if data.get('market_status') == 'open':
                open_markets.append(data.get('market_name', market_key))
        
        return open_markets

def main():
    """테스트 실행"""
    print("🌏 아시아 시장 데이터 수집기 테스트")
    print("=" * 50)
    
    collector = AsianMarketsCollector()
    
    # 종합 데이터 수집 (소량 테스트)
    asian_data = collector.get_comprehensive_asian_data()
    
    # 결과 출력
    print(f"\n📊 수집 결과:")
    
    # 시장 지수
    indices = asian_data.get('market_indices', {})
    print(f"시장 지수: {len(indices)}개")
    
    for market_key, data in indices.items():
        if 'current_price' in data:
            print(f"  {data['market_name']}: {data['current_price']} ({data['change_percent']:+.2f}%)")
    
    # 주요 주식
    stocks = asian_data.get('major_stocks', {})
    total_stocks = sum(len(market_stocks) for market_stocks in stocks.values())
    print(f"\n주요 주식: {total_stocks}개")
    
    # 시장 요약
    summary = asian_data.get('market_summary', {})
    if summary:
        print(f"\n시장 요약:")
        print(f"  상승 시장: {summary.get('positive_markets', 0)}개")
        print(f"  하락 시장: {summary.get('negative_markets', 0)}개")
        print(f"  평균 변화율: {summary.get('average_change', 0)}%")
        
        best = summary.get('best_performer')
        if best:
            print(f"  최고 성과: {best['market']} ({best['change_percent']:+.2f}%)")

if __name__ == "__main__":
    main()
