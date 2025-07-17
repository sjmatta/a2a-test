#!/bin/bash

# Stop all A2A services

echo "🛑 Stopping A2A Services..."

if [ -f .service_pids ]; then
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            echo "Stopping process $pid..."
            kill $pid
        fi
    done < .service_pids
    
    rm -f .service_pids
    echo "✅ All services stopped!"
else
    echo "No service PIDs found. Services may not be running."
fi

# Also kill any python processes running our servers (backup cleanup)
pkill -f "search_server.py" 2>/dev/null || true
pkill -f "knowledge_server.py" 2>/dev/null || true
pkill -f "aggregation_server.py" 2>/dev/null || true
pkill -f "registry.py" 2>/dev/null || true

echo "🧹 Cleanup complete!"