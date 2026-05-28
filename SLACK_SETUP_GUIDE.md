# 📱 Slack 알림 System Configuration Guide

Fundamental Agent의 Slack 알림 Features을 Configuration하는 방법을 안내합니다.

## 🔧 1단계: Slack 웹훅 Create

### 1.1 Slack 앱 Create
1. [Slack API 웹사이트](https://api.slack.com/apps)에 접속
2. **"Create New App"** 클릭
3. **"From scratch"** 선택
4. 앱 이름 입력 (예: "Economic News Bot")
5. workspace 선택 후 **"Create App"** 클릭

### 1.2 Incoming Webhooks 활성화
1. Create된 앱의 Configuration 페이지에서 **"Incoming Webhooks"** 클릭
2. **"Activate Incoming Webhooks"** 토글을 **ON**으로 변경
3. **"Add New Webhook to Workspace"** 클릭
4. 알림을 받을 채널 선택 (예: #economic-alerts)
5. **"Allow"** 클릭

### 1.3 웹훅 URL Copy
- Create된 웹훅 URL을 Copy합니다
- 형태: `https://hooks.slack.com/services/xxxxx/xxxxx/xxxxx`

## 🏗️ 2단계: 채널 Configuration

### 2.1 알림 채널 Create
다음 채널들을 Create하는 것을 권장합니다:

```
#economic-alerts     - 일반 Economic  알림
#economic-critical   - 긴급 알림
#economic-summary    - 시장 요약
#economic-news       - News 업데이트
#economic-system     - System Status
```

### 2.2 채널 Configuration
- 각 채널의 목적에 맞는 설명 Add
- 필요시 채널을 프라이빗으로 Configuration
- 관련 팀원들을 채널에 초대

## ⚙️ 3단계: System Configuration

### 3.1 환경 변수 Configuration
```bash
# 환경 변수로 웹훅 URL Configuration
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/xxxxx/xxxxx/xxxxx"

# 또는 .bashrc에 Add
echo 'export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/xxxxx/xxxxx/xxxxx"' >> ~/.bashrc
source ~/.bashrc
```

### 3.2 Configuration File Create
```bash
# Configuration File Copy 및 Modify
cp config/slack_config_template.json config/slack_config.json

# Configuration File 편집
nano config/slack_config.json
```

### 3.3 Configuration File 예시
```json
{
  "webhook_url": "https://hooks.slack.com/services/xxxxx/xxxxx/xxxxx",
  "channel": "#economic-alerts",
  "notification_settings": {
    "send_summary": true,
    "send_critical_alerts": true,
    "send_news_updates": true,
    "summary_interval_minutes": 60,
    "min_alert_severity": 0.6
  }
}
```

## 🚀 4단계: System Run

### 4.1 Dependencies Installation
```bash
pip install aiohttp
```

### 4.2 Test Run
```bash
# Slack 알림 Test
python notifications/slack_notifier.py

# 통합 System Test
python notifications/integrated_slack_monitor.py
```

### 4.3 연속 모니터링 Start
```bash
# 백그라운드 Run
nohup python notifications/integrated_slack_monitor.py > logs/slack_monitor.log 2>&1 &

# 또는 screen Usage
screen -S slack_monitor
python notifications/integrated_slack_monitor.py
# Ctrl+A, D로 detach
```

## 📊 5단계: 알림 유형별 Configuration

### 5.1 긴급 알림 (Critical Alerts)
- **트리거**: 심각도 0.6 이상의 이벤트
- **빈도**: 쿨다운 15분 (긴급시 5분)
- **내용**: 이벤트 상세 Information, 거래 시사점
- **채널**: #economic-critical

### 5.2 시장 요약 (Market Summary)
- **트리거**: 1시간마다 또는 고위험 상황
- **내용**: 전체 위험도, 주요 이벤트, 인사이트
- **채널**: #economic-summary

### 5.3 News 업데이트 (News Updates)
- **트리거**: AI news generation 완료시
- **내용**: 헤드라인, 주요 포인트
- **채널**: #economic-news

### 5.4 System Status (System Status)
- **트리거**: Start/종료/오류 발생시
- **내용**: System Status, 통계 Information
- **채널**: #economic-system

## 🎨 6단계: customization

### 6.1 이모지 customization
```json
{
  "custom_emojis": {
    "surge": "🚀",
    "drop": "💥",
    "volatility": "🌪️"
  }
}
```

### 6.2 메시지 템플릿 Modify
```json
{
  "message_templates": {
    "critical_alert": {
      "title_prefix": "🚨 긴급 알림",
      "mention_users": ["@here"]
    }
  }
}
```

### 6.3 알림 필터링
```json
{
  "notification_settings": {
    "min_alert_severity": 0.7,
    "max_alerts_per_hour": 10,
    "cooldown_minutes": 30
  }
}
```

## 🔍 7단계: 모니터링 및 관리

### 7.1 로그 Check
```bash
# 실시간 로그 모니터링
tail -f logs/slack_monitor.log

# 오류 로그 검색
grep "ERROR" logs/slack_monitor.log
```

### 7.2 통계 Check
```bash
# 알림 통계 조회
python -c "
from notifications.integrated_slack_monitor import SlackIntegratedMonitor
import asyncio
import json

async def show_stats():
    config = {'webhook_url': 'dummy'}
    monitor = SlackIntegratedMonitor(config['webhook_url'])
    stats = monitor.get_alert_statistics()
    print(json.dumps(stats, indent=2))

asyncio.run(show_stats())
"
```

### 7.3 Configuration 업데이트
```bash
# Configuration File Modify 후 System 재Start
pkill -f "integrated_slack_monitor"
python notifications/integrated_slack_monitor.py
```

## 🚨 8단계: Troubleshooting

### 8.1 일반적인 문제들

**웹훅 URL 오류**
```
❌ 오류: Invalid webhook URL
✅ 해결: 웹훅 URL 형식 Check 및 재Create
```

**채널 Permissions 오류**
```
❌ 오류: channel_not_found
✅ 해결: 봇을 채널에 초대하거나 퍼블릭 채널 Usage
```

**알림 과다 발생**
```
❌ 문제: 너무 많은 알림
✅ 해결: min_alert_severity 값 증가 (0.6 → 0.8)
```

### 8.2 디버깅 모드
```bash
# 디버그 로그 활성화
export SLACK_DEBUG=true
python notifications/integrated_slack_monitor.py
```

### 8.3 Test 명령어
```bash
# 웹훅 연결 Test
curl -X POST -H 'Content-type: application/json' \
--data '{"text":"Test 메시지"}' \
YOUR_WEBHOOK_URL

# Python Test
python -c "
import asyncio
from notifications.slack_notifier import SlackNotifier

async def test():
    notifier = SlackNotifier('YOUR_WEBHOOK_URL')
    result = await notifier._send_webhook({'text': 'Test'})
    print('성공' if result else '실패')

asyncio.run(test())
"
```

## 📱 9단계: 모바일 알림 Configuration

### 9.1 Slack 모바일 앱 Configuration
1. Slack 모바일 앱 Installation
2. workspace 로그인
3. 알림 Configuration에서 채널별 알림 활성화
4. 긴급 알림 채널은 "모든 메시지" 알림 Configuration

### 9.2 키워드 알림 Configuration
- "CRITICAL", "HIGH RISK", "긴급" 등 키워드 알림 Configuration
- 특정 심볼 (예: "AAPL", "TSLA") 알림 Configuration

## 🔒 10단계: Security 고려사항

### 10.1 웹훅 URL Security
- 웹훅 URL을 코드에 직접 포함하지 말 것
- 환경 변수나 암호화된 Configuration File Usage
- 정기적으로 웹훅 URL 재Create

### 10.2 채널 접근 제어
- 민감한 Information는 프라이빗 채널 Usage
- 팀원별 채널 접근 Permissions 관리
- 봇 Permissions 최소화

## 📞 Support 및 Contact

문제가 발생하거나 Add Features이 필요한 경우:
1. 로그 File Check (`logs/slack_monitor.log`)
2. GitHub Issues에 문제 보고
3. Configuration File 및 환경 변수 재Check

---

**Notes**: 
- 웹훅 URL은 외부에 노출되지 않도록 주의하세요
- 과도한 알림은 Slack Usage량 제한에 걸릴 수 있습니다
- 중요한 투자 결정은 알림에만 의존하지 마세요
