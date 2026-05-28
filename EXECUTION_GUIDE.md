# 🚀 전체 프로젝트 Run Guide

Fundamental Agent의 모든 Features을 Run하는 종합 Guide입니다.

## 📋 Table of Contents

1. [빠른 Start](#빠른-Start)
2. [Run 모드별 Guide](#Run-모드별-Guide)
3. [Docker Run](#docker-Run)
4. [System 모니터링](#System-모니터링)
5. [Troubleshooting](#문제-해결)

## 🚀 빠른 Start

### 1. 환경 Configuration Check
```bash
# 초기 Configuration 및 환경 Check
python3 run_complete_system.py --mode setup
```

### 2. 간편 Run (추천)
```bash
# 대화형 메뉴로 Run
./quick_start.sh
```

### 3. 전체 System Run
```bash
# 모든 Features 통합 Run
python3 run_complete_system.py --mode full
```

## 📊 Run 모드별 Guide

### 🎯 **1. 전체 System 모드 (`full`)**
모든 Features을 통합하여 Run합니다.

```bash
python3 run_complete_system.py --mode full
```

**Run 과정:**
1. 📊 고도화된 이벤트 감지 (기술적/감정/상관관계 Analysis)
2. 🤖 AI news generation (AWS Bedrock Claude)
3. 📱 Slack 알림 전송 (우선순위 알림 + 시장 요약)
4. 💾 Result 저장 (JSON + HTML)

**필요 조건:**
- ✅ AWS 자격증명 Configuration
- ✅ Slack 웹훅 URL Configuration

### 🤖 **2. AI news generation 모드 (`news-only`)**
AI 기반 Fundamental Agent만 Create합니다.

```bash
python3 run_complete_system.py --mode news-only
```

**특징:**
- AWS Bedrock Claude 모델 Usage
- 다중 Agent System (Data 수집 → News 작성 → 콘텐츠 최적화)
- HTML 형식으로 출력

### 📊 **3. 이벤트 모니터링 모드 (`monitoring-only`)**
시장 이벤트 감지 및 Analysis만 수행합니다.

```bash
python3 run_complete_system.py --mode monitoring-only
```

**Analysis 항목:**
- 📈 기술적 Analysis (RSI, MACD, 볼린저 밴드 등 13가지 지표)
- 💭 감정 Analysis (News 피드 기반 시장 심리)
- 🔗 상관관계 Analysis (시장 간 상관관계 이탈)
- 🔄 섹터 로테이션 감지

### 📱 **4. Slack 알림 모드 (`slack-only`)**
Slack 알림 System만 Run합니다.

```bash
python3 run_complete_system.py --mode slack-only
```

**알림 유형:**
- 🚨 긴급 알림 (심각도 0.6 이상)
- 📋 시장 요약 (1시간마다)
- 📰 News 업데이트
- 🔧 System Status

### 📈 **5. Dashboard 모드 (`dashboard`)**
Streamlit 웹 Dashboard를 Run합니다.

```bash
python3 run_complete_system.py --mode dashboard
```

**접속:** http://localhost:8501

**Features:**
- 📊 실시간 시장 Data 차트
- 📰 AI Create 기사 뷰어
- 🖼️ 자동 이미지 Create
- 📢 맞춤형 광고

### 🧪 **6. Test 모드 (`test`)**
System 전체 Test를 Run합니다.

```bash
python3 run_complete_system.py --mode test
```

### ⚙️ **7. Configuration 모드 (`setup`)**
초기 Configuration 및 환경 Check을 수행합니다.

```bash
python3 run_complete_system.py --mode setup
```

## 🔄 대화형 모드

모든 모드를 대화형으로 선택할 수 있습니다.

```bash
# Python 스크립트
python3 run_complete_system.py --interactive

# 또는 간편 스크립트
./quick_start.sh
```

## 🐳 Docker Run

### Docker로 Run하기

```bash
# 1. Docker 이미지 빌드
docker build -t economic-news-system .

# 2. 환경 변수 File Create
cp .env.example .env
# .env File 편집하여 실제 값 입력

# 3. Docker 컨테이너 Run
docker run -d \
  --name economic-news \
  --env-file .env \
  -p 8501:8501 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/output:/app/output \
  economic-news-system

# 4. 로그 Check
docker logs -f economic-news
```

### Docker Compose로 Run하기

```bash
# 1. 환경 변수 Configuration
cp .env.example .env
# .env File 편집

# 2. 서비스 Start
docker-compose up -d

# 3. Status Check
docker-compose ps

# 4. 로그 Check
docker-compose logs -f economic-news-system

# 5. 서비스 Stop
docker-compose down
```

## 📊 System 모니터링

### 실시간 System Status Check

```bash
# 현재 Status Check
python3 system_monitor.py

# 연속 모니터링 (60초 간격)
python3 system_monitor.py --continuous

# 리포트 저장
python3 system_monitor.py --save
```

### 모니터링 항목

- 💻 **System 리소스**: CPU, 메모리, 디스크 Usage률
- 🔄 **Process Status**: 관련 Process Run Status
- 📄 **로그 Information**: 로그 File 크기 및 라인 수
- 📁 **출력 File**: Create된 File 통계
- 🔧 **서비스 Status**: AWS, Slack, Python 패키지 Status

### 백그라운드 Run 관리

```bash
# Slack 모니터링 Start
./start_background_monitoring.sh

# Status Check
./check_monitoring_status.sh

# Stop
./stop_monitoring.sh
```

## 🔧 고급 Run 옵션

### 로그 레벨 조정

```bash
# 디버그 모드
python3 run_complete_system.py --mode full --log-level DEBUG

# 오류만 표시
python3 run_complete_system.py --mode full --log-level ERROR
```

### User 정의 Configuration File

```bash
# 커스텀 Configuration File Usage
python3 run_complete_system.py --mode full --config config/custom.json
```

### 특정 Features 조합

```bash
# 모니터링 + Slack 알림
python3 run_complete_system.py --mode monitoring-only
python3 run_complete_system.py --mode slack-only

# news generation + Dashboard
python3 run_complete_system.py --mode news-only &
python3 run_complete_system.py --mode dashboard
```

## 📋 Run 체크리스트

### 🔧 **사전 준비**
- [ ] Python 3.8+ Installation
- [ ] Dependencies 패키지 Installation (`pip install -r requirements.txt`)
- [ ] AWS CLI Configuration (`aws configure`)
- [ ] Slack 웹훅 URL Configuration

### ⚙️ **환경 Configuration**
- [ ] `.env` File Create 및 Configuration
- [ ] Directory Permissions Check
- [ ] Run File Permissions 부여 (`chmod +x *.py *.sh`)

### 🧪 **Test**
- [ ] System Test Run (`--mode test`)
- [ ] AWS 연결 Check
- [ ] Slack 알림 Test

### 🚀 **Run**
- [ ] 원하는 모드 선택
- [ ] 로그 File Check
- [ ] 출력 Result 검증

## 🚨 Troubleshooting

### 일반적인 문제들

**1. AWS 자격증명 오류**
```bash
# 자격증명 Check
aws sts get-caller-identity

# 재Configuration
aws configure
```

**2. Python 패키지 누락**
```bash
# Dependencies 재Installation
pip install -r requirements.txt

# 특정 패키지 Installation
pip install boto3 streamlit pandas
```

**3. Permissions 오류**
```bash
# Run Permissions 부여
chmod +x run_complete_system.py quick_start.sh

# Directory Permissions Check
ls -la logs/ output/
```

**4. Slack 알림 실패**
```bash
# 웹훅 URL Test
curl -X POST -H 'Content-type: application/json' \
--data '{"text":"Test"}' $SLACK_WEBHOOK_URL
```

**5. 메모리 부족**
```bash
# System 리소스 Check
python3 system_monitor.py

# Process Check
ps aux | grep python
```

### 로그 Analysis

```bash
# 오류 로그 Check
grep "ERROR" logs/complete_system_*.log

# 최근 로그 Check
tail -f logs/complete_system_$(date +%Y%m%d).log

# 특정 모듈 로그 필터링
grep "slack_notifier" logs/complete_system_*.log
```

### 디버깅 모드

```bash
# 상세 디버그 Information
python3 run_complete_system.py --mode full --log-level DEBUG

# 단계별 Run
python3 run_complete_system.py --mode monitoring-only
python3 run_complete_system.py --mode news-only
python3 run_complete_system.py --mode slack-only
```

## 📞 Support 및 Contact

### 로그 File 위치
- **메인 로그**: `logs/complete_system_YYYYMMDD.log`
- **System 모니터**: `logs/system_monitor_YYYYMMDD.log`
- **Slack 모니터링**: `logs/slack_monitoring.log`

### 출력 File 위치
- **Run Result**: `output/complete_system_YYYYMMDD_HHMMSS.json`
- **Create 기사**: `output/article_YYYYMMDD_HHMMSS.html`
- **System 리포트**: `logs/system_report_YYYYMMDD_HHMMSS.json`

### GitHub Issues
문제 발생 시 다음 Information와 함께 이슈를 Create해주세요:
- Run 명령어
- 오류 메시지
- 로그 File 내용
- System 환경 Information

---

## 🎉 성공적인 Run을 위한 팁

1. **단계별 Run**: 처음에는 `setup` → `test` → `monitoring-only` 순으로 Test
2. **로그 모니터링**: Run 중 로그를 실시간으로 Check
3. **리소스 관리**: System 모니터로 리소스 Usage량 Check
4. **정기 점검**: 주기적으로 System Status 및 로그 File Cleanup
5. **백업**: 중요한 Configuration File과 출력 Result 백업

**이제 완전한 Fundamental Agent을 자유롭게 활용하세요!** 🚀✨
