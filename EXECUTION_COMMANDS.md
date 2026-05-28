# 🚀 Fundamental Agent Run 명령어 Guide

## 📋 전체 System Run (추천)

### 1️⃣ **원클릭 Run (가장 간단)**
```bash
./run_news_system.sh
```

### 2️⃣ **Python 직접 Run**
```bash
python run_complete_news_system.py
```

### 3️⃣ **단계별 Run**
```bash
# 1단계: 이벤트 감지
python event_detection_slack_system.py

# 2단계: 기사 Create (Strands Agent System)
python -c "
import asyncio
from agents import main_orchestrator
from agents.strands_framework import StrandContext
from datetime import datetime

async def run():
    event = {
        'symbol': 'AAPL',
        'event_type': 'price_change', 
        'severity': 'medium',
        'title': 'AAPL 주가 변동',
        'description': 'AAPL 주가 변동이 감지되었습니다.',
        'timestamp': datetime.now().isoformat()
    }
    
    context = StrandContext(
        strand_id='manual_test',
        input_data={'event': event}
    )
    
    result = await main_orchestrator.process(context)
    print('✅ 기사 Create 완료:', result.get('status'))

asyncio.run(run())
"
```

## 🎯 Run 모드별 명령어

### 🔄 **연속 모니터링 모드**
```bash
# in background 지속적으로 Run
nohup python run_complete_news_system.py &

# Status Check
ps aux | grep run_complete_news_system

# Stop
pkill -f run_complete_news_system
```

### 📊 **Test 모드**
```bash
# System Status Test
python test_strands_system.py

# 개별 컴포넌트 Test
python -c "
from agents import DataAnalysisStrand
import asyncio

async def test():
    agent = DataAnalysisStrand()
    print('능력:', agent.get_capabilities())

asyncio.run(test())
"
```

### 🌐 **Streamlit Dashboard**
```bash
# 최신 Create된 기사 보기
streamlit run streamlit_articles/$(ls -t streamlit_articles/article_*.py | head -1)

# 또는 간단하게
./run_latest_article.sh
```

## 📈 **Run Result Check**

### Create된 File 위치:
- **📰 기사**: `output/automated_articles/`
- **📊 차트**: `output/charts/`
- **🖼️ 이미지**: `output/images/`
- **🌐 Streamlit**: `streamlit_articles/`
- **📋 로그**: `logs/`

### Check 명령어:
```bash
# 최신 기사 Check
ls -la output/automated_articles/ | tail -5

# Create된 차트 개수
ls output/charts/*.html | wc -l

# 로그 실시간 모니터링
tail -f logs/complete_system_$(date +%Y%m%d).log
```

## 🔧 **Troubleshooting**

### 환경 Configuration Check:
```bash
# 환경 변수 Check
python check_env.py

# AWS 연결 Test
python test_aws_quick.py

# Slack 웹훅 Test
python test_slack_webhook.py
```

### Dependencies Installation:
```bash
pip install -r requirements.txt
```

### Permissions Configuration:
```bash
chmod +x *.sh
```

## ⚡ **빠른 Run 체크리스트**

1. **환경 변수 Configuration Check**:
   - ✅ `AWS_DEFAULT_REGION=us-east-1`
   - ✅ `ALPHA_VANTAGE_API_KEY=your_key`
   - ✅ `SLACK_WEBHOOK_URL=your_webhook` (선택사항)

2. **Directory 구조 Check**:
   ```bash
   ls -la agents/  # 8개 File 있어야 함
   ```

3. **Run**:
   ```bash
   ./run_news_system.sh
   ```

4. **Result Check**:
   ```bash
   ls output/automated_articles/
   streamlit run streamlit_articles/$(ls -t streamlit_articles/article_*.py | head -1)
   ```

## 🎉 **성공 시 출력 예시**

```
🚀 Fundamental Agent Start
==================================================
📊 Run Result:
Status: success
Run 시간: 45.2초
감지된 이벤트: 2개
Create된 기사: 2개
Slack 알림: 3개

🎉 전체 System Run 완료!

💡 Create된 기사 Check:
  1. streamlit run streamlit_articles/article_AAPL_20250807_120530.py
  2. streamlit run streamlit_articles/article_TSLA_20250807_120545.py
```

## 📞 **Support**

문제 발생 시:
1. 로그 File Check: `logs/complete_system_YYYYMMDD.log`
2. System Test: `python test_strands_system.py`
3. 환경 Configuration Check: `python check_env.py`
