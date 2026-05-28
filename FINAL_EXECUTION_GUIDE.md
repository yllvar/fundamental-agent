# 🎉 Fundamental Agent - 최종 Run Guide

## ✅ Troubleshooting 완료!

**OrchestratorStrand import 오류**가 Modify되었고, **HTML 기사 Create System**이 성공적으로 작동합니다!

## 🚀 Execution Method (3가지 옵션)

### 1️⃣ **HTML 기사 Create System (추천 - 안정적)**
```bash
./run_html_articles.sh
```
**특징:**
- ✅ 오류 없이 안정적 작동
- ✅ AI 기사 Create (AWS Bedrock Claude)
- ✅ 아름다운 HTML File Create
- ✅ Slack 알림 자동 전송
- ✅ 실시간 시장 Data 수집

### 2️⃣ **통합 Strands Agent System**
```bash
./run_news_system.sh
```
**특징:**
- 🔧 Import 오류 Modify됨
- 📊 차트 4개 + 이미지 3개 Create
- 🌐 Streamlit 웹페이지 Create
- 📢 광고 추천 System

### 3️⃣ **Slack 알림 포함 Run**
```bash
./run_with_slack_alerts.sh
```
**특징:**
- 📱 향상된 Slack 알림
- 🔍 연결 Test 포함
- 📊 상세한 Run Result

## 📊 Run Result 예시

### HTML 기사 Create System Result
```
🎉 HTML 기사 Create 및 Slack 전송 완료!

📊 Run Result:
Status: success
Run 시간: 37.3초
처리된 이벤트: 2개
Create된 기사: 2개
Slack 알림: 2개

💡 Create된 HTML 기사:
  1. output/html_articles/AAPL_article_20250807_073312.html
  2. output/html_articles/TSLA_article_20250807_073329.html

📱 Slack 채널에서 알림을 Check하세요!
```

## 📱 Slack 알림 내용

### 1. 기사 Create 완료 알림
```
📰 AI Economic  기사 Create 완료

AAPL 주가 5.1% 상승

애플이 올해 한 달러를 기록했다. 이는 올해 새로운 아이폰 모델 출시에 대한 기대감이 반영된 것으로 보인다...

📊 종목: AAPL
📈 변동률: +5.09%
💰 현재가: $213.25
⚠️ 심각도: high

📄 HTML File: AAPL_article_20250807_073312.html
🤖 AI가 실시간 Data를 Analysis하여 자동 Create한 기사입니다.
```

## 📄 Create되는 File들

### HTML 기사 System
```
output/
├── html_articles/
│   ├── AAPL_article_20250807_073312.html    # 완성된 HTML 기사
│   └── TSLA_article_20250807_073329.html
└── market_data/
    └── market_data_20250807_073253.json     # 수집된 시장 Data
```

### 통합 Strands System
```
output/
├── automated_articles/
│   ├── AAPL_20250807_072719.json           # 구조화된 기사 Data
│   └── AAPL_20250807_072719.html           # HTML 기사
├── charts/
│   ├── AAPL_price_volume_20250807.html     # 가격/거래량 차트
│   ├── AAPL_technical_20250807.html        # 기술적 Analysis 차트
│   ├── AAPL_recent_20250807.html           # 최근 동향 차트
│   └── AAPL_comparison_20250807.html       # 비교 Analysis 차트
├── images/
│   ├── AAPL_article_illustration.png       # 기사 일러스트
│   ├── AAPL_price_change.png              # 가격 변동 차트
│   └── AAPL_wordcloud.png                 # word cloud
└── streamlit_articles/
    └── article_AAPL_20250807.py           # Streamlit 웹페이지
```

## 🌐 HTML 기사 Check 방법

### browser 열기
```bash
# 최신 Create된 HTML 기사 열기
open $(ls -t output/html_articles/*.html | head -1)

# 특정 File 열기
open output/html_articles/AAPL_article_20250807_073312.html
```

### 웹서버로 서빙 (선택사항)
```bash
# Python 간단 웹서버
cd output/html_articles
python -m http.server 8000

# browser 접속: http://localhost:8000
```

## 🔧 Troubleshooting

### 1. Import 오류 발생 시
```bash
python fix_orchestrator_import.py
```

### 2. Slack 알림 안 옴
```bash
python test_slack_notification.py
```

### 3. AWS 연결 문제
```bash
aws sts get-caller-identity
aws bedrock list-foundation-models --region us-east-1
```

### 4. 한글 폰트 문제
```bash
./install_korean_fonts.sh
```

## 🎯 자동화 Configuration

### Cron으로 정기 Run
```bash
# 매시간 HTML 기사 Create
0 * * * * cd /path/to/fundamental_agent && ./run_html_articles.sh

# 주식 시장 개장 시간에만 (월-금 9:30-16:00)
30 9-15 * * 1-5 cd /path/to/fundamental_agent && ./run_html_articles.sh
```

### 백그라운드 Run
```bash
# in background Run
nohup ./run_html_articles.sh > logs/html_articles.log 2>&1 &

# Run Status Check
ps aux | grep html_article_slack_system
```

## 📋 Add 명령어

```bash
# System Status Check
python test_agents_system.py

# 최신 HTML 기사 보기
open $(ls -t output/html_articles/*.html | head -1)

# 시장 Data Check
cat $(ls -t output/market_data/*.json | head -1) | jq .

# Slack 연결 Test
python test_slack_notification.py

# 로그 Check
tail -f logs/complete_system_$(date +%Y%m%d).log
```

## 🎉 성공 Check 체크리스트

- [ ] ✅ HTML 기사 Create System Run 성공
- [ ] ✅ AWS Bedrock으로 AI 기사 Create 완료
- [ ] ✅ 아름다운 HTML File Create됨
- [ ] ✅ Slack 알림 2개 전송 성공
- [ ] ✅ 실시간 시장 Data 수집 완료
- [ ] ✅ browser HTML 기사 Check 가능

## 💡 권장 Usage

1. **일일 News Create**: `./run_html_articles.sh` (안정적)
2. **풍부한 콘텐츠**: `./run_news_system.sh` (차트+이미지 포함)
3. **Test 및 Check**: `python test_slack_notification.py`

**현재 Status**: 🎉 **모든 System 정상 작동!**
