#!/usr/bin/env python3
"""
Streamlit Application Runner Script
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """Run Streamlit application"""
    
    # Set current directory to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Streamlit app path
    app_path = "streamlit_app/app.py"
    
    # Streamlit run command
    cmd = [
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.address", "0.0.0.0",
        "--server.port", "8501",
        "--theme.primaryColor", "#1f77b4",
        "--theme.backgroundColor", "#ffffff",
        "--theme.secondaryBackgroundColor", "#f0f2f6",
        "--theme.textColor", "#262730"
    ]
    
    print("🚀 Starting Fundamental Agent Dashboard...")
    print(f"📍 URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to exit.")
    print("-" * 50)
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n\U0001f44b Dashboard shut down.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Run error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
