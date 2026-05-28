# 📱 Slack 알림 통합 Guide

## 🎯 Overview

Fundamental Agent이 .env File의 Slack 웹훅 URL을 Usage하여 실시간 알림을 전송합니다.

## ✅ Configuration 완료 Status

### .env File Configuration Check됨
```bash
# Slack 알림 Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxxxx/xxxxx/xxxxx

# AWS Configuration
AWS_DEFAULT_REGION=us-east-1

# 기타 API 키들
ALPHA_VANTAGE_API_KEY=9TLAUWS4L3099YK3
FRED_API_KEY=d4235fa1b67058fff90f8a9cc43793c8
```

## 🚀 Execution Method

### 1️⃣ **Slack 알림 포함 통합 Run (추천)**
```bash
./run_with_slack_alerts.sh
```

### 2️⃣ **기본 통합 Run**
```bash
./run_news_system.sh
# 또는
python run_complete_news_system.py
```

### 3️⃣ **Slack 알림만 Test**
```bash
python test_slack_notification.py
```

## 📱 Slack 알림 유형

### 1. System Start 알림
```
🤖 Fundamental Agent Start - 연결 Test
```

### 2. System Run 요약 알림
```
🤖 AI Fundamental Agent
📊 감지된 이벤트: 1개
📰 Create된 기사: 1개
🎯 대상 심볼: AAPL
⏰ Run 시간: 2025-08-07 07:27
```

### 3. 개별 기사 완성 알림
```
📰 새 기사: 애플 주가 상승, 신제품 출시 기대감 반영

애플이 올해 한 달러를 기록했다. 이는 올해 새로운 아이폰 모델 출시에 대한 기대감이 반영된 것으로 보인다...

📊 심볼: AAPL
📈 이벤트: price_change  
⭐ 품질점수: 7.9/10
📢 광고 추천: 3개
```

## 📊 Run Result 예시

### 성공적인 Run
```json
{
  "status": "success",
  "execution_time": 31.9,
  "events_detected": 1,
  "articles_generated": 1,
  "slack_notifications": 2,
  "slack_results": [
    {"status": "success", "message": "Slack 알림 전송 성공"},
    {"status": "success", "message": "Slack 알림 전송 성공"}
  ]
}
```

## 🔧 Troubleshooting

### Slack 알림이 오지 않는 경우

1. **웹훅 URL Check**
```bash
# .env File Check
cat .env | grep SLACK_WEBHOOK_URL

# 연결 Test
python test_slack_notification.py
```

2. **수동 Test**
```bash
curl -X POST -H 'Content-type: application/json' \
--data '{"text":"Test 메시지"}' \
"https://hooks.slack.com/services/xxxxx/xxxxx/xxxxx"
```

3. **로그 Check**
```bash
# Run 로그에서 Slack 관련 오류 Check
grep -i "slack" logs/complete_system_$(date +%Y%m%d).log
```

### 일반적인 오류들

**오류 1: 웹훅 URL 만료**
```
❌ Slack 알림 전송 실패: 404
```
→ Slack 앱에서 새 웹훅 URL Create 필요

**오류 2: 네트워크 연결 문제**
```
❌ 네트워크 오류: Connection timeout
```
→ 인터넷 연결 및 방화벽 Configuration Check

**오류 3: 메시지 형식 오류**
```
❌ Slack 알림 전송 실패: 400
```
→ 메시지 JSON 형식 Check

## 🎯 자동화 Configuration

### Cron으로 정기 Run + Slack 알림
```bash
# 매시간 Run하여 Slack 알림 전송
0 * * * * cd /path/to/fundamental_agent && ./run_with_slack_alerts.sh

# 매일 오전 9시 Run
0 9 * * * cd /path/to/fundamental_agent && ./run_with_slack_alerts.sh

# 주식 시장 개장 시간에만 Run (월-금 9:30-16:00)
30 9-15 * * 1-5 cd /path/to/fundamental_agent && ./run_with_slack_alerts.sh
```

### 백그라운드 Run
```bash
# in background Run하며 Slack 알림 전송
nohup ./run_with_slack_alerts.sh > logs/background_slack.log 2>&1 &

# Run Status Check
ps aux | grep run_complete_news_system
```

## 📈 Slack 알림 최적화

### 알림 빈도 조절
- **긴급 이벤트**: 즉시 알림
- **일반 이벤트**: 1시간마다 요약 알림
- **System Status**: 매일 1회 요약

### 알림 내용 customization
`run_complete_news_system.py`의 메시지 Create 함수를 Modify하여 알림 내용을 조절할 수 있습니다.

## 🔒 Security 고려사항

1. **웹훅 URL Security**
   - .env File을 .gitignore에 Add
   - 웹훅 URL을 공개 Repository에 Commit하지 않음

2. **접근 Permissions 관리**
   - Slack 앱 Permissions을 필요한 채널로만 제한
   - 정기적으로 웹훅 URL 갱신

## 📞 Support

### Test 명령어들
```bash
# 전체 Slack 알림 Test
python test_slack_notification.py

# 통합 System + Slack Run
./run_with_slack_alerts.sh

# System Status Check
python test_agents_system.py
```

### 로그 File 위치
- Run 로그: `logs/complete_system_YYYYMMDD.log`
- 백그라운드 로그: `logs/background_slack.log`

## 🎉 성공 Check

System이 정상 작동하면 Slack 채널에서 다음과 같은 알림들을 받게 됩니다:

1. ✅ **연결 Test 메시지** (System Start 시)
2. 📊 **System Run 요약** (전체 파이프라인 완료 시)
3. 📰 **개별 기사 알림** (기사 Create 완료 시)

**현재 Status**: ✅ 모든 Configuration 완료, Test 성공!
