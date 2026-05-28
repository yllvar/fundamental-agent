# 🔗 SSH 터널링으로 Streamlit 접속하기

## ✅ EC2 서버 준비 완료!
Streamlit 서버가 EC2에서 정상적으로 Run 중입니다.
- 서버 주소: 0.0.0.0:8501
- Status: 🟢 Run 중

## 🖥️ 로컬 PC에서 연결하기

### Windows (PowerShell 또는 CMD)
```cmd
ssh -L 8501:localhost:8501 -i "C:\path\to\your-key.pem" ec2-user@[EC2-PUBLIC-IP]
```

### Mac/Linux (터미널)
```bash
ssh -L 8501:localhost:8501 -i ~/.ssh/your-key.pem ec2-user@[EC2-PUBLIC-IP]
```

## 🔧 실제 명령어 예시

**EC2 퍼블릭 IP를 Check하고 아래 명령어에서 [EC2-PUBLIC-IP] 부분을 실제 IP로 바꾸세요:**

### Windows 예시:
```cmd
ssh -L 8501:localhost:8501 -i "C:\Users\YourName\Downloads\your-key.pem" ec2-user@3.34.123.456
```

### Mac/Linux 예시:
```bash
ssh -L 8501:localhost:8501 -i ~/.ssh/your-key.pem ec2-user@3.34.123.456
```

## 📱 browser 접속

SSH 터널이 연결되면 browser 다음 주소로 접속:
```
http://localhost:8501
```

## 🔍 연결 Check 방법

### 1. SSH 터널 연결 성공 시 표시되는 메시지:
```
Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 6.2.0-1009-aws x86_64)
...
ec2-user@ip-xxx-xxx-xxx-xxx:~$
```

### 2. browser 접속 Check:
- 주소창에 `http://localhost:8501` 입력
- "🤖 Fundamental Agent 통합 System" 페이지가 로드되면 성공!

## 🛠️ Troubleshooting

### SSH 연결 실패 시:
1. **키 File Permissions Check** (Mac/Linux):
   ```bash
   chmod 400 ~/.ssh/your-key.pem
   ```

2. **EC2 퍼블릭 IP Check**:
   - AWS 콘솔에서 EC2 인스턴스의 퍼블릭 IP Check

3. **Security 그룹 Check**:
   - SSH(22) 포트가 열려있는지 Check

### 브라우저 접속 실패 시:
1. **터널 연결 Status Check**:
   - SSH 터미널이 연결된 Status여야 함

2. **로컬 포트 충돌 Check**:
   ```bash
   # Mac/Linux
   lsof -i :8501
   
   # Windows
   netstat -ano | findstr :8501
   ```

3. **다른 포트 Usage**:
   ```bash
   ssh -L 8502:localhost:8501 -i key.pem ec2-user@[IP]
   # browser http://localhost:8502 접속
   ```

## 🎯 성공 Check 체크리스트

- [ ] SSH 터널 연결 성공
- [ ] browser http://localhost:8501 접속 가능
- [ ] Streamlit Dashboard 로딩 완료
- [ ] sidebar "🚀 모니터링 Start" 버튼 Check
- [ ] 실시간 Data 업데이트 Check

## 🚀 다음 단계

연결이 성공하면:
1. sidebar "🚀 모니터링 Start" 클릭
2. 실시간 Data 모니터링 Check
3. 이벤트 감지 시 Slack 알림 Test
4. AI 기사 Create Features Test

---

**💡 팁**: SSH 터널은 터미널을 닫으면 연결이 끊어집니다. 
계속 Usage하려면 터미널을 열어둔 Status로 유지하세요!
