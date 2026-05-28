#!/usr/bin/env python3
"""
시스템 상태 모니터링 스크립트
전체 시스템의 상태를 실시간으로 모니터링
"""

import os
import sys
import time
import psutil
import json
from datetime import datetime, timedelta
from typing import Dict, List
import subprocess

class SystemMonitor:
    """시스템 모니터링 클래스"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.log_file = f"logs/system_monitor_{datetime.now().strftime('%Y%m%d')}.log"
        
    def get_system_info(self) -> Dict:
        """시스템 정보 수집"""
        return {
            "timestamp": datetime.now().isoformat(),
            "uptime": str(datetime.now() - self.start_time),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
                "used": psutil.virtual_memory().used
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent
            },
            "network": dict(psutil.net_io_counters()._asdict()) if psutil.net_io_counters() else {}
        }
    
    def get_process_info(self) -> List[Dict]:
        """프로젝트 관련 프로세스 정보"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
            try:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                
                # 프로젝트 관련 프로세스 필터링
                if any(keyword in cmdline.lower() for keyword in [
                    'economic', 'streamlit', 'run_complete_system'
                ]):
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cmdline": cmdline,
                        "cpu_percent": proc.info['cpu_percent'],
                        "memory_percent": proc.info['memory_percent'],
                        "status": proc.status()
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes
    
    def get_log_info(self) -> Dict:
        """로그 파일 정보"""
        log_info = {}
        
        if os.path.exists('logs'):
            for filename in os.listdir('logs'):
                if filename.endswith('.log'):
                    filepath = os.path.join('logs', filename)
                    stat = os.stat(filepath)
                    
                    log_info[filename] = {
                        "size_bytes": stat.st_size,
                        "size_mb": round(stat.st_size / 1024 / 1024, 2),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "lines": self._count_lines(filepath)
                    }
        
        return log_info
    
    def get_output_info(self) -> Dict:
        """출력 파일 정보"""
        output_info = {
            "total_files": 0,
            "total_size_mb": 0,
            "recent_files": []
        }
        
        if os.path.exists('output'):
            files = []
            for filename in os.listdir('output'):
                if filename.endswith(('.json', '.html')):
                    filepath = os.path.join('output', filename)
                    stat = os.stat(filepath)
                    
                    files.append({
                        "name": filename,
                        "size_bytes": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime)
                    })
            
            # 최신 파일 순으로 정렬
            files.sort(key=lambda x: x['modified'], reverse=True)
            
            output_info["total_files"] = len(files)
            output_info["total_size_mb"] = round(sum(f['size_bytes'] for f in files) / 1024 / 1024, 2)
            output_info["recent_files"] = [
                {
                    "name": f["name"],
                    "size_mb": round(f["size_bytes"] / 1024 / 1024, 2),
                    "modified": f["modified"].isoformat()
                }
                for f in files[:5]
            ]
        
        return output_info
    
    def get_service_status(self) -> Dict:
        """서비스 상태 확인"""
        status = {
            "aws_credentials": self._check_aws_credentials(),
            "telegram_configured": self._check_telegram(),
            "python_packages": self._check_python_packages(),
            "file_permissions": self._check_file_permissions()
        }
        
        return status
    
    def _count_lines(self, filepath: str) -> int:
        """파일 라인 수 계산"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
    
    def _check_aws_credentials(self) -> bool:
        """AWS 자격증명 확인"""
        try:
            result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_telegram(self) -> bool:
        """Telegram 설정 확인"""
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if bot_token and chat_id:
            return True
        
        try:
            with open('config/telegram_config.txt', 'r') as f:
                config = f.read().strip().split(':')
                return len(config) == 2 and bool(config[0]) and bool(config[1])
        except FileNotFoundError:
            return False
    
    def _check_python_packages(self) -> Dict:
        """Python 패키지 확인"""
        required_packages = [
            'boto3', 'streamlit', 'pandas', 'numpy', 
            'yfinance', 'aiohttp', 'plotly', 'scipy'
        ]
        
        package_status = {}
        for package in required_packages:
            try:
                __import__(package)
                package_status[package] = True
            except ImportError:
                package_status[package] = False
        
        return package_status
    
    def _check_file_permissions(self) -> Dict:
        """파일 권한 확인"""
        executable_files = [
            'run_complete_system.py',
            'quick_start.sh',
        ]
        
        permission_status = {}
        for file in executable_files:
            if os.path.exists(file):
                permission_status[file] = os.access(file, os.X_OK)
            else:
                permission_status[file] = None  # 파일 없음
        
        return permission_status
    
    def generate_report(self) -> Dict:
        """종합 리포트 생성"""
        report = {
            "report_info": {
                "generated_at": datetime.now().isoformat(),
                "monitor_uptime": str(datetime.now() - self.start_time)
            },
            "system_info": self.get_system_info(),
            "processes": self.get_process_info(),
            "logs": self.get_log_info(),
            "outputs": self.get_output_info(),
            "services": self.get_service_status()
        }
        
        return report
    
    def print_status(self):
        """상태 정보 출력"""
        report = self.generate_report()
        
        print("🖥️  시스템 모니터링 리포트")
        print("=" * 50)
        print(f"📅 생성 시간: {report['report_info']['generated_at']}")
        print(f"⏱️  모니터 가동 시간: {report['report_info']['monitor_uptime']}")
        print()
        
        # 시스템 리소스
        sys_info = report['system_info']
        print("💻 시스템 리소스:")
        print(f"  CPU 사용률: {sys_info['cpu_percent']:.1f}%")
        print(f"  메모리 사용률: {sys_info['memory']['percent']:.1f}%")
        print(f"  디스크 사용률: {sys_info['disk']['percent']:.1f}%")
        print()
        
        # 프로세스 정보
        processes = report['processes']
        print(f"🔄 관련 프로세스: {len(processes)}개")
        for proc in processes:
            print(f"  PID {proc['pid']}: {proc['name']} (CPU: {proc['cpu_percent']:.1f}%, MEM: {proc['memory_percent']:.1f}%)")
        print()
        
        # 서비스 상태
        services = report['services']
        print("🔧 서비스 상태:")
        print(f"  AWS 자격증명: {'✅' if services['aws_credentials'] else '❌'}")
        print(f"  Telegram: {'✅' if services['telegram_configured'] else '❌'}")
        
        # Python 패키지
        packages = services['python_packages']
        missing_packages = [pkg for pkg, status in packages.items() if not status]
        if missing_packages:
            print(f"  누락된 패키지: {', '.join(missing_packages)}")
        else:
            print("  Python 패키지: ✅ 모두 설치됨")
        print()
        
        # 로그 정보
        logs = report['logs']
        print(f"📄 로그 파일: {len(logs)}개")
        for filename, info in logs.items():
            print(f"  {filename}: {info['size_mb']}MB ({info['lines']} 줄)")
        print()
        
        # 출력 정보
        outputs = report['outputs']
        print(f"📁 출력 파일: {outputs['total_files']}개 ({outputs['total_size_mb']}MB)")
        for file_info in outputs['recent_files'][:3]:
            print(f"  {file_info['name']}: {file_info['size_mb']}MB")
        print()
    
    def save_report(self, filename: str = None):
        """리포트 저장"""
        if not filename:
            filename = f"logs/system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = self.generate_report()
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"💾 리포트 저장: {filename}")
        except Exception as e:
            print(f"❌ 리포트 저장 실패: {str(e)}")
    
    def continuous_monitor(self, interval: int = 60):
        """연속 모니터링"""
        print(f"🔄 연속 모니터링 시작 (간격: {interval}초)")
        print("Ctrl+C로 중지할 수 있습니다.")
        print()
        
        try:
            while True:
                self.print_status()
                print(f"⏳ {interval}초 대기 중...")
                print("-" * 50)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n👋 모니터링이 중지되었습니다.")

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="시스템 상태 모니터링")
    parser.add_argument("--continuous", action='store_true', help="연속 모니터링")
    parser.add_argument("--interval", type=int, default=60, help="모니터링 간격 (초)")
    parser.add_argument("--save", action='store_true', help="리포트 저장")
    parser.add_argument("--output", help="리포트 저장 파일명")
    
    args = parser.parse_args()
    
    # 로그 디렉토리 생성
    os.makedirs('logs', exist_ok=True)
    
    monitor = SystemMonitor()
    
    if args.continuous:
        monitor.continuous_monitor(args.interval)
    else:
        monitor.print_status()
        
        if args.save:
            monitor.save_report(args.output)

if __name__ == "__main__":
    main()
