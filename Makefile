.PHONY: help install clean start interactive search start-services stop-services distributed-start distributed-search status

# Default target
help:
	@echo "🚀 A2A Research Demo - Available Commands:"
	@echo ""
	@echo "📦 Setup:"
	@echo "  make install               - Install dependencies"
	@echo ""
	@echo "🔄 Single Process Mode (Simulated A2A):"
	@echo "  make start                 - Start interactive research demo"
	@echo "  make search QUERY='text'   - Run single search query"
	@echo ""
	@echo "🌐 Distributed Mode (True A2A):"
	@echo "  make start-services        - Start all A2A service servers"
	@echo "  make distributed-start     - Start distributed interactive demo"
	@echo "  make distributed-search QUERY='text' - Run distributed search"
	@echo "  make stop-services         - Stop all service servers"
	@echo "  make status                - Check service status"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean                 - Clean temporary files"
	@echo "  make help                  - Show this help message"
	@echo ""
	@echo "💡 Examples:"
	@echo "  make start-services"
	@echo "  make distributed-search QUERY='machine learning climate'"
	@echo "  make search QUERY='quantum computing' MAX=3"

# Install dependencies
install:
	uv sync

# Single process mode (original)
start:
	uv run main.py --interactive

interactive: start

search:
	@if [ -z "$(QUERY)" ]; then \
		echo "Error: Please provide a QUERY. Example: make search QUERY='machine learning'"; \
		exit 1; \
	fi
	uv run main.py --query "$(QUERY)" --max-results $(if $(MAX),$(MAX),5)

# Distributed mode (true A2A)
start-services:
	@echo "🚀 Starting distributed A2A services..."
	@./scripts/start_services.sh

stop-services:
	@./scripts/stop_services.sh

distributed-start:
	@echo "🌐 Starting distributed A2A research client..."
	uv run distributed_main.py --interactive

distributed-search:
	@if [ -z "$(QUERY)" ]; then \
		echo "Error: Please provide a QUERY. Example: make distributed-search QUERY='machine learning'"; \
		exit 1; \
	fi
	uv run distributed_main.py --query "$(QUERY)" --max-results $(if $(MAX),$(MAX),5)

status:
	@echo "🔍 Checking service status..."
	@curl -s http://127.0.0.1:8000/services 2>/dev/null | python -m json.tool || echo "❌ Services not running. Run 'make start-services' first."

# Clean temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -f .service_pids