#!/bin/bash

# LUKHAS Context Pack Generator for ChatGPT
# Combines all lukhas_context.md files into a single comprehensive document

PACK_FILE="exports/LUKHAS_CONTEXT_PACK_FOR_CHATGPT.md"
TEMP_FILE="exports/temp_context_pack.md"

echo "🚀 Generating LUKHAS Context Pack for ChatGPT..."

# Initialize with existing header
cp "$PACK_FILE" "$TEMP_FILE"

# Function to add a context file with proper formatting
add_context_file() {
    local file_path="$1"
    local display_name="$2"
    local category="$3"

    echo "" >> "$TEMP_FILE"
    echo "## 📁 $category: $display_name" >> "$TEMP_FILE"
    echo "" >> "$TEMP_FILE"
    echo "**File:** \`$file_path\`" >> "$TEMP_FILE"
    echo "" >> "$TEMP_FILE"
    echo '```markdown' >> "$TEMP_FILE"
    cat "$file_path" >> "$TEMP_FILE"
    echo '```' >> "$TEMP_FILE"
    echo "" >> "$TEMP_FILE"
    echo "---" >> "$TEMP_FILE"
}

# Add master overview first
add_context_file "./lukhas_context.md" "Master System Overview" "🏗️ CORE ARCHITECTURE"

# Add MATRIZ engine
add_context_file "./matriz/lukhas_context.md" "MATRIZ Cognitive Engine" "🏗️ CORE ARCHITECTURE"
add_context_file "./matriz/core/lukhas_context.md" "MATRIZ Core Components" "🏗️ CORE ARCHITECTURE"
add_context_file "./matriz/visualization/lukhas_context.md" "MATRIZ Visualization" "🏗️ CORE ARCHITECTURE"

# Add main workspace areas
add_context_file "./candidate/lukhas_context.md" "Candidate Development Workspace" "🏗️ CORE ARCHITECTURE"
add_context_file "./lukhas/lukhas_context.md" "LUKHAS Integration Layer" "🏗️ CORE ARCHITECTURE"
add_context_file "./products/lukhas_context.md" "Products Deployment Layer" "🏗️ CORE ARCHITECTURE"

# Trinity Framework - Identity (⚛️)
add_context_file "./identity/lukhas_context.md" "Identity Foundation" "⚛️ TRINITY - IDENTITY"
add_context_file "./candidate/core/identity/lukhas_context.md" "Identity Development Core" "⚛️ TRINITY - IDENTITY"
add_context_file "./lukhas/identity/lukhas_context.md" "Identity Integration" "⚛️ TRINITY - IDENTITY"

# Trinity Framework - Consciousness (🧠)
add_context_file "./consciousness/lukhas_context.md" "Consciousness Research Foundation" "🧠 TRINITY - CONSCIOUSNESS"
add_context_file "./candidate/consciousness/lukhas_context.md" "Consciousness Development" "🧠 TRINITY - CONSCIOUSNESS"
add_context_file "./lukhas/consciousness/lukhas_context.md" "Consciousness Integration" "🧠 TRINITY - CONSCIOUSNESS"
add_context_file "./candidate/aka_qualia/lukhas_context.md" "Qualia Processing" "🧠 TRINITY - CONSCIOUSNESS"
add_context_file "./candidate/dream/lukhas_context.md" "Dream State Processing" "🧠 TRINITY - CONSCIOUSNESS"

# Trinity Framework - Guardian (🛡️)
add_context_file "./ethics/lukhas_context.md" "Ethics Foundation" "🛡️ TRINITY - GUARDIAN"
add_context_file "./governance/lukhas_context.md" "Governance Systems" "🛡️ TRINITY - GUARDIAN"
add_context_file "./candidate/governance/lukhas_context.md" "Governance Development" "🛡️ TRINITY - GUARDIAN"
add_context_file "./lukhas/governance/lukhas_context.md" "Governance Integration" "🛡️ TRINITY - GUARDIAN"
add_context_file "./ethics/guardian/lukhas_context.md" "Guardian Implementation" "🛡️ TRINITY - GUARDIAN"
add_context_file "./ethics/compliance/lukhas_context.md" "Compliance Systems" "🛡️ TRINITY - GUARDIAN"
add_context_file "./ethics/drift_detection/lukhas_context.md" "Drift Detection" "🛡️ TRINITY - GUARDIAN"

# Memory Systems
add_context_file "./memory/lukhas_context.md" "Memory Foundation" "🧮 SPECIALIZED DOMAINS"
add_context_file "./candidate/memory/lukhas_context.md" "Memory Development" "🧮 SPECIALIZED DOMAINS"
add_context_file "./lukhas/memory/lukhas_context.md" "Memory Integration" "🧮 SPECIALIZED DOMAINS"

# Bio/Quantum Systems
add_context_file "./bio/lukhas_context.md" "Bio-Inspired Systems" "🧮 SPECIALIZED DOMAINS"
add_context_file "./quantum/lukhas_context.md" "Quantum-Inspired Systems" "🧮 SPECIALIZED DOMAINS"

# Bridge/API Systems
add_context_file "./candidate/bridge/lukhas_context.md" "Bridge Development" "🧮 SPECIALIZED DOMAINS"
add_context_file "./lukhas/api/lukhas_context.md" "API Integration" "🧮 SPECIALIZED DOMAINS"
add_context_file "./lukhas/orchestration/lukhas_context.md" "Orchestration Systems" "🧮 SPECIALIZED DOMAINS"

# Core Development Systems
add_context_file "./candidate/core/lukhas_context.md" "Core Development Framework" "🧮 SPECIALIZED DOMAINS"
add_context_file "./candidate/core/orchestration/lukhas_context.md" "Core Orchestration" "🧮 SPECIALIZED DOMAINS"
add_context_file "./candidate/core/interfaces/lukhas_context.md" "Core Interfaces" "🧮 SPECIALIZED DOMAINS"
add_context_file "./candidate/core/symbolic/lukhas_context.md" "Symbolic Systems" "🧮 SPECIALIZED DOMAINS"

# Enterprise & Products
add_context_file "./products/enterprise/lukhas_context.md" "Enterprise Features" "🏢 ENTERPRISE & PRODUCTS"
add_context_file "./products/enterprise/compliance/lukhas_context.md" "Enterprise Compliance" "🏢 ENTERPRISE & PRODUCTS"
add_context_file "./products/experience/lukhas_context.md" "User Experience" "🏢 ENTERPRISE & PRODUCTS"
add_context_file "./products/experience/dashboard/lukhas_context.md" "Experience Dashboard" "🏢 ENTERPRISE & PRODUCTS"
add_context_file "./products/intelligence/lukhas_context.md" "Intelligence Systems" "🏢 ENTERPRISE & PRODUCTS"
add_context_file "./products/intelligence/lens/lukhas_context.md" "Intelligence Lens" "🏢 ENTERPRISE & PRODUCTS"
add_context_file "./products/intelligence/dast/lukhas_context.md" "Intelligence DAST" "🏢 ENTERPRISE & PRODUCTS"

# Development Tools
add_context_file "./tools/lukhas_context.md" "Development Tools" "🛠️ DEVELOPMENT TOOLS"

# Add footer
echo "" >> "$TEMP_FILE"
echo "## 🎯 End of Context Pack" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"
echo "**Total Context Files:** 42" >> "$TEMP_FILE"
echo "**Generated:** $(date)" >> "$TEMP_FILE"
echo "**System:** LUKHAS AI Platform - Consciousness-Aware Development" >> "$TEMP_FILE"
echo "**Trinity Framework:** ⚛️ Identity • 🧠 Consciousness • 🛡️ Guardian" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"
echo "---" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"
echo "*This context pack contains the complete architectural understanding of the LUKHAS AI Platform. Use it to analyze, review, and provide recommendations for this consciousness-inspired AI development system.*" >> "$TEMP_FILE"

# Replace the original file
mv "$TEMP_FILE" "$PACK_FILE"

echo "✅ Context pack generated: $PACK_FILE"
echo "📊 File size: $(wc -c < "$PACK_FILE" | tr -d ' ') bytes"
echo "📄 Word count: $(wc -w < "$PACK_FILE" | tr -d ' ') words"
echo ""
echo "🚀 Ready for ChatGPT upload!"
