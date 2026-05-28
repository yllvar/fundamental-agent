#!/usr/bin/env python3
"""
환경변수 설정 확인 스크립트
"""

import os


def check_environment():
    print("🔍 환경변수 설정 확인")
    print("=" * 40)

    # DeepSeek API 키 확인
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if api_key:
        print(f"✅ DEEPSEEK_API_KEY: {api_key[:8]}...{api_key[-4:]}")
    else:
        print("❌ DEEPSEEK_API_KEY: 설정되지 않음")

    # Telegram 확인
    telegram_bot = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat = os.getenv('TELEGRAM_CHAT_ID')
    if telegram_bot and telegram_chat:
        print(f"✅ TELEGRAM_BOT_TOKEN: 설정됨")
        print(f"✅ TELEGRAM_CHAT_ID: 설정됨")
    else:
        print("❌ TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID: 설정되지 않음")

    # .env 파일 확인
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        print(f"✅ .env 파일 존재: {env_file}")
    else:
        print(f"❌ .env 파일 없음: {env_file}")

    # config 파일 확인
    config_file = os.path.join(os.path.dirname(__file__), 'config', 'default.json')
    if os.path.exists(config_file):
        print(f"✅ config 파일 존재: {config_file}")
    else:
        print(f"❌ config 파일 없음: {config_file}")


if __name__ == "__main__":
    check_environment()
