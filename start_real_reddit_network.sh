#!/bin/bash

echo "📱 Reddit Data-based Network Analysis Dashboard"
echo "=================================================="

# Navigate to current directory
cd "$(dirname "$0")"

# Check .env file
if [ ! -f ".env" ]; then
    echo "❌ .env file not found."
    echo "Please configure Reddit API keys."
    exit 1
fi

# Check Reddit API keys
if ! grep -q "REDDIT_CLIENT_ID" .env; then
    echo "❌ REDDIT_CLIENT_ID not set in .env."
    exit 1
fi

if ! grep -q "REDDIT_CLIENT_SECRET" .env; then
    echo "❌ REDDIT_CLIENT_SECRET not set in .env."
    exit 1
fi

echo "✅ Reddit API keys verified"

# Activate virtual environment if present
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Check and install required packages
echo "📦 Checking required packages..."
pip install -q streamlit plotly networkx pandas numpy praw python-dotenv

# Test Reddit connection
echo "🔍 Testing Reddit connection..."
python -c "
from dotenv import load_dotenv
load_dotenv()
from data_monitoring.real_reddit_collector import RealRedditCollector
try:
    collector = RealRedditCollector()
    print('✅ Reddit API connection successful')
except Exception as e:
    print(f'❌ Reddit API connection failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Reddit connection test failed"
    echo "🔧 Resolution:"
    echo "1. Check Reddit API keys in .env file"
    echo "2. Check internet connection"
    echo "3. Check Reddit API rate limits"
    exit 1
fi

# Run Streamlit
echo "🌐 Running Reddit Network Analysis Dashboard..."
echo "📍 URL: http://localhost:8501"
echo "🔧 Press Ctrl+C to stop"
echo ""
echo "📱 Analyzing network using real Reddit data."
echo "🕸️ Collecting real-time data from 8 economic subreddits."
echo ""

streamlit run run_real_reddit_network.py --server.port 8501 --server.address 0.0.0.0
