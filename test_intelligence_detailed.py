#!/usr/bin/env python3
"""
Alpha Vantage Intelligence API 상세 테스트
모든 엔드포인트의 작동 상태를 확인합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_monitoring.alphavantage_intelligence import AlphaVantageIntelligence
from datetime import datetime, timedelta
import json

def test_all_intelligence_endpoints():
    """모든 Intelligence API 엔드포인트 테스트"""
    
    print("🧠 Alpha Vantage Intelligence API 상세 테스트")
    print("=" * 60)
    
    intelligence = AlphaVantageIntelligence()
    
    # 1. Market Status 테스트
    print("\n1️⃣ Market Status (시장 상태)")
    print("-" * 40)
    try:
        market_status = intelligence.get_market_status()
        print(f"✅ 수집된 시장: {len(market_status)}개")
        for status in market_status[:5]:  # 상위 5개만 표시
            print(f"  📍 {status.market} ({status.region}): {status.current_status}")
            if status.notes:
                print(f"     📝 {status.notes}")
    except Exception as e:
        print(f"❌ Market Status 오류: {e}")
    
    # 2. Market News & Sentiment 테스트
    print("\n2️⃣ Market News & Sentiment (시장 뉴스 및 감정)")
    print("-" * 40)
    try:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%dT%H%M")
        market_news = intelligence.get_market_news_sentiment(
            tickers="AAPL,MSFT,GOOGL,TSLA,NVDA",
            time_from=yesterday,
            limit=10
        )
        print(f"✅ 수집된 뉴스: {len(market_news)}개")
        for news in market_news[:3]:  # 상위 3개만 표시
            print(f"  📰 {news.title[:60]}...")
            print(f"     📊 감정: {news.overall_sentiment_label} ({news.overall_sentiment_score:.3f})")
            print(f"     🏢 출처: {news.source}")
            if news.topics:
                topics = [topic.get('topic', '') for topic in news.topics[:2]]
                print(f"     🏷️ 주제: {', '.join(topics)}")
    except Exception as e:
        print(f"❌ Market News 오류: {e}")
    
    # 3. Top Gainers, Losers, Most Active 테스트
    print("\n3️⃣ Top Gainers, Losers & Most Active (상위 종목)")
    print("-" * 40)
    try:
        top_movers = intelligence.get_top_gainers_losers()
        print(f"✅ 수집된 카테고리: {len(top_movers)}개")
        
        for category, movers in top_movers.items():
            print(f"\n  📈 {category.upper()}:")
            for mover in movers[:3]:  # 상위 3개만 표시
                print(f"    {mover.ticker}: ${mover.price} ({mover.change_percentage}%)")
                print(f"      거래량: {mover.volume:,}")
    except Exception as e:
        print(f"❌ Top Movers 오류: {e}")
    
    # 4. Insider Transactions 테스트
    print("\n4️⃣ Insider Transactions (내부자 거래)")
    print("-" * 40)
    try:
        insider_transactions = intelligence.get_insider_transactions()
        print(f"✅ 수집된 거래: {len(insider_transactions)}개")
        for trans in insider_transactions[:3]:  # 상위 3개만 표시
            print(f"  🏢 {trans.symbol} ({trans.name})")
            print(f"     📋 {trans.summary}")
            print(f"     🔄 {trans.transaction_type} - {trans.acquisition_or_disposition}")
    except Exception as e:
        print(f"❌ Insider Transactions 오류: {e}")
    
    # 5. Advanced Analytics (Sliding Window) 테스트
    print("\n5️⃣ Advanced Analytics - Sliding Window (고급 분석)")
    print("-" * 40)
    try:
        analytics_symbols = ["AAPL", "MSFT"]
        analytics_data = intelligence.get_analytics_sliding_window(
            symbols=analytics_symbols,
            range_="1month",
            window_size=10,
            calculations="MEAN,STDDEV"
        )
        print(f"✅ 분석된 심볼: {len(analytics_data)}개")
        
        for symbol, data_points in analytics_data.items():
            print(f"\n  📊 {symbol} 분석:")
            for point in data_points[-3:]:  # 최근 3개만 표시
                print(f"    {point.metric}: {point.value:.4f} ({point.timestamp.strftime('%Y-%m-%d')})")
    except Exception as e:
        print(f"❌ Advanced Analytics 오류: {e}")
    
    # 6. 종합 데이터 수집 테스트
    print("\n6️⃣ Comprehensive Intelligence Collection (종합 수집)")
    print("-" * 40)
    try:
        comprehensive_data = intelligence.collect_comprehensive_intelligence()
        
        summary = {
            "market_status": len(comprehensive_data.get("market_status", [])),
            "market_news": len(comprehensive_data.get("market_news", [])),
            "top_movers_categories": len(comprehensive_data.get("top_movers", {})),
            "insider_transactions": len(comprehensive_data.get("insider_transactions", [])),
            "analytics_symbols": len(comprehensive_data.get("analytics", {}))
        }
        
        print("✅ 종합 데이터 수집 완료:")
        for key, count in summary.items():
            print(f"  📊 {key}: {count}개")
        
        # 하이라이트 추출
        print("\n🔥 주요 하이라이트:")
        
        # 최고 상승/하락 종목
        top_movers = comprehensive_data.get("top_movers", {})
        if "top_gainers" in top_movers and top_movers["top_gainers"]:
            top_gainer = top_movers["top_gainers"][0]
            print(f"  📈 최고 상승: {top_gainer['ticker']} ({top_gainer['change_percentage']}%)")
        
        if "top_losers" in top_movers and top_movers["top_losers"]:
            top_loser = top_movers["top_losers"][0]
            print(f"  📉 최고 하락: {top_loser['ticker']} ({top_loser['change_percentage']}%)")
        
        # 개장 시장 수
        market_status = comprehensive_data.get("market_status", [])
        open_markets = [m for m in market_status if m.get("current_status") == "open"]
        print(f"  🌍 현재 개장 시장: {len(open_markets)}개")
        
        # 감정 분석 요약
        market_news = comprehensive_data.get("market_news", [])
        if market_news:
            sentiments = [news.get("overall_sentiment_score", 0) for news in market_news]
            avg_sentiment = sum(sentiments) / len(sentiments)
            print(f"  💭 평균 시장 감정: {avg_sentiment:.3f}")
        
    except Exception as e:
        print(f"❌ 종합 수집 오류: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 테스트 완료!")

if __name__ == "__main__":
    test_all_intelligence_endpoints()
