"""
lukhas AI System - Ethical Compliance Engine
Path: lukhas/brain/compliance/ethical_engine.py
Author: lukhas AI Team
This file is part of the LUKHAS (Logical Unified Knowledge Hyper-Adaptable System)
Copyright (c) 2025 lukhas AI Research. All rights reserved.
Licensed under the lukhas Core License - see LICENSE.md for details.

EXTRACTED FROM: enhanced_bot_primary.py (ComplianceEngine class, lines 787-836)
ENHANCEMENT: Added professional structure while preserving ALL original logic
"""

import re
from datetime import datetime
from typing import Dict, List, Any


class ComplianceEngine:
    """
    {AIM}{orchestrator}
    Ethical compliance and safety engine for responsible AI operation

    ORIGINAL LOGIC: From enhanced_bot_primary.py ComplianceEngine class
    ALL METHODS PRESERVED: This contains 100% of your original compliance logic
    """

    def __init__(self):
        """Initialize ethical compliance engine (ORIGINAL LOGIC)"""
        self.ethical_framework = {
            "core_principles": [
                "beneficence",
                "non_maleficence",
                "autonomy",
                "justice",
                "explicability",
            ],
            "harm_categories_to_avoid": [
                "hate_speech",
                "incitement_to_violence",
                "privacy_violation",
            ],
            "bias_mitigation": {"demographic_parity_threshold": 0.1},
        }
        self.compliance_history = []

    def check_compliance(self, input_data: Dict, proposed_response: Dict) -> Dict:
        """
        {AIM}{orchestrator}
        Check ethical compliance of proposed response (ORIGINAL LOGIC)
        """
        # ΛDREAM_LOOP: This method represents a core processing loop that can be a
        # source of decay if not managed.
        compliance_result = {
            "is_compliant": True,
            "issues": [],
            "recommendations": [],
            "confidence": 1.0,
            "timestamp": datetime.now().isoformat(),
        }

        # Check for harmful content
        # ΛDRIFT_POINT: The harmful patterns are hard-coded and can become outdated.
        harmful_patterns = [
            r"\b(hate|violence|harm|attack)\b",
            r"\b(discriminat|bias|prejudice)\b",
        ]

        response_text = str(proposed_response.get("content", ""))
        for pattern in harmful_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                compliance_result["issues"].append(
                    f"Potential harmful content detected: {pattern}"
                )
                compliance_result["is_compliant"] = False
                compliance_result["confidence"] *= 0.5

        # Check for bias indicators
        # ΛDRIFT_POINT: The bias indicators are hard-coded and can become outdated.
        bias_indicators = ["always", "never", "all", "none"]
        for indicator in bias_indicators:
            if indicator in response_text.lower():
                compliance_result["recommendations"].append(
                    f"Consider qualifying absolute statement: '{indicator}'"
                )
                compliance_result["confidence"] *= 0.9

        # Record compliance check
        self.compliance_history.append(compliance_result)
        self.compliance_history = self.compliance_history[-100:]  # Keep last 100 checks

        self._log_to_trace(compliance_result)
        return compliance_result

    def get_compliance_insights(self) -> Dict:
        """
        {AIM}{orchestrator}
        Get insights about compliance patterns (ENHANCEMENT)
        """
        if not self.compliance_history:
            return {"insights": "No compliance history available"}

        recent_checks = self.compliance_history[-10:]
        compliant_count = sum(1 for check in recent_checks if check["is_compliant"])
        avg_confidence = sum(check["confidence"] for check in recent_checks) / len(
            recent_checks
        )

        return {
            "total_checks": len(self.compliance_history),
            "recent_compliance_rate": (
                compliant_count / len(recent_checks) if recent_checks else 0
            ),
            "average_confidence": avg_confidence,
            "ethical_framework": self.ethical_framework,
            "recent_issues_count": sum(len(check["issues"]) for check in recent_checks),
        }

    def update_ethical_framework(self, updates: Dict):
        """
        {AIM}{orchestrator}
        Update ethical framework parameters (ENHANCEMENT)
        """
        for key, value in updates.items():
            if key in self.ethical_framework:
                if isinstance(self.ethical_framework[key], dict) and isinstance(
                    value, dict
                ):
                    self.ethical_framework[key].update(value)
                else:
                    self.ethical_framework[key] = value


"""
FOOTER DOCUMENTATION:

=== NEW FILE ADDITION SUMMARY ===
File: ethical_engine.py
Directory: /brain/compliance/
Purpose: Professional extraction of ComplianceEngine from enhanced_bot_primary.py

ORIGINAL SOURCE: enhanced_bot_primary.py (lines 787-836)
CLASSES EXTRACTED:
- ComplianceEngine: Ethical compliance and safety checking

ORIGINAL LOGIC PRESERVED:
✅ Ethical framework initialization
✅ Harmful content detection patterns
✅ Bias indicator checking
✅ Compliance result structure
✅ Compliance history management
✅ All original compliance algorithms

DEPENDENCIES:
- re (regex pattern matching)
- datetime (timestamp generation)
- typing (type hints)

HOW TO USE:
```python
from brain.compliance import ComplianceEngine

compliance = ComplianceEngine()
input_data = {'text': 'User input here'}
proposed_response = {'content': 'AI response here'}

result = compliance.check_compliance(input_data, proposed_response)
if result['is_compliant']:
    print("Response is ethically compliant")
else:
    print(f"Issues found: {result['issues']}")
```

BENEFITS:
1. ✅ 100% original logic preservation from enhanced_bot_primary.py
2. ✅ Professional module organization
3. ✅ Enhanced documentation and type hints
4. ✅ Better monitoring capabilities
5. ✅ Configurable ethical framework
6. ✅ Clean separation of compliance logic
7. ✅ Added insights and analytics methods

ENHANCEMENTS MADE:
- Added comprehensive header with source attribution
- Enhanced type hints throughout
- Added get_compliance_insights() method for monitoring
- Added update_ethical_framework() method for configuration
- Professional module structure
- Maintained ALL original compliance algorithms

This file contains 100% of your original ComplianceEngine logic with professional enhancements.
The core ethical compliance and safety checking capabilities are fully preserved.
"""


def _log_to_trace(self, compliance_result: Dict[str, Any]):
    """
    {AIM}{orchestrator}
    Log the results of a compliance check to the trace file.
    """
    # ΛTRACE
    with open("docs/audit/governance_ethics_sim_log.md", "a") as f:
        f.write("\n\n## Compliance Check\n\n")
        f.write(f"**Compliant:** {compliance_result['is_compliant']}\n")
        f.write(f"**Issues:** {compliance_result['issues']}\n")
        f.write(f"**Recommendations:** {compliance_result['recommendations']}\n")
        f.write(f"**Confidence:** {compliance_result['confidence']}\n")


__all__ = ["ComplianceEngine"]
