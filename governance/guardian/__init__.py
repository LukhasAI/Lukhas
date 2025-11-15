"""Bridge for governance.guardian package."""

from __future__ import annotations

try:
    from lukhas_website.lukhas.governance.guardian import get_guardian
except ImportError:
    try:
        from labs.governance.guardian import get_guardian
    except ImportError:
        # Fallback stub
        def get_guardian():
            """Fallback guardian stub"""
            class MockGuardian:
                enabled = True
                async def validate_request_async(self, request):
                    return {"approved": True, "reason": "Mock", "confidence": 0.95}
            return MockGuardian()

__all__ = ["get_guardian"]
