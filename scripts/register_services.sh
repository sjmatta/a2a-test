#!/bin/bash

# Register services with the registry

echo "📋 Registering services with registry..."

register_service() {
    local service_name=$1
    local port=$2
    
    echo "Registering $service_name..."
    curl -s -X POST "http://127.0.0.1:8000/register" \
        -H "Content-Type: application/json" \
        -d "{
            \"service_name\": \"$service_name\",
            \"host\": \"127.0.0.1\",
            \"port\": $port,
            \"health_endpoint\": \"/health\"
        }" || echo "Failed to register $service_name"
}

# Wait for registry to be ready
echo "Waiting for registry to be ready..."
for i in {1..10}; do
    if curl -s http://127.0.0.1:8000/health >/dev/null 2>&1; then
        echo "Registry is ready!"
        break
    fi
    echo "Waiting for registry... ($i/10)"
    sleep 2
done

# Register all services
register_service "web-search" 8001
register_service "knowledge-extraction" 8002
register_service "research-aggregation" 8003

echo "✅ Service registration complete!"
echo ""
echo "🔍 Service status:"
curl -s http://127.0.0.1:8000/services | python -m json.tool 2>/dev/null || echo "No services found"