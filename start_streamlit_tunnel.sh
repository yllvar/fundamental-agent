#!/bin/bash
# SSH tunnel Streamlit start script

echo "🚀 Streamlit Intelligence Dashboard (SSH tunnel mode)"
echo "=" * 60

# Navigate to project directory
cd /home/ec2-user/projects/ABP/fundamental_agent

# Activate virtual environment
echo "📦 Activating virtual environment..."
source /home/ec2-user/dl_env/bin/activate

# Set API keys
export ALPHA_VANTAGE_API_KEY=9TLAUWS4L3099YK3

echo "🔑 API keys configured"
echo "📊 Starting Dashboard..."
echo ""
echo "🌐 Access method:"
echo "  Local browser: http://localhost:8501"
echo "  Or: http://127.0.0.1:8501"
echo ""
echo "⚠️ Keep SSH tunnel connection active!"
echo "🛑 Exit: Ctrl+C"
echo ""

# Run Streamlit (localhost mode)
streamlit run streamlit_intelligence_dashboard.py --server.address localhost --server.port 8501
