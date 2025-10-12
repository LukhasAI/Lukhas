#!/usr/bin/env python3
"""
Orchestration Router with Plan Verifier Integration
===================================================

Task 5: Integration hook for plan verification before execution.
This router demonstrates how to integrate the PlanVerifier into
the orchestration flow for fail-closed safety.

#TAG:orchestration
#TAG:task5
#TAG:router
"""
import logging
import time
from typing import Any, Dict, Optional

from .plan_verifier import VerificationContext, get_plan_verifier

logger = logging.getLogger(__name__)


class OrchestrationRouter:
    """
    Orchestration router with integrated plan verification.

    Provides fail-closed safety by verifying all action plans
    before execution through the PlanVerifier.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize orchestration router.

        Args:
            config: Optional configuration for both router and plan verifier
        """
        self.config = config or {}
        self.plan_verifier = get_plan_verifier(self.config.get('plan_verifier'))

        # Router configuration
        self.enable_verification = self.config.get('enable_verification', True)
        self.bypass_verification_for_safe_actions = self.config.get(
            'bypass_verification_for_safe_actions', True
        )

        # Safe actions that can bypass verification (for performance)
        self.safe_actions = set(self.config.get(
            'safe_actions',
            ['status_check', 'health_check', 'log_event', 'metrics_update']
        ))

        logger.info(f"OrchestrationRouter initialized: verification={self.enable_verification}")

    async def execute_plan(
        self,
        plan: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute action plan with pre-execution verification.

        This is the main integration point where plan verification
        happens before any action execution.

        Args:
            plan: Action plan to execute
            context: Optional execution context

        Returns:
            Execution result with verification details
        """
        execution_start = time.perf_counter()
        context = context or {}

        # Create verification context
        verification_ctx = VerificationContext(
            user_id=context.get('user_id'),
            session_id=context.get('session_id'),
            request_id=context.get('request_id'),
            metadata=context.get('metadata')
        )

        # Step 1: Plan verification (unless bypassed)
        should_verify = self._should_verify_plan(plan)
        if should_verify:
            logger.info(f"Verifying plan: {plan.get('action', 'unknown')}")

            verification_outcome = self.plan_verifier.verify(plan, verification_ctx)

            if not verification_outcome.allow:
                # Plan denied - fail closed
                logger.warning(
                    f"Plan verification DENIED: action={plan.get('action')}, "
                    f"reasons={verification_outcome.reasons}"
                )

                return {
                    'status': 'denied',
                    'action': plan.get('action'),
                    'verification': {
                        'result': 'deny',
                        'reasons': verification_outcome.reasons,
                        'plan_hash': verification_outcome.plan_hash,
                        'verification_time_ms': verification_outcome.verification_time_ms
                    },
                    'execution_time_ms': (time.perf_counter() - execution_start) * 1000,
                    'timestamp': verification_outcome.context.timestamp
                }

            logger.info(
                f"Plan verification ALLOWED: action={plan.get('action')} "
                f"({verification_outcome.verification_time_ms:.2f}ms)"
            )

        else:
            logger.debug(f"Bypassing verification for safe action: {plan.get('action')}")
            verification_outcome = None

        # Step 2: Execute the plan (simulation for demo)
        try:
            execution_result = await self._execute_action(plan, context)

            execution_time_ms = (time.perf_counter() - execution_start) * 1000

            # Step 3: Return success with verification details
            result = {
                'status': 'success',
                'action': plan.get('action'),
                'result': execution_result,
                'execution_time_ms': execution_time_ms,
                'timestamp': time.time()
            }

            # Include verification details if performed
            if verification_outcome:
                result['verification'] = {
                    'result': 'allow',
                    'reasons': verification_outcome.reasons,
                    'plan_hash': verification_outcome.plan_hash,
                    'verification_time_ms': verification_outcome.verification_time_ms
                }

            return result

        except Exception as e:
            logger.error(f"Plan execution failed: {e}")

            execution_time_ms = (time.perf_counter() - execution_start) * 1000

            return {
                'status': 'error',
                'action': plan.get('action'),
                'error': str(e),
                'execution_time_ms': execution_time_ms,
                'timestamp': time.time(),
                'verification': {
                    'result': 'allow' if verification_outcome else 'bypassed',
                    'reasons': verification_outcome.reasons if verification_outcome else ['safe_action_bypass'],
                    'plan_hash': verification_outcome.plan_hash if verification_outcome else 'bypassed',
                    'verification_time_ms': verification_outcome.verification_time_ms if verification_outcome else 0
                } if verification_outcome or should_verify else None
            }

    def _should_verify_plan(self, plan: Dict[str, Any]) -> bool:
        """
        Determine if plan should go through verification.

        Args:
            plan: Action plan to check

        Returns:
            True if verification should be performed
        """
        if not self.enable_verification:
            return False

        action = plan.get('action', '')

        # Bypass verification for explicitly safe actions
        if (self.bypass_verification_for_safe_actions and
            isinstance(action, str) and
            action in self.safe_actions):
            return False

        return True

    async def _execute_action(
        self,
        plan: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the verified action plan.

        This is a simulation for demonstration. In a real implementation,
        this would dispatch to the appropriate action handlers.

        Args:
            plan: Verified action plan
            context: Execution context

        Returns:
            Action execution result
        """
        action = plan.get('action', 'unknown')
        params = plan.get('params', {})

        # Simulate different action types
        if action == 'external_call':
            return await self._execute_external_call(params)
        elif action == 'process_data':
            return await self._execute_data_processing(params)
        elif action == 'batch_process':
            return await self._execute_batch_processing(params)
        elif action in self.safe_actions:
            return await self._execute_safe_action(action, params)
        else:
            return await self._execute_generic_action(action, params)

    async def _execute_external_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate external API call execution."""
        url = params.get('url', '')
        method = params.get('method', 'GET')

        # Simulate API call delay
        await self._simulate_delay(params.get('estimated_time_seconds', 1))

        return {
            'type': 'external_call',
            'url': url,
            'method': method,
            'status_code': 200,
            'response_size': 1024,
            'simulated': True
        }

    async def _execute_data_processing(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate data processing execution."""
        batch_size = params.get('batch_size', 1)

        # Simulate processing delay
        await self._simulate_delay(params.get('estimated_time_seconds', 0.1))

        return {
            'type': 'data_processing',
            'records_processed': batch_size,
            'processing_time_ms': batch_size * 10,  # 10ms per record
            'simulated': True
        }

    async def _execute_batch_processing(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate batch processing execution."""
        batch_size = params.get('batch_size', 100)

        # Simulate longer processing delay
        await self._simulate_delay(params.get('estimated_time_seconds', 5))

        return {
            'type': 'batch_processing',
            'batch_size': batch_size,
            'processing_time_ms': batch_size * 50,  # 50ms per item
            'simulated': True
        }

    async def _execute_safe_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute safe actions that bypass verification."""
        return {
            'type': 'safe_action',
            'action': action,
            'params': params,
            'verified': False,
            'simulated': True
        }

    async def _execute_generic_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute generic actions."""
        await self._simulate_delay(0.1)  # Small delay

        return {
            'type': 'generic_action',
            'action': action,
            'params': params,
            'simulated': True
        }

    async def _simulate_delay(self, seconds: float):
        """Simulate execution delay for demonstration."""
        # In tests, use a minimal delay to avoid slowing down the suite
        import asyncio
        delay = min(seconds, 0.01)  # Cap at 10ms for tests
        await asyncio.sleep(delay)

    def get_verifier_stats(self) -> Dict[str, Any]:
        """Get plan verifier statistics."""
        return {
            'ledger_entries': len(self.plan_verifier.verification_ledger),
            'last_10_verifications': self.plan_verifier.verification_ledger[-10:] if self.plan_verifier.verification_ledger else [],
            'config': {
                'enable_verification': self.enable_verification,
                'bypass_safe_actions': self.bypass_verification_for_safe_actions,
                'safe_actions': list(self.safe_actions)
            }
        }


# Factory function for easy integration
def create_orchestration_router(config: Optional[Dict[str, Any]] = None) -> OrchestrationRouter:
    """
    Create orchestration router with plan verification.

    Args:
        config: Optional configuration

    Returns:
        Configured OrchestrationRouter instance
    """
    return OrchestrationRouter(config)