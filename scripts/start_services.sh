#!/bin/bash

# Start all A2A services for distributed demo

echo "🚀 Starting A2A Service Infrastructure..."
echo ""

# Function to start a service in the background
start_service() {
    local service_name=$1
    local script_path=$2
    local port=$3
    
    echo "Starting $service_name on port $port..."
    uv run python $script_path $port &
    
    # Store PID for later cleanup
    echo $! >> .service_pids
    
    # Wait a bit for service to start
    sleep 2
}

# Clean up any existing PID file
rm -f .service_pids

# Start services in order
start_service "Service Registry" "src/a2a_research/servers/registry.py" 8000
start_service "Web Search Service" "src/a2a_research/servers/search_server.py" 8001
start_service "Knowledge Extraction Service" "src/a2a_research/servers/knowledge_server.py" 8002
start_service "Research Aggregation Service" "src/a2a_research/servers/aggregation_server.py" 8003

echo ""
echo "✅ All services started!"
echo ""

# Register services with the registry
./scripts/register_services.sh

echo ""
echo "Service URLs:"
echo "  📋 Registry:     http://127.0.0.1:8000"
echo "  🔍 Search:       http://127.0.0.1:8001"
echo "  🧠 Knowledge:    http://127.0.0.1:8002"
echo "  📊 Aggregation:  http://127.0.0.1:8003"
echo ""
echo "🔧 To stop services: make stop-services"
echo "🎯 To run research:   make distributed-search QUERY='your query'"
echo "🔄 To run interactive: make distributed-start"