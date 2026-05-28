# 🤖 통합 Fundamental Agent - 최종 Run Guide

## 🎯 완성된 System Overview

통합 Fundamental Agent이 성공적으로 has been built! 이 System은 다음 Features들을 하나의 Streamlit Dashboard에서 제공합니다:

### ✅ 구현된 주요 Features
1. **📊 실시간 Data 모니터링**: Yahoo Finance API를 통한 주식 Data 수집
2. **🚨 지능형 이벤트 감지**: 가격 변동, 거래량 급증, VIX 변동성 감지
3. **📱 Slack 자동 알림**: 이벤트 감지 시 즉시 Slack 채널로 알림 전송
4. **📰 AI 기사 자동 Create**: 감지된 이벤트 기반 Economic  기사 자동 작성
5. **🎛️ 통합 제어판**: 모든 Features을 하나의 웹 인터페이스에서 관리

## 🚀 System Execution Method

### 1. 사전 Test (필수)
```bash
# 모든 구성 요소 Test
python test_integrated_dashboard.py
```

### 2. 통합 Dashboard Run
```bash
# 방법 1: 셸 스크립트 Usage (권장)
./start_integrated_system.sh

# 방법 2: Python 스크립트 Usage
python run_integrated_dashboard.py

# 방법 3: Streamlit 직접 Run
streamlit run integrated_dashboard.py --server.port=8501 --server.address=0.0.0.0
```

### 3. 브라우저 접속
- **로컬 접속**: http://localhost:8501
- **원격 접속**: http://[서버IP]:8501

## 🎛️ Dashboard Usage

### 📊 실시간 모니터링 Tab
1. **사이드바**에서 "🚀 모니터링 Start" 버튼 클릭
2. **주요 지수 현황** 실시간 Check (S&P 500, NASDAQ, VIX 등)
3. **실시간 차트** 및 **이벤트 타임라인** 모니터링

### 🚨 이벤트 감지 Tab
1. 감지된 이벤트 통계 Check
2. 최근 이벤트 목록에서 상세 Information Check
3. "🔍 최신 이벤트 상세 보기"로 심층 Analysis

### 📰 AI 기사 Tab
1. 자동 Create된 기사 목록 Check
2. 기사 품질 점수 및 메타Data 검토
3. "📝 Test 기사 Create"으로 수동 기사 Create

### 📱 Slack 알림 Tab
1. Slack 웹훅 Configuration Status Check
2. 알림 Configuration 조정 (임계값, 알림 유형)
3. Test 알림 전송으로 연동 Check

## 🔧 주요 Configuration

### 환경 변수 (.env File)
```bash
# Slack 알림
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxxxx/xxxxx/xxxxx

# Data 수집
ALPHA_VANTAGE_API_KEY=your_api_key

# AWS Configuration
AWS_DEFAULT_REGION=us-east-1
```

### 모니터링 Configuration
- **모니터링 간격**: 10초~300초 (기본: 60초)
- **알림 임계값**: 1%~10% (기본: 3%)
- **모니터링 대상**: AAPL, GOOGL, MSFT, TSLA, NVDA, ^GSPC, ^IXIC, ^VIX

## 📊 이벤트 감지 로직

### 가격 변동 기반
- **3% 이상 변동**: 심각도 0.7 (긴급 알림 + 기사 Create)
- **2-3% 변동**: 심각도 0.5 (일반 알림)

### 거래량 기반
- **평균 대비 2배 이상**: 심각도 0.6 (알림 전송)

### VIX 특별 모니터링
- **25 이상**: 심각도 0.8 (고변동성 경고)

## 📱 Slack 알림 유형

### 1. 이벤트 감지 알림
```
🚨 시장 이벤트 감지
AAPL Price Spike
현재가: $213.25 (+3.5%)
심각도: HIGH
```

### 2. 기사 Create 알림
```
📰 AI 기사 Create 완료
Apple 주가 3.5% 상승, 기술주 강세 지속
품질점수: 8.5/10
단어수: 245개
```

### 3. System Status 알림
```
🤖 System Status 리포트
Status: 🟢 정상 운영
모니터링: 활성
감지된 이벤트: 3개
Create된 기사: 2개
```

## 🛠️ Troubleshooting

### 일반적인 문제

#### 1. Test 실패 시
```bash
# Dependencies 재Installation
pip install -r requirements.txt

# 환경 변수 Check
cat .env

# AWS 자격 증명 Check
aws sts get-caller-identity
```

#### 2. Slack 알림 실패 시
```bash
# 웹훅 URL Test
curl -X POST -H 'Content-type: application/json' \
--data '{"text":"Test"}' $SLACK_WEBHOOK_URL
```

#### 3. Data 수집 실패 시
- 인터넷 연결 Check
- Yahoo Finance API Status Check
- 방화벽 Configuration Check

## 📈 System 모니터링

### 로그 Check
```bash
# 실시간 로그
tail -f logs/fundamental_agent_$(date +%Y%m%d).log

# 오류 검색
grep "ERROR" logs/fundamental_agent_$(date +%Y%m%d).log
```

### 성능 모니터링
- **CPU Usage률**: 모니터링 간격 조정으로 제어
- **메모리 Usage량**: 이벤트 히스토리 자동 정리
- **네트워크**: API 호출 제한 준수

## 🎯 성공적인 Run Check

### 1. Test Result
```bash
🎉 모든 Test가 passed!
총 4개 Test 중 4개 통과
- 모듈 Import: ✅ 통과
- 환경 변수: ✅ 통과  
- Data 수집: ✅ 통과
- Slack 웹훅: ✅ 통과
```

### 2. Dashboard 접속 Check
- browser http://localhost:8501 접속
- 4개 Tab 모두 정상 표시
- 사이드바 제어판 정상 작동

### 3. 실시간 Features Check
- 모니터링 Start 후 실시간 Data 업데이트
- 이벤트 감지 시 Slack 알림 수신
- 기사 자동 Create 및 표시

## 🚀 다음 단계

### 확장 가능한 Features
1. **AWS Bedrock 연동**: 더 고품질 AI 기사 Create
2. **Add Data 소스**: Alpha Vantage, FRED API 활용
3. **고급 Analysis**: 기술적 지표, 감정 Analysis Add
4. **모바일 최적화**: 반응형 디자인 개선

### 운영 최적화
1. **자동화**: cron job을 통한 스케줄링
2. **확장성**: Docker 컨테이너화
3. **모니터링**: System 헬스 체크 Add
4. **백업**: Data 및 Configuration 백업 자동화

---

## 🎉 축하합니다!

통합 Fundamental Agent이 성공적으로 has been built. 이제 다음 명령어로 System을 Run하고 실시간 Fundamental Agent 모니터링을 Start하세요:

```bash
./start_integrated_system.sh
```

System이 정상적으로 작동하면 Slack 채널에서 실시간 알림을 받을 수 있고, 웹 Dashboard에서 모든 Features을 모니터링할 수 있습니다! 🚀📊📰📱
