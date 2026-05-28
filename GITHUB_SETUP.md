# 🚀 GitHub Repository Configuration Guide

## 📋 현재 Status
✅ Git Repository 초기화 완료  
✅ 모든 File Commit 완료 (33개 File, 6,820줄)  
✅ Commit 메시지: "🎉 Initial commit: Economic News AI System with Streamlit Dashboard"

## 🔗 GitHub Repository Create 및 연결

### 1단계: GitHub에서 새 Repository Create
1. GitHub (https://github.com)에 로그인
2. "New repository" 클릭
3. Repository Information 입력:
   - **Repository name**: `economic-news-ai-system`
   - **Description**: `AWS Bedrock과 Strands Agent를 활용한 지능형 Economic  기사 자동 Create System`
   - **Visibility**: Public (또는 Private)
   - **Initialize**: ❌ README, .gitignore, license 체크 해제 (이미 있음)

### 2단계: 원격 Repository 연결 및 Push
```bash
# 현재 Directory에서 Run
cd /home/ec2-user/projects/ABP/fundamental_agent

# 원격 Repository Add (YOUR_USERNAME을 실제 GitHub User명으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/economic-news-ai-system.git

# 기본 Branch를 main으로 변경 (선택사항)
git branch -M main

# GitHub에 Push
git push -u origin main
```

### 3단계: 인증 (필요시)
GitHub 인증이 필요한 경우:
```bash
# Personal Access Token Usage (추천)
# GitHub Settings > Developer settings > Personal access tokens에서 토큰 Create
# Username: GitHub User명
# Password: Create한 Personal Access Token

# 또는 SSH 키 Usage
ssh-keygen -t ed25519 -C "your_email@example.com"
# Create된 공개키를 GitHub Settings > SSH and GPG keys에 Add
```

## 📊 Repository 내용

### 📁 주요 Directory 구조
```
economic-news-ai-system/
├── agents/                     # 🤖 Multi-agent system
├── streamlit_app/             # 📊 Web dashboard
├── config/                    # ⚙️ Configuration files
├── output/                    # 📄 Generated articles
├── data_monitoring/           # 📈 Data collection
├── logs/                      # 📝 System logs
├── README.md                  # 📖 Project documentation
├── PROJECT_SUMMARY.md         # 📋 Detailed project summary
└── requirements.txt           # 📦 Dependencies
```

### 🎯 주요 Features
- **🤖 Multi-agent System**: AWS Bedrock 기반 지능형 Agent들
- **📊 Streamlit Dashboard**: 인터랙티브 웹 인터페이스
- **📈 Real-time Data**: 실시간 주식 및 Economic  Data 수집
- **📰 AI Article Generation**: Claude 3 Sonnet으로 고품질 기사 Create
- **🖼️ Image Generation**: 자동 illustration 및 word cloud
- **📢 Smart Ads**: 기사 내용 기반 맞춤형 광고 추천

### 📈 성능 지표
- **System Test**: 6/6 통과 (100%)
- **기사 Create 시간**: 평균 107초
- **품질 점수**: 평균 83/100점
- **Data 소스**: 11개 주식, 2개 Economic 지표, 5개 News피드

## 🚀 Usage

### 즉시 Run
```bash
# Streamlit Dashboard Run
python demo_streamlit.py

# 전체 파이프라인 Run
python main.py --mode full --market-summary

# System Test
python test_system.py
```

### Installation
```bash
# Dependencies Installation
pip install -r requirements.txt

# AWS 자격 증명 Configuration
aws configure
```

## 🏷️ 추천 GitHub 태그
`aws-bedrock` `ai-agents` `economic-news` `streamlit` `langchain` `claude-3` `financial-data` `automated-journalism` `data-visualization` `python`

## 📝 License
MIT License (LICENSE File Add 권장)

---

**💡 팁**: Repository Create 후 GitHub Actions를 Configuration하여 자동 Test 및 배포 pipeline 구축할 수 있습니다.
