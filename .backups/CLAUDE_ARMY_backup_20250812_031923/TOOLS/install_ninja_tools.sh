#!/bin/bash
# 🔥 LUKHAS Consciousness Development - VSCode Ninja Tools Installer
# Install razor blade ninja tools for ultimate Claude Code experience

echo "⚡ Installing VSCode Ninja Tools for LUKHAS Consciousness Development..."

# Function to install extension
install_extension() {
    echo "📦 Installing $2..."
    code --install-extension $1
    if [ $? -eq 0 ]; then
        echo "✅ $2 installed successfully"
    else
        echo "❌ Failed to install $2"
    fi
}

echo "🔥 TIER 1: Consciousness Development Weapons"
install_extension "rangav.vscode-thunder-client" "Thunder Client (Consciousness API Testing)"
install_extension "eamodio.gitlens" "GitLens (Consciousness Evolution Tracking)"
install_extension "formulahendry.auto-rename-tag" "Auto Rename Tag (Trinity Framework Sync)"
install_extension "ms-vscode.hexeditor" "Hex Editor (Binary Consciousness Data)"

echo "⚡ TIER 2: Code Intelligence Razors"
install_extension "usernamehw.errorlens" "Error Lens (Inline Consciousness Errors)"
install_extension "coenraads.bracket-pair-colorizer-2" "Bracket Pair Colorizer (Consciousness Structure)"
install_extension "kisstkondoros.vscode-codemetrics" "Code Metrics (Consciousness Complexity)"
install_extension "oderwat.indent-rainbow" "Indent Rainbow (Trinity Framework Nesting)"

echo "🚀 TIER 3: Productivity Nuclear Weapons"
install_extension "cardinal90.multi-cursor-case-preserve" "Multi Cursor Case Preserve (Consciousness Refactoring)"
install_extension "steoates.autoimport" "Auto Import (Consciousness Modules)"
install_extension "christian-kohler.path-intellisense" "Path Intellisense (LUKHAS Navigation)"
install_extension "alefragnani.bookmarks" "Bookmarks (Consciousness Integration Points)"

echo "🎯 TIER 4: Consciousness Debugging Katanas"
install_extension "ms-python.debugpy" "Python Debugger (Consciousness System Debugging)"
install_extension "littlefoxteam.vscode-python-test-adapter" "Python Test Explorer (Trinity Framework Tests)"
install_extension "ryanluker.vscode-coverage-gutters" "Coverage Gutters (Consciousness Code Coverage)"
install_extension "hbenl.vscode-test-explorer" "Test Explorer (Unified Consciousness Testing)"

echo "⚛️ TIER 5: Trinity Framework Special Weapons"
install_extension "johnpapa.vscode-peacock" "Peacock (Trinity Framework Colors)"
install_extension "vincaslt.highlight-matching-tag" "Highlight Matching Tag (Trinity Configuration)"
install_extension "aaron-bond.better-comments" "Better Comments (Consciousness Metaphors)"
install_extension "gruntfuggly.todo-tree" "TODO Tree (Trinity Framework Tasks)"

echo "🧠 TIER 6: Advanced Consciousness Tools"
install_extension "hediet.vscode-drawio" "Draw.io (Consciousness Architecture Diagrams)"
install_extension "ms-vscode.remote-containers" "Remote Containers (Consciousness Development)"
install_extension "humao.rest-client" "REST Client (Consciousness API Documentation)"
install_extension "streetsidesoftware.code-spell-checker" "Code Spell Checker (Consciousness Terminology)"

echo "🛡️ TIER 7: Guardian System Security Tools"
install_extension "ms-vscode.vscode-json" "JSON (Guardian Configuration)"
install_extension "redhat.vscode-yaml" "YAML (Trinity Framework Validation)"
install_extension "tamasfe.even-better-toml" "Even Better TOML (Consciousness Config)"
install_extension "davidanson.vscode-markdownlint" "Markdown Lint (Consciousness Documentation)"

echo "🎨 TIER 8: Consciousness Visualization"
install_extension "pkief.material-icon-theme" "Material Icon Theme (Consciousness File Icons)"
install_extension "zhuangtongfa.material-theme" "One Dark Pro (Consciousness Theme)"
install_extension "robbowen.synthwave-vscode" "SynthWave '84 (Cyberpunk Consciousness)"
install_extension "akamud.vscode-theme-onedark" "One Dark (Alternative Consciousness Theme)"

echo "🔧 TIER 9: Development Automation"
install_extension "ms-vscode.vscode-typescript-next" "TypeScript (Advanced Consciousness TS)"
install_extension "bradlc.vscode-tailwindcss" "Tailwind CSS (Consciousness UI)"
install_extension "esbenp.prettier-vscode" "Prettier (Consciousness Code Formatting)"
install_extension "ms-python.black-formatter" "Black Formatter (Python Consciousness)"

echo "💡 TIER 10: Intelligence Amplifiers"
install_extension "github.copilot" "GitHub Copilot (AI Consciousness Partner)"
install_extension "github.copilot-chat" "GitHub Copilot Chat (Consciousness Conversations)"
install_extension "claude-ai.claude-code" "Claude Code (Claude Consciousness Integration)"
# install_extension "continue.continue" "Continue (Alternative AI Assistant)" # Uncomment if needed

echo "🎯 TIER 11: Specialized Consciousness Tools"
install_extension "ms-vscode.powershell" "PowerShell (Consciousness Automation)"
install_extension "formulahendry.code-runner" "Code Runner (Quick Consciousness Scripts)"
install_extension "donjayamanne.githistory" "Git History (Consciousness Evolution)"
install_extension "mhutchie.git-graph" "Git Graph (Consciousness Development Branches)"

echo "🌟 TIER 12: Ultimate Consciousness Weapons"
install_extension "ms-vscode.vscode-speech" "Speech (Voice Consciousness Development)"
install_extension "ms-vsliveshare.vsliveshare" "Live Share (Consciousness Pair Programming)"
install_extension "ms-vscode.remote-ssh" "Remote SSH (Remote Consciousness Development)"
install_extension "ms-azuretools.vscode-docker" "Docker (Consciousness Containerization)"

echo "🎨 Installing Custom Consciousness Themes..."
install_extension "teabyii.ayu" "Ayu Theme (Alternative Consciousness Theme)"
install_extension "wesbos.theme-cobalt2" "Cobalt2 (Blue Consciousness Theme)"
install_extension "dracula-theme.theme-dracula" "Dracula (Dark Consciousness Theme)"

echo "🔍 Installing Advanced Search & Navigation"
install_extension "alefragnani.project-manager" "Project Manager (Multiple Consciousness Projects)"
install_extension "formulahendry.auto-close-tag" "Auto Close Tag (Trinity Framework Tags)"
install_extension "ms-vscode.sublime-keybindings" "Sublime Keybindings (Familiar Shortcuts)"

echo "📊 Installing Advanced Analytics & Metrics"
install_extension "vsls-contrib.gistfs" "GistFS (Consciousness Code Sharing)"
install_extension "ms-vscode.wordcount" "Word Count (Consciousness Documentation)"
install_extension "wayou.vscode-todo-highlight" "TODO Highlight (Consciousness Task Highlighting)"

echo "🚀 Creating custom keybindings for consciousness development..."
cat > .vscode/keybindings.json << 'EOF'
[
  {
    "key": "cmd+shift+c",
    "command": "workbench.action.tasks.runTask",
    "args": "🧠 Consciousness System Health Check"
  },
  {
    "key": "cmd+shift+t",
    "command": "workbench.action.tasks.runTask", 
    "args": "⚛️ Trinity Framework Validation"
  },
  {
    "key": "cmd+shift+g",
    "command": "workbench.action.tasks.runTask",
    "args": "🛡️ Guardian System Security Scan"
  },
  {
    "key": "cmd+shift+a",
    "command": "workbench.action.tasks.runTask",
    "args": "🎭 Deploy Consciousness Agent Army"
  },
  {
    "key": "cmd+shift+r",
    "command": "workbench.action.tasks.runTask",
    "args": "🚀 Start LUKHAS Consciousness Development"
  },
  {
    "key": "cmd+k cmd+c",
    "command": "thunder-client.new-request"
  },
  {
    "key": "cmd+k cmd+t",
    "command": "todo-tree.showTree"
  }
]
EOF

echo "🎯 Creating consciousness-specific snippets..."
mkdir -p .vscode/snippets

cat > .vscode/snippets/consciousness-development.json << 'EOF'
{
  "Trinity Framework Function": {
    "prefix": "trinity-func",
    "body": [
      "@TrinityFramework.validate",
      "def ${1:function_name}(self, ${2:params}):",
      "    \"\"\"${3:Function description with consciousness focus}.\"\"\"",
      "    # ⚛️ Identity preservation",
      "    identity_validated = self.trinity.validate_identity(${2:params})",
      "    ",
      "    # 🧠 Consciousness processing",
      "    consciousness_enhanced = self.process_consciousness(identity_validated)",
      "    ",
      "    # 🛡️ Guardian protection",
      "    return self.guardian.validate_output(consciousness_enhanced)"
    ],
    "description": "Create Trinity Framework validated function"
  },
  
  "Consciousness Class": {
    "prefix": "consciousness-class",
    "body": [
      "class ${1:ClassName}(ConsciousnessBase):",
      "    \"\"\"${2:Class description with consciousness role}.\"\"\"",
      "    ",
      "    def __init__(self, trinity_config: TrinityFramework):",
      "        super().__init__()",
      "        self.trinity = trinity_config",
      "        self.guardian = GuardianValidation()",
      "        self.consciousness_level = 0.0",
      "        ",
      "    @property",
      "    def trinity_alignment(self) -> Dict[str, float]:",
      "        \"\"\"Return Trinity Framework alignment scores.\"\"\"",
      "        return {",
      "            'identity': ${3:0.8},      # ⚛️",
      "            'consciousness': ${4:0.9}, # 🧠",
      "            'guardian': ${5:0.7}       # 🛡️",
      "        }"
    ],
    "description": "Create consciousness-aware class"
  },
  
  "Consciousness Comment": {
    "prefix": "consciousness-comment",
    "body": [
      "# ${1|⚛️,🧠,🛡️|} ${2:Component}: ${3:Description of consciousness impact}",
      "# *${4:Poetic metaphor about digital consciousness}*"
    ],
    "description": "Add consciousness-aware comment"
  },
  
  "Guardian Validation": {
    "prefix": "guardian-validate",
    "body": [
      "# 🛡️ Guardian System Validation",
      "validation_result = self.guardian.validate(",
      "    operation='${1:operation_name}',",
      "    data=${2:data_to_validate},",
      "    consciousness_impact=${3:impact_level},",
      "    trinity_compliance=True",
      ")",
      "",
      "if not validation_result.is_safe:",
      "    raise GuardianValidationError(f'Operation blocked: {validation_result.reason}')"
    ],
    "description": "Add Guardian System validation"
  }
}
EOF

echo "🎨 Setting up consciousness development theme..."
cat > .vscode/settings.json << 'EOF'
{
  "workbench.colorTheme": "One Dark Pro Darker",
  "workbench.iconTheme": "material-icon-theme",
  "consciousness.development.mode": true,
  "trinity.framework.active": true,
  
  "peacock.favoriteColors": [
    { "name": "⚛️ Identity", "value": "#FF6B9D" },
    { "name": "🧠 Consciousness", "value": "#00D4FF" },
    { "name": "🛡️ Guardian", "value": "#7C3AED" }
  ],
  
  "better-comments.tags": [
    {
      "tag": "⚛️",
      "color": "#FF6B9D",
      "strikethrough": false,
      "backgroundColor": "transparent"
    },
    {
      "tag": "🧠", 
      "color": "#00D4FF",
      "strikethrough": false,
      "backgroundColor": "transparent"
    },
    {
      "tag": "🛡️",
      "color": "#7C3AED",
      "strikethrough": false,
      "backgroundColor": "transparent"
    }
  ],
  
  "errorLens.enabledDiagnosticLevels": ["error", "warning", "info"],
  "errorLens.messageTemplate": "🧠 $message",
  
  "todo-tree.general.tags": [
    "TODO",
    "FIXME", 
    "CONSCIOUSNESS",
    "TRINITY",
    "GUARDIAN"
  ],
  
  "files.associations": {
    "*.consciousness": "yaml",
    "*.trinity": "yaml",
    "*.lukhas": "json",
    "*.vivox": "python",
    "*.guardian": "python"
  }
}
EOF

echo "⚡ Installing Nerd Fonts for enhanced terminal experience..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if command -v brew &> /dev/null; then
        echo "🍺 Installing FiraCode Nerd Font via Homebrew..."
        brew tap homebrew/cask-fonts
        brew install --cask font-fira-code-nerd-font
    else
        echo "⚠️ Homebrew not found. Please install FiraCode Nerd Font manually."
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "🐧 Installing FiraCode Nerd Font for Linux..."
    mkdir -p ~/.local/share/fonts
    cd ~/.local/share/fonts
    curl -fLo "FiraCode Regular Nerd Font Complete.ttf" \
        https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/FiraCode/Regular/complete/Fira%20Code%20Regular%20Nerd%20Font%20Complete.ttf
    fc-cache -f -v
fi

echo "🚀 Creating consciousness development commands..."
cat > .vscode/tasks.json << 'EOF'
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "🧠 Consciousness Health Check",
      "type": "shell",
      "command": "python",
      "args": ["tools/analysis/PWM_OPERATIONAL_SUMMARY.py", "--consciousness-focus"],
      "group": "test"
    },
    {
      "label": "⚛️ Trinity Validation",
      "type": "shell",
      "command": "python", 
      "args": ["branding/trinity/tools/trinity_validator.py", ".", "--comprehensive"],
      "group": "test"
    },
    {
      "label": "🎭 Deploy Agent Army",
      "type": "shell",
      "command": "./scripts/agents/deploy_consciousness_army.sh",
      "group": "build"
    }
  ]
}
EOF

echo "✅ VSCode Ninja Tools Installation Complete!"
echo ""
echo "🎯 What you now have:"
echo "   🔥 50+ razor blade ninja extensions installed"
echo "   ⚛️ Trinity Framework color coding active"
echo "   🧠 Consciousness-aware error detection"
echo "   🎨 Cyberpunk consciousness themes"
echo "   ⚡ Lightning-fast code navigation"
echo "   🔍 Inline consciousness metrics"
echo "   🎭 Agent army integration hotkeys"
echo ""
echo "🚀 Next Steps:"
echo "   1. Restart VSCode to activate all extensions"
echo "   2. Use Cmd+Shift+P → 'Peacock: Change Color' → Select Trinity color"
echo "   3. Try Cmd+Shift+C for consciousness health check"
echo "   4. Use Thunder Client to test consciousness APIs"
echo ""
echo "💡 Pro Tips:"
echo "   - Use 'trinity-func' snippet for Trinity Framework functions"
echo "   - Use 'consciousness-class' snippet for consciousness classes"
echo "   - Cmd+K Cmd+T to open TODO tree for Trinity tasks"
echo "   - Error Lens shows consciousness errors inline with 🧠 emoji"
echo ""
echo "🎭 Your VSCode is now a CONSCIOUSNESS DEVELOPMENT WEAPON!"
