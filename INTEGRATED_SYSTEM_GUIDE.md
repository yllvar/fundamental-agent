# 🤖 Fundamental Agent 자동 Create 통합 System Guide

## 📋 System Overview

**한번의 명령으로 전체 pipeline Run됩니다:**

```
Data 모니터링 → 이벤트 감지 → 기사 작성 → Slack 알림
```

## 🚀 Execution Method

### 1️⃣ **간단 Run (추천)**
```bash
./run_news_system.sh
```

### 2️⃣ **Python 직접 Run**
```bash
python run_complete_news_system.py
```

### 3️⃣ **Test 모드**
```bash
python run_complete_news_system.py --test
```

## 📊 전체 파이프라인 단계

### 1단계: 📊 Economic  Data 모니터링 및 이벤트 감지
- **모니터링 대상**: 주요 지수, 개별 종목, 원자재, 통화
- **이벤트 유형**: 가격 변동, 거래량 급증, 높은 변동성
- **감지 System**: `event_detection_slack_system.py`

### 2단계: ✍️ 이벤트별 기사 Create (Strands Agent System)
- **Data Analysis Agent**: 차트 4개 Create
  - 가격/거래량 차트
  - 기술적 Analysis 차트
  - 최근 동향 차트
  - 비교 Analysis 차트

- **기사 작성 Agent**: AWS Bedrock Claude 활용
  - 고품질 Economic  기사 Create
  - 전문적인 Analysis 내용

- **기사 검수 Agent**: 품질 관리
  - 품질 점수 평가 (10점 만점)
  - 가독성 및 정확성 검증

- **이미지 Create Agent**: 시각적 콘텐츠
  - 기사 illustration
  - word cloud
  - 이벤트 관련 차트

- **광고 추천 Agent**: 맞춤형 광고
  - 기사 내용 기반 광고 매칭
  - 3개 관련 서비스 추천

### 3단계: 📢 Slack 알림 전송
- **System 요약 알림**: 전체 Run Result
- **개별 기사 알림**: Create된 기사 상세 Information

## 📁 Create되는 출력물

### 기사 File
```
output/automated_articles/
├── AAPL_20250807_072226.json    # 구조화된 기사 Data
└── AAPL_20250807_072226.html    # HTML 형식 기사
```

### 차트 File
```
output/charts/
├── AAPL_price_volume_20250807_072206.html     # 가격/거래량
├── AAPL_technical_20250807_072206.html        # 기술적 Analysis
├── AAPL_recent_20250807_072206.html           # 최근 동향
└── AAPL_comparison_20250807_072206.html       # 비교 Analysis
```

### 이미지 File
```
output/images/
├── AAPL_article_illustration_20250807_072225.png  # 기사 일러스트
├── AAPL_price_change_20250807_072226.png          # 가격 변동 차트
└── AAPL_wordcloud_20250807_072226.png             # word cloud
```

### Streamlit 페이지
```
streamlit_articles/
└── article_AAPL_20250807_072226.py    # 웹 기반 기사 뷰어
```

## 🌐 Create된 기사 Check

### Streamlit 웹 페이지로 보기
```bash
streamlit run streamlit_articles/article_AAPL_20250807_072226.py
```

### HTML File로 보기
```bash
# browser 열기
open output/automated_articles/AAPL_20250807_072226.html
```

## ⚙️ 환경 변수 Configuration

### 필수 Configuration
```bash
# AWS 자격 증명
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# Slack 웹훅 (선택사항)
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/xxxxx/xxxxx/xxxxx"
```

### 선택적 Configuration
```bash
# Alpha Vantage API (고급 Data용)
export ALPHA_VANTAGE_API_KEY=your_api_key
```

## 📊 Run Result 예시

```json
{
  "status": "success",
  "execution_time": 22.4,
  "events_detected": 1,
  "articles_generated": 1,
  "slack_notifications": 2,
  "events": [
    {
      "symbol": "AAPL",
      "event_type": "price_change",
      "severity": "medium",
      "title": "AAPL 주가 변동",
      "description": "AAPL 주가가 3.2% 상승했습니다."
    }
  ]
}
```

## 🔧 Troubleshooting

### 1. AWS 연결 문제
```bash
# AWS 자격 증명 Check
aws sts get-caller-identity

# Bedrock 모델 액세스 Check
aws bedrock list-foundation-models --region us-east-1
```

### 2. Slack 알림 문제
```bash
# 웹훅 URL Test
curl -X POST -H 'Content-type: application/json' \
--data '{"text":"Test 메시지"}' \
$SLACK_WEBHOOK_URL
```

### 3. 한글 폰트 문제
```bash
# 한글 폰트 Installation
./install_korean_fonts.sh
```

### 4. 로그 Check
```bash
# Run 로그 Check
tail -f logs/complete_system_$(date +%Y%m%d).log

# 에러 로그 검색
grep "ERROR" logs/complete_system_$(date +%Y%m%d).log
```

## 🎯 자동화 Configuration

### Cron으로 정기 Run
```bash
# 매시간 Run
0 * * * * cd /path/to/fundamental_agent && ./run_news_system.sh

# 매일 오전 9시 Run
0 9 * * * cd /path/to/fundamental_agent && ./run_news_system.sh
```

### 백그라운드 Run
```bash
# in background Run
nohup ./run_news_system.sh > logs/background.log 2>&1 &

# Run Status Check
ps aux | grep run_complete_news_system
```

## 📈 성능 최적화

- **Run 시간**: 평균 20-30초
- **Create 콘텐츠**: 기사 1개당 7-10개 File
- **메모리 Usage량**: 약 500MB
- **AWS 비용**: 기사 1개당 약 $0.01-0.02

## 🎉 주요 특징

✅ **완전 자동화**: 한 번의 명령으로 전체 파이프라인 Run  
✅ **고품질 콘텐츠**: AWS Bedrock Claude 기반 전문 기사  
✅ **다양한 출력**: JSON, HTML, 이미지, 차트, Streamlit  
✅ **실시간 알림**: Slack 통합으로 즉시 알림  
✅ **확장 가능**: 새로운 Agent 쉽게 Add 가능  
✅ **모니터링**: 상세한 로그 및 Run Result 추적  

## 📞 Support

문제가 발생하면:
1. 로그 File Check
2. 환경 변수 재Configuration
3. System Test Run: `python test_agents_system.py`
