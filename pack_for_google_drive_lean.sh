#!/bin/bash
set -euo pipefail

# LUKHAS AI - Lean Google Drive Package Script  
# Creates minimal, focused package with only essential code and documentation
# Author: LUKHAS AI T4 Team

# Configuration
PROJECT_NAME="LUKHAS-AI-LEAN"
VERSION=$(date +"%d%b%Y-%H%M")
OUTPUT_DIR="$HOME/LOCAL-REPOS"
PACKAGE_NAME="${PROJECT_NAME}-${VERSION}"
TEMP_DIR="/tmp/${PACKAGE_NAME}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🎯 LUKHAS AI - Lean Package Creator${NC}"
echo -e "${BLUE}====================================${NC}"
echo ""

# Create temp directory
mkdir -p "$TEMP_DIR/$PACKAGE_NAME"

echo -e "${YELLOW}📦 Including only essential components...${NC}"

# Copy CORE documentation (essential)
echo "  📄 Core documentation..."
cp README.md "$TEMP_DIR/$PACKAGE_NAME/" 2>/dev/null || true
cp CLAUDE.md "$TEMP_DIR/$PACKAGE_NAME/" 2>/dev/null || true
cp MATRIZ_CONSCIOUSNESS_ARCHITECTURE.md "$TEMP_DIR/$PACKAGE_NAME/" 2>/dev/null || true

# Copy PRODUCTION code (lukhas/ directory)
echo "  🏭 Production code (lukhas/)..."
if [ -d "lukhas" ]; then
    cp -r lukhas "$TEMP_DIR/$PACKAGE_NAME/"
    # Clean Python artifacts
    find "$TEMP_DIR/$PACKAGE_NAME/lukhas" -name "*.pyc" -delete 2>/dev/null || true
    find "$TEMP_DIR/$PACKAGE_NAME/lukhas" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
fi

# Copy CANDIDATE code (needs imports/connections but not experimental)
echo "  🔧 Candidate code (candidate/)..."
if [ -d "candidate" ]; then
    cp -r candidate "$TEMP_DIR/$PACKAGE_NAME/"
    # Clean Python artifacts
    find "$TEMP_DIR/$PACKAGE_NAME/candidate" -name "*.pyc" -delete 2>/dev/null || true
    find "$TEMP_DIR/$PACKAGE_NAME/candidate" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
fi

# Copy NEW enterprise infrastructure (src/ directory - the Phase 2 work)
echo "  🏢 Enterprise infrastructure (src/)..."
if [ -d "src" ]; then
    cp -r src "$TEMP_DIR/$PACKAGE_NAME/"
fi

# Copy essential configuration files
echo "  ⚙️  Configuration files..."
cp pyproject.toml "$TEMP_DIR/$PACKAGE_NAME/" 2>/dev/null || true
cp pytest.ini "$TEMP_DIR/$PACKAGE_NAME/" 2>/dev/null || true
cp Makefile "$TEMP_DIR/$PACKAGE_NAME/" 2>/dev/null || true
cp requirements*.txt "$TEMP_DIR/$PACKAGE_NAME/" 2>/dev/null || true

# Copy key API and integration files
echo "  🔌 API & integration code..."
if [ -d "api" ]; then
    cp -r api "$TEMP_DIR/$PACKAGE_NAME/"
fi
if [ -d "bridge" ]; then
    cp -r bridge "$TEMP_DIR/$PACKAGE_NAME/"
fi

# Copy main entry points
echo "  🚀 Entry points..."
cp main.py "$TEMP_DIR/$PACKAGE_NAME/" 2>/dev/null || true

# Copy essential tools (only the most important ones)
echo "  🛠️  Essential tools..."
mkdir -p "$TEMP_DIR/$PACKAGE_NAME/tools"
if [ -d "tools/analysis" ]; then
    cp -r tools/analysis "$TEMP_DIR/$PACKAGE_NAME/tools/"
fi

# Copy governance and security (critical for LUKHAS)
echo "  🛡️  Governance & security..."
if [ -d "governance" ]; then
    cp -r governance "$TEMP_DIR/$PACKAGE_NAME/"
fi

# Copy consciousness and memory systems (core LUKHAS features)
echo "  🧠 Consciousness systems..."
if [ -d "consciousness" ]; then
    cp -r consciousness "$TEMP_DIR/$PACKAGE_NAME/"
fi
if [ -d "memory" ]; then
    cp -r memory "$TEMP_DIR/$PACKAGE_NAME/"
fi

# Create package manifest
echo -e "${YELLOW}📝 Creating package manifest...${NC}"
cat > "$TEMP_DIR/$PACKAGE_NAME/PACKAGE_MANIFEST.md" << EOF
# LUKHAS AI Lean Package - $VERSION

## 🎯 What's Included

### **Core Production Systems**
- **lukhas/** - Production-grade Python modules ($(find "$TEMP_DIR/$PACKAGE_NAME/lukhas" -name "*.py" 2>/dev/null | wc -l | tr -d ' ') files)
- **candidate/** - Development modules needing import connections ($(find "$TEMP_DIR/$PACKAGE_NAME/candidate" -name "*.py" 2>/dev/null | wc -l | tr -d ' ') files)
- **src/** - Enterprise TypeScript infrastructure (Phase 2 work)
- **consciousness/** - Core consciousness and awareness systems  
- **memory/** - Fold-based memory and persistence
- **governance/** - Ethics, security, and compliance systems
- **api/** - REST API endpoints and GraphQL schemas
- **bridge/** - External service integrations (OpenAI, Anthropic, etc.)

### **Essential Documentation** 
- **README.md** - System overview and setup
- **CLAUDE.md** - Development guidelines and architecture
- **MATRIZ_CONSCIOUSNESS_ARCHITECTURE.md** - Core technical documentation

### **Configuration**
- **pyproject.toml** - Python project configuration
- **pytest.ini** - Testing configuration  
- **Makefile** - Build and development commands
- **requirements.txt** - Python dependencies

### **Key Tools**
- **tools/analysis/** - System analysis and monitoring tools
- **main.py** - Primary system entry point

## 🚫 What's Excluded (By Design)

- **.git/** - Git history (use separate bundle if needed)
- **node_modules/** - JavaScript dependencies (install via npm)
- **__pycache__/** - Python cache files
- **test_results/** - Test output and logs
- **trace/** - Debug traces and temporary files
- **.venv/** - Virtual environment

## 📊 Package Stats

- **Creation Date**: $(date)
- **Package Size**: $(du -sh "$TEMP_DIR/$PACKAGE_NAME" | cut -f1)
- **Python Files**: $(find "$TEMP_DIR/$PACKAGE_NAME" -name "*.py" 2>/dev/null | wc -l | tr -d ' ')
- **TypeScript Files**: $(find "$TEMP_DIR/$PACKAGE_NAME" -name "*.ts" 2>/dev/null | wc -l | tr -d ' ')
- **Total Files**: $(find "$TEMP_DIR/$PACKAGE_NAME" -type f 2>/dev/null | wc -l | tr -d ' ')

## 🚀 Quick Start

1. Extract package
2. \`pip install -r requirements.txt\`
3. \`make test\` (optional)
4. \`python main.py\`

## 🎯 Focus

This lean package contains only the **essential production code** and **enterprise infrastructure** needed to run LUKHAS AI. Perfect for deployment, sharing, or archival without development artifacts.

---
*Generated by LUKHAS AI Lean Packaging System*
EOF

# Calculate statistics
ORIGINAL_SIZE=$(du -sk . | cut -f1)
PACKAGE_SIZE=$(du -sk "$TEMP_DIR/$PACKAGE_NAME" | cut -f1)
REDUCTION=$((ORIGINAL_SIZE - PACKAGE_SIZE))

echo ""
echo -e "${GREEN}✅ Lean package created successfully${NC}"
echo "  Original repo: $(numfmt --to=iec ${ORIGINAL_SIZE}K)"
echo "  Lean package: $(numfmt --to=iec ${PACKAGE_SIZE}K)"
echo "  Size reduction: $(numfmt --to=iec ${REDUCTION}K) ($(( REDUCTION * 100 / ORIGINAL_SIZE ))%)"

# Create final archive
echo -e "${YELLOW}🗜️  Creating final archive...${NC}"
cd "$TEMP_DIR"
tar -czf "$OUTPUT_DIR/${PACKAGE_NAME}.tar.gz" "$PACKAGE_NAME"

# Generate checksum  
cd "$OUTPUT_DIR"
sha256sum "${PACKAGE_NAME}.tar.gz" > "${PACKAGE_NAME}.sha256"

FINAL_SIZE=$(du -sk "${OUTPUT_DIR}/${PACKAGE_NAME}.tar.gz" | cut -f1)

echo ""
echo -e "${GREEN}🎉 Lean Package Complete!${NC}"
echo -e "${GREEN}=========================${NC}"
echo ""
echo -e "${BLUE}📁 Output:${NC} $OUTPUT_DIR/${PACKAGE_NAME}.tar.gz"
echo -e "${BLUE}📊 Final Size:${NC} $(numfmt --to=iec ${FINAL_SIZE}K)"
echo -e "${BLUE}💾 Reduction:${NC} $(( (ORIGINAL_SIZE - FINAL_SIZE) * 100 / ORIGINAL_SIZE ))% smaller than original"
echo ""
echo -e "${YELLOW}✨ Ready for Google Drive upload!${NC}"

# Cleanup
rm -rf "$TEMP_DIR"

echo "📍 Package location: $OUTPUT_DIR"