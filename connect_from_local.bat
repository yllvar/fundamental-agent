@echo off
echo 🚀 EC2 Streamlit 대시보드 연결 스크립트
echo.

REM 설정 변수 (사용자가 수정해야 함)
set EC2_IP=YOUR_EC2_PUBLIC_IP
set KEY_FILE=C:\path\to\your-key.pem
set LOCAL_PORT=8501
set REMOTE_PORT=8501

echo 📋 연결 정보:
echo    EC2 IP: %EC2_IP%
echo    키 파일: %KEY_FILE%
echo    로컬 포트: %LOCAL_PORT%
echo    원격 포트: %REMOTE_PORT%
echo.

echo ⚠️  주의: EC2_IP와 KEY_FILE 경로를 실제 값으로 수정하세요!
echo.

REM SSH 터널 생성
echo 🔗 SSH 터널을 생성합니다...
ssh -L %LOCAL_PORT%:localhost:%REMOTE_PORT% -i "%KEY_FILE%" ec2-user@%EC2_IP%

echo.
echo 📱 터널이 연결되면 브라우저에서 다음 주소로 접속하세요:
echo    http://localhost:%LOCAL_PORT%
echo.
pause
