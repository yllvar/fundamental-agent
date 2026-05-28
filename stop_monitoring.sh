#!/bin/bash

# Stop Slack Economic Alert Monitoring

echo "🔚 Stopping Slack Economic Alert Monitoring"
echo "================================"

cd /home/ec2-user/projects/ABP/fundamental_agent

# Check PID file
if [ -f "logs/monitoring.pid" ]; then
    PID=$(cat logs/monitoring.pid)
    
    # Check if process is running
    if ps -p $PID > /dev/null 2>&1; then
        echo "📋 Monitoring process found (PID: $PID)"
        echo "🔄 Stopping process..."
        
        # Stop process
        kill $PID
        
        # Wait for stop
        sleep 2
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️  Force stopping..."
            kill -9 $PID
        fi
        
        echo "✅ Monitoring process stopped"
        
        # Remove PID file
        rm -f logs/monitoring.pid
        
    else
        echo "ℹ️  PID file exists but process is not running."
        rm -f logs/monitoring.pid
    fi
else
    echo "ℹ️  PID file not found."
fi

# Check and stop all related processes
PROCESSES=$(pgrep -f "start_slack_monitoring.py")
if [ ! -z "$PROCESSES" ]; then
    echo "🔄 Stopping related processes..."
    pkill -f "start_slack_monitoring.py"
    echo "✅ All related processes stopped"
fi

echo ""
echo "📊 Current status:"
if pgrep -f "start_slack_monitoring.py" > /dev/null; then
    echo "🔴 Some processes are still running."
    echo "   Manual check: ps aux | grep start_slack_monitoring"
else
    echo "🟢 All monitoring processes stopped"
fi

echo ""
echo "🚀 To restart: ./start_background_monitoring.sh"
