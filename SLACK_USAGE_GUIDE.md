# 📱 Slack Economic  알림 System Usage

웹훅 URL이 Configuration되어 Slack 알림 System이 is ready!

## 🎯 **Configuration 완료 Status**

✅ **웹훅 URL**: `https://hooks.slack.com/services/xxxxx/xxxxx/xxxxx`  
✅ **Configuration File**: `config/slack_config.json`  
✅ **연결 Test**: 성공  
✅ **실제 알림 Test**: 성공 (8개 이벤트 감지, 위험도 VERY_HIGH)

## 🚀 **Usage 방법**

### **1. 즉시 Test (단일 Run)**
```bash
# 현재 시장 상황 Analysis + Slack 알림 전송
python demo_slack_alerts.py
# Run 시 'y' 입력하면 실제 Slack으로 알림 전송
```

### **2. 연속 모니터링 Start**
```bash
# 포그라운드 Run (터미널에서 직접 Check)
python start_slack_monitoring.py

# 백그라운드 Run (서버용)
./start_background_monitoring.sh
```

### **3. 모니터링 관리**
```bash
# Status Check
./check_monitoring_status.sh

# 모니터링 Stop
./stop_monitoring.sh

# 로그 실시간 Check
tail -f logs/background_monitoring.log
```

## 📊 **받게 될 알림 유형**

### **1. 시장 요약 알림 (1시간마다)**
```
📊 Market Analysis Summary - 2025-08-05 11:30

위험도: 🔴 VERY HIGH
감지된 이벤트: 8개
위험 점수: 1.00/1.00

🚨 주요 알림:
1. [^VIX] CBOE Volatility Index: ^VIX MACD 강세 신호
2. [GOOGL] Alphabet Inc.: GOOGL MACD 강세 신호
3. [MSFT] Microsoft Corporation: MSFT MACD 강세 신호

💡 주요 인사이트:
• 가장 빈번한 이벤트: momentum_divergence (6회)
• 고심각도 이벤트 5개 발생
```

### **2. 긴급 알림 (심각도 0.6 이상)**
```
🔴 CRITICAL ALERT 📈

AAPL - Technical Breakout
심볼: AAPL
심각도: 0.85
시간: 11:30:15

상세 Information:
• change_percent: -2.5
• current_price: 202.38
• volume: 104301700
• confidence: 0.8
```

### **3. News 업데이트 알림**
```
📰 새로운 AI Fundamental Agent가 Create되었습니다

AI Create Fundamental Agent 업데이트
Create 시간: 2025-08-05 11:30:00
```

### **4. System Status 알림**
```
🔧 System Status Report

System Status: 🟢 Run 중
모니터링 심볼: 13개
최근 위험도: VERY_HIGH
마지막 Analysis: 2025-08-05T11:30:00
```

## ⚙️ **알림 Configuration customization**

### **현재 Configuration (`config/slack_config.json`)**
```json
{
  "notification_settings": {
    "send_summary": true,              // 시장 요약 알림
    "send_critical_alerts": true,      // 긴급 알림
    "send_news_updates": true,         // News 업데이트
    "summary_interval_minutes": 60,    // 요약 알림 간격 (1시간)
    "min_alert_severity": 0.6,         // 최소 알림 심각도
    "max_alerts_per_hour": 15,         // 시간당 최대 알림 수
    "cooldown_minutes": 15             // 동일 심볼 쿨다운 (15분)
  }
}
```

### **Configuration 변경 방법**
```bash
# Configuration File 편집
nano config/slack_config.json

# 변경 후 모니터링 재Start
./stop_monitoring.sh
./start_background_monitoring.sh
```

### **추천 Configuration 조합**

**🔥 적극적 알림 (트레이더용)**
```json
{
  "min_alert_severity": 0.5,
  "max_alerts_per_hour": 25,
  "cooldown_minutes": 10,
  "summary_interval_minutes": 30
}
```

**🛡️ 보수적 알림 (장기투자자용)**
```json
{
  "min_alert_severity": 0.8,
  "max_alerts_per_hour": 8,
  "cooldown_minutes": 30,
  "summary_interval_minutes": 120
}
```

## 📱 **모바일 알림 최적화**

### **Slack 모바일 앱 Configuration**
1. **Slack 앱 Installation** (iOS/Android)
2. workspace 로그인
3. **Configuration → 알림 → 모바일 Push 알림**
4. **"모든 새 메시지"** 또는 **"직접 메시지, 멘션, 키워드"** 선택

### **키워드 알림 Configuration**
- **"CRITICAL"**, **"긴급"**, **"HIGH"** 등 키워드 알림 Configuration
- 관심 종목 심볼 Add (예: "AAPL", "TSLA", "NVDA")

## 📊 **모니터링 현황 Check**

### **실시간 Status Check**
```bash
# 전체 Status Check
./check_monitoring_status.sh

# 로그 실시간 모니터링
tail -f logs/background_monitoring.log

# 오류 로그만 Check
grep ERROR logs/background_monitoring.log
```

### **알림 통계 Check**
```bash
# 오늘 전송된 알림 수
grep "Slack 알림 전송 성공" logs/slack_monitoring.log | wc -l

# 최근 오류 Check
grep "ERROR" logs/slack_monitoring.log | tail -5
```

## 🔧 **Troubleshooting**

### **일반적인 문제들**

**1. 알림이 오지 않음**
```bash
# Process Status Check
./check_monitoring_status.sh

# 웹훅 URL Test
curl -X POST -H 'Content-type: application/json' \
--data '{"text":"Test 메시지"}' \
"https://hooks.slack.com/services/xxxxx/xxxxx/xxxxx"
```

**2. 알림이 너무 많음**
```bash
# Configuration File에서 조정
nano config/slack_config.json
# min_alert_severity를 0.6에서 0.8로 증가
# max_alerts_per_hour를 15에서 8로 감소
```

**3. Process가 Stop됨**
```bash
# 로그 Check
tail -20 logs/background_monitoring.log

# 재Start
./start_background_monitoring.sh
```

### **고급 디버깅**
```bash
# 상세 로그 활성화
export SLACK_DEBUG=true
python start_slack_monitoring.py

# 네트워크 연결 Check
ping hooks.slack.com

# 디스크 공간 Check
df -h
```

## 🎯 **최적 Usage 팁**

### **1. 시간대별 알림 관리**
- **장중 (9:30-16:00)**: 적극적 알림 (심각도 0.5 이상)
- **장후 (16:00-9:30)**: 보수적 알림 (심각도 0.8 이상)

### **2. 종목별 관심도 Configuration**
- **핵심 종목**: 모든 알림 수신
- **관심 종목**: 중요 알림만 수신
- **기타 종목**: 긴급 알림만 수신

### **3. 알림 피로도 관리**
- 주말/휴일에는 알림 빈도 감소
- 중요한 회의/이벤트 시간에는 일시 Stop

## 📞 **Support 및 Contact**

### **로그 File 위치**
- **메인 로그**: `logs/background_monitoring.log`
- **Slack 로그**: `logs/slack_monitoring.log`
- **이벤트 로그**: `logs/advanced_events_*.json`

### **백업 및 복구**
```bash
# Configuration 백업
cp config/slack_config.json config/slack_config_backup.json

# 로그 아카이브
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

---

## 🎉 **축하합니다!**

이제 **24/7 실시간 Economic  알림 System**이 완전히 Configuration되었습니다!

**다음과 같은 상황에서 즉시 Slack 알림을 받게 됩니다:**
- 📈 주식 급등/급락 (5% 이상)
- ⚡ 높은 변동성 감지 (15% 이상)
- 📊 거래량 급증 (평균 대비 3배 이상)
- 🚀 기술적 돌파 (볼린저 밴드, RSI 과매수/과매도)
- 💭 시장 감정 급변 (공포/탐욕 지수 극값)
- 🔄 모멘텀 다이버전스 (MACD 신호 변화)
- 🌊 시장 체제 변화 (VIX 20% 이상 변동)

**모바일에서도 즉시 알림을 받으실 수 있습니다!** 📱✨
