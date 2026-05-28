# 🚀 Fundamental Agent Run Guide

## 📋 주요 Run 스크립트 목록

### 🎯 **1. 전체 자동화 System (추천)**

#### 🔥 **가장 완전한 Run**
```bash
# 전체 자동화 Test (이벤트 감지 → 기사 Create → Slack 알림)
python test_full_automation.py
```
**포함 Features:**
- ✅ 이벤트 자동 감지
- ✅ Data Analysis 및 차트 Create
- ✅ AI 기사 작성
- ✅ 이미지 Create
- ✅ 기사 검수
- ✅ 광고 추천
- ✅ Streamlit 페이지 Create
- ✅ Slack 다중 메시지 전송

#### 🎭 **orchestrator 직접 Run**
```bash
# 통합 orchestrator Agent Run
python agents/orchestrator_agent.py
```

### 🎨 **2. Streamlit Dashboard**

#### 📊 **기본 Dashboard**
```bash
# 기본 Streamlit Dashboard
python demo_streamlit.py
# 또는
python run_streamlit.py
```

#### 🌐 **종합 Dashboard**
```bash
# 종합 Dashboard (여러 페이지)
python streamlit_comprehensive_dashboard.py
# 또는
./start_comprehensive_dashboard.sh
```

#### 🔗 **SSH 터널과 함께 Run**
```bash
# SSH 터널을 통한 외부 접근
./start_streamlit_tunnel.sh
```

### 📱 **3. Slack 알림 System**

#### ⚡ **즉시 Slack 알림 Test**
```bash
# Slack 알림 Features Test
python demo_slack_alerts.py
```

#### 🔄 **백그라운드 모니터링**
```bash
# 백그라운드 모니터링 Start
./start_background_monitoring.sh

# Status Check
./check_monitoring_status.sh

# 모니터링 Stop
./stop_monitoring.sh
```

#### 📧 **Slack 연결 Test**
```bash
# Slack 웹훅 연결 Test
python test_slack_connection.py
```

### 🔍 **4. 개별 컴포넌트 Test**

#### 🧪 **System 전체 Test**
```bash
# 전체 System Status Check
python test_system.py

# AWS 연결만 Test
python test_system.py aws

# Data 수집만 Test
python test_system.py data
```

#### 📊 **이벤트 감지 Test**
```bash
# 고급 이벤트 감지 System
python demo_advanced_events.py

# 이벤트 감지 + Slack System
python event_detection_slack_system.py
```

### 🛠️ **5. 개발 및 디버깅**

#### 🔧 **메인 파이프라인**
```bash
# 기본 파이프라인 Run
python main.py --mode full

# 특정 모드 Run
python main.py --mode data          # Data 수집만
python main.py --mode article       # 기사 작성만
```

#### 📈 **완전한 파이프라인**
```bash
# 전체 파이프라인 (구버전)
python run_full_pipeline.py

# 완전한 System (신버전)
python run_complete_system.py
```

### 🚀 **6. 빠른 Start 스크립트**

#### ⚡ **원클릭 Run**
```bash
# 빠른 Start (모든 Configuration 자동)
./quick_start.sh
```

#### 🔄 **News 파이프라인**
```bash
# news generation 파이프라인
./run_news_pipeline.sh
```

---

## 📝 **Run 순서 추천**

### 🥇 **초보자용 (처음 Run)**
```bash
# 1. System Status Check
python test_system.py

# 2. Slack 연결 Test
python test_slack_connection.py

# 3. 전체 System Run
python test_full_automation.py

# 4. Streamlit Dashboard Check
python demo_streamlit.py
```

### 🥈 **일반 User용**
```bash
# 1. 전체 자동화 Run
python test_full_automation.py

# 2. Dashboard에서 Result Check
python streamlit_comprehensive_dashboard.py
```

### 🥉 **고급 User용**
```bash
# 1. 백그라운드 모니터링 Start
./start_background_monitoring.sh

# 2. Dashboard Run
./start_comprehensive_dashboard.sh

# 3. Status 모니터링
./check_monitoring_status.sh
```

---

## 🔧 **환경 Configuration Check**

### 📋 **필수 환경 변수**
```bash
# 환경 변수 Check
python check_env.py

# AWS Configuration Check
python test_aws_quick.py
```

### 🔑 **API 키 Configuration Check**
```bash
# Alpha Vantage API Test
python test_alphavantage_simple.py

# FRED API Test
python test_fred_connection.py
```

---

## 📊 **출력 Result Check**

### 📁 **Create된 File 위치**
- **기사 File**: `output/automated_articles/`
- **차트 이미지**: `output/images/`
- **Streamlit 페이지**: `streamlit_articles/`
- **로그 File**: `logs/`

### 🔗 **접근 URL**
- **로컬 Streamlit**: `http://localhost:8501`
- **SSH 터널**: `http://localhost:8501` (터널 Configuration 후)

---

## ⚠️ **Troubleshooting**

### 🚨 **일반적인 오류**
```bash
# AWS 자격 증명 문제
aws configure list

# Python 패키지 문제
pip install -r requirements.txt

# 포트 충돌 문제
lsof -i :8501
```

### 📞 **도움말**
```bash
# 각 스크립트의 도움말
python main.py --help
python test_system.py --help
```

---

## 🎯 **권장 Run 명령어**

### 🔥 **가장 추천하는 Execution Method**
```bash
# 터미널 1: 전체 자동화 System
python test_full_automation.py

# 터미널 2: Streamlit Dashboard
python streamlit_comprehensive_dashboard.py

# 터미널 3: 백그라운드 모니터링 (선택사항)
./start_background_monitoring.sh
```

이렇게 Run하면:
1. 📰 자동으로 Economic  기사가 Create됩니다
2. 📱 Slack에 알림이 전송됩니다
3. 🌐 웹 Dashboard에서 Result를 Check할 수 있습니다
4. 📊 실시간 모니터링이 가능합니다

---

**💡 팁**: 처음 Run할 때는 `python test_full_automation.py`를 Usage하여 전체 System이 정상 작동하는지 Check한 후, 필요에 따라 다른 스크립트들을 Usage하세요!
