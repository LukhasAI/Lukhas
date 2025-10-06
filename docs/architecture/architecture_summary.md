---
status: wip
type: documentation
---
# LUKHAS Architecture Analysis Report

Generated: 2025-09-10 12:44:35

## System Overview
- **Total Modules**: 113
- **Total Dependencies**: 17
- **Average Dependencies per Module**: 0.15
- **Cross-Lane Dependencies**: 9

## Distribution by Layer
- **Application**: 103 modules (91.2%)\n- **Foundational**: 3 modules (2.7%)\n- **Infrastructure**: 6 modules (5.3%)\n- **Interface**: 1 modules (0.9%)\n\n## Distribution by Tier\n- **Tier 1**: 10 modules (8.8%)\n- **Tier 2**: 81 modules (71.7%)\n- **Tier 3**: 22 modules (19.5%)\n\n## Distribution by Lane\n- **branding**: 22 modules (19.5%)\n- **candidate**: 29 modules (25.7%)\n- **lukhas**: 20 modules (17.7%)\n- **matriz**: 6 modules (5.3%)\n- **products**: 9 modules (8.0%)\n- **tools**: 27 modules (23.9%)\n\n## Highly Coupled Modules (Top 10)\n- **products.enterprise**: 5 dependencies\n- **lukhas.rl**: 4 dependencies\n- **candidate.governance**: 2 dependencies\n- **lukhas.emotion**: 2 dependencies\n- **products.security**: 2 dependencies\n- **candidate.core**: 1 dependencies\n- **lukhas.governance**: 1 dependencies\n\n## Cross-Lane Dependencies (9)\n- lukhas.security → candidate.governance\n- lukhas.emotion → candidate.core\n- lukhas.consciousness → products.enterprise\n- lukhas.memory → products.enterprise\n- candidate.consciousness → products.enterprise\n- candidate.memory → products.enterprise\n- candidate.governance → products.enterprise\n- lukhas.consciousness → products.security\n- lukhas.identity → products.security\n
## Recommendations
1. **Reduce Cross-Lane Dependencies**: Consider refactoring to minimize dependencies between lanes
2. **Monitor Highly Coupled Modules**: Review modules with excessive dependencies
3. **Layer Violations**: Ensure higher layers don't depend on lower layers inappropriately
4. **Module Consolidation**: Consider merging small, tightly coupled modules
