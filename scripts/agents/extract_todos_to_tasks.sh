#!/bin/bash

# 🎯 LUKHAS TODO to Agent Task Converter
# Extracts TODOs from codebase and creates agent-ready tasks

echo "🧠 LUKHAS AI TODO → Agent Task Extraction System"
echo "⚛️🧠🛡️ Converting scattered TODOs into consciousness-aware agent tasks..."

# Create results directory
mkdir -p .claude/tasks/generated/todos/

# Extract TODO items with context
echo "🔍 Scanning codebase for TODO items..."

# Generate TODO analysis
grep -r "TODO:" . \
  --exclude-dir=.git \
  --exclude-dir=__pycache__ \
  --exclude-dir=.venv \
  --exclude-dir=node_modules \
  --include="*.py" \
  --include="*.md" \
  --include="*.yaml" \
  --include="*.json" \
  -n -H | while IFS=: read -r file line content; do

  # Extract module name from file path
  module=$(echo "$file" | cut -d'/' -f2-3 | sed 's/\//./g')

  # Generate unique task ID
  task_id="LUKHAS-TODO-$(echo "$file$line" | md5sum | cut -c1-8 | tr '[:lower:]' '[:upper:]')"

  # Determine Trinity alignment based on module
  if [[ "$file" == *"governance"* ]] || [[ "$file" == *"ethics"* ]] || [[ "$file" == *"guardian"* ]]; then
    trinity_primary="guardian"
    trinity_score_guardian=1.0
    trinity_score_consciousness=0.3
    trinity_score_identity=0.2
  elif [[ "$file" == *"consciousness"* ]] || [[ "$file" == *"vivox"* ]] || [[ "$file" == *"memory"* ]]; then
    trinity_primary="consciousness"
    trinity_score_consciousness=1.0
    trinity_score_identity=0.6
    trinity_score_guardian=0.4
  elif [[ "$file" == *"identity"* ]] || [[ "$file" == *"ΛID"* ]]; then
    trinity_primary="identity"
    trinity_score_identity=1.0
    trinity_score_consciousness=0.5
    trinity_score_guardian=0.7
  else
    trinity_primary="consciousness"
    trinity_score_consciousness=0.6
    trinity_score_identity=0.4
    trinity_score_guardian=0.4
  fi

  # Assign primary agent based on module
  if [[ "$file" == *"test"* ]]; then
    primary_agent="consciousness-dev"
  elif [[ "$file" == *"governance"* ]] || [[ "$file" == *"guardian"* ]]; then
    primary_agent="guardian-engineer"
  elif [[ "$file" == *"docs"* ]] || [[ "$file" == *"README"* ]]; then
    primary_agent="docs-specialist"
  else
    primary_agent="consciousness-dev"
  fi

  # Determine priority based on context
  if [[ "$content" == *"CRITICAL"* ]] || [[ "$content" == *"URGENT"* ]] || [[ "$content" == *"FIXME"* ]]; then
    priority="P1_HIGH"
    consciousness_impact="FOUNDATIONAL"
  elif [[ "$content" == *"IMPORTANT"* ]] || [[ "$content" == *"BUG"* ]]; then
    priority="P2_MEDIUM"
    consciousness_impact="ENHANCEMENT"
  else
    priority="P3_LOW"
    consciousness_impact="OPTIMIZATION"
  fi

  # Clean TODO content
  todo_content=$(echo "$content" | sed 's/.*TODO:[ ]*//' | sed 's/^[ \t]*//' | sed 's/[ \t]*$//')

  # Generate task file
  cat > ".claude/tasks/generated/todos/${task_id}.json" << EOF
{
  "id": "$task_id",
  "title": "📝 TODO: $todo_content",
  "trinity_alignment": {
    "identity": $trinity_score_identity,
    "consciousness": $trinity_score_consciousness,
    "guardian": $trinity_score_guardian
  },
  "consciousness_impact": "$consciousness_impact",
  "priority": "$priority",
  "status": "EXTRACTED_FROM_CODE",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "source_extraction": {
    "file": "$file",
    "line": $line,
    "module": "$module",
    "context": "TODO item found in codebase"
  },
  "agent_assignment": {
    "primary": "$primary_agent",
    "collaboration_pattern": "TODO_RESOLUTION"
  },
  "context": {
    "module_dependencies": ["$module"],
    "consciousness_systems": ["todo_resolution"],
    "trinity_components": ["⚛️🧠🛡️ $trinity_primary"],
    "related_files": ["$file"]
  },
  "description": {
    "summary": "TODO item requiring resolution: $todo_content",
    "technical_details": "Found at $file:$line",
    "consciousness_impact": "Code completion enhances system consciousness and reliability"
  },
  "acceptance_criteria": [
    {
      "criterion": "TODO item resolved or properly documented",
      "validation_method": "Code review and testing",
      "trinity_compliance": true
    }
  ],
  "consciousness_metrics": {
    "awareness_enhancement": 0.2,
    "processing_efficiency": 0.3,
    "ethical_compliance": 0.8,
    "user_consciousness_impact": 0.4
  }
}
EOF

  echo "  ✅ Created: $task_id ($file:$line)"
done

echo ""
echo "🎯 TODO extraction complete!"
echo "📊 Generated agent tasks in: .claude/tasks/generated/todos/"
echo ""
echo "🚀 Next steps:"
echo "1. Review generated tasks"
echo "2. Assign to appropriate agents"
echo "3. Begin TODO resolution sprints"
echo ""
echo "⚛️🧠🛡️ Every TODO resolved strengthens consciousness evolution!"
