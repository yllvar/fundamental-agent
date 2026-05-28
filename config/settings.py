"""
시스템 설정 관리 모듈
"""

import json
import os
from typing import Dict, Any
from pathlib import Path


def load_config(config_path: str = None) -> Dict[str, Any]:
    """설정 파일 로드"""

    # 기본 설정
    default_config = {
        "model_id": "deepseek-v4-flash",
        "temperature": 0.7,
        "max_tokens": 4000,

        # 데이터 수집 설정
        "data_collection": {
            "stock_symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "SPY", "QQQ"],
            "economic_indicators": ["^GSPC", "^DJI", "^IXIC", "^VIX"],
            "news_feeds": [
                "https://feeds.bloomberg.com/markets/news.rss",
                "https://feeds.reuters.com/reuters/businessNews",
                "https://rss.cnn.com/rss/money_latest.rss"
            ],
            "update_interval_minutes": 30
        },

        # 기사 생성 설정
        "article_generation": {
            "default_types": ["market_summary", "stock_focus"],
            "default_length": "medium",
            "max_articles_per_run": 5
        },

        # 최적화 설정
        "optimization": {
            "default_focus": ["readability", "seo", "engagement"],
            "quality_threshold": 80
        },

        # 출력 설정
        "output": {
            "directory": "output",
            "save_html": True,
            "save_json": True,
            "backup_days": 30
        },

        # 스케줄 설정
        "schedule": {
            "data_collection_interval": 30,
            "article_generation_interval": 60,
            "optimization_interval": 120,
            "enabled": False
        },

        # 로깅 설정
        "logging": {
            "level": "INFO",
            "file_rotation": True,
            "max_file_size_mb": 10,
            "backup_count": 5
        }
    }

    # 설정 파일이 지정된 경우 로드
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)

            # 기본 설정과 파일 설정 병합
            default_config.update(file_config)

        except Exception as e:
            print(f"설정 파일 로드 오류: {e}")
            print("기본 설정을 사용합니다.")

    # 환경 변수 오버라이드
    if os.getenv("DEEPSEEK_API_KEY"):
        default_config["api_key_set"] = True

    if os.getenv("MODEL_ID"):
        default_config["model_id"] = os.getenv("MODEL_ID")

    return default_config


def save_config(config: Dict[str, Any], config_path: str) -> None:
    """설정을 파일로 저장"""
    try:
        # 디렉토리 생성
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"설정 저장 완료: {config_path}")

    except Exception as e:
        print(f"설정 저장 오류: {e}")


def create_sample_config(output_path: str = "config/sample.json") -> None:
    """샘플 설정 파일 생성"""
    sample_config = {
        "model_id": "deepseek-v4-flash",
        "temperature": 0.7,
        "max_tokens": 4000,

        "data_collection": {
            "stock_symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"],
            "update_interval_minutes": 30
        },

        "article_generation": {
            "default_types": ["market_summary"],
            "default_length": "medium"
        },

        "output": {
            "directory": "output",
            "save_html": True,
            "save_json": True
        },

        "schedule": {
            "enabled": False,
            "data_collection_interval": 30,
            "article_generation_interval": 60
        }
    }

    save_config(sample_config, output_path)
    print(f"샘플 설정 파일 생성: {output_path}")


if __name__ == "__main__":
    # 테스트 및 샘플 생성
    print("설정 모듈 테스트")

    # 기본 설정 로드
    config = load_config()
    print(f"기본 설정 로드 완료: {len(config)} 항목")

    # 샘플 설정 파일 생성
    create_sample_config()
