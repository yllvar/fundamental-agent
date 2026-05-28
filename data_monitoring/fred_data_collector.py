#!/usr/bin/env python3
"""
FRED (Federal Reserve Economic Data) 수집기
"""

import os
import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import time

class FREDDataCollector:
    """FRED 경제 데이터 수집기"""
    
    def __init__(self, api_key: str = None):
        """FRED API 클라이언트 초기화"""
        self.logger = logging.getLogger(__name__)
        
        # FRED API 키 설정 (환경변수 우선)
        self.api_key = api_key or os.getenv('FRED_API_KEY')
        
        if not self.api_key:
            self.logger.warning("⚠️ FRED API 키가 설정되지 않음. Demo 모드로 실행")
            self.api_key = "demo"
        
        self.base_url = "https://api.stlouisfed.org/fred"
        self.last_call_time = 0
        self.rate_limit_delay = 1  # FRED는 관대한 편
        
        # Demo 모드 확인
        self.demo_mode = (self.api_key == "demo")
        
        if self.demo_mode:
            self.logger.info("🔧 FRED Demo 모드 활성화")
        else:
            self.logger.info(f"🔑 FRED API 키 설정 완료: {self.api_key[:8]}...")
        
        # 주요 경제 지표 시리즈 ID
        self.key_series = {
            # 금리 관련
            "federal_funds_rate": "FEDFUNDS",
            "10_year_treasury": "GS10",
            "3_month_treasury": "GS3M",
            "mortgage_rate": "MORTGAGE30US",
            
            # 인플레이션
            "cpi": "CPIAUCSL",
            "core_cpi": "CPILFESL",
            "pce": "PCEPI",
            "core_pce": "PCEPILFE",
            
            # 고용
            "unemployment_rate": "UNRATE",
            "nonfarm_payrolls": "PAYEMS",
            "labor_force_participation": "CIVPART",
            "initial_claims": "ICSA",
            
            # GDP 및 성장
            "gdp": "GDP",
            "real_gdp": "GDPC1",
            "gdp_growth": "A191RL1Q225SBEA",
            "industrial_production": "INDPRO",
            
            # 소비 및 지출
            "retail_sales": "RSAFS",
            "consumer_sentiment": "UMCSENT",
            "personal_income": "PI",
            "personal_spending": "PCE",
            
            # 주택
            "housing_starts": "HOUST",
            "existing_home_sales": "EXHOSLUSM495S",
            "home_price_index": "CSUSHPISA",
            
            # 통화 및 신용
            "money_supply_m1": "M1SL",
            "money_supply_m2": "M2SL",
            "bank_credit": "TOTBKCR",
            
            # 국제 무역
            "trade_balance": "BOPGSTB",
            "exports": "EXPGS",
            "imports": "IMPGS"
        }
        
        self.logger.info("✅ FRED 데이터 수집기 초기화 완료")
    
    def _wait_for_rate_limit(self):
        """Rate limit 대기"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - time_since_last_call
            time.sleep(wait_time)
        
        self.last_call_time = time.time()
    
    def get_series_data(self, series_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """특정 시리즈 데이터 조회"""
        self._wait_for_rate_limit()
        
        try:
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "limit": limit,
                "sort_order": "desc"  # 최신 데이터부터
            }
            
            response = requests.get(
                f"{self.base_url}/series/observations",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "observations" in data:
                    observations = []
                    for obs in data["observations"]:
                        if obs["value"] != ".":  # 결측값 제외
                            try:
                                observations.append({
                                    "date": obs["date"],
                                    "value": float(obs["value"]),
                                    "series_id": series_id
                                })
                            except (ValueError, TypeError):
                                continue
                    
                    self.logger.debug(f"✅ {series_id}: {len(observations)}개 데이터 수집")
                    return observations
                else:
                    self.logger.warning(f"⚠️ {series_id}: 데이터 없음")
                    return []
            else:
                self.logger.error(f"❌ {series_id}: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ {series_id} 조회 오류: {e}")
            return []
    
    def get_series_info(self, series_id: str) -> Dict[str, Any]:
        """시리즈 정보 조회"""
        self._wait_for_rate_limit()
        
        try:
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json"
            }
            
            response = requests.get(
                f"{self.base_url}/series",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "seriess" in data and len(data["seriess"]) > 0:
                    series_info = data["seriess"][0]
                    return {
                        "id": series_info.get("id", ""),
                        "title": series_info.get("title", ""),
                        "units": series_info.get("units", ""),
                        "frequency": series_info.get("frequency", ""),
                        "last_updated": series_info.get("last_updated", ""),
                        "notes": series_info.get("notes", "")
                    }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"❌ {series_id} 정보 조회 오류: {e}")
            return {}
    
    def collect_key_indicators(self) -> Dict[str, Any]:
        """주요 경제 지표 수집"""
        self.logger.info("📊 FRED 주요 경제 지표 수집 시작")
        
        # Demo 모드일 때는 샘플 데이터 생성
        if self.demo_mode:
            return self._generate_demo_data()
        
        fred_data = {
            "timestamp": datetime.now().isoformat(),
            "indicators": {},
            "summary": {}
        }
        
        collected_count = 0
        
        for indicator_name, series_id in self.key_series.items():
            try:
                # 시리즈 정보 조회
                series_info = self.get_series_info(series_id)
                
                # 최근 데이터 조회 (최근 12개월)
                series_data = self.get_series_data(series_id, limit=12)
                
                if series_data:
                    # 최신값과 이전값 비교
                    latest_value = series_data[0]["value"]
                    previous_value = series_data[1]["value"] if len(series_data) > 1 else latest_value
                    change = latest_value - previous_value
                    change_pct = (change / previous_value * 100) if previous_value != 0 else 0
                    
                    fred_data["indicators"][indicator_name] = {
                        "series_id": series_id,
                        "title": series_info.get("title", indicator_name),
                        "units": series_info.get("units", ""),
                        "frequency": series_info.get("frequency", ""),
                        "latest_value": latest_value,
                        "latest_date": series_data[0]["date"],
                        "previous_value": previous_value,
                        "change": round(change, 4),
                        "change_percent": round(change_pct, 2),
                        "data_points": len(series_data),
                        "historical_data": series_data[:6]  # 최근 6개월만 저장
                    }
                    
                    collected_count += 1
                    self.logger.debug(f"✅ {indicator_name}: {latest_value}")
                
            except Exception as e:
                self.logger.error(f"❌ {indicator_name} 수집 오류: {e}")
                continue
        
        # 요약 정보 생성
        fred_data["summary"] = {
            "total_indicators": len(self.key_series),
            "collected_indicators": collected_count,
            "collection_time": datetime.now().isoformat(),
            "key_highlights": self._generate_highlights(fred_data["indicators"])
        }
        
        self.logger.info(f"✅ FRED 데이터 수집 완료: {collected_count}/{len(self.key_series)}개 지표")
        return fred_data
    
    def _generate_demo_data(self) -> Dict[str, Any]:
        """Demo 모드용 샘플 데이터 생성"""
        self.logger.info("📊 FRED Demo 데이터 생성 중...")
        
        import random
        from datetime import datetime, timedelta
        
        demo_data = {
            "timestamp": datetime.now().isoformat(),
            "indicators": {},
            "summary": {}
        }
        
        # 샘플 지표 데이터
        sample_indicators = {
            "federal_funds_rate": {
                "title": "Federal Funds Effective Rate",
                "units": "Percent",
                "latest_value": 5.25,
                "change": 0.25,
                "base_values": [5.0, 5.0, 5.25, 5.25, 5.25, 5.25]
            },
            "unemployment_rate": {
                "title": "Unemployment Rate",
                "units": "Percent",
                "latest_value": 3.8,
                "change": -0.1,
                "base_values": [4.0, 3.9, 3.9, 3.8, 3.8, 3.8]
            },
            "cpi": {
                "title": "Consumer Price Index for All Urban Consumers",
                "units": "Index 1982-1984=100",
                "latest_value": 307.2,
                "change": 0.8,
                "base_values": [305.1, 305.8, 306.4, 306.8, 307.0, 307.2]
            },
            "gdp_growth": {
                "title": "Real Gross Domestic Product",
                "units": "Percent Change at Annual Rate",
                "latest_value": 2.1,
                "change": -0.3,
                "base_values": [2.8, 2.6, 2.4, 2.2, 2.1, 2.1]
            }
        }
        
        for indicator_name, sample_data in sample_indicators.items():
            # 과거 6개월 데이터 생성
            historical_data = []
            base_date = datetime.now()
            
            for i, value in enumerate(sample_data["base_values"]):
                date_str = (base_date - timedelta(days=30*i)).strftime("%Y-%m-%d")
                historical_data.append({
                    "date": date_str,
                    "value": value,
                    "series_id": self.key_series.get(indicator_name, "DEMO")
                })
            
            # 변화율 계산
            latest_value = sample_data["latest_value"]
            previous_value = sample_data["base_values"][1] if len(sample_data["base_values"]) > 1 else latest_value
            change = sample_data["change"]
            change_pct = (change / previous_value * 100) if previous_value != 0 else 0
            
            demo_data["indicators"][indicator_name] = {
                "series_id": self.key_series.get(indicator_name, "DEMO"),
                "title": sample_data["title"],
                "units": sample_data["units"],
                "frequency": "Monthly",
                "latest_value": latest_value,
                "latest_date": datetime.now().strftime("%Y-%m-%d"),
                "previous_value": previous_value,
                "change": round(change, 4),
                "change_percent": round(change_pct, 2),
                "data_points": len(historical_data),
                "historical_data": historical_data
            }
        
        # 요약 정보 생성
        demo_data["summary"] = {
            "total_indicators": len(self.key_series),
            "collected_indicators": len(sample_indicators),
            "collection_time": datetime.now().isoformat(),
            "key_highlights": self._generate_highlights(demo_data["indicators"]),
            "demo_mode": True
        }
        
        self.logger.info(f"✅ FRED Demo 데이터 생성 완료: {len(sample_indicators)}개 지표")
        return demo_data
    
    def _generate_highlights(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """주요 하이라이트 생성"""
        highlights = {}
        
        try:
            # 금리 동향
            if "federal_funds_rate" in indicators:
                fed_rate = indicators["federal_funds_rate"]
                highlights["interest_rates"] = {
                    "federal_funds_rate": fed_rate["latest_value"],
                    "change": fed_rate["change"],
                    "trend": "상승" if fed_rate["change"] > 0 else "하락" if fed_rate["change"] < 0 else "보합"
                }
            
            # 인플레이션 동향
            if "cpi" in indicators:
                cpi = indicators["cpi"]
                highlights["inflation"] = {
                    "cpi_change": cpi["change_percent"],
                    "trend": "상승" if cpi["change"] > 0 else "하락" if cpi["change"] < 0 else "보합"
                }
            
            # 고용 동향
            if "unemployment_rate" in indicators:
                unemployment = indicators["unemployment_rate"]
                highlights["employment"] = {
                    "unemployment_rate": unemployment["latest_value"],
                    "change": unemployment["change"],
                    "trend": "개선" if unemployment["change"] < 0 else "악화" if unemployment["change"] > 0 else "보합"
                }
            
            # GDP 성장
            if "gdp_growth" in indicators:
                gdp_growth = indicators["gdp_growth"]
                highlights["growth"] = {
                    "gdp_growth_rate": gdp_growth["latest_value"],
                    "trend": "확장" if gdp_growth["latest_value"] > 2 else "둔화" if gdp_growth["latest_value"] > 0 else "수축"
                }
        
        except Exception as e:
            self.logger.error(f"하이라이트 생성 오류: {e}")
        
        return highlights
    
    def get_economic_calendar(self) -> List[Dict[str, Any]]:
        """경제 캘린더 (주요 발표 일정)"""
        # FRED API로는 직접 캘린더를 가져올 수 없지만,
        # 주요 지표들의 발표 주기를 기반으로 예상 일정 생성
        
        calendar_items = []
        
        # 월별 발표 지표들
        monthly_indicators = [
            ("CPI", "소비자물가지수", "매월 중순"),
            ("고용통계", "비농업부문 고용", "매월 첫째 금요일"),
            ("소매판매", "소매판매지수", "매월 중순"),
            ("산업생산", "산업생산지수", "매월 중순")
        ]
        
        # 분기별 발표 지표들
        quarterly_indicators = [
            ("GDP", "국내총생산", "분기 말 발표"),
            ("PCE", "개인소비지출", "분기별")
        ]
        
        for name, description, schedule in monthly_indicators + quarterly_indicators:
            calendar_items.append({
                "indicator": name,
                "description": description,
                "schedule": schedule,
                "importance": "high"
            })
        
        return calendar_items

def main():
    """테스트 실행"""
    print("📊 FRED 데이터 수집기 테스트")
    print("=" * 40)
    
    collector = FREDDataCollector()
    
    # 주요 지표 수집
    fred_data = collector.collect_key_indicators()
    
    # 결과 출력
    summary = fred_data.get("summary", {})
    print(f"\n📈 수집 결과:")
    print(f"  총 지표: {summary.get('total_indicators', 0)}개")
    print(f"  수집 성공: {summary.get('collected_indicators', 0)}개")
    
    # 주요 하이라이트
    highlights = summary.get("key_highlights", {})
    if highlights:
        print(f"\n🔥 주요 하이라이트:")
        for category, data in highlights.items():
            print(f"  {category}: {data}")
    
    # 일부 지표 상세 출력
    indicators = fred_data.get("indicators", {})
    if indicators:
        print(f"\n📊 주요 지표 (상위 5개):")
        for i, (name, data) in enumerate(list(indicators.items())[:5], 1):
            print(f"  {i}. {data['title']}: {data['latest_value']} {data['units']}")
            print(f"     변화: {data['change']:+.2f} ({data['change_percent']:+.1f}%)")

if __name__ == "__main__":
    main()
