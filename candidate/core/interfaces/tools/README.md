# Lukhas Cognitive AI System Tools

This directory contains various tools and utilities for the Lukhas Cognitive system, organized by function.

## Directory Structure

```
tools/
├── cli/         # Command line interface tools
│   ├── command_registry.py    # Command registration and management
│   ├── lucasdream_cli.py     # Dream system CLI interface
│   └── speak.py              # Voice interface utilities
├── dao/         # Decentralized Autonomous Organization tools
│   ├── dao_propose.py        # DAO proposal management
│   └── dao_vote.py          # DAO voting system
├── dev/         # Development utilities
│   └── audit_shortcut.sh     # Quick audit tool
├── research/    # Research and dashboard tools
│   ├── dev_dashboard.py      # Developer dashboard
│   └── research_dashboard.py # Research metrics dashboard
└── security/    # Security and access control
    ├── access_matrix.json       # Access control definitions
    ├── secure_context_policy.json # Security policies
    └── session_logger.py        # Session logging utility

## Usage

### CLI Tools
- `command_registry.py`: Register and manage system commands
- `lucasdream_cli.py`: Interface with the dream system
- `speak.py`: Voice interface control

### DAO Tools
- `dao_propose.py`: Create and manage proposals
- `dao_vote.py`: Vote on proposals

### Development Tools
- `audit_shortcut.sh`: Quick system audit utility

### Research Tools
- `dev_dashboard.py`: Development metrics and monitoring
- `research_dashboard.py`: Research progress tracking

### Security Tools
- `session_logger.py`: Track and log system sessions
- `secure_context_policy.json`: Security policy definitions
- `access_matrix.json`: Access control configuration

## Integration with Test Suite

Tools are covered by the test suite configured in jest.config.integration.ts. Run tests with:
\`\`\`bash
npm test
\`\`\`
