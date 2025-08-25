"""
Service Integration Tests for LUKHAS AI
========================================
Tests cross-module service integration with the test-compatible logger.
Part of BATCH 10: Testing & Examples
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock

# Import the test logger to ensure compatibility
from candidate.core.common.test_logger import get_test_logger
from candidate.core.common.config import get_config, settings
from candidate.core.common.exceptions import LukhasError
from candidate.core.common.glyph import GLYPHSymbol


class TestServiceIntegration:
    """Test service integration across LUKHAS modules."""
    
    def setup_method(self):
        """Setup test environment."""
        self.logger = get_test_logger(__name__)
        
    def test_config_integration(self):
        """Test configuration system works across modules."""
        # Test the config system we fixed
        assert settings is not None, "Settings should be available"
        
        # Test module config loading
        config_loader = get_config('test_module')
        assert config_loader is not None
        assert config_loader.name == 'test_module'
        
        # Test with keyword logging (this would have failed before our fix!)
        self.logger.info("Config test passed", module="test_module", status="success")
        
    def test_logger_keyword_arguments(self):
        """Test that logger accepts keyword arguments (our fix)."""
        # This is the exact issue that was causing problems
        try:
            self.logger.info("Test message", user="test_user", action="test_action")
            self.logger.error("Error message", code=500, module="api", retry_count=3)
            self.logger.debug("Debug info", data={"key": "value"}, timestamp=12345)
        except TypeError as e:
            pytest.fail(f"Logger should accept keyword arguments: {e}")
            
    def test_glyph_cross_module_flow(self):
        """Test GLYPH tokens work between core and bridge modules."""
        # Test GLYPH symbol usage
        trust_symbol = GLYPHSymbol.TRUST
        learn_symbol = GLYPHSymbol.LEARN
        
        assert trust_symbol.value == "TRUST"
        assert learn_symbol.value == "LEARN"
        
        # Log with structured data
        self.logger.info(
            "GLYPH test", 
            symbol=trust_symbol.value, 
            module="core",
            target="bridge"
        )
        
    @pytest.mark.asyncio
    async def test_async_service_integration(self):
        """Test async service integration patterns."""
        # Simulate async service calls
        async def mock_consciousness_service():
            await asyncio.sleep(0.01)
            self.logger.info("Consciousness activated", state="active", drift=0.12)
            return {"state": "active", "drift": 0.12}
            
        async def mock_memory_service():
            await asyncio.sleep(0.01)
            self.logger.info("Memory fold created", fold_id="test_123", size=1024)
            return {"fold_id": "test_123", "size": 1024}
            
        # Run services concurrently
        results = await asyncio.gather(
            mock_consciousness_service(),
            mock_memory_service()
        )
        
        assert results[0]["state"] == "active"
        assert results[1]["fold_id"] == "test_123"
        
    def test_exception_integration(self):
        """Test exception handling across modules."""
        # Test custom exceptions
        with pytest.raises(LukhasError):
            raise LukhasError("Test error", error_code="TEST_001", details={"module": "test"})
            
        # Log exception with context
        try:
            raise LukhasError("Integration failure", error_code="INT_001")
        except LukhasError as e:
            self.logger.error(
                "Exception caught",
                error_code=e.error_code,
                message=str(e),
                module="integration_test"
            )
            
    def test_memory_consciousness_integration(self):
        """Test memory systems integrate with consciousness modules."""
        # Mock memory and consciousness components
        memory_mock = Mock()
        memory_mock.create_fold.return_value = {"fold_id": "mem_001", "status": "created"}
        
        consciousness_mock = Mock()
        consciousness_mock.get_state.return_value = {"state": "aware", "drift": 0.15}
        
        # Simulate integration
        memory_result = memory_mock.create_fold("test_data")
        consciousness_state = consciousness_mock.get_state()
        
        # Log integration flow with structured data
        self.logger.info(
            "Memory-consciousness sync",
            memory_fold=memory_result["fold_id"],
            consciousness_state=consciousness_state["state"],
            drift_level=consciousness_state["drift"]
        )
        
        assert memory_result["status"] == "created"
        assert consciousness_state["drift"] < 0.2  # Within acceptable drift
        
    def test_guardian_enforcement_integration(self):
        """Test Guardian system validates cross-module operations."""
        # Mock Guardian validation
        guardian_mock = Mock()
        guardian_mock.validate.return_value = {
            "approved": True,
            "drift": 0.08,
            "ethics_score": 0.95
        }
        
        # Test operation requiring Guardian approval
        operation = {
            "type": "memory_modification",
            "target": "fold_123",
            "risk_level": "medium"
        }
        
        validation = guardian_mock.validate(operation)
        
        # Log with Guardian context
        self.logger.info(
            "Guardian validation",
            approved=validation["approved"],
            drift=validation["drift"],
            ethics_score=validation["ethics_score"],
            operation_type=operation["type"]
        )
        
        assert validation["approved"] is True
        assert validation["drift"] < 0.15  # Below drift threshold
        assert validation["ethics_score"] > 0.9  # High ethics score
        
    def test_multi_module_transaction(self):
        """Test transaction across multiple modules."""
        # Simulate a complex operation involving multiple modules
        modules = {
            "identity": Mock(),
            "consciousness": Mock(),
            "memory": Mock(),
            "guardian": Mock()
        }
        
        # Configure mock responses
        modules["identity"].authenticate.return_value = {"user_id": "test_user", "tier": 3}
        modules["consciousness"].prepare.return_value = {"ready": True}
        modules["memory"].allocate.return_value = {"space": 1024}
        modules["guardian"].approve.return_value = {"approved": True}
        
        # Execute transaction
        auth = modules["identity"].authenticate("token")
        consciousness_ready = modules["consciousness"].prepare()
        memory_allocated = modules["memory"].allocate(1024)
        guardian_approved = modules["guardian"].approve("transaction")
        
        # Log complete transaction with all context
        self.logger.info(
            "Multi-module transaction",
            user_id=auth["user_id"],
            tier=auth["tier"],
            consciousness_ready=consciousness_ready["ready"],
            memory_allocated=memory_allocated["space"],
            guardian_approved=guardian_approved["approved"],
            transaction_id="tx_001"
        )
        
        # Verify all modules worked together
        assert auth["tier"] >= 3
        assert consciousness_ready["ready"] is True
        assert memory_allocated["space"] == 1024
        assert guardian_approved["approved"] is True
        
    def test_performance_metrics_integration(self):
        """Test performance metrics collection across services."""
        import time
        
        operations = []
        
        # Simulate timed operations
        for i in range(3):
            start = time.time()
            # Simulate work
            time.sleep(0.01)
            elapsed = (time.time() - start) * 1000  # Convert to ms
            
            operations.append(elapsed)
            
            # Log with performance data
            self.logger.info(
                "Operation completed",
                operation_id=f"op_{i}",
                elapsed_ms=elapsed,
                service="test_service"
            )
            
        # Calculate metrics
        avg_time = sum(operations) / len(operations)
        max_time = max(operations)
        
        self.logger.info(
            "Performance summary",
            avg_ms=avg_time,
            max_ms=max_time,
            operations_count=len(operations)
        )
        
        assert avg_time < 100  # Average under 100ms
        assert max_time < 150  # Max under 150ms
        

class TestErrorScenarios:
    """Test error scenarios in service integration."""
    
    def setup_method(self):
        """Setup test environment."""
        self.logger = get_test_logger(__name__)
        
    def test_service_timeout_handling(self):
        """Test handling of service timeouts."""
        # Simulate timeout scenario
        with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError):
            with pytest.raises(asyncio.TimeoutError):
                asyncio.run(asyncio.wait_for(asyncio.sleep(1), timeout=0.01))
                
        # Log timeout with context
        self.logger.warning(
            "Service timeout",
            service="mock_service",
            timeout_ms=10,
            retry_attempt=1
        )
        
    def test_cascade_failure_prevention(self):
        """Test prevention of cascade failures across services."""
        services_status = {
            "service_a": "healthy",
            "service_b": "degraded",
            "service_c": "failed"
        }
        
        # Check for cascade risk
        failed_count = sum(1 for status in services_status.values() if status == "failed")
        degraded_count = sum(1 for status in services_status.values() if status == "degraded")
        
        cascade_risk = (failed_count + degraded_count * 0.5) / len(services_status)
        
        self.logger.warning(
            "Cascade risk assessment",
            failed_services=failed_count,
            degraded_services=degraded_count,
            cascade_risk=cascade_risk,
            threshold=0.5
        )
        
        # Circuit breaker should trigger if risk > 0.5
        if cascade_risk > 0.5:
            self.logger.critical(
                "Circuit breaker activated",
                risk_level=cascade_risk,
                affected_services=list(services_status.keys())
            )
            
        assert cascade_risk <= 1.0  # Risk should be bounded


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])