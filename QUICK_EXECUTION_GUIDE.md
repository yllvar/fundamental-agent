# ⚡ 빠른 Run Guide

Fundamental Agent을 즉시 Run하는 방법입니다.

## 🚀 1분 만에 Start하기

### 1️⃣ **환경 Configuration Check**
```bash
python3 run_complete_system.py --mode setup
```

### 2️⃣ **간편 Run 메뉴**
```bash
./quick_start.sh
```

### 3️⃣ **전체 System Run**
```bash
python3 run_complete_system.py --mode full
```

## 📋 주요 Run 명령어

| 명령어 | 설명 | 필요 조건 |
|--------|------|-----------|
| `./quick_start.sh` | 🎯 대화형 메뉴 | 없음 |
| `--mode full` | 🚀 전체 System | AWS + Slack |
| `--mode news-only` | 🤖 AI News만 | AWS |
| `--mode monitoring-only` | 📊 모니터링만 | 없음 |
| `--mode slack-only` | 📱 Slack 알림만 | Slack |
| `--mode dashboard` | 📈 웹 Dashboard | 없음 |
| `--mode test` | 🧪 System Test | 없음 |

## 🔧 필수 Configuration

### AWS Configuration (AI News Create용)
```bash
aws configure
# 또는
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
export AWS_DEFAULT_REGION="us-east-1"
```

### Slack Configuration (알림용)
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/xxxxx/xxxxx/xxxxx"
```

## 📊 Run Result Check

### 로그 File
```bash
tail -f logs/complete_system_$(date +%Y%m%d).log
```

### 출력 File
```bash
ls -la output/
```

### System Status
```bash
python3 system_monitor.py
```

## 🚨 Troubleshooting

### Dependencies Installation
```bash
pip install -r requirements.txt
```

### Permissions Configuration
```bash
chmod +x *.py *.sh
```

### AWS 연결 Test
```bash
aws sts get-caller-identity
```

### Slack 연결 Test
```bash
curl -X POST -H 'Content-type: application/json' \
--data '{"text":"Test"}' $SLACK_WEBHOOK_URL
```

## 🎯 추천 Run 순서

1. **초기 Configuration**: `--mode setup`
2. **System Test**: `--mode test`  
3. **모니터링 Test**: `--mode monitoring-only`
4. **news generation Test**: `--mode news-only`
5. **전체 System**: `--mode full`

## 📱 백그라운드 Run

### Slack 연속 모니터링
```bash
./start_background_monitoring.sh    # Start
./check_monitoring_status.sh        # Status Check
./stop_monitoring.sh                # Stop
```

## 🎉 성공 Check

Run이 성공하면 다음을 Check할 수 있습니다:

- ✅ **로그 File**: `logs/` Directory에 Run 로그
- ✅ **출력 File**: `output/` Directory에 JSON/HTML Result
- ✅ **Slack 알림**: Configuration된 채널에 실시간 알림
- ✅ **Dashboard**: http://localhost:8501 에서 웹 인터페이스

---

**🚀 이제 완전한 Fundamental Agent을 Usage할 준비가 되었습니다!**
