#!/bin/bash

# SynthIQ Demo Script
# Starts all services and runs a demo job

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
ORCHESTRATOR_URL="http://localhost:8080"
INGESTOR_URL="http://localhost:8081"
SUMMARIZE_URL="http://localhost:8082"
VIZ_URL="http://localhost:8083"
FRONTEND_URL="http://localhost:5174"

# Demo URLs
DEMO_URLS=(
    "https://en.wikipedia.org/wiki/Artificial_intelligence"
    "https://en.wikipedia.org/wiki/Machine_learning"
    "https://en.wikipedia.org/wiki/Deep_learning"
)

DEMO_GOAL="Summarize the key concepts and differences between AI, ML, and deep learning"

echo -e "${BLUE}🚀 SynthIQ Demo Script${NC}"
echo ""

# Function to check if a service is running
check_service() {
    local url=$1
    local name=$2
    
    if curl -s -f "$url/healthz" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name is running"
        return 0
    else
        echo -e "${RED}✗${NC} $name is not running"
        return 1
    fi
}

# Function to wait for a service to be ready
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=0
    
    echo -n "Waiting for $name to be ready..."
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "$url/healthz" > /dev/null 2>&1; then
            echo -e " ${GREEN}ready!${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
        echo -n "."
    done
    echo -e " ${RED}timeout!${NC}"
    return 1
}

# Function to start a service in background
start_service() {
    local service_dir=$1
    local port=$2
    local name=$3
    
    echo -e "${YELLOW}Starting $name on port $port...${NC}"
    
    cd "$service_dir" || exit 1
    
    # Check if venv exists, create if not
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment for $name..."
        python3 -m venv .venv
    fi
    
    source .venv/bin/activate
    pip install -q -r requirements.txt 2>/dev/null || true
    
    # Set environment variables
    export PORT=$port
    export VERSION=0.1.0
    export FRONTEND_ORIGIN=$FRONTEND_URL
    export INGESTOR_URL=$INGESTOR_URL
    export SUMMARIZE_URL=$SUMMARIZE_URL
    export VIZ_URL=$VIZ_URL
    
    # Start service in background
    python main.py > "/tmp/synthiq_${name}.log" 2>&1 &
    echo $! > "/tmp/synthiq_${name}.pid"
    
    cd - > /dev/null
}

# Check if services are already running
echo "Checking for existing services..."
if check_service "$ORCHESTRATOR_URL" "Orchestrator" || \
   check_service "$INGESTOR_URL" "Ingestor" || \
   check_service "$SUMMARIZE_URL" "Summarize" || \
   check_service "$VIZ_URL" "Viz"; then
    echo -e "${YELLOW}Some services are already running.${NC}"
    read -p "Do you want to stop them and start fresh? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Stopping existing services..."
        ./scripts/stop.sh || true
        sleep 2
    else
        echo "Using existing services..."
    fi
fi

# Start services
echo ""
echo -e "${BLUE}Starting services...${NC}"

# Start Ingestor
start_service "ingestor" 8081 "Ingestor"
wait_for_service "$INGESTOR_URL" "Ingestor"

# Start Summarize
start_service "summarize" 8082 "Summarize"
wait_for_service "$SUMMARIZE_URL" "Summarize"

# Start Viz
start_service "viz" 8083 "Viz"
wait_for_service "$VIZ_URL" "Viz"

# Start Orchestrator
start_service "orchestrator" 8080 "Orchestrator"
wait_for_service "$ORCHESTRATOR_URL" "Orchestrator"

# Start Frontend (optional)
if command -v npm &> /dev/null; then
    echo -e "${YELLOW}Starting frontend...${NC}"
    cd frontend || exit 1
    npm install > /dev/null 2>&1 || true
    npm run dev > "/tmp/synthiq_frontend.log" 2>&1 &
    echo $! > "/tmp/synthiq_frontend.pid"
    cd - > /dev/null
    sleep 3
fi

echo ""
echo -e "${GREEN}All services are running!${NC}"
echo ""

# Create demo job
echo -e "${BLUE}Creating demo job...${NC}"

# Build sources JSON
SOURCES_JSON="["
for i in "${!DEMO_URLS[@]}"; do
    if [ $i -gt 0 ]; then
        SOURCES_JSON+=","
    fi
    SOURCES_JSON+="{\"type\":\"url\",\"value\":\"${DEMO_URLS[$i]}\"}"
done
SOURCES_JSON+="]"

# Create job
JOB_RESPONSE=$(curl -s -X POST "$ORCHESTRATOR_URL/jobs" \
    -H "Content-Type: application/json" \
    -d "{
        \"sources\": $SOURCES_JSON,
        \"goal\": \"$DEMO_GOAL\"
    }")

JOB_ID=$(echo "$JOB_RESPONSE" | grep -o '"job_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$JOB_ID" ]; then
    echo -e "${RED}Failed to create job${NC}"
    echo "Response: $JOB_RESPONSE"
    exit 1
fi

echo -e "${GREEN}Job created: $JOB_ID${NC}"
echo ""

# Poll for job completion
echo -e "${BLUE}Waiting for job to complete...${NC}"
MAX_ATTEMPTS=60
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    JOB_STATUS=$(curl -s "$ORCHESTRATOR_URL/jobs/$JOB_ID")
    STATUS=$(echo "$JOB_STATUS" | grep -o '"status":"[^"]*' | cut -d'"' -f4)
    
    if [ "$STATUS" = "done" ]; then
        echo -e "${GREEN}Job completed!${NC}"
        echo ""
        echo "Job Results:"
        echo "$JOB_STATUS" | python3 -m json.tool 2>/dev/null || echo "$JOB_STATUS"
        echo ""
        
        # Open browser
        if command -v open &> /dev/null; then
            echo "Opening job detail page..."
            open "$FRONTEND_URL/jobs/$JOB_ID" 2>/dev/null || true
        elif command -v xdg-open &> /dev/null; then
            echo "Opening job detail page..."
            xdg-open "$FRONTEND_URL/jobs/$JOB_ID" 2>/dev/null || true
        fi
        
        echo ""
        echo -e "${GREEN}Demo complete!${NC}"
        echo "Frontend: $FRONTEND_URL"
        echo "Job ID: $JOB_ID"
        echo ""
        echo "To stop services, run: ./scripts/stop.sh"
        exit 0
    elif [ "$STATUS" = "error" ]; then
        ERROR=$(echo "$JOB_STATUS" | grep -o '"error":"[^"]*' | cut -d'"' -f4)
        echo -e "${RED}Job failed: $ERROR${NC}"
        exit 1
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    sleep 2
    echo -n "."
done

echo ""
echo -e "${YELLOW}Job did not complete within timeout${NC}"
echo "Job ID: $JOB_ID"
echo "Check status: curl $ORCHESTRATOR_URL/jobs/$JOB_ID"
echo ""
echo "To stop services, run: ./scripts/stop.sh"

