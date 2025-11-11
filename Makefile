.PHONY: help test lint fmt clean install dev

help:
	@echo "SynthIQ Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make test      - Run all tests"
	@echo "  make lint      - Run linting (ruff)"
	@echo "  make fmt        - Format code (black + ruff format)"
	@echo "  make install    - Install all dependencies"
	@echo "  make dev        - Start all services in dev mode"
	@echo "  make clean      - Clean build artifacts"

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	@for service in orchestrator ingestor summarize viz; do \
		echo "Installing $$service..."; \
		python3 -m pip install -q -r $$service/requirements.txt || true; \
	done
	@echo "Installing dev dependencies..."
	@python3 -m pip install -q -r dev-requirements.txt || true
	@echo "Installing frontend dependencies..."
	@cd frontend && npm install

# Run tests
test:
	@echo "Running tests..."
	@python3 -m pytest orchestrator/tests/ -v || echo "Orchestrator tests failed"
	@python3 -m pytest summarize/tests/ -v || echo "Summarize tests failed"
	@python3 -m pytest ingestor/tests/ -v || echo "Ingestor tests failed"
	@python3 -m pytest viz/tests/ -v || echo "Viz tests failed"

# Lint code
lint:
	@echo "Running ruff lint..."
	@for service in orchestrator ingestor summarize viz; do \
		echo "Linting $$service..."; \
		ruff check $$service || true; \
	done
	@echo "Running frontend typecheck..."
	@cd frontend && npm run typecheck || true

# Format code
fmt:
	@echo "Formatting Python code with black..."
	@for service in orchestrator ingestor summarize viz; do \
		echo "Formatting $$service..."; \
		black $$service || true; \
	done
	@echo "Formatting with ruff..."
	@for service in orchestrator ingestor summarize viz; do \
		echo "Ruff format $$service..."; \
		ruff format $$service || true; \
	done

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	@find . -type d -name ".venv" -prune -o -type d -name "node_modules" -prune -o -type d -name "dist" -exec rm -r {} + 2>/dev/null || true
	@echo "Clean complete"

# Dev mode (start all services)
dev:
	@echo "Starting all services..."
	@echo "Orchestrator: http://localhost:8080"
	@echo "Ingestor: http://localhost:8081"
	@echo "Summarize: http://localhost:8082"
	@echo "Viz: http://localhost:8083"
	@echo "Frontend: http://localhost:5174"
	@echo ""
	@echo "Press Ctrl+C to stop all services"
	@trap 'kill 0' INT; \
	cd orchestrator && python main.py & \
	cd ../ingestor && python main.py & \
	cd ../summarize && python main.py & \
	cd ../viz && python main.py & \
	cd ../frontend && npm run dev & \
	wait

