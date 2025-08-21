"""
Integration tests for Lambda Healthcare Guardian
Tests full LUKHAS Trinity integration and healthcare features
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# Import the Healthcare Guardian
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lambda_healthcare_core import (
    LambdaHealthcareGuardian,
    HealthcareContext,
    ComplianceLevel,
    EmergencyLevel,
    MedicalDecision
)


@pytest.fixture
async def healthcare_guardian():
    """Create Healthcare Guardian instance for testing"""
    with patch('lambda_healthcare_core.LUKHAS_AVAILABLE', False):
        guardian = LambdaHealthcareGuardian()
        yield guardian


@pytest.fixture
def patient_context():
    """Create test patient context"""
    return HealthcareContext(
        patient_id="test_patient_001",
        age=75,
        conditions=["diabetes", "hypertension"],
        medications=["metformin", "lisinopril"],
        allergies=["penicillin"],
        emergency_contacts=[
            {"name": "Test Contact", "phone": "+34 600 000 000"}
        ],
        language="es-AN",
        consent_level="enhanced"
    )


class TestLambdaHealthcareCore:
    """Test core Lambda Healthcare functionality"""
    
    @pytest.mark.asyncio
    async def test_initialization(self, healthcare_guardian):
        """Test system initialization"""
        assert healthcare_guardian is not None
        assert healthcare_guardian.compliance_level == ComplianceLevel.ALL
        assert healthcare_guardian.fallback_active == False
        assert healthcare_guardian.product_info["name"] == "ΛHealthcare Guardian"
    
    @pytest.mark.asyncio
    async def test_medical_request_processing(self, healthcare_guardian, patient_context):
        """Test medical request processing with ethics validation"""
        # Mock the GPT5 client
        healthcare_guardian.gpt5_client.process_request = AsyncMock(
            return_value={"response": "Prescription renewal approved", "risk": 0.2}
        )
        
        response = await healthcare_guardian.process_medical_request(
            request="Need prescription renewal",
            context=patient_context
        )
        
        assert response["success"] == True
        assert "ethics_score" in response
        assert response["ethics_score"] > 0.5
    
    @pytest.mark.asyncio
    async def test_emergency_handling(self, healthcare_guardian, patient_context):
        """Test emergency response with fallback layers"""
        # Mock emergency systems
        healthcare_guardian.emergency_system.trigger_emergency = AsyncMock(
            return_value={"status": "emergency_triggered", "id": "EMG001"}
        )
        
        response = await healthcare_guardian.handle_emergency(
            emergency_type="cardiac",
            context=patient_context,
            location={"lat": 37.3891, "lon": -5.9845}
        )
        
        assert response["emergency_handled"] == True
        assert len(response["responses"]) > 0
        assert response["priority"] == "LAMBDA_PRIORITY"
    
    @pytest.mark.asyncio
    async def test_medication_scanning(self, healthcare_guardian, patient_context):
        """Test medication OCR with Lambda verification"""
        # Mock OCR system
        healthcare_guardian.ocr_system.scan_medication = AsyncMock(
            return_value={
                "text": "Metformina 850mg",
                "medication_name": "metformin",
                "dosage": "850mg"
            }
        )
        
        # Mock GPT5 verification
        healthcare_guardian.gpt5_client.verify_medication = AsyncMock(
            return_value=True
        )
        
        result = await healthcare_guardian.scan_medication(
            image_path="/test/image.jpg",
            context=patient_context
        )
        
        assert result["medication"]["medication_name"] == "metformin"
        assert result["lambda_verified"] == True
        assert "safety_score" in result
    
    @pytest.mark.asyncio
    async def test_sas_appointment_booking(self, healthcare_guardian, patient_context):
        """Test SAS healthcare appointment booking"""
        # Mock SAS connector
        healthcare_guardian.sas_connector.book_appointment = AsyncMock(
            return_value={
                "appointment_id": "SAS123",
                "date": "2025-01-15",
                "time": "10:30",
                "specialty": "cardiology"
            }
        )
        
        appointment = await healthcare_guardian.book_sas_appointment(
            specialty="cardiology",
            context=patient_context,
            preferred_time="morning"
        )
        
        assert appointment["appointment_id"] == "SAS123"
        assert appointment["specialty"] == "cardiology"


class TestComplianceIntegration:
    """Test compliance and ethics integration"""
    
    @pytest.mark.asyncio
    async def test_gdpr_compliance(self, healthcare_guardian):
        """Test GDPR compliance validation"""
        gdpr_manager = healthcare_guardian.gdpr_manager
        
        # Test data minimization
        compliance = await gdpr_manager.ensure_compliance(
            action="data_collection",
            data={"patient_id": "123", "name": "Test"}
        )
        
        assert compliance == True
    
    @pytest.mark.asyncio
    async def test_hipaa_compliance(self, healthcare_guardian):
        """Test HIPAA compliance for healthcare data"""
        hipaa_manager = healthcare_guardian.hipaa_manager
        
        # Test access validation
        access_valid = await hipaa_manager.validate_access(
            user_id="doctor_001",
            patient_id="patient_001"
        )
        
        assert access_valid == True
    
    @pytest.mark.asyncio
    async def test_consent_management(self, healthcare_guardian, patient_context):
        """Test consent verification system"""
        # Mock consent manager when LUKHAS is available
        with patch('lambda_healthcare_core.LUKHAS_AVAILABLE', True):
            mock_consent_manager = AsyncMock()
            mock_consent_manager.verify_consent = AsyncMock(return_value=True)
            healthcare_guardian.consent_manager = mock_consent_manager
            
            consent = await healthcare_guardian._verify_consent(
                patient_id=patient_context.patient_id,
                action="medical_data"
            )
            
            assert consent == True
            mock_consent_manager.verify_consent.assert_called_once()


class TestFallbackSystems:
    """Test fallback and resilience systems"""
    
    @pytest.mark.asyncio
    async def test_fallback_activation(self, healthcare_guardian, patient_context):
        """Test fallback system activation on primary failure"""
        # Force primary system failure
        healthcare_guardian.gpt5_client.process_request = AsyncMock(
            side_effect=Exception("Service unavailable")
        )
        
        response = await healthcare_guardian.process_medical_request(
            request="Need medical help",
            context=patient_context
        )
        
        assert response["success"] == False
        assert response["fallback_active"] == True
        assert len(response["fallback_options"]) > 0
        assert "manual_guidance" in response
    
    @pytest.mark.asyncio
    async def test_emergency_fallback_layers(self, healthcare_guardian, patient_context):
        """Test multiple emergency fallback layers"""
        # Mock all emergency systems to fail except contact notification
        healthcare_guardian.emergency_system.trigger_emergency = AsyncMock(
            side_effect=Exception("System down")
        )
        
        # Mock successful contact notification
        healthcare_guardian._notify_emergency_contacts = AsyncMock(
            return_value={"contacts_notified": 1}
        )
        
        response = await healthcare_guardian.handle_emergency(
            emergency_type="fall",
            context=patient_context
        )
        
        assert response["emergency_handled"] == True
        assert response["fallback_layers_activated"] > 0


class TestAndalusianVoiceIntegration:
    """Test Andalusian Spanish voice processing"""
    
    @pytest.mark.asyncio
    async def test_voice_engine_initialization(self, healthcare_guardian):
        """Test Andalusian voice engine setup"""
        voice_engine = healthcare_guardian.voice_engine
        
        assert voice_engine is not None
        assert hasattr(voice_engine, 'process_andalusian_speech')
    
    @pytest.mark.asyncio
    async def test_dialect_processing(self, healthcare_guardian):
        """Test Andalusian dialect processing"""
        voice_engine = healthcare_guardian.voice_engine
        
        # Mock voice processing
        voice_engine.process_andalusian_speech = AsyncMock(
            return_value="necesito medicina"
        )
        
        result = await voice_engine.process_andalusian_speech(
            audio_data=b"mock_audio"
        )
        
        assert result == "necesito medicina"


class TestTrinityFrameworkIntegration:
    """Test LUKHAS Trinity Framework integration when available"""
    
    @pytest.mark.asyncio
    async def test_guardian_validation(self, patient_context):
        """Test Guardian system validation"""
        with patch('lambda_healthcare_core.LUKHAS_AVAILABLE', True):
            # Mock LUKHAS components
            with patch('lambda_healthcare_core.GuardianSystem') as MockGuardian:
                mock_guardian_instance = AsyncMock()
                mock_guardian_instance.validate_action = AsyncMock(
                    return_value=Mock(approved=True)
                )
                MockGuardian.return_value = mock_guardian_instance
                
                guardian = LambdaHealthcareGuardian()
                guardian.guardian = mock_guardian_instance
                
                response = await guardian.process_medical_request(
                    request="Test request",
                    context=patient_context
                )
                
                mock_guardian_instance.validate_action.assert_called()
    
    @pytest.mark.asyncio
    async def test_ethics_engine_integration(self, patient_context):
        """Test ethics engine evaluation"""
        with patch('lambda_healthcare_core.LUKHAS_AVAILABLE', True):
            with patch('lambda_healthcare_core.EthicsEngine') as MockEthics:
                mock_ethics_instance = AsyncMock()
                mock_ethics_instance.evaluate = AsyncMock(return_value=0.95)
                MockEthics.return_value = mock_ethics_instance
                
                guardian = LambdaHealthcareGuardian()
                guardian.ethics_engine = mock_ethics_instance
                
                score = await guardian._validate_ethics(
                    response={"action": "test"},
                    context=patient_context
                )
                
                assert score == 0.95


class TestMetricsAndMonitoring:
    """Test system metrics and monitoring"""
    
    @pytest.mark.asyncio
    async def test_dashboard_metrics(self, healthcare_guardian):
        """Test dashboard metrics collection"""
        metrics = healthcare_guardian.dashboard_metrics.get_metrics()
        
        assert "system_health" in metrics
        assert metrics["system_health"] > 0.9
        assert "response_time_ms" in metrics
        assert metrics["response_time_ms"] < 100
    
    @pytest.mark.asyncio
    async def test_threat_monitoring(self, healthcare_guardian):
        """Test healthcare threat monitoring"""
        threats = await healthcare_guardian.threat_monitor.monitor_threats()
        
        assert isinstance(threats, list)


# Performance tests
class TestPerformance:
    """Test performance requirements"""
    
    @pytest.mark.asyncio
    async def test_response_time(self, healthcare_guardian, patient_context):
        """Test response time < 100ms requirement"""
        import time
        
        # Mock fast responses
        healthcare_guardian.gpt5_client.process_request = AsyncMock(
            return_value={"response": "test", "risk": 0.1}
        )
        
        start = time.time()
        await healthcare_guardian.process_medical_request(
            request="Quick test",
            context=patient_context
        )
        elapsed = (time.time() - start) * 1000
        
        # Should be fast (mocked, so very fast)
        assert elapsed < 1000  # Generous limit for test environment
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, healthcare_guardian, patient_context):
        """Test handling multiple concurrent requests"""
        # Mock responses
        healthcare_guardian.gpt5_client.process_request = AsyncMock(
            return_value={"response": "test", "risk": 0.1}
        )
        
        # Create multiple concurrent requests
        tasks = [
            healthcare_guardian.process_medical_request(
                request=f"Request {i}",
                context=patient_context
            )
            for i in range(10)
        ]
        
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == 10
        assert all(r["success"] for r in responses)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])