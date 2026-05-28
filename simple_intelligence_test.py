#!/usr/bin/env python3
"""
간단한 Intelligence API 테스트
"""

import requests
import os
from dataclasses import dataclass
from typing import List, Dict, Any
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
class TopMover:
    ticker: str
    price: float
    change_amount: float
    change_percentage: str
    volume: int

def get_market_status() -> List[MarketStatus]:
    """시장 상태 조회"""
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
    
    params = {
        "function": "MARKET_STATUS",
        "apikey": api_key
    }
    
    response = requests.get("https://www.alphavantage.co/query", params=params, timeout=30)
    data = response.json()
    
    markets = data.get("markets", [])
    market_statuses = []
    
    print(f"📊 API에서 받은 시장 데이터: {len(markets)}개")
    
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
            print(f"✅ 파싱 성공 {i+1}: {market_status.region} ({market_status.current_status})")
        except Exception as e:
            print(f"❌ 파싱 실패 {i+1}: {e}")
            print(f"   데이터: {market_data}")
    
    return market_statuses

def get_top_movers() -> Dict[str, List[TopMover]]:
    """상위 종목 조회"""
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
    
    params = {
        "function": "TOP_GAINERS_LOSERS",
        "apikey": api_key
    }
    
    response = requests.get("https://www.alphavantage.co/query", params=params, timeout=30)
    data = response.json()
    
    result = {
        "top_gainers": [],
        "top_losers": [],
        "most_actively_traded": []
    }
    
    for category in ["top_gainers", "top_losers", "most_actively_traded"]:
        items = data.get(category, [])
        print(f"📊 API에서 받은 {category} 데이터: {len(items)}개")
        
        for i, item in enumerate(items):
            try:
                top_mover = TopMover(
                    ticker=item.get("ticker", ""),
                    price=float(item.get("price", 0)),
                    change_amount=float(item.get("change_amount", 0)),
                    change_percentage=item.get("change_percentage", "0%"),
                    volume=int(item.get("volume", 0))
                )
                result[category].append(top_mover)
                print(f"✅ 파싱 성공 {category} {i+1}: {top_mover.ticker} ({top_mover.change_percentage})")
            except Exception as e:
                print(f"❌ 파싱 실패 {category} {i+1}: {e}")
                print(f"   데이터: {item}")
    
    return result

def main():
    """메인 테스트"""
    print("🧠 간단한 Intelligence API 테스트")
    print("=" * 50)
    
    # 1. Market Status 테스트
    print("\n1️⃣ Market Status 테스트:")
    market_statuses = get_market_status()
    print(f"📊 최종 결과: {len(market_statuses)}개 시장")
    
    if market_statuses:
        open_markets = [m for m in market_statuses if m.current_status == "open"]
        closed_markets = [m for m in market_statuses if m.current_status == "closed"]
        
        print(f"🟢 개장 시장: {len(open_markets)}개")
        print(f"🔴 폐장 시장: {len(closed_markets)}개")
        
        print("\n상위 5개 시장:")
        for market in market_statuses[:5]:
            status_emoji = "🟢" if market.current_status == "open" else "🔴"
            print(f"  {status_emoji} {market.region}: {market.current_status}")
    
    # 2. Top Movers 테스트
    print("\n2️⃣ Top Movers 테스트:")
    top_movers = get_top_movers()
    
    for category, movers in top_movers.items():
        print(f"\n📈 {category.replace('_', ' ').title()}: {len(movers)}개")
        
        if movers:
            print("  상위 3개:")
            for mover in movers[:3]:
                print(f"    {mover.ticker}: {mover.change_percentage} (거래량: {mover.volume:,})")
    
    # 3. 결과 저장
    result = {
        "market_status": [
            {
                "region": m.region,
                "current_status": m.current_status,
                "primary_exchanges": m.primary_exchanges
            }
            for m in market_statuses
        ],
        "top_movers": {
            category: [
                {
                    "ticker": m.ticker,
                    "change_percentage": m.change_percentage,
                    "volume": m.volume
                }
                for m in movers[:5]  # 상위 5개만
            ]
            for category, movers in top_movers.items()
        }
    }
    
    with open("output/simple_intelligence_test.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 테스트 완료! 결과 저장: output/simple_intelligence_test.json")

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    main()
