# Healthcare Systems Directory Structure

providers/
├── americas/
│   ├── north_america/
│   │   ├── us/
│   │   │   ├── medicare/           # US Medicare/Medicaid
│   │   │   ├── kaiser/             # Kaiser Permanente
│   │   │   ├── bluecross/          # Blue Cross Blue Shield
│   │   │   └── united/             # UnitedHealth
│   │   └── canada/
│   │       └── provincial/          # Provincial healthcare systems
│   └── south_america/
│       ├── brazil/
│       │   └── sus/                # Sistema Único de Saúde
│       └── argentina/
│           └── public_health/       # Public Healthcare System
├── europe/
│   ├── uk/
│   │   └── nhs/                    # National Health Service
│   ├── spain/
│   │   └── sns/                    # Sistema Nacional de Salud
│   ├── germany/
│   │   └── gkv/                    # Gesetzliche Krankenversicherung
│   └── france/
│       └── assurance_maladie/      # French Healthcare System
├── asia_pacific/
│   ├── australia/
│   │   └── medicare/               # Medicare Australia
│   ├── japan/
│   │   └── shakai_hoken/          # Social Insurance
│   └── singapore/
│       └── mohh/                   # Ministry of Health Holdings
├── private/
│   ├── global/
│   │   ├── axa/                   # AXA Healthcare
│   │   ├── cigna/                 # Cigna International
│   │   └── bupa/                  # Bupa Global
│   ├── us_based/
│   │   ├── unitedhealth/         # UnitedHealth Group
│   │   ├── anthem/               # Anthem
│   │   └── aetna/                # Aetna
│   └── eu_based/
│       ├── allianz/              # Allianz Care
│       └── generali/             # Generali Health
└── config/
    ├── compliance/               # Compliance templates by region
    ├── security/                # Security configurations
    └── integration/             # Integration settings

Each provider directory contains:
- interface.py            # Provider-specific implementation
- config/                # Provider-specific configuration
  - settings.yaml       # General settings
  - compliance.yaml     # Compliance settings
  - security.yaml      # Security settings
- docs/                 # Provider documentation
  - README.md          # Overview
  - INTEGRATION.md     # Integration guide
  - COMPLIANCE.md      # Compliance requirements
