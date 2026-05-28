# 🖥️ 로컬 PC에서 Run하기 Guide

## 방법 1: SCP로 File Copy

### Windows (PowerShell)
```powershell
# 프로젝트 Folder Create
mkdir C:\fundamental_agent
cd C:\fundamental_agent

# EC2에서 전체 프로젝트 Copy
scp -r -i "C:\path\to\your-key.pem" ec2-user@[EC2-IP]:/home/ec2-user/projects/ABP/fundamental_agent/* .
```

### Mac/Linux
```bash
# 프로젝트 Folder Create
mkdir ~/fundamental_agent
cd ~/fundamental_agent

# EC2에서 전체 프로젝트 Copy
scp -r -i ~/.ssh/your-key.pem ec2-user@[EC2-IP]:/home/ec2-user/projects/ABP/fundamental_agent/* .
```

## 방법 2: rsync Usage (더 효율적)

### Mac/Linux
```bash
# 초기 동기화
rsync -avz -e "ssh -i ~/.ssh/your-key.pem" \
  ec2-user@[EC2-IP]:/home/ec2-user/projects/ABP/fundamental_agent/ \
  ~/fundamental_agent/

# 업데이트 시 (변경된 File만 동기화)
rsync -avz --delete -e "ssh -i ~/.ssh/your-key.pem" \
  ec2-user@[EC2-IP]:/home/ec2-user/projects/ABP/fundamental_agent/ \
  ~/fundamental_agent/
```

## 방법 3: GitHub Usage (권장)

### EC2에서 GitHub에 Push
```bash
cd /home/ec2-user/projects/ABP/fundamental_agent

# Git Configuration (처음만)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 변경사항 Commit
git add .
git commit -m "Update economic news system"
git push origin main
```

### 로컬에서 Clone
```bash
# 로컬 PC에서
git clone https://github.com/your-username/fundamental_agent.git
cd fundamental_agent
```

## 로컬 환경 Configuration

### 1. Python 가상환경 Create
```bash
# Python 3.8+ 필요
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 2. Dependencies Installation
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 Configuration
`.env` File을 로컬에 Copy하거나 새로 Create:
```bash
# .env File 내용
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxxxx/xxxxx/xxxxx
ALPHA_VANTAGE_API_KEY=your_api_key
FRED_API_KEY=your_fred_key
AWS_DEFAULT_REGION=us-east-1
```

### 4. AWS 자격 증명 Configuration
```bash
# AWS CLI Installation 및 Configuration
pip install awscli
aws configure
```

### 5. System Test
```bash
python test_integrated_dashboard.py
```

### 6. Streamlit Run
```bash
streamlit run integrated_dashboard.py
```

### 7. 브라우저 접속
자동으로 브라우저가 열리거나 `http://localhost:8501` 접속
