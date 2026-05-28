# 🔧 Slack 웹훅 Configuration Guide

## 현재 문제
- 기존 웹훅 URL이 "no_service" 응답을 반환
- 웹훅이 비활성화되었거나 Remove된 Status

## 해결 방법

### 1. 새로운 Slack 앱 Create

1. **Slack API 사이트 접속**
   - https://api.slack.com/apps 방문
   - "Create New App" 클릭

2. **앱 Create**
   - "From scratch" 선택
   - App Name: "Fundamental Agent" (또는 원하는 이름)
   - Workspace: 알림을 받을 workspace 선택

### 2. Incoming Webhooks 활성화

1. **Features > Incoming Webhooks** 메뉴 선택
2. **Activate Incoming Webhooks** 토글을 ON으로 Configuration
3. **Add New Webhook to Workspace** 버튼 클릭
4. 알림을 받을 채널 선택 (예: #general, #Economic News)
5. **Allow** 버튼 클릭

### 3. 웹훅 URL Copy

Create된 웹훅 URL을 Copy합니다:
```
https://hooks.slack.com/services/xxxxx/xxxxx/xxxxx.../B.../...
```

### 4. System에 웹훅 URL Configuration

아래 명령어로 새 웹훅 URL을 Configuration하세요:

```bash
# 웹훅 URL을 File에 저장
echo "새로운_웹훅_URL" > config/slack_webhook.txt

# 또는 환경변수로 Configuration
export SLACK_WEBHOOK_URL="새로운_웹훅_URL"
```

### 5. Test

```bash
# 웹훅 Test
python3 test_slack_webhook.py

# 또는 curl로 직접 Test
curl -X POST -H 'Content-type: application/json' \
--data '{"text":"✅ 새 웹훅 Test 성공!"}' \
"새로운_웹훅_URL"
```

## Add Configuration (선택사항)

### 앱 customization
- **Display Information**: 앱 이름, 아이콘, 설명 Configuration
- **Bot Users**: 봇 User Add (고급 Features용)

### Permissions Configuration
- **OAuth & Permissions**: 필요한 경우 Add Permissions Configuration

## Troubleshooting

### 여전히 "no_service" 오류가 발생하는 경우:
1. 웹훅 URL이 올바르게 Copy되었는지 Check
2. workspace 관리자 Permissions Check
3. 앱이 workspace에 정상 Installation되었는지 Check

### 메시지가 전송되지 않는 경우:
1. 채널 Permissions Check
2. 앱이 해당 채널에 접근 Permissions이 있는지 Check
3. JSON 형식이 올바른지 Check

## Security Notes
- 웹훅 URL을 공개 Repository에 업로드하지 마세요
- 환경변수나 Configuration File로 안전하게 관리하세요
- 정기적으로 웹훅 URL을 갱신하세요
