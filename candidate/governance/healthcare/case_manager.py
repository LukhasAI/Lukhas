"""
Case Manager for Healthcare Governance

Manages clinical cases, reviews, and consultations with support
for various EHR system integrations. Integrated with LUKHAS governance
and ethical oversight systems.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Optional

from ..common import GlyphIntegrationMixin

# Authentication and authorization imports
try:
    from ..identity.core.unified_auth_manager import UnifiedAuthManager
    from ..identity.lambda_id_auth import AuthTier

    AUTH_AVAILABLE = True
except ImportError:
    # Fallback for development/testing
    AUTH_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Authentication system not available, using development fallback")

from consent.service import ConsentService
from enterprise.compliance.data_protection_service import DataProtectionService

logger = logging.getLogger(__name__)


class CaseManager(GlyphIntegrationMixin):
    """
    Healthcare case management system with governance integration

    Manages clinical cases, provider reviews, and patient consultations
    while ensuring compliance with healthcare regulations and LUKHAS
    ethical standards.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize case manager with configuration"""
        super().__init__()
        self.config = config or {}
        self._init_authentication()
        self.consent_service = ConsentService()
        self.data_protection_service = DataProtectionService()
        asyncio.run(self.consent_service.initialize())
        asyncio.run(self.data_protection_service.initialize())
        self.cases = {}  # This will be replaced by a proper database
        logger.info("🏥 Healthcare CaseManager initialized")

    def _init_authentication(self):
        """Initialize authentication and authorization system"""
        if AUTH_AVAILABLE:
            self.auth_manager = UnifiedAuthManager()
            self.auth_enabled = True
            logger.info("🔐 Authentication system initialized")
        else:
            self.auth_manager = None
            self.auth_enabled = False
            logger.warning("⚠️  Running with authentication fallback - not for production")

    async def create_case(
        self,
        user_id: str,
        symptoms: list[str],
        ai_assessment: dict[str, Any],
        priority: str = "normal",
        consent_token: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Create a new clinical case with governance validation

        Args:
            user_id: ID of the user/patient
            symptoms: List of reported symptoms
            ai_assessment: Initial AI assessment
            priority: Case priority level
            consent_token: Patient consent verification token

        Returns:
            Created case details with governance metadata
        """
        try:
            # Validate consent
            consent_valid = await self.consent_service.verify_capability_token(
                consent_token, ["healthcare.case.create"]
            )
            if not consent_valid["valid"]:
                raise ValueError("Patient consent is not valid for case creation")

            # Perform ethical validation
            ethical_result = await self._validate_case_ethics(user_id, symptoms, ai_assessment)
            if not ethical_result["approved"]:
                raise ValueError(f"Ethical validation failed: {ethical_result['reason']}")

            case_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()

            case_data = {
                "symptoms": symptoms,
                "ai_assessment": ai_assessment,
            }

            encrypted_case_data, _ = await self.data_protection_service.protect_data(case_data, "pii_protection")

            case = {
                "case_id": case_id,
                "user_id": user_id,
                "priority": priority,
                "status": "pending_review",
                "created_at": timestamp,
                "updates": [],
                "encrypted_data": encrypted_case_data,
                "governance": {
                    "consent_grant_id": consent_valid["claims"]["grant_id"],
                    "ethical_approval": True,
                    "compliance_status": "validated",
                    "audit_trail": [
                        {
                            "action": "case_created",
                            "timestamp": timestamp,
                            "user": "system",
                            "details": {"priority": priority},
                        }
                    ],
                },
                "symbolic_pattern": ["🏥", "📋", "✅"],
            }

            self.cases[case_id] = case

            # Log case creation in governance audit trail
            await self._log_governance_action(case_id, "case_created", {"user_id": user_id, "priority": priority})

            logger.info(f"🏥 Case created: {case_id} for user {user_id}")
            return case

        except Exception as e:
            logger.error(f"Error creating case: {e!s}")
            raise

    async def get_provider_cases(
        self, provider_id: str, filters: Optional[dict[str, Any]] = None
    ) -> list[dict[str, Any]]:
        """
        Get cases for a specific provider with governance filtering

        Args:
            provider_id: ID of the healthcare provider
            filters: Optional filters for case selection

        Returns:
            List of matching cases with governance metadata
        """
        try:
            # Validate provider permissions
            if not await self._validate_provider_access(provider_id):
                raise ValueError("Provider access denied")

            filters = filters or {}
            cases = []

            for case in self.cases.values():
                if self._case_matches_filters(case, provider_id, filters):
                    # Decrypt case data
                    decrypted_data = await self.data_protection_service.unprotect_data(case["encrypted_data"])
                    case_copy = case.copy()
                    case_copy.update(decrypted_data)
                    del case_copy["encrypted_data"]

                    # Add governance metadata
                    case_copy["governance"]["access_granted_to"] = provider_id
                    cases.append(case_copy)

            # Sort by priority and creation time
            cases.sort(
                key=lambda x: (
                    x["priority"] == "urgent",
                    x["priority"] == "high",
                    x["created_at"],
                ),
                reverse=True,
            )

            await self._log_governance_action(
                f"provider_{provider_id}",
                "cases_accessed",
                {"case_count": len(cases), "filters": filters},
            )

            return cases

        except Exception as e:
            logger.error(f"Error retrieving provider cases: {e!s}")
            raise

    def _case_matches_filters(self, case: dict[str, Any], provider_id: str, filters: dict[str, Any]) -> bool:
        """Check if a case matches the given filters with governance rules"""
        # Check provider assignment or general access
        if not (case.get("assigned_provider") == provider_id or self._has_general_access(provider_id)):
            return False

        # Check status filter
        if "status" in filters and case["status"] != filters["status"]:
            return False

        # Check priority filter
        if "priority" in filters and case["priority"] != filters["priority"]:
            return False

        # Check date range
        if "date_from" in filters:
            case_date = datetime.fromisoformat(case["created_at"])
            if case_date < datetime.fromisoformat(filters["date_from"]):
                return False

        if "date_to" in filters:
            case_date = datetime.fromisoformat(case["created_at"])
            if case_date > datetime.fromisoformat(filters["date_to"]):
                return False

        # Check governance compliance
        return case.get("governance", {}).get("compliance_status") == "validated"

    async def update_case(self, case_id: str, update_data: dict[str, Any], provider_id: str) -> dict[str, Any]:
        """
        Update a case with provider review and governance validation

        Args:
            case_id: ID of the case
            update_data: Update information
            provider_id: ID of the provider making the update

        Returns:
            Updated case information
        """
        try:
            if case_id not in self.cases:
                raise ValueError(f"Case {case_id} not found")

            # Validate provider permissions for this case
            if not await self._validate_case_update_permission(case_id, provider_id):
                raise ValueError("Provider not authorized to update this case")

            case = self.cases[case_id]

            # Decrypt case data
            decrypted_data = await self.data_protection_service.unprotect_data(case["encrypted_data"])
            case.update(decrypted_data)

            timestamp = datetime.utcnow().isoformat()

            # Create update record with governance metadata
            update = {
                "update_id": str(uuid.uuid4()),
                "provider_id": provider_id,
                "timestamp": timestamp,
                "data": update_data,
                "governance": {"validated": True, "audit_logged": True},
            }

            # Add to case updates
            if "updates" not in case:
                case["updates"] = []
            case["updates"].append(update)

            # Update case status if provided
            if "status" in update_data:
                old_status = case["status"]
                case["status"] = update_data["status"]
                case["governance"]["audit_trail"].append(
                    {
                        "action": "status_changed",
                        "timestamp": timestamp,
                        "user": provider_id,
                        "details": {"from": old_status, "to": update_data["status"]},
                    }
                )

            # Update priority if provided
            if "priority" in update_data:
                old_priority = case["priority"]
                case["priority"] = update_data["priority"]
                case["governance"]["audit_trail"].append(
                    {
                        "action": "priority_changed",
                        "timestamp": timestamp,
                        "user": provider_id,
                        "details": {
                            "from": old_priority,
                            "to": update_data["priority"],
                        },
                    }
                )

            # Update symbolic pattern based on case status
            case["symbolic_pattern"] = self._get_case_symbolic_pattern(case)

            # Encrypt the updated data
            case_data = {
                "symptoms": case["symptoms"],
                "ai_assessment": case["ai_assessment"],
            }
            encrypted_case_data, _ = await self.data_protection_service.protect_data(case_data, "pii_protection")
            case["encrypted_data"] = encrypted_case_data
            del case["symptoms"]
            del case["ai_assessment"]

            await self._log_governance_action(
                case_id,
                "case_updated",
                {"provider_id": provider_id, "update_fields": list(update_data.keys())},
            )

            logger.info(f"🏥 Case updated: {case_id} by {provider_id}")
            return case

        except Exception as e:
            logger.error(f"Error updating case: {e!s}")
            raise

    async def create_consultation(
        self,
        provider_id: str,
        user_id: str,
        consultation_type: str,
        consent_token: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Create a new consultation session with governance oversight

        Args:
            provider_id: ID of the healthcare provider
            user_id: ID of the user/patient
            consultation_type: Type of consultation
            consent_token: Patient consent verification token

        Returns:
            Consultation session details with governance metadata
        """
        try:
            # Validate consent if required
            if self.consent_required and not consent_token:
                raise ValueError("Patient consent required for consultation")

            # Validate provider permissions
            if not await self._validate_provider_access(provider_id):
                raise ValueError("Provider access denied")

            session_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()

            session = {
                "session_id": session_id,
                "provider_id": provider_id,
                "user_id": user_id,
                "consultation_type": consultation_type,
                "status": "active",
                "start_time": timestamp,
                "notes": [],
                "governance": {
                    "consent_token": consent_token,
                    "compliance_status": "validated",
                    "audit_trail": [
                        {
                            "action": "consultation_started",
                            "timestamp": timestamp,
                            "user": provider_id,
                            "details": {"type": consultation_type},
                        }
                    ],
                },
                "symbolic_pattern": ["👨‍⚕️", "💬", "🏥"],
            }

            await self._log_governance_action(
                session_id,
                "consultation_created",
                {
                    "provider_id": provider_id,
                    "user_id": user_id,
                    "type": consultation_type,
                },
            )

            logger.info(f"🏥 Consultation created: {session_id}")
            return session

        except Exception as e:
            logger.error(f"Error creating consultation: {e!s}")
            raise

    async def get_case(self, case_id: str, requestor_id: str) -> dict[str, Any]:
        """
        Get case details by ID with access validation

        Args:
            case_id: ID of the case
            requestor_id: ID of the entity requesting case details

        Returns:
            Case details with appropriate governance filtering
        """
        try:
            if case_id not in self.cases:
                raise ValueError(f"Case {case_id} not found")

            # Validate access permissions
            if not await self._validate_case_access(case_id, requestor_id):
                raise ValueError("Access denied to case")

            case = self.cases[case_id].copy()

            # Decrypt case data
            decrypted_data = await self.data_protection_service.unprotect_data(case["encrypted_data"])
            case.update(decrypted_data)
            del case["encrypted_data"]

            # Add access log to governance trail
            case["governance"]["audit_trail"].append(
                {
                    "action": "case_accessed",
                    "timestamp": datetime.utcnow().isoformat(),
                    "user": requestor_id,
                    "details": {"access_type": "read"},
                }
            )

            await self._log_governance_action(case_id, "case_accessed", {"requestor_id": requestor_id})

            return case

        except Exception as e:
            logger.error(f"Error retrieving case: {e!s}")
            raise

    # Governance and validation methods

    async def _validate_case_ethics(
        self, user_id: str, symptoms: list[str], ai_assessment: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate case creation against ethical guidelines"""
        # TODO: Integrate with LUKHAS ethical engine
        return {
            "approved": True,
            "reason": "Ethical validation passed",
            "confidence": 0.95,
        }

    async def _validate_provider_access(self, provider_id: str) -> bool:
        """Validate provider access permissions"""
        if not self.auth_enabled:
            logger.warning("⚠️  Authentication disabled - allowing access for development")
            return True

        try:
            # Verify provider identity and permissions
            auth_result = await self.auth_manager.validate_provider_credentials(provider_id)

            # Check minimum tier requirement for healthcare providers
            required_tier = AuthTier.TIER_2  # Healthcare providers need at least Tier 2
            if auth_result.tier.value < required_tier.value:
                logger.warning(f"Provider {provider_id} insufficient tier: {auth_result.tier} < {required_tier}")
                return False

            # Check healthcare-specific permissions
            has_healthcare_scope = await self.auth_manager.check_scope(provider_id, "healthcare.provider.access")
            if not has_healthcare_scope:
                logger.warning(f"Provider {provider_id} missing healthcare.provider.access scope")
                return False

            logger.info(f"✅ Provider {provider_id} access validated (tier: {auth_result.tier})")
            return True

        except Exception as e:
            logger.error(f"❌ Provider access validation failed for {provider_id}: {e}")
            return False

    async def _validate_case_update_permission(self, case_id: str, provider_id: str) -> bool:
        """Validate provider permission to update specific case"""
        if not self.auth_enabled:
            logger.warning("⚠️  Authentication disabled - allowing case updates for development")
            return True

        # First validate general provider access
        if not await self._validate_provider_access(provider_id):
            return False

        try:
            # Check if case exists
            if case_id not in self.cases:
                logger.warning(f"Case {case_id} not found")
                return False

            case = self.cases[case_id]

            # Check if provider is assigned to this case
            if provider_id in case.get("assigned_providers", []):
                logger.info(f"✅ Provider {provider_id} is assigned to case {case_id}")
                return True

            # Check if provider has supervisor role and sufficient tier
            auth_result = await self.auth_manager.validate_provider_credentials(provider_id)
            has_supervisor_scope = await self.auth_manager.check_scope(provider_id, "healthcare.case.supervise")

            if has_supervisor_scope and auth_result.tier.value >= AuthTier.TIER_3.value:
                logger.info(f"✅ Provider {provider_id} has supervisor access to case {case_id}")
                return True

            # Check emergency access permissions
            has_emergency_scope = await self.auth_manager.check_scope(provider_id, "healthcare.emergency.access")
            if has_emergency_scope and case.get("priority") == "emergency":
                logger.info(f"✅ Provider {provider_id} has emergency access to case {case_id}")
                return True

            logger.warning(f"❌ Provider {provider_id} denied access to case {case_id}")
            return False

        except Exception as e:
            logger.error(f"❌ Case update permission validation failed for {case_id}/{provider_id}: {e}")
            return False

    async def _validate_case_access(self, case_id: str, requestor_id: str) -> bool:
        """Validate access to case details with comprehensive authentication"""
        if not self.auth_enabled:
            logger.warning("⚠️  Authentication disabled - allowing case access for development")
            return True

        try:
            # Check if case exists
            if case_id not in self.cases:
                logger.warning(f"Case {case_id} not found")
                return False

            case = self.cases[case_id]

            # Check if requestor is the patient (owns the case)
            if requestor_id == case.get("user_id"):
                logger.info(f"✅ Patient {requestor_id} accessing own case {case_id}")
                return True

            # Validate if requestor is a healthcare provider
            if not await self._validate_provider_access(requestor_id):
                logger.warning(f"❌ Non-provider {requestor_id} denied access to case {case_id}")
                return False

            # Check if provider is assigned to this case
            if requestor_id in case.get("assigned_providers", []):
                logger.info(f"✅ Assigned provider {requestor_id} accessing case {case_id}")
                return True

            # Check provider tier and permissions
            auth_result = await self.auth_manager.validate_provider_credentials(requestor_id)

            # Tier 3+ providers with supervisor scope can access any case
            has_supervisor_scope = await self.auth_manager.check_scope(requestor_id, "healthcare.case.supervise")
            if has_supervisor_scope and auth_result.tier.value >= AuthTier.TIER_3.value:
                logger.info(f"✅ Supervisor {requestor_id} accessing case {case_id}")
                return True

            # Emergency access for urgent/emergency cases
            case_priority = case.get("priority", "normal")
            if case_priority in ["urgent", "emergency"]:
                has_emergency_scope = await self.auth_manager.check_scope(requestor_id, "healthcare.emergency.access")
                if has_emergency_scope and auth_result.tier.value >= AuthTier.TIER_2.value:
                    logger.info(f"✅ Emergency access granted to {requestor_id} for case {case_id}")
                    return True

            # Check if requestor has consent from patient for this specific case
            consent_token = case.get("governance", {}).get("consent_token")
            if consent_token:
                has_consent_access = await self.auth_manager.verify_patient_consent(
                    requestor_id, case.get("user_id"), consent_token
                )
                if has_consent_access:
                    logger.info(f"✅ Consent-based access granted to {requestor_id} for case {case_id}")
                    return True

            # Check general healthcare read permissions for Tier 2+ providers
            has_read_scope = await self.auth_manager.check_scope(requestor_id, "healthcare.case.read")
            if has_read_scope and auth_result.tier.value >= AuthTier.TIER_2.value:
                # Additional check: ensure case is not marked as restricted
                if not case.get("governance", {}).get("restricted_access", False):
                    logger.info(f"✅ General read access granted to {requestor_id} for case {case_id}")
                    return True
                else:
                    logger.warning(f"❌ Case {case_id} has restricted access, denied to {requestor_id}")
                    return False

            logger.warning(f"❌ Access denied to {requestor_id} for case {case_id} - insufficient permissions")
            return False

        except Exception as e:
            logger.error(f"❌ Case access validation failed for {case_id}/{requestor_id}: {e}")
            # Fail secure - deny access on any error
            return False

    def _has_general_access(self, provider_id: str) -> bool:
        """Check if provider has general case access"""
        # TODO: Implement role-based access control
        return True

    def _get_case_symbolic_pattern(self, case: dict[str, Any]) -> list[str]:
        """Get symbolic pattern based on case status and priority"""
        status = case.get("status", "unknown")
        priority = case.get("priority", "normal")

        patterns = {
            "pending_review": ["🏥", "⏳", "📋"],
            "under_review": ["👨‍⚕️", "🔍", "📊"],
            "completed": ["✅", "📝", "🏥"],
            "urgent": ["🚨", "🏥", "⚡"],
            "high": ["⚠️", "🏥", "📈"],
            "normal": ["🏥", "📋", "✅"],
        }

        return patterns.get(status, patterns.get(priority, ["🏥", "❓", "📋"]))

    async def _log_governance_action(self, entity_id: str, action: str, metadata: dict[str, Any]):
        """Log action in governance audit trail"""
        if not hasattr(self, "case_audit_trail"):
            self.case_audit_trail = {}

        if entity_id not in self.case_audit_trail:
            self.case_audit_trail[entity_id] = []

        self.case_audit_trail[entity_id].append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "action": action,
                "metadata": metadata,
                "source": "case_manager",
            }
        )

        # TODO: Forward to main governance audit system
        logger.debug(f"🔍 Governance action logged: {action} for {entity_id}")

    # Public API methods for governance integration

    def get_governance_summary(self) -> dict[str, Any]:
        """Get governance and compliance summary"""
        total_cases = len(self.cases)
        compliant_cases = len(
            [case for case in self.cases.values() if case.get("governance", {}).get("compliance_status") == "validated"]
        )

        return {
            "total_cases": total_cases,
            "compliant_cases": compliant_cases,
            "compliance_rate": (compliant_cases / total_cases if total_cases > 0 else 1.0),
            "consent_enforcement": self.consent_required,
            "ethical_validation": self.ethical_checks_enabled,
            "audit_trail_entries": sum(len(trail) for trail in self.case_audit_trail.values()),
        }

    def get_case_statistics(self) -> dict[str, Any]:
        """Get case management statistics"""
        if not self.cases:
            return {"total_cases": 0}

        status_counts = {}
        priority_counts = {}

        for case in self.cases.values():
            status = case.get("status", "unknown")
            priority = case.get("priority", "normal")

            status_counts[status] = status_counts.get(status, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        return {
            "total_cases": len(self.cases),
            "status_distribution": status_counts,
            "priority_distribution": priority_counts,
            "average_updates_per_case": sum(len(case.get("updates", [])) for case in self.cases.values())
            / len(self.cases),
        }

    async def enforce_healthcare_data_retention(self):
        """Enforce data retention policies for healthcare data."""
        retention_period_days = self.config.get("healthcare_retention_days", 2555)
        await self.data_protection_service.enforce_retention_policy(retention_period_days)
        logger.info(f"Enforced healthcare data retention policy ({retention_period_days} days).")

    async def share_case_with_third_party(self, case_id: str, third_party_name: str, requestor_id: str):
        """Share a case with a third party after verifying BAA."""
        # First, check if the requestor has access to the case
        await self.get_case(case_id, requestor_id)

        # Check for a valid BAA
        baa = await self.data_protection_service.get_baa(third_party_name)
        if not baa:
            raise ValueError(f"No valid Business Associate Agreement found for {third_party_name}")

        # Share the case data
        logger.info(f"Sharing case {case_id} with {third_party_name} (BAA validated).")
        # In a real implementation, this would trigger a secure data sharing process.
        return {
            "status": "success",
            "message": f"Case {case_id} shared with {third_party_name}",
        }
