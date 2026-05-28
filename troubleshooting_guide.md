# 🛠️ 연결 Troubleshooting Guide

## 일반적인 문제들

### 1. SSH 터널 연결 실패
**증상**: `ssh: connect to host [IP] port 22: Connection refused`

**해결책**:
```bash
# EC2 인스턴스 Status Check
aws ec2 describe-instances --instance-ids [INSTANCE-ID]

# Security 그룹에서 SSH(22) 포트 Check
# 키 File Permissions Check (Mac/Linux)
chmod 400 ~/.ssh/your-key.pem
```

### 2. Streamlit 서버 Start 실패
**증상**: `ModuleNotFoundError` 또는 `ImportError`

**해결책**:
```bash
# 가상환경 활성화 (있는 경우)
source venv/bin/activate

# Dependencies 재Installation
pip install -r requirements.txt

# Python 경로 Check
which python
python --version
```

### 3. 포트 8501 접속 불가
**증상**: browser "연결할 수 없음"

**해결책**:
```bash
# 포트 Usage Check
netstat -tlnp | grep :8501

# 방화벽 Check (Ubuntu)
sudo ufw status

# Streamlit Process 재Start
pkill -f streamlit
./start_streamlit_with_tunnel.sh
```

### 4. 로컬 포트 충돌
**증상**: `bind: Address already in use`

**해결책**:
```bash
# 다른 포트 Usage
ssh -L 8502:localhost:8501 -i key.pem ec2-user@[IP]

# 또는 기존 Process 종료
lsof -ti:8501 | xargs kill -9
```

## 연결 Test 명령어

### EC2에서 Run
```bash
# 서버 Status Check
./check_streamlit_status.sh

# 수동 Test
curl http://localhost:8501
```

### 로컬에서 Run
```bash
# SSH 연결 Test
ssh -i key.pem ec2-user@[EC2-IP] "echo 'SSH 연결 성공'"

# 포트 포워딩 Test
curl http://localhost:8501
```

## 성능 최적화

### 1. 메모리 Usage량 줄이기
```python
# Streamlit Configuration Add
st.set_page_config(
    page_title="Economic News",
    layout="wide",
    initial_sidebar_state="collapsed"  # 사이드바 접기
)
```

### 2. 캐싱 활용
```python
@st.cache_data(ttl=60)  # 60초 캐시
def load_market_data():
    # Data 로딩 로직
    pass
```

### 3. 백그라운드 Run
```bash
# nohup으로 백그라운드 Run
nohup streamlit run app.py > streamlit.log 2>&1 &

# screen Usage
screen -S streamlit
streamlit run app.py
# Ctrl+A, D로 detach
```
