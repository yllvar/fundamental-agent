"""
시장 상관관계 분석 모듈
"""

import numpy as np
import pandas as pd
import yfinance as yf
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import logging
from scipy.stats import pearsonr
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

class CorrelationStrength(Enum):
    VERY_STRONG = "very_strong"      # |r| >= 0.8
    STRONG = "strong"                # 0.6 <= |r| < 0.8
    MODERATE = "moderate"            # 0.4 <= |r| < 0.6
    WEAK = "weak"                    # 0.2 <= |r| < 0.4
    VERY_WEAK = "very_weak"          # |r| < 0.2

class CorrelationDirection(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

@dataclass
class CorrelationPair:
    symbol1: str
    symbol2: str
    correlation: float  # -1.0 to 1.0
    strength: CorrelationStrength
    direction: CorrelationDirection
    p_value: float
    is_significant: bool  # p < 0.05
    
    # 시간별 상관관계 변화
    correlation_1d: float
    correlation_1w: float
    correlation_1m: float
    
    # 상관관계 안정성
    stability_score: float  # 0.0 to 1.0

@dataclass
class MarketCorrelationBreak:
    timestamp: datetime
    symbol1: str
    symbol2: str
    expected_correlation: float
    actual_correlation: float
    deviation_magnitude: float
    significance: float  # 0.0 to 1.0
    description: str

@dataclass
class SectorCorrelation:
    sector_name: str
    symbols: List[str]
    internal_correlation: float  # 섹터 내 평균 상관관계
    market_correlation: float    # 시장 지수와의 상관관계
    correlation_matrix: pd.DataFrame
    
    # 섹터 로테이션 지표
    rotation_signal: str  # "inflow", "outflow", "neutral"
    rotation_strength: float  # 0.0 to 1.0

class CorrelationAnalyzer:
    """시장 상관관계 분석 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 주요 시장 지수 및 섹터 정의
        self.market_indices = {
            "^GSPC": "S&P 500",
            "^IXIC": "NASDAQ",
            "^DJI": "Dow Jones",
            "^VIX": "VIX"
        }
        
        self.sector_etfs = {
            "Technology": ["XLK", "QQQ", "AAPL", "MSFT", "GOOGL", "NVDA"],
            "Healthcare": ["XLV", "JNJ", "PFE", "UNH", "ABBV"],
            "Financial": ["XLF", "JPM", "BAC", "WFC", "GS"],
            "Energy": ["XLE", "XOM", "CVX", "COP", "SLB"],
            "Consumer": ["XLY", "AMZN", "TSLA", "HD", "MCD"],
            "Industrial": ["XLI", "BA", "CAT", "GE", "MMM"]
        }
        
        # 상관관계 기준값 (정상 범위)
        self.normal_correlations = {
            ("^GSPC", "^IXIC"): 0.85,  # S&P 500과 NASDAQ
            ("^GSPC", "^DJI"): 0.90,   # S&P 500과 Dow Jones
            ("^GSPC", "^VIX"): -0.75,  # S&P 500과 VIX
            ("XLK", "QQQ"): 0.95,      # 기술 섹터 ETF와 NASDAQ
        }
    
    def analyze_market_correlations(self, symbols: List[str], period: str = "3mo") -> Dict[str, CorrelationPair]:
        """시장 상관관계 분석"""
        try:
            # 데이터 수집
            price_data = self._collect_price_data(symbols, period)
            
            if price_data.empty:
                self.logger.error("No price data available")
                return {}
            
            # 수익률 계산
            returns = price_data.pct_change().dropna()
            
            # 모든 쌍에 대한 상관관계 계산
            correlations = {}
            
            for i, symbol1 in enumerate(symbols):
                for j, symbol2 in enumerate(symbols[i+1:], i+1):
                    if symbol1 in returns.columns and symbol2 in returns.columns:
                        corr_pair = self._calculate_correlation_pair(
                            returns[symbol1], returns[symbol2], symbol1, symbol2
                        )
                        if corr_pair:
                            correlations[f"{symbol1}_{symbol2}"] = corr_pair
            
            return correlations
            
        except Exception as e:
            self.logger.error(f"Error analyzing correlations: {str(e)}")
            return {}
    
    def detect_correlation_breaks(self, symbols: List[str]) -> List[MarketCorrelationBreak]:
        """상관관계 이탈 감지"""
        breaks = []
        
        try:
            # 현재 상관관계 계산
            current_correlations = self.analyze_market_correlations(symbols, "1mo")
            
            for pair_key, corr_pair in current_correlations.items():
                symbol1, symbol2 = pair_key.split('_')
                pair_tuple = (symbol1, symbol2)
                reverse_tuple = (symbol2, symbol1)
                
                # 기준 상관관계 확인
                expected_corr = None
                if pair_tuple in self.normal_correlations:
                    expected_corr = self.normal_correlations[pair_tuple]
                elif reverse_tuple in self.normal_correlations:
                    expected_corr = self.normal_correlations[reverse_tuple]
                
                if expected_corr is not None:
                    deviation = abs(corr_pair.correlation - expected_corr)
                    
                    # 임계값을 넘는 이탈 감지 (0.2 이상 차이)
                    if deviation > 0.2:
                        significance = min(1.0, deviation / 0.5)  # 0.5 차이를 최대로 정규화
                        
                        break_event = MarketCorrelationBreak(
                            timestamp=datetime.now(),
                            symbol1=symbol1,
                            symbol2=symbol2,
                            expected_correlation=expected_corr,
                            actual_correlation=corr_pair.correlation,
                            deviation_magnitude=deviation,
                            significance=significance,
                            description=f"{symbol1}과 {symbol2}의 상관관계가 예상({expected_corr:.2f})에서 {deviation:.2f} 이탈"
                        )
                        breaks.append(break_event)
            
        except Exception as e:
            self.logger.error(f"Error detecting correlation breaks: {str(e)}")
        
        return breaks
    
    def analyze_sector_correlations(self) -> Dict[str, SectorCorrelation]:
        """섹터별 상관관계 분석"""
        sector_analyses = {}
        
        for sector_name, symbols in self.sector_etfs.items():
            try:
                # 섹터 내 상관관계 분석
                sector_analysis = self._analyze_single_sector(sector_name, symbols)
                if sector_analysis:
                    sector_analyses[sector_name] = sector_analysis
                    
            except Exception as e:
                self.logger.error(f"Error analyzing sector {sector_name}: {str(e)}")
                continue
        
        return sector_analyses
    
    def _collect_price_data(self, symbols: List[str], period: str) -> pd.DataFrame:
        """가격 데이터 수집"""
        price_data = pd.DataFrame()
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                
                if not hist.empty:
                    price_data[symbol] = hist['Close']
                    
            except Exception as e:
                self.logger.error(f"Error collecting data for {symbol}: {str(e)}")
                continue
        
        return price_data.dropna()
    
    def _calculate_correlation_pair(self, series1: pd.Series, series2: pd.Series, 
                                  symbol1: str, symbol2: str) -> Optional[CorrelationPair]:
        """두 시계열 간 상관관계 계산"""
        try:
            # 전체 기간 상관관계
            correlation, p_value = pearsonr(series1, series2)
            
            # 기간별 상관관계
            correlation_1d = pearsonr(series1.tail(1), series2.tail(1))[0] if len(series1) >= 1 else correlation
            correlation_1w = pearsonr(series1.tail(5), series2.tail(5))[0] if len(series1) >= 5 else correlation
            correlation_1m = pearsonr(series1.tail(20), series2.tail(20))[0] if len(series1) >= 20 else correlation
            
            # 상관관계 강도 분류
            strength = self._classify_correlation_strength(abs(correlation))
            
            # 방향 분류
            if correlation > 0.1:
                direction = CorrelationDirection.POSITIVE
            elif correlation < -0.1:
                direction = CorrelationDirection.NEGATIVE
            else:
                direction = CorrelationDirection.NEUTRAL
            
            # 안정성 점수 계산
            stability_score = self._calculate_stability_score([correlation_1d, correlation_1w, correlation_1m, correlation])
            
            return CorrelationPair(
                symbol1=symbol1,
                symbol2=symbol2,
                correlation=correlation,
                strength=strength,
                direction=direction,
                p_value=p_value,
                is_significant=p_value < 0.05,
                correlation_1d=correlation_1d,
                correlation_1w=correlation_1w,
                correlation_1m=correlation_1m,
                stability_score=stability_score
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating correlation for {symbol1}-{symbol2}: {str(e)}")
            return None
    
    def _classify_correlation_strength(self, abs_correlation: float) -> CorrelationStrength:
        """상관관계 강도 분류"""
        if abs_correlation >= 0.8:
            return CorrelationStrength.VERY_STRONG
        elif abs_correlation >= 0.6:
            return CorrelationStrength.STRONG
        elif abs_correlation >= 0.4:
            return CorrelationStrength.MODERATE
        elif abs_correlation >= 0.2:
            return CorrelationStrength.WEAK
        else:
            return CorrelationStrength.VERY_WEAK
    
    def _calculate_stability_score(self, correlations: List[float]) -> float:
        """상관관계 안정성 점수 계산"""
        if len(correlations) < 2:
            return 0.5
        
        # 표준편차가 낮을수록 안정성이 높음
        std_dev = np.std(correlations)
        stability = max(0.0, 1.0 - std_dev * 2)  # 표준편차 0.5를 기준으로 정규화
        
        return min(1.0, stability)
    
    def _analyze_single_sector(self, sector_name: str, symbols: List[str]) -> Optional[SectorCorrelation]:
        """단일 섹터 분석"""
        try:
            # 가격 데이터 수집
            price_data = self._collect_price_data(symbols, "3mo")
            
            if price_data.empty or len(price_data.columns) < 2:
                return None
            
            # 수익률 계산
            returns = price_data.pct_change().dropna()
            
            # 상관관계 매트릭스 계산
            correlation_matrix = returns.corr()
            
            # 섹터 내 평균 상관관계 (대각선 제외)
            mask = np.triu(np.ones_like(correlation_matrix, dtype=bool), k=1)
            internal_correlation = correlation_matrix.where(mask).stack().mean()
            
            # 시장 지수와의 상관관계 (S&P 500 사용)
            market_data = self._collect_price_data(["^GSPC"], "3mo")
            market_correlation = 0.0
            
            if not market_data.empty:
                market_returns = market_data.pct_change().dropna()
                sector_avg_returns = returns.mean(axis=1)
                
                if len(market_returns) > 0 and len(sector_avg_returns) > 0:
                    # 공통 인덱스로 정렬
                    common_index = market_returns.index.intersection(sector_avg_returns.index)
                    if len(common_index) > 10:
                        market_correlation = pearsonr(
                            market_returns.loc[common_index, "^GSPC"],
                            sector_avg_returns.loc[common_index]
                        )[0]
            
            # 섹터 로테이션 신호 계산
            rotation_signal, rotation_strength = self._calculate_rotation_signal(
                returns, market_correlation
            )
            
            return SectorCorrelation(
                sector_name=sector_name,
                symbols=list(price_data.columns),
                internal_correlation=internal_correlation,
                market_correlation=market_correlation,
                correlation_matrix=correlation_matrix,
                rotation_signal=rotation_signal,
                rotation_strength=rotation_strength
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing sector {sector_name}: {str(e)}")
            return None
    
    def _calculate_rotation_signal(self, returns: pd.DataFrame, market_correlation: float) -> Tuple[str, float]:
        """섹터 로테이션 신호 계산"""
        try:
            # 최근 성과 분석 (지난 20일)
            recent_returns = returns.tail(20)
            sector_performance = recent_returns.mean().mean()  # 섹터 평균 수익률
            
            # 시장 대비 상대 성과
            market_data = self._collect_price_data(["^GSPC"], "1mo")
            if not market_data.empty:
                market_returns = market_data.pct_change().dropna().tail(20)
                market_performance = market_returns.mean().iloc[0]
                
                relative_performance = sector_performance - market_performance
                
                # 로테이션 신호 결정
                if relative_performance > 0.002:  # 0.2% 이상 아웃퍼폼
                    signal = "inflow"
                    strength = min(1.0, abs(relative_performance) * 100)
                elif relative_performance < -0.002:  # 0.2% 이상 언더퍼폼
                    signal = "outflow"
                    strength = min(1.0, abs(relative_performance) * 100)
                else:
                    signal = "neutral"
                    strength = 0.5
            else:
                signal = "neutral"
                strength = 0.5
            
            return signal, strength
            
        except Exception as e:
            self.logger.error(f"Error calculating rotation signal: {str(e)}")
            return "neutral", 0.5
    
    def get_correlation_insights(self, correlations: Dict[str, CorrelationPair]) -> List[str]:
        """상관관계 분석 인사이트 생성"""
        insights = []
        
        # 강한 상관관계 찾기
        strong_correlations = [
            pair for pair in correlations.values() 
            if pair.strength in [CorrelationStrength.STRONG, CorrelationStrength.VERY_STRONG]
        ]
        
        if strong_correlations:
            insights.append(f"강한 상관관계 {len(strong_correlations)}개 발견")
        
        # 부정적 상관관계 찾기
        negative_correlations = [
            pair for pair in correlations.values() 
            if pair.direction == CorrelationDirection.NEGATIVE and abs(pair.correlation) > 0.4
        ]
        
        if negative_correlations:
            insights.append(f"강한 역상관관계 {len(negative_correlations)}개 발견")
        
        # 불안정한 상관관계 찾기
        unstable_correlations = [
            pair for pair in correlations.values() 
            if pair.stability_score < 0.5
        ]
        
        if unstable_correlations:
            insights.append(f"불안정한 상관관계 {len(unstable_correlations)}개 발견")
        
        return insights

# 테스트 함수
def test_correlation_analyzer():
    analyzer = CorrelationAnalyzer()
    
    # 주요 지수 상관관계 분석
    symbols = ["^GSPC", "^IXIC", "^DJI", "^VIX", "AAPL", "MSFT", "GOOGL"]
    
    print("=== 시장 상관관계 분석 ===")
    correlations = analyzer.analyze_market_correlations(symbols)
    
    for pair_key, corr_pair in list(correlations.items())[:5]:
        print(f"{corr_pair.symbol1} - {corr_pair.symbol2}:")
        print(f"  상관계수: {corr_pair.correlation:.3f}")
        print(f"  강도: {corr_pair.strength.value}")
        print(f"  안정성: {corr_pair.stability_score:.2f}")
        print()
    
    # 상관관계 이탈 감지
    print("=== 상관관계 이탈 감지 ===")
    breaks = analyzer.detect_correlation_breaks(symbols)
    
    for break_event in breaks:
        print(f"이탈 감지: {break_event.description}")
        print(f"  심각도: {break_event.significance:.2f}")
        print()
    
    # 섹터 분석
    print("=== 섹터 상관관계 분석 ===")
    sector_analyses = analyzer.analyze_sector_correlations()
    
    for sector_name, analysis in list(sector_analyses.items())[:3]:
        print(f"{sector_name} 섹터:")
        print(f"  내부 상관관계: {analysis.internal_correlation:.3f}")
        print(f"  시장 상관관계: {analysis.market_correlation:.3f}")
        print(f"  로테이션 신호: {analysis.rotation_signal}")
        print()

if __name__ == "__main__":
    test_correlation_analyzer()
