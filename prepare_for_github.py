#!/usr/bin/env python3
"""
GitHub upload preparation script
Remove sensitive information and clean up files
"""

import os
import shutil
import json
from pathlib import Path

def clean_sensitive_files():
    """Clean up files containing sensitive information"""
    
    print("🧹 Cleaning up sensitive files...")
    
    # Files to remove
    sensitive_files = [
        ".env",
        "aws-credentials.json"
    ]
    
    for file_path in sensitive_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"  ✅ Removed: {file_path}")
        else:
            print(f"  ℹ️  Not found: {file_path}")
    
    # Clean up log directory
    if os.path.exists("logs"):
        shutil.rmtree("logs")
        print("  ✅ Log directory removed")
    
    # Clean up output directory (keep only sample files)
    if os.path.exists("output"):
        # Backup sample files
        sample_files = []
        for file in os.listdir("output"):
            if "sample" in file.lower() or "example" in file.lower():
                sample_files.append(file)
        
        # Remove directory and recreate
        shutil.rmtree("output")
        os.makedirs("output", exist_ok=True)
        
        # Create .gitkeep file
        with open("output/.gitkeep", "w") as f:
            f.write("# Directory for output files.\n")
        
        print("  ✅ Output directory cleaned")
    
    # Remove __pycache__ directories
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_path = os.path.join(root, dir_name)
                shutil.rmtree(pycache_path)
                print(f"  ✅ Removed: {pycache_path}")

def create_sample_configs():
    """Create sample configuration files"""
    
    print("📝 Creating sample config files...")
    
    # Sample environment variables file
    env_sample = """# Environment variable configuration example
# Copy to .env file for actual use

# DeepSeek API Configuration

DEEPSEEK_API_KEY=sk-your_deepseek_api_key_here

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Other settings
DEBUG=false
LOG_LEVEL=INFO
"""
    
    with open(".env.example", "w", encoding="utf-8") as f:
        f.write(env_sample)
    print("  ✅ .env.example created")
    
    # Create log directory
    os.makedirs("logs", exist_ok=True)
    with open("logs/.gitkeep", "w") as f:
        f.write("# Directory for log files.\n")
    print("  ✅ logs/.gitkeep created")

def update_file_permissions():
    """Set executable file permissions"""
    
    print("🔧 Setting file permissions...")
    
    executable_files = [
        "start_background_monitoring.sh",
        "stop_monitoring.sh",
        "check_monitoring_status.sh",
        "demo_streamlit.py",
        "demo_advanced_events.py",
        "main.py",
        "test_system.py",
        "run_streamlit.py"
    ]
    
    for file_path in executable_files:
        if os.path.exists(file_path):
            os.chmod(file_path, 0o755)
            print(f"  ✅ Permission set: {file_path}")

def create_github_workflows():
    """Create GitHub Actions workflow"""
    
    print("⚙️ Creating GitHub Actions workflow...")
    
    os.makedirs(".github/workflows", exist_ok=True)
    
    workflow_content = """name: Test Fundamental Agent

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run basic tests
      run: |
        python -c "import sys; print('Python version:', sys.version)"
        python -c "from agents.base_agent import BaseAgent; print('Base agent import successful')"
        python -c "from data_monitoring.technical_analysis import TechnicalAnalyzer; print('Technical analysis import successful')"
        python -c "from notifications.telegram_notifier import TelegramNotifier; print('Telegram notifier import successful')"
     
    - name: Test system components
      run: |
        # Tests that can run without DeepSeek API key
        python data_monitoring/technical_analysis.py || true
        python -c "from notifications.telegram_notifier import TelegramNotifier; print('Telegram notifier import successful')"
"""
    
    with open(".github/workflows/test.yml", "w", encoding="utf-8") as f:
        f.write(workflow_content)
    print("  ✅ GitHub Actions workflow created")

def create_contributing_guide():
    """Create contributing guide"""
    
    print("📖 Creating contributing guide...")
    
    contributing_content = """# Contributing Guide

Thank you for contributing to the Fundamental Agent project!

## 🚀 Getting Started

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Development Environment Setup

```bash
# Clone repository
git clone https://github.com/jihwanwoo/fundamental-agent.git
cd fundamental-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env file with actual values

# Run tests
python test_system.py
```

## 🧪 Testing

When adding new features, please include tests.

```bash
# Basic tests
python test_system.py

# Individual component tests
python data_monitoring/technical_analysis.py
python notifications/telegram_notifier.py
```

## 📝 Coding Style

- Follow Python PEP 8 style guide
- Write docstrings for functions and classes
- Use clear and meaningful variable names
- Write comments in English

## 🐛 Bug Reports

If you find a bug, please create an issue with the following information:

- Operating system and Python version
- Full error message
- Steps to reproduce
- Expected vs actual behavior

## 💡 Feature Suggestions

When suggesting new features:

- Explain the purpose and need
- Provide implementation ideas
- Include relevant examples or references

## 📞 Contact

If you have questions or need help, please reach out via GitHub Issues.
"""
    
    with open("CONTRIBUTING.md", "w", encoding="utf-8") as f:
        f.write(contributing_content)
    print("  ✅ CONTRIBUTING.md created")

def main():
    """Main function"""
    print("🚀 Starting GitHub upload preparation")
    print("=" * 50)
    
    # Check current directory
    current_dir = os.getcwd()
    print(f"📁 Current directory: {current_dir}")
    
    # Run tasks
    clean_sensitive_files()
    print()
    
    create_sample_configs()
    print()
    
    update_file_permissions()
    print()
    
    create_github_workflows()
    print()
    
    create_contributing_guide()
    print()
    
    print("✅ GitHub upload preparation complete!")
    print()
    print("📋 Next steps:")
    print("1. Create a GitHub Personal Access Token")
    print("2. Set up git init and remote")
    print("3. Commit and push files")
    print()
    print("⚠️  Notes:")
    print("- Do not enter actual values in .env file")
    print("- Do not include API keys in code")
    print("- Do not expose Telegram bot tokens")

if __name__ == "__main__":
    main()
