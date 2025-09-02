#!/bin/bash
# =============================================================================
# LUKHΛS Demo Setup Script
# =============================================================================
# Sets up and launches the LUKHΛS system for OpenAI review demonstration
# Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
# =============================================================================

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Print header
print_header() {
    clear
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${CYAN}        🛡️  LUKHΛS AGI System Demo Setup  🛡️${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}Trinity Framework: ⚛️ 🧠 🛡️${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}\n"
}

# Check Python installation
check_python() {
    echo -e "${BLUE}Checking Python installation...${NC}"
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo -e "${GREEN}✓ Python found: $PYTHON_VERSION${NC}"
        return 0
    else
        echo -e "${RED}✗ Python 3 not found. Please install Python 3.8+${NC}"
        return 1
    fi
}

# Check and activate virtual environment
setup_venv() {
    echo -e "\n${BLUE}Setting up virtual environment...${NC}"

    # Check if .venv exists
    if [ -d ".venv" ]; then
        echo -e "${GREEN}✓ Virtual environment found${NC}"
    else
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv .venv
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Virtual environment created${NC}"
        else
            echo -e "${RED}✗ Failed to create virtual environment${NC}"
            return 1
        fi
    fi

    # Activate virtual environment
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source .venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
}

# Install dependencies
install_dependencies() {
    echo -e "\n${BLUE}Installing dependencies...${NC}"

    if [ -f "requirements.txt" ]; then
        pip install -q --upgrade pip
        pip install -q -r requirements.txt
        echo -e "${GREEN}✓ Core dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠ requirements.txt not found${NC}"
    fi

    # Install FastAPI and Uvicorn if not present
    pip install -q fastapi uvicorn
    echo -e "${GREEN}✓ FastAPI and Uvicorn ready${NC}"
}

# Initialize data directory
setup_data() {
    echo -e "\n${BLUE}Initializing data directory...${NC}"

    # Create data directory
    mkdir -p data
    mkdir -p guardian_audit/logs
    mkdir -p meta_dashboard/static

    # Initialize demo user if not exists
    if [ ! -f "data/users.json" ]; then
        echo -e "${YELLOW}Creating demo user database...${NC}"
        python3 -c "from identity.user_db import user_db; print('Demo user initialized')"
    fi

    echo -e "${GREEN}✓ Data directory ready${NC}"
}

# Create demo FastAPI app
create_demo_app() {
    echo -e "\n${BLUE}Creating demo application...${NC}"

    cat > demo_app.py << 'EOF'
"""
LUKHΛS Demo Application
======================
FastAPI application for OpenAI review demonstration.
"""

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
import uvicorn

# Import identity system
from identity import identity_router, get_current_user, AuthContext
from meta_dashboard.routes.log_route import log_router

# Create app
app = FastAPI(
    title="LUKHΛS AGI System",
    description="Trinity Framework Protected AGI Platform",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="meta_dashboard/static"), name="static")

# Include routers
app.include_router(identity_router)
app.include_router(log_router)

# Root redirect to login
@app.get("/")
async def root():
    return RedirectResponse(url="/static/login.html")

# Meta dashboard overview (protected)
@app.get("/meta/overview")
async def meta_overview(user: AuthContext = Depends(get_current_user)):
    return {
        "page": "Meta Dashboard Overview",
        "user": user.email,
        "tier": user.tier,
        "glyphs": user.glyphs,
        "trinity_score": user.trinity_score,
        "message": "Dashboard UI would be rendered here"
    }

# Meta trends (protected)
@app.get("/meta/trends")
async def meta_trends(user: AuthContext = Depends(get_current_user)):
    return {
        "page": "Meta Dashboard Trends",
        "user": user.email,
        "tier": user.tier,
        "charts": ["Trinity Score Timeline", "Drift Analysis", "Intervention History"],
        "message": "Trends visualization would be rendered here"
    }

# Symbolic map
@app.get("/meta/symbolic-map")
async def symbolic_map():
    return FileResponse("meta_dashboard/templates/symbolic_map.html")

if __name__ == "__main__":
    print("\n🛡️ LUKHΛS Demo Server Starting...")
    print("⚛️ 🧠 🛡️ Trinity Framework Active\n")
    print("Demo Credentials:")
    print("  Email: reviewer@openai.com")
    print("  Password: demo_password")
    print("  Tier: T5 (Guardian)\n")
    print("Access Points:")
    print("  Login: http://localhost:8000/static/login.html")
    print("  API Docs: http://localhost:8000/docs")
    print("  Symbolic Map: http://localhost:8000/meta/symbolic-map\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

    echo -e "${GREEN}✓ Demo application created${NC}"
}

# Generate token cards
generate_artifacts() {
    echo -e "\n${BLUE}Generating review artifacts...${NC}"

    # Generate API token cards
    if [ -f "meta_dashboard/generate_token_cards.py" ]; then
        python3 meta_dashboard/generate_token_cards.py > /dev/null 2>&1
        echo -e "${GREEN}✓ API token cards generated${NC}"
    fi

    # Create reviewer token file
    cat > meta_dashboard/reviewer_token.json << EOF
{
    "reviewer": {
        "email": "reviewer@openai.com",
        "token": "LUKHAS-T5-GATE",
        "tier": "T5",
        "tier_name": "Guardian",
        "glyphs": ["🛡️", "⚛️", "🧠"],
        "access_level": "Full System Access",
        "trinity_score": 1.0,
        "note": "Pre-configured for OpenAI review"
    }
}
EOF

    echo -e "${GREEN}✓ Reviewer token file created${NC}"
}

# Launch server
launch_demo() {
    echo -e "\n${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${GREEN}LUKHΛS Demo Ready!${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}\n"

    echo -e "${CYAN}Demo Access:${NC}"
    echo -e "  ${BOLD}Login URL:${NC} http://localhost:8000/static/login.html"
    echo -e "  ${BOLD}Email:${NC} reviewer@openai.com"
    echo -e "  ${BOLD}Password:${NC} demo_password"
    echo -e "  ${BOLD}API Docs:${NC} http://localhost:8000/docs"

    echo -e "\n${CYAN}Key Endpoints:${NC}"
    echo -e "  ${BOLD}/identity/login${NC} - Authentication"
    echo -e "  ${BOLD}/meta/overview${NC} - Dashboard overview"
    echo -e "  ${BOLD}/meta/trends${NC} - Trends analysis"
    echo -e "  ${BOLD}/api/meta/log${NC} - System logs"
    echo -e "  ${BOLD}/meta/symbolic-map${NC} - Symbolic reference"

    echo -e "\n${YELLOW}Starting server...${NC}\n"

    # Launch the demo
    python3 demo_app.py
}

# Error handler
handle_error() {
    echo -e "\n${RED}Error: Setup failed at step: $1${NC}"
    echo -e "${YELLOW}Please check the error messages above and try again.${NC}"
    exit 1
}

# Main execution
main() {
    print_header

    # Change to script directory
    cd "$(dirname "$0")/.." || handle_error "Directory navigation"

    # Run setup steps
    check_python || handle_error "Python check"
    setup_venv || handle_error "Virtual environment"
    install_dependencies || handle_error "Dependencies"
    setup_data || handle_error "Data initialization"
    create_demo_app || handle_error "Demo app creation"
    generate_artifacts || handle_error "Artifact generation"

    # Launch demo
    launch_demo
}

# Run main function
main
