#!/usr/bin/env python3
"""
완전한 Alpha Vantage Intelligence API 통합
Demo 키와 새 API 키를 지능적으로 관리
"""

import os
import requests
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)

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
class TopMover:
    ticker: str
    price: float
    change_amount: float
    change_percentage: str
    volume: int

@dataclass
class NewsItem:
    title: str
    source: str
    time_published: datetime
    summary: str
    overall_sentiment_score: float
    overall_sentiment_label: str
    url: str
    topics: List[Dict[str, Any]]

@dataclass
class InsiderTransaction:
    symbol: str
    name: str
    summary: str
    transaction_type: str
    acquisition_or_disposition: str

class AlphaVantageIntelligenceComplete:
    """완전한 Alpha Vantage Intelligence API 클라이언트"""
    
    def __init__(self):
        """초기화 및 지능적 API 키 관리"""
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://www.alphavantage.co/query"
        self.last_call_time = 0
        self.rate_limit_delay = 12  # 초
        
        # API 키 지능적 선택
        self.api_key = self._select_best_api_key()
        self.logger.info(f"🔑 선택된 API 키: {self.api_key}")
        
        # 사용 가능한 기능 확인
        self.available_functions = self._check_available_functions()
        self.logger.info(f"✅ 사용 가능한 기능: {list(self.available_functions.keys())}")
    
    def _select_best_api_key(self) -> str:
        """최적의 API 키 선택"""
        
        # 1. 환경변수에서 새 API 키 확인
        new_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if new_key and new_key != "demo":
            self.logger.info(f"🔍 새 API 키 테스트 중: {new_key}")
            if self._test_api_key(new_key):
                self.logger.info("✅ 새 API 키 활성화 확인됨")
                return new_key
            else:
                self.logger.info("⏳ 새 API 키가 아직 활성화되지 않음")
        
        # 2. Demo 키 테스트
        self.logger.info("🔍 Demo 키 테스트 중")
        if self._test_api_key("demo"):
            self.logger.info("✅ Demo 키 사용 가능")
            return "demo"
        
        # 3. 하드코딩된 새 키 테스트
        hardcoded_key = "9TLAUWS4L3099YK3"
        self.logger.info(f"🔍 하드코딩된 키 테스트 중: {hardcoded_key}")
        if self._test_api_key(hardcoded_key):
            self.logger.info("✅ 하드코딩된 키 활성화 확인됨")
            return hardcoded_key
        
        # 4. 기본값으로 demo 반환
        self.logger.warning("⚠️ 모든 키 테스트 실패. Demo 키를 기본값으로 사용")
        return "demo"
    
    def _test_api_key(self, api_key: str) -> bool:
        """API 키 활성화 상태 테스트"""
        try:
            params = {
                "function": "MARKET_STATUS",
                "apikey": api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            # 실제 데이터가 있으면 활성화됨
            return "markets" in data and len(data["markets"]) > 0
            
        except Exception as e:
            self.logger.debug(f"API 키 테스트 실패: {e}")
            return False
    
    def _check_available_functions(self) -> Dict[str, bool]:
        """사용 가능한 기능들 확인"""
        functions = {
            "MARKET_STATUS": False,
            "TOP_GAINERS_LOSERS": False,
            "NEWS_SENTIMENT": False,
            "INSIDER_TRANSACTIONS": False,
            "EARNINGS_CALL_TRANSCRIPT": False
        }
        
        # Market Status 테스트
        try:
            if self._test_function("MARKET_STATUS"):
                functions["MARKET_STATUS"] = True
        except:
            pass
        
        # Top Gainers/Losers 테스트
        try:
            if self._test_function("TOP_GAINERS_LOSERS"):
                functions["TOP_GAINERS_LOSERS"] = True
        except:
            pass
        
        return functions
    
    def _test_function(self, function_name: str) -> bool:
        """특정 기능 테스트"""
        try:
            params = {
                "function": function_name,
                "apikey": self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            # 에러나 정보 메시지만 있으면 실패
            if "Error Message" in data or ("Information" in data and "rate limit" in data["Information"]):
                return False
            
            # 실제 데이터 키가 있으면 성공
            data_keys = ["markets", "top_gainers", "feed", "data", "transcript"]
            return any(key in data for key in data_keys)
            
        except Exception:
            return False
    
    def _wait_for_rate_limit(self):
        """Rate limit 대기"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - time_since_last_call
            self.logger.debug(f"Rate limit 대기: {wait_time:.1f}초")
            time.sleep(wait_time)
        
        self.last_call_time = time.time()
    
    def get_market_status(self) -> List[MarketStatus]:
        """글로벌 시장 상태 조회"""
        if not self.available_functions.get("MARKET_STATUS", False):
            self.logger.warning("Market Status 기능을 사용할 수 없습니다")
            return []
        
        self._wait_for_rate_limit()
        
        try:
            params = {
                "function": "MARKET_STATUS",
                "apikey": self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "markets" not in data:
                self.logger.warning(f"Market status 데이터 없음: {list(data.keys())}")
                return []
            
            markets = data["markets"]
            market_statuses = []
            
            for market_data in markets:
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
                except Exception as e:
                    self.logger.debug(f"Market status 파싱 오류: {e}")
                    continue
            
            self.logger.info(f"✅ 시장 상태 수집: {len(market_statuses)}개")
            return market_statuses
            
        except Exception as e:
            self.logger.error(f"Market status 조회 오류: {e}")
            return []
    
    def get_top_gainers_losers(self) -> Dict[str, List[TopMover]]:
        """상위 상승/하락/거래량 종목 조회"""
        if not self.available_functions.get("TOP_GAINERS_LOSERS", False):
            self.logger.warning("Top Gainers/Losers 기능을 사용할 수 없습니다")
            return {"top_gainers": [], "top_losers": [], "most_actively_traded": []}
        
        self._wait_for_rate_limit()
        
        try:
            params = {
                "function": "TOP_GAINERS_LOSERS",
                "apikey": self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            result = {
                "top_gainers": [],
                "top_losers": [],
                "most_actively_traded": []
            }
            
            for category in ["top_gainers", "top_losers", "most_actively_traded"]:
                items = data.get(category, [])
                
                for item in items:
                    try:
                        top_mover = TopMover(
                            ticker=item.get("ticker", ""),
                            price=float(item.get("price", 0)),
                            change_amount=float(item.get("change_amount", 0)),
                            change_percentage=item.get("change_percentage", "0%"),
                            volume=int(item.get("volume", 0))
                        )
                        result[category].append(top_mover)
                    except Exception as e:
                        self.logger.debug(f"Top mover 파싱 오류: {e}")
                        continue
            
            total_items = sum(len(movers) for movers in result.values())
            self.logger.info(f"✅ 상위 종목 수집: {total_items}개")
            return result
            
        except Exception as e:
            self.logger.error(f"Top gainers/losers 조회 오류: {e}")
            return {"top_gainers": [], "top_losers": [], "most_actively_traded": []}
    
    def collect_comprehensive_intelligence(self) -> Dict[str, Any]:
        """종합 Intelligence 데이터 수집"""
        self.logger.info("🧠 종합 Intelligence 데이터 수집 시작")
        
        intelligence_data = {
            "timestamp": datetime.now().isoformat(),
            "api_key_used": self.api_key,
            "available_functions": self.available_functions,
            "market_status": [],
            "top_gainers_losers": {},
            "summary": {}
        }
        
        try:
            # 1. 시장 상태 수집
            self.logger.info("🌍 시장 상태 수집 중...")
            market_statuses = self.get_market_status()
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
                for status in market_statuses
            ]
            
            # 2. 상위 종목 수집
            self.logger.info("📈 상위 종목 수집 중...")
            top_movers = self.get_top_gainers_losers()
            
            for category, movers in top_movers.items():
                intelligence_data["top_gainers_losers"][category] = [
                    {
                        "ticker": mover.ticker,
                        "price": mover.price,
                        "change_amount": mover.change_amount,
                        "change_percentage": mover.change_percentage,
                        "volume": mover.volume
                    }
                    for mover in movers
                ]
            
            # 3. 요약 생성
            intelligence_data["summary"] = self._generate_summary(intelligence_data)
            
        except Exception as e:
            self.logger.error(f"종합 데이터 수집 오류: {e}")
        
        total_items = (
            len(intelligence_data["market_status"]) +
            sum(len(movers) for movers in intelligence_data["top_gainers_losers"].values())
        )
        
        self.logger.info(f"✅ 종합 Intelligence 데이터 수집 완료: {total_items}개 항목")
        return intelligence_data
    
    def _generate_summary(self, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 요약 생성"""
        summary = {
            "collection_time": datetime.now().isoformat(),
            "data_counts": {},
            "market_analysis": {},
            "top_movers_analysis": {},
            "highlights": {}
        }
        
        try:
            # 데이터 개수
            market_status = intelligence_data.get("market_status", [])
            top_movers = intelligence_data.get("top_gainers_losers", {})
            
            summary["data_counts"] = {
                "market_status": len(market_status),
                "top_gainers": len(top_movers.get("top_gainers", [])),
                "top_losers": len(top_movers.get("top_losers", [])),
                "most_active": len(top_movers.get("most_actively_traded", []))
            }
            
            # 시장 분석
            if market_status:
                open_markets = [m for m in market_status if m["current_status"] == "open"]
                closed_markets = [m for m in market_status if m["current_status"] == "closed"]
                
                summary["market_analysis"] = {
                    "total_markets": len(market_status),
                    "open_markets": len(open_markets),
                    "closed_markets": len(closed_markets),
                    "open_regions": [m["region"] for m in open_markets]
                }
            
            # 상위 종목 분석
            if "top_gainers" in top_movers and top_movers["top_gainers"]:
                top_gainer = top_movers["top_gainers"][0]
                summary["highlights"]["top_gainer"] = {
                    "ticker": top_gainer["ticker"],
                    "change_percentage": top_gainer["change_percentage"]
                }
            
            if "top_losers" in top_movers and top_movers["top_losers"]:
                top_loser = top_movers["top_losers"][0]
                summary["highlights"]["top_loser"] = {
                    "ticker": top_loser["ticker"],
                    "change_percentage": top_loser["change_percentage"]
                }
            
            if "most_actively_traded" in top_movers and top_movers["most_actively_traded"]:
                most_active = top_movers["most_actively_traded"][0]
                summary["highlights"]["most_active"] = {
                    "ticker": most_active["ticker"],
                    "volume": most_active["volume"]
                }
        
        except Exception as e:
            self.logger.error(f"요약 생성 오류: {e}")
            summary["error"] = str(e)
        
        return summary
    
    def save_intelligence_data(self, intelligence_data: Dict[str, Any], filename: str = None):
        """Intelligence 데이터 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"intelligence_complete_{timestamp}.json"
        
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(intelligence_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📁 Intelligence 데이터 저장: {filepath}")

def main():
    """테스트 실행"""
    print("🧠 완전한 Alpha Vantage Intelligence API 테스트")
    print("=" * 60)
    
    # Intelligence API 초기화
    intelligence = AlphaVantageIntelligenceComplete()
    
    # 종합 데이터 수집
    data = intelligence.collect_comprehensive_intelligence()
    
    # 결과 출력
    summary = data.get("summary", {})
    data_counts = summary.get("data_counts", {})
    market_analysis = summary.get("market_analysis", {})
    highlights = summary.get("highlights", {})
    
    print(f"\n📊 수집 결과:")
    print(f"  🔑 사용된 API 키: {data.get('api_key_used', 'unknown')}")
    print(f"  🌍 시장 상태: {data_counts.get('market_status', 0)}개")
    print(f"  📈 상승 종목: {data_counts.get('top_gainers', 0)}개")
    print(f"  📉 하락 종목: {data_counts.get('top_losers', 0)}개")
    print(f"  🔥 활발한 거래: {data_counts.get('most_active', 0)}개")
    
    if market_analysis:
        print(f"\n🌍 시장 분석:")
        print(f"  📊 총 시장: {market_analysis.get('total_markets', 0)}개")
        print(f"  🟢 개장 시장: {market_analysis.get('open_markets', 0)}개")
        print(f"  🔴 폐장 시장: {market_analysis.get('closed_markets', 0)}개")
        
        open_regions = market_analysis.get('open_regions', [])
        if open_regions:
            print(f"  🌏 개장 지역: {', '.join(open_regions[:5])}")
    
    if highlights:
        print(f"\n🔥 주요 하이라이트:")
        if "top_gainer" in highlights:
            gainer = highlights["top_gainer"]
            print(f"  📈 최고 상승: {gainer['ticker']} ({gainer['change_percentage']})")
        
        if "top_loser" in highlights:
            loser = highlights["top_loser"]
            print(f"  📉 최고 하락: {loser['ticker']} ({loser['change_percentage']})")
        
        if "most_active" in highlights:
            active = highlights["most_active"]
            print(f"  🔥 최고 거래량: {active['ticker']} ({active['volume']:,})")
    
    # 데이터 저장
    intelligence.save_intelligence_data(data)
    
    print(f"\n✅ 테스트 완료!")

if __name__ == "__main__":
    main()
