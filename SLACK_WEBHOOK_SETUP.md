
🔧 Slack 웹훅 재Create 단계:

1. 📱 Slack workspace 접속
   - workspace: T098W0CB96Z
   - https://app.slack.com/client/T098W0CB96Z

2. 🛠️ 앱 관리 페이지 접속
   - https://api.slack.com/apps
   - 기존 앱이 있다면 Check, 없다면 새로 Create

3. 🆕 새 앱 Create (필요한 경우)
   - "Create New App" → "From scratch"
   - App Name: "Economic NewsSystem" 
   - Workspace: 해당 workspace 선택

4. 📨 Incoming Webhooks Configuration
   - Features → Incoming Webhooks
   - "Activate Incoming Webhooks" ON
   - "Add New Webhook to Workspace"
   - 채널 선택 (예: #general, #alerts)

5. 🔗 새 웹훅 URL Copy
   - Create된 URL을 Copy
   - 형식: https://hooks.slack.com/services/xxxxx/xxxxx/xxxxx.../B.../...

6. ⚙️ System에 적용
   echo "새_웹훅_URL" > config/slack_webhook.txt
   python3 test_slack_webhook.py

🚨 중요 사항:
- 기존 웹훅이 Remove되었거나 비활성화됨
- workspace 관리자 Permissions 필요할 수 있음
- 앱이 workspace에서 제거되었을 가능성
        