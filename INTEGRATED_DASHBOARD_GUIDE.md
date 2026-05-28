# 🤖 통합 Fundamental Agent Dashboard Guide

## 📋 Overview

통합 Fundamental Agent은 **Data 모니터링**, **이벤트 감지**, **Slack 알림**, **AI 기사 Create**을 하나의 Streamlit Dashboard에서 관리할 수 있는 통합 솔루션입니다.

## 🚀 빠른 Start

### 1. System Test
```bash
# 모든 구성 요소 Test
python test_integrated_dashboard.py
```

### 2. Dashboard Run
```bash
# 방법 1: 셸 스크립트 Usage (권장)
./start_integrated_system.sh

# 방법 2: Python 스크립트 직접 Run
python run_integrated_dashboard.py

# 방법 3: Streamlit 직접 Run
streamlit run integrated_dashboard.py
```

### 3. 브라우저 접속
- 로컬: http://localhost:8501
- 원격 서버: http://[서버IP]:8501

## 🎛️ Dashboard 구성

### 📊 실시간 모니터링 Tab
- **주요 지수 현황**: S&P 500, NASDAQ, VIX, 달러 인덱스
- **실시간 차트**: 주가 추이, 거래량, 변화율
- **이벤트 타임라인**: 감지된 이벤트의 시간별 분포

### 🚨 이벤트 감지 Tab
- **이벤트 통계**: 총 감지 이벤트, 긴급 이벤트, 처리된 이벤트
- **실시간 이벤트 목록**: 최근 감지된 이벤트 테이블
- **상세 Information**: 개별 이벤트의 세부 Analysis

### 📰 AI 기사 Tab
- **기사 Create 현황**: 총 Create 기사, 품질 점수, 처리 시간
- **기사 목록**: Create된 기사의 제목, 내용, 메타Data
- **수동 기사 Create**: Test용 기사 Create Features

### 📱 Slack 알림 Tab
- **알림 Configuration**: 이벤트 감지, 기사 Create, 시간별 요약 알림
- **Test 알림**: System Status, 이벤트 감지, 기사 Create Test
- **알림 로그**: 최근 전송된 알림 내역

## 🎛️ 사이드바 제어판

### 📊 모니터링 제어
- **🚀 모니터링 Start**: 실시간 Data 수집 및 이벤트 감지 Start
- **⏹️ 모니터링 Stop**: 모니터링 Process Stop
- **Status 표시**: 현재 모니터링 Status (활성/비활성)

### ⚙️ Configuration
- **모니터링 간격**: 10초~300초 (기본: 60초)
- **알림 임계값**: 1%~10% (기본: 3%)

### 📱 Slack Configuration
- **웹훅 Status**: Slack 웹훅 URL Configuration Check
- **Configuration Guide**: 미Configuration 시 안내 메시지

### ✍️ 수동 기사 Create
- **📝 Test 기사 Create**: 샘플 이벤트 기반 기사 Create

## 🔧 주요 Features

### 1. 실시간 Data 모니터링
- **Data 소스**: Yahoo Finance API
- **모니터링 대상**: AAPL, GOOGL, MSFT, TSLA, NVDA, ^GSPC, ^IXIC, ^VIX
- **업데이트 주기**: 1분 (Configuration 가능)

### 2. 지능형 이벤트 감지
- **가격 변동**: 2% 이상 변화 시 이벤트 감지
- **거래량 급증**: 평균 대비 2배 이상 시 감지
- **VIX 특별 모니터링**: 25 이상 시 고변동성 경고
- **심각도 분류**: Low, Medium, High, Critical

### 3. 자동 기사 Create
- **트리거 조건**: 심각도 0.7 이상 이벤트
- **기사 구성**: 제목, 리드, 본문, 결론
- **품질 평가**: 1-10점 자동 채점
- **메타Data**: 심볼, 이벤트 유형, Create 시간

### 4. Slack 통합 알림
- **이벤트 알림**: 심각도 0.6 이상 이벤트 즉시 알림
- **기사 알림**: 새 기사 Create 완료 시 알림
- **System Status**: 주기적 System 현황 리포트
- **Rich 메시지**: Slack Blocks API 활용한 구조화된 메시지

## 📊 이벤트 유형

### 가격 기반 이벤트
- **price_spike**: 3% 이상 급등
- **price_drop**: 3% 이상 급락
- **price_change**: 2-3% 변동

### 거래량 기반 이벤트
- **volume_spike**: 평균 대비 2배 이상 거래량

### 변동성 기반 이벤트
- **high_volatility**: VIX 25 이상

## 🔔 알림 Configuration

### 알림 유형
1. **이벤트 감지 알림**: 실시간 시장 이벤트
2. **기사 Create 알림**: AI 기사 완성 통지
3. **System Status 알림**: 주기적 Status 리포트

### 알림 임계값
- **기본값**: 3% 가격 변동
- **조정 범위**: 1% ~ 10%
- **심각도 기준**: 0.6 이상 자동 알림

## 🛠️ Troubleshooting

### 일반적인 문제

#### 1. 모니터링이 Start되지 않음
```bash
# 환경 변수 Check
python test_integrated_dashboard.py

# 로그 Check
tail -f logs/fundamental_agent_$(date +%Y%m%d).log
```

#### 2. Slack 알림이 전송되지 않음
```bash
# 웹훅 URL Check
echo $SLACK_WEBHOOK_URL

# 수동 Test
curl -X POST -H 'Content-type: application/json' \
--data '{"text":"Test"}' $SLACK_WEBHOOK_URL
```

#### 3. Data 수집 실패
- 인터넷 연결 Check
- Yahoo Finance API Status Check
- 방화벽 Configuration Check

#### 4. 차트가 표시되지 않음
- Plotly Installation Check: `pip install plotly`
- 브라우저 JavaScript 활성화 Check

### 로그 Check
```bash
# 실시간 로그 모니터링
tail -f logs/fundamental_agent_$(date +%Y%m%d).log

# 오류 로그 검색
grep "ERROR" logs/fundamental_agent_$(date +%Y%m%d).log
```

## 📈 성능 최적화

### 1. 모니터링 간격 조정
- **고빈도**: 10-30초 (높은 리소스 Usage)
- **표준**: 60초 (권장)
- **저빈도**: 300초 (낮은 리소스 Usage)

### 2. 메모리 관리
- 이벤트 히스토리: 최근 10개만 유지
- 기사 목록: 자동 정리 Features
- 차트 Data: 캐싱 활용

### 3. 네트워크 최적화
- API 호출 제한 준수
- 실패 시 재시도 로직
- 타임아웃 Configuration

## 🔒 Security 고려사항

### 환경 변수 관리
```bash
# .env File Permissions Configuration
chmod 600 .env

# 민감한 Information Check
grep -E "(KEY|TOKEN|SECRET)" .env
```

### Slack 웹훅 Security
- 웹훅 URL 외부 노출 금지
- 정기적인 웹훅 URL 갱신
- 알림 내용 민감 Information 필터링

## 📚 Add 리소스

### 관련 문서
- [SLACK_SETUP_GUIDE.md](SLACK_SETUP_GUIDE.md): Slack Configuration Guide
- [EXECUTION_GUIDE.md](EXECUTION_GUIDE.md): 전체 System Run Guide
- [README.md](README.md): 프로젝트 전체 Overview

### Support 및 Contact
- GitHub Issues: 버그 리포트 및 Features 요청
- 로그 File: 문제 진단을 위한 상세 Information
- Test 스크립트: System Status 자가 진단

---

## 🎉 성공적인 Run 예시

```bash
$ python test_integrated_dashboard.py
🤖 통합 Dashboard Test Start
==================================================
📦 모듈 import Test 중...
✅ Streamlit 로드 성공
✅ Pandas 로드 성공
✅ Plotly 로드 성공
✅ yfinance 로드 성공
✅ requests 로드 성공
✅ python-dotenv 로드 성공

⚙️ 환경 변수 Test 중...
✅ SLACK_WEBHOOK_URL: Configuration됨
✅ ALPHA_VANTAGE_API_KEY: Configuration됨
✅ AWS_DEFAULT_REGION: Configuration됨

📊 Data 수집 Test 중...
✅ AAPL Data 수집 성공: 78개 Data포인트
   최신 가격: $213.25

📱 Slack 웹훅 Test 중...
✅ Slack 웹훅 Test 성공

==================================================
📋 Test Result 요약
==================================================
모듈 Import: ✅ 통과
환경 변수: ✅ 통과
Data 수집: ✅ 통과
Slack 웹훅: ✅ 통과

총 4개 Test 중 4개 통과

🎉 모든 Test가 passed!
💡 다음 명령어로 통합 Dashboard를 Run하세요:
   ./start_integrated_system.sh
```

이제 통합 Dashboard가 완전히 is ready! 🚀
