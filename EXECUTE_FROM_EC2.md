# 🚀 EC2 터미널에서 Run하기

## 현재 상황
- EC2에 SSH로 접속 완료 ✅
- 프로젝트 Folder: `/home/ec2-user/projects/ABP/fundamental_agent`

## Run 명령어 (순서대로)

### 1. 프로젝트 Folder로 Move
```bash
cd /home/ec2-user/projects/ABP/fundamental_agent
```

### 2. 현재 위치 Check
```bash
pwd
ls -la integrated_dashboard.py
```

### 3. System Test (선택사항)
```bash
python test_integrated_dashboard.py
```

### 4. Streamlit Run
```bash
# 포그라운드 Run (터미널을 닫으면 종료됨)
streamlit run integrated_dashboard.py

# 또는 백그라운드 Run (터미널을 닫아도 계속 Run)
nohup streamlit run integrated_dashboard.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

## 🔗 로컬 PC에서 접속하기

### 방법 1: 새 터미널 창에서 SSH 터널 Create
현재 EC2 연결을 유지한 채로 **로컬 PC의 새 터미널**에서:
```bash
ssh -L 8501:localhost:8501 -i ~/.ssh/your-key.pem ec2-user@98.80.100.116
```

### 방법 2: 현재 연결 종료 후 포트 포워딩으로 재연결
```bash
# 현재 EC2 세션에서
exit

# 로컬 PC에서 포트 포워딩과 함께 재연결
ssh -L 8501:localhost:8501 -i ~/.ssh/your-key.pem ec2-user@98.80.100.116

# 다시 프로젝트 Folder로 Move
cd /home/ec2-user/projects/ABP/fundamental_agent

# Streamlit Run
streamlit run integrated_dashboard.py
```

## 📱 브라우저 접속
SSH 터널이 연결된 Status에서 browser:
```
http://localhost:8501
```

## 🔍 Run Status Check
```bash
# Streamlit Process Check
ps aux | grep streamlit

# 포트 Usage Check
netstat -tlnp | grep :8501

# 로그 Check (백그라운드 Run 시)
tail -f streamlit.log
```

## 💡 추천 방법
**방법 2 (재연결)**를 추천합니다:
1. 현재 세션 종료
2. 포트 포워딩으로 재연결
3. Streamlit Run
4. browser 접속
