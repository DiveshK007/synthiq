#!/bin/bash

# SynthIQ Stop Script
# Stops all running SynthIQ services

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Stopping SynthIQ services...${NC}"

# Stop services by PID files
SERVICES=("orchestrator" "ingestor" "summarize" "viz" "frontend")

for service in "${SERVICES[@]}"; do
    PID_FILE="/tmp/synthiq_${service}.pid"
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "Stopping $service (PID: $PID)..."
            kill "$PID" 2>/dev/null || true
            rm "$PID_FILE"
            echo -e "${GREEN}✓${NC} $service stopped"
        else
            rm "$PID_FILE"
        fi
    fi
done

# Also kill by port (fallback)
PORTS=(8080 8081 8082 8083 5174)

for port in "${PORTS[@]}"; do
    PID=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$PID" ]; then
        echo -e "Killing process on port $port (PID: $PID)..."
        kill "$PID" 2>/dev/null || true
    fi
done

# Kill Python processes that might be running services
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "uvicorn.*main:app" 2>/dev/null || true

# Kill frontend dev server
pkill -f "vite.*5174" 2>/dev/null || true

echo ""
echo -e "${GREEN}All services stopped!${NC}"

