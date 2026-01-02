#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Starting MiniDB Database Application ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to check if server is ready
wait_for_server() {
    echo -e "${YELLOW}Waiting for server to be ready...${NC}"
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8080/api/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Server is ready!${NC}"
            return 0
        fi
        echo -e "${YELLOW}  Attempt $attempt/$max_attempts - server not ready yet...${NC}"
        sleep 1
        ((attempt++))
    done
    
    echo -e "${RED}✗ Server failed to start within timeout${NC}"
    return 1
}

# Function to start server in background
start_server() {
    echo -e "${GREEN}[1/2] Starting server.py...${NC}"
    cd /app
    python server.py > /tmp/server.log 2>&1 &
    SERVER_PID=$!
    echo $SERVER_PID > /tmp/server.pid
    echo -e "${GREEN}  Server started with PID: $SERVER_PID${NC}"
}

# Function to start GUI
start_gui() {
    echo -e "${GREEN}[2/2] Starting gui.py...${NC}"
    cd /app
    python gui.py
    GUI_EXIT_CODE=$?
    
    # When GUI exits, stop the server
    if [ -f /tmp/server.pid ]; then
        SERVER_PID=$(cat /tmp/server.pid)
        echo -e "${YELLOW}Stopping server (PID: $SERVER_PID)...${NC}"
        kill $SERVER_PID 2>/dev/null
        rm /tmp/server.pid
    fi
    
    exit $GUI_EXIT_CODE
}

# Main execution
main() {
    # Start the server first
    start_server
    
    # Wait for server to be ready
    if ! wait_for_server; then
        echo -e "${RED}Failed to start server. Check /tmp/server.log for details${NC}"
        cat /tmp/server.log
        exit 1
    fi
    
    # Display server information
    echo ""
    echo -e "${GREEN}Server Information:${NC}"
    echo "  - URL: http://localhost:8080"
    echo "  - API Endpoints:"
    echo "    * GET  /api/health    - Health check"
    echo "    * GET  /api/tables    - List all tables"
    echo "    * POST /api/tables    - Create table"
    echo "    * POST /api/query     - Execute SQL query"
    echo "    * POST /api/nlp       - Natural language query"
    echo ""
    echo -e "${GREEN}Starting GUI...${NC}"
    echo ""
    
    # Start the GUI
    start_gui
}

# Run main function
main "$@"
