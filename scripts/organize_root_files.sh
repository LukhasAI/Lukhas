#!/bin/bash

# Root Files Organization Script
# Moves files from root to appropriate directories
# Safe to run multiple times - uses mv with 2>/dev/null

echo "🗂️ Organizing Root Directory Files..."
echo "="
echo

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p docs/{setup,architecture,roadmap,planning,reports,integration,openai,executive,releases,api,collaboration}
mkdir -p scripts/{integration,testing,utilities}
mkdir -p tests/{integration,tools}
mkdir -p backups
mkdir -p out

# Move documentation files
echo "📄 Moving documentation files..."

# Collaboration docs
mv AI_COLLABORATION_ACKNOWLEDGMENT.md docs/collaboration/ 2>/dev/null && echo "  ✓ AI_COLLABORATION_ACKNOWLEDGMENT.md → docs/collaboration/"

# Setup docs
mv AI_INTEGRATION_SETUP.md docs/setup/ 2>/dev/null && echo "  ✓ AI_INTEGRATION_SETUP.md → docs/setup/"
mv AI_SETUP_CURRENT.md docs/setup/ 2>/dev/null && echo "  ✓ AI_SETUP_CURRENT.md → docs/setup/"

# Architecture docs
mv README_NEXT_GEN.md docs/architecture/ 2>/dev/null && echo "  ✓ README_NEXT_GEN.md → docs/architecture/"
mv README_TRINITY.md docs/architecture/ 2>/dev/null && echo "  ✓ README_TRINITY.md → docs/architecture/"

# Executive docs
mv CEO_EXECUTIVE_REVIEW_AUGUST_2025.md docs/executive/ 2>/dev/null && echo "  ✓ CEO_EXECUTIVE_REVIEW_AUGUST_2025.md → docs/executive/"
mv INVESTOR_OVERVIEW.md docs/executive/ 2>/dev/null && echo "  ✓ INVESTOR_OVERVIEW.md → docs/executive/"
mv PROFESSIONAL_DEVELOPMENT_ROADMAP.md docs/executive/ 2>/dev/null && echo "  ✓ PROFESSIONAL_DEVELOPMENT_ROADMAP.md → docs/executive/"

# Roadmap docs
mv LUKHAS_UNIVERSAL_LANGUAGE_ROADMAP.md docs/roadmap/ 2>/dev/null && echo "  ✓ LUKHAS_UNIVERSAL_LANGUAGE_ROADMAP.md → docs/roadmap/"
mv OPENAI_LUKHAS_2026-2030_COLLABORATION_VISION.md docs/roadmap/ 2>/dev/null && echo "  ✓ OPENAI_LUKHAS_2026-2030_COLLABORATION_VISION.md → docs/roadmap/"
mv OPENAI_LUKHAS_2030_COLLABORATION_VISION.md docs/roadmap/ 2>/dev/null && echo "  ✓ OPENAI_LUKHAS_2030_COLLABORATION_VISION.md → docs/roadmap/"
mv ROADMAP_OPENAI_ALIGNMENT.md docs/roadmap/ 2>/dev/null && echo "  ✓ ROADMAP_OPENAI_ALIGNMENT.md → docs/roadmap/"
mv UNIVERSAL_SYMBOL_COMMUNICATION_BLUEPRINT.md docs/roadmap/ 2>/dev/null && echo "  ✓ UNIVERSAL_SYMBOL_COMMUNICATION_BLUEPRINT.md → docs/roadmap/"
mv UNIVERSAL_SYMBOL_TRINITY_BLUEPRINT.md docs/roadmap/ 2>/dev/null && echo "  ✓ UNIVERSAL_SYMBOL_TRINITY_BLUEPRINT.md → docs/roadmap/"

# Planning docs
mv LUKHAS_ACTION_PLANS.md docs/planning/ 2>/dev/null && echo "  ✓ LUKHAS_ACTION_PLANS.md → docs/planning/"
mv HIDDEN_POWER_ACTION_PLAN.md docs/planning/ 2>/dev/null && echo "  ✓ HIDDEN_POWER_ACTION_PLAN.md → docs/planning/"
mv IMMEDIATE_ACTIONS.md docs/planning/ 2>/dev/null && echo "  ✓ IMMEDIATE_ACTIONS.md → docs/planning/"
mv IMMEDIATE_NEXT_STEPS.md docs/planning/ 2>/dev/null && echo "  ✓ IMMEDIATE_NEXT_STEPS.md → docs/planning/"
mv TASKS_OPENAI_ALIGNMENT.md docs/planning/ 2>/dev/null && echo "  ✓ TASKS_OPENAI_ALIGNMENT.md → docs/planning/"
mv CLAUDE_CODE_TASKS.md docs/planning/ 2>/dev/null && echo "  ✓ CLAUDE_CODE_TASKS.md → docs/planning/"
mv .copilot_tasks.md docs/planning/ 2>/dev/null && echo "  ✓ .copilot_tasks.md → docs/planning/"

# Reports
mv COMPREHENSIVE_STRESS_TEST_RESULTS_AUG_7_2025.md docs/reports/ 2>/dev/null && echo "  ✓ COMPREHENSIVE_STRESS_TEST_RESULTS_AUG_7_2025.md → docs/reports/"
mv CRITICAL_FIX_NEEDED_model_communication_engine.md docs/reports/ 2>/dev/null && echo "  ✓ CRITICAL_FIX_NEEDED_model_communication_engine.md → docs/reports/"
mv CRITICAL_GAPS_IMPROVEMENT_PLAN.md docs/reports/ 2>/dev/null && echo "  ✓ CRITICAL_GAPS_IMPROVEMENT_PLAN.md → docs/reports/"
mv ETHICAL_ALIGNMENT_BREAKTHROUGH_ANALYSIS.md docs/reports/ 2>/dev/null && echo "  ✓ ETHICAL_ALIGNMENT_BREAKTHROUGH_ANALYSIS.md → docs/reports/"
mv VALIDATION_REPORT.md docs/reports/ 2>/dev/null && echo "  ✓ VALIDATION_REPORT.md → docs/reports/"

# OpenAI docs
mv FINAL_OPENAI_STATUS.md docs/openai/ 2>/dev/null && echo "  ✓ FINAL_OPENAI_STATUS.md → docs/openai/"
mv INTEGRATION_TEST_CHECKLIST.md docs/openai/ 2>/dev/null && echo "  ✓ INTEGRATION_TEST_CHECKLIST.md → docs/openai/"
mv OPENAI_INPUT_OUTPUT_REPORT.md docs/openai/ 2>/dev/null && echo "  ✓ OPENAI_INPUT_OUTPUT_REPORT.md → docs/openai/"
mv PRODUCTION_TEST_REPORT.md docs/openai/ 2>/dev/null && echo "  ✓ PRODUCTION_TEST_REPORT.md → docs/openai/"
mv TOOL_EXECUTOR_IMPLEMENTATION.md docs/openai/ 2>/dev/null && echo "  ✓ TOOL_EXECUTOR_IMPLEMENTATION.md → docs/openai/"
mv TOOL_INTEGRATION_COMPLETE.md docs/openai/ 2>/dev/null && echo "  ✓ TOOL_INTEGRATION_COMPLETE.md → docs/openai/"
mv GPT5_AUDITS_LUKHAS_PWM.md docs/openai/ 2>/dev/null && echo "  ✓ GPT5_AUDITS_LUKHAS_PWM.md → docs/openai/"
mv IMPLEMENTATION_SUMMARY.md docs/openai/ 2>/dev/null && echo "  ✓ IMPLEMENTATION_SUMMARY.md → docs/openai/"

# Release docs
mv PR1_COMPLETE.md docs/releases/ 2>/dev/null && echo "  ✓ PR1_COMPLETE.md → docs/releases/"
mv PR2_COMPLETE.md docs/releases/ 2>/dev/null && echo "  ✓ PR2_COMPLETE.md → docs/releases/"
mv SPRINT_COMPLETE.md docs/releases/ 2>/dev/null && echo "  ✓ SPRINT_COMPLETE.md → docs/releases/"

# Integration docs
mv LUKHAS_DREAM_API_COLLABORATION.md docs/integration/ 2>/dev/null && echo "  ✓ LUKHAS_DREAM_API_COLLABORATION.md → docs/integration/"
mv LUKHAS_AI_QUICK_REFERENCE.md docs/integration/ 2>/dev/null && echo "  ✓ LUKHAS_AI_QUICK_REFERENCE.md → docs/integration/"

# General docs
mv AUTHORS.md docs/ 2>/dev/null && echo "  ✓ AUTHORS.md → docs/"
mv INFO_README.md docs/ 2>/dev/null && echo "  ✓ INFO_README.md → docs/"
mv QUICK_START.md docs/ 2>/dev/null && echo "  ✓ QUICK_START.md → docs/"
mv PROVENANCE.yaml docs/ 2>/dev/null && echo "  ✓ PROVENANCE.yaml → docs/"

echo
echo "🐍 Moving Python scripts..."

# Testing scripts
mv launch_readiness_check.py scripts/testing/ 2>/dev/null && echo "  ✓ launch_readiness_check.py → scripts/testing/"
mv live_integration_test.py scripts/testing/ 2>/dev/null && echo "  ✓ live_integration_test.py → scripts/testing/"
mv live_openai_smoke_test.py scripts/testing/ 2>/dev/null && echo "  ✓ live_openai_smoke_test.py → scripts/testing/"
mv mock_integration_demo.py scripts/testing/ 2>/dev/null && echo "  ✓ mock_integration_demo.py → scripts/testing/"
mv production_test_mock.py scripts/testing/ 2>/dev/null && echo "  ✓ production_test_mock.py → scripts/testing/"
mv production_test_suite.py scripts/testing/ 2>/dev/null && echo "  ✓ production_test_suite.py → scripts/testing/"
mv smoke_check.py scripts/testing/ 2>/dev/null && echo "  ✓ smoke_check.py → scripts/testing/"

# Integration scripts
mv demo_tool_gating.py scripts/integration/ 2>/dev/null && echo "  ✓ demo_tool_gating.py → scripts/integration/"
mv demo_tool_governance.py scripts/integration/ 2>/dev/null && echo "  ✓ demo_tool_governance.py → scripts/integration/"
mv governance_extended.py scripts/integration/ 2>/dev/null && echo "  ✓ governance_extended.py → scripts/integration/"

# Utility scripts
mv IMMEDIATE_CONFIG_ANALYSIS.py scripts/utilities/ 2>/dev/null && echo "  ✓ IMMEDIATE_CONFIG_ANALYSIS.py → scripts/utilities/"

echo
echo "🔧 Moving shell scripts..."
mv format_code.sh scripts/utilities/ 2>/dev/null && echo "  ✓ format_code.sh → scripts/utilities/"
mv setup_test_environment.sh scripts/utilities/ 2>/dev/null && echo "  ✓ setup_test_environment.sh → scripts/utilities/"
mv vs_code_reset_commands.sh scripts/utilities/ 2>/dev/null && echo "  ✓ vs_code_reset_commands.sh → scripts/utilities/"

echo
echo "🧪 Moving test files..."
mv test_complete_openai_flow.py tests/integration/ 2>/dev/null && echo "  ✓ test_complete_openai_flow.py → tests/integration/"
mv test_final_integration.py tests/integration/ 2>/dev/null && echo "  ✓ test_final_integration.py → tests/integration/"
mv test_lukhas_ai_setup.py tests/integration/ 2>/dev/null && echo "  ✓ test_lukhas_ai_setup.py → tests/integration/"
mv test_openai_connection.py tests/integration/ 2>/dev/null && echo "  ✓ test_openai_connection.py → tests/integration/"
mv test_openai_responses.py tests/integration/ 2>/dev/null && echo "  ✓ test_openai_responses.py → tests/integration/"
mv test_tool_analytics.py tests/tools/ 2>/dev/null && echo "  ✓ test_tool_analytics.py → tests/tools/"
mv test_tool_executor.py tests/tools/ 2>/dev/null && echo "  ✓ test_tool_executor.py → tests/tools/"
mv test_tool_integration.py tests/tools/ 2>/dev/null && echo "  ✓ test_tool_integration.py → tests/tools/"
mv test_tool_integration_complete.py tests/tools/ 2>/dev/null && echo "  ✓ test_tool_integration_complete.py → tests/tools/"

echo
echo "📁 Moving other files..."
mv openapi.json out/ 2>/dev/null && echo "  ✓ openapi.json → out/"
mv intelligence_engine.py.bkup backups/ 2>/dev/null && echo "  ✓ intelligence_engine.py.bkup → backups/"

echo
echo "🧹 Cleaning up temporary files..."
rm -f .DS_Store && echo "  ✓ Removed .DS_Store"
rm -f claude_context.txt && echo "  ✓ Removed claude_context.txt"
rm -f .coverage && echo "  ✓ Removed .coverage"

echo
echo "="
echo "✅ Root directory organization complete!"
echo
echo "📊 Summary:"
echo "  • Documentation organized in /docs/"
echo "  • Scripts organized in /scripts/"
echo "  • Tests organized in /tests/"
echo "  • Temporary files cleaned up"
echo
echo "Files remaining in root (as intended):"
ls -1 *.* 2>/dev/null | head -20

echo
echo "💡 Tip: Run 'git status' to review changes before committing"