#!/usr/bin/env python3
"""
SSH 터널링 문제 해결 스크립트
"""

import subprocess
import os
import time

def check_port_usage(port=8501):
    """포트 사용 상태 확인"""
    print(f"🔍 포트 {port} 사용 상태 확인")
    print("-" * 30)
    
    try:
        # lsof 명령어로 포트 사용 확인
        result = subprocess.run(['lsof', '-i', f':{port}'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            print(f"⚠️ 포트 {port}이 사용 중입니다:")
            print(result.stdout)
            
            # PID 추출 및 종료 제안
            lines = result.stdout.strip().split('\n')[1:]  # 헤더 제외
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    pid = parts[1]
                    print(f"📋 프로세스 종료 명령어: kill -9 {pid}")
            
            return True
        else:
            print(f"✅ 포트 {port}이 사용 가능합니다.")
            return False
            
    except FileNotFoundError:
        print("⚠️ lsof 명령어를 찾을 수 없습니다. netstat으로 시도합니다.")
        
        try:
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
            if f":{port}" in result.stdout:
                print(f"⚠️ 포트 {port}이 사용 중일 수 있습니다.")
                return True
            else:
                print(f"✅ 포트 {port}이 사용 가능합니다.")
                return False
        except:
            print("❌ 포트 상태를 확인할 수 없습니다.")
            return False

def kill_ssh_tunnels():
    """기존 SSH 터널 프로세스 종료"""
    print("\n🔧 기존 SSH 터널 프로세스 정리")
    print("-" * 30)
    
    try:
        # SSH 터널 프로세스 찾기
        result = subprocess.run(['pgrep', '-f', 'ssh.*8501'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"🔍 발견된 SSH 터널 프로세스: {len(pids)}개")
            
            for pid in pids:
                try:
                    subprocess.run(['kill', '-9', pid], check=True)
                    print(f"✅ 프로세스 {pid} 종료됨")
                except:
                    print(f"❌ 프로세스 {pid} 종료 실패")
        else:
            print("✅ 기존 SSH 터널 프로세스가 없습니다.")
            
    except FileNotFoundError:
        print("⚠️ pgrep 명령어를 찾을 수 없습니다.")

def suggest_alternative_ports():
    """대안 포트 제안"""
    print("\n🔄 대안 포트 제안")
    print("-" * 30)
    
    alternative_ports = [8502, 8503, 8504, 8505]
    
    for port in alternative_ports:
        if not check_port_usage(port):
            print(f"✅ 포트 {port} 사용 가능")
            print(f"📋 대안 SSH 터널 명령어:")
            print(f"ssh -L {port}:localhost:8501 -i ~/Desktop/keys/EC2-DeepLearning.pem ec2-user@98.80.100.116")
            print(f"브라우저 접근: http://localhost:{port}")
            return port
    
    print("⚠️ 모든 대안 포트가 사용 중입니다.")
    return None

def create_tunnel_scripts():
    """터널링 스크립트 생성"""
    print("\n📝 터널링 스크립트 생성")
    print("-" * 30)
    
    # 기본 터널 스크립트
    basic_script = """#!/bin/bash
# SSH 터널링 스크립트

echo "🔧 SSH 터널 설정 중..."

# 기존 터널 정리
pkill -f "ssh.*8501" 2>/dev/null

# 포트 사용 확인
if lsof -i:8501 >/dev/null 2>&1; then
    echo "⚠️ 포트 8501이 사용 중입니다. 프로세스를 종료합니다."
    lsof -ti:8501 | xargs kill -9 2>/dev/null
    sleep 2
fi

echo "🚀 SSH 터널 생성 중..."
ssh -L 8501:localhost:8501 -i ~/Desktop/keys/EC2-DeepLearning.pem ec2-user@98.80.100.116
"""
    
    with open('create_tunnel.sh', 'w') as f:
        f.write(basic_script)
    
    os.chmod('create_tunnel.sh', 0o755)
    print("✅ create_tunnel.sh 생성됨")
    
    # 백그라운드 터널 스크립트
    background_script = """#!/bin/bash
# 백그라운드 SSH 터널링 스크립트

echo "🔧 백그라운드 SSH 터널 설정 중..."

# 기존 터널 정리
pkill -f "ssh.*8501" 2>/dev/null

# 백그라운드 터널 생성
ssh -L 8501:localhost:8501 -i ~/Desktop/keys/EC2-DeepLearning.pem -f -N ec2-user@98.80.100.116

if [ $? -eq 0 ]; then
    echo "✅ 백그라운드 터널 생성 성공"
    echo "🌐 브라우저에서 http://localhost:8501 접근 가능"
    echo "🛑 터널 종료: pkill -f 'ssh.*8501'"
else
    echo "❌ 터널 생성 실패"
fi
"""
    
    with open('create_background_tunnel.sh', 'w') as f:
        f.write(background_script)
    
    os.chmod('create_background_tunnel.sh', 0o755)
    print("✅ create_background_tunnel.sh 생성됨")

def main():
    """메인 문제 해결 프로세스"""
    print("🔧 SSH 터널링 문제 해결")
    print("=" * 40)
    
    # 1. 포트 사용 상태 확인
    port_in_use = check_port_usage(8501)
    
    # 2. 기존 SSH 터널 정리
    kill_ssh_tunnels()
    
    # 3. 대안 포트 제안
    if port_in_use:
        alternative_port = suggest_alternative_ports()
    
    # 4. 터널링 스크립트 생성
    create_tunnel_scripts()
    
    # 5. 해결 방법 요약
    print("\n" + "=" * 40)
    print("🎯 권장 해결 방법")
    print("-" * 20)
    print("1️⃣ 자동 스크립트 사용:")
    print("   ./create_tunnel.sh")
    print("")
    print("2️⃣ 백그라운드 터널:")
    print("   ./create_background_tunnel.sh")
    print("")
    print("3️⃣ 수동 명령어:")
    print("   pkill -f 'ssh.*8501'")
    print("   ssh -L 8501:localhost:8501 -i ~/Desktop/keys/EC2-DeepLearning.pem ec2-user@98.80.100.116")
    print("")
    print("4️⃣ 문제 지속 시:")
    print("   다른 포트 사용 (8502, 8503 등)")

if __name__ == "__main__":
    main()
