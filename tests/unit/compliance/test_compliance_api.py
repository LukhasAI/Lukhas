from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, Mock

import pytest
from consent.api import ConsentService, get_consent_service
from enterprise.compliance.api import (
    get_data_protection_service,
    router as protection_router,
    user_router,
)
from enterprise.compliance.data_protection_service import DataProtectionService
from fastapi import FastAPI
from fastapi.testclient import TestClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler"""
    # We don't need to do anything here for the tests, as the services are mocked.
    yield


@pytest.fixture
def mock_dp_service():
    """Mock data protection service"""
    service = Mock(spec=DataProtectionService)
    from datetime import datetime, timezone

    from enterprise.compliance.data_protection_service import ProtectionPolicy

    mock_policy = ProtectionPolicy(
        policy_id="pii_protection",
        name="PII Protection",
        description="Test policy",
        data_types=["email"],
        protection_level="HIGH",
        encryption_required=True,
        encryption_type="SYMMETRIC",
        key_rotation_days=90,
        anonymization_methods=[],
        retain_utility=True,
        authorized_roles=[],
        audit_required=True,
        gdpr_article_25=True,
        gdpr_article_32=True,
        cache_encrypted=False,
        background_processing=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        version="1.0",
    )
    service.protection_policies = {"pii_protection": mock_policy}
    service.protect_data = AsyncMock(return_value=({"encrypted": True}, {}))
    service.unprotect_data = AsyncMock(return_value="test")
    from datetime import timedelta

    from enterprise.compliance.data_protection_service import GDPRAssessment

    mock_assessment = GDPRAssessment(
        activity_id="test",
        compliance_status="Fully Compliant",
        assessment_date=datetime.now(timezone.utc),
        lawfulness_score=1.0,
        privacy_rights_score=1.0,
        security_score=1.0,
        transparency_score=1.0,
        overall_score=1.0,
        violations=[],
        recommendations=[],
        next_review_date=datetime.now(timezone.utc) + timedelta(days=180),
    )
    service.assess_processing_activity = AsyncMock(return_value=mock_assessment)
    service.get_user_data = AsyncMock(return_value=[])
    service.delete_user_data = AsyncMock(return_value=1)
    service.update_protected_data = AsyncMock(return_value={"status": "success"})
    return service


@pytest.fixture
def mock_consent_service():
    """Mock consent service"""
    service = Mock(spec=ConsentService)
    service.get_all_user_consent_grants = AsyncMock(return_value=[])
    service.delete_user_consent_grants = AsyncMock(return_value=1)
    service.update_consent_grant = AsyncMock(return_value={"status": "success"})
    return service


@pytest.fixture
def client(mock_dp_service, mock_consent_service):
    app = FastAPI(lifespan=lifespan)
    app.dependency_overrides[get_data_protection_service] = lambda: mock_dp_service
    app.dependency_overrides[get_consent_service] = lambda: mock_consent_service
    app.include_router(protection_router)
    app.include_router(user_router)
    return TestClient(app)


def test_list_policies(client):
    """Test the /protection/policies endpoint."""
    response = client.get("/protection/policies")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "PII Protection"


def test_protect_data(client, mock_dp_service):
    """Test the /protection/protect endpoint."""
    response = client.post("/protection/protect", json={"data": "test", "policy_id": "pii_protection"})
    assert response.status_code == 200
    data = response.json()
    assert data["protected_data"]["encrypted"] is True


def test_unprotect_data(client, mock_dp_service):
    """Test the /protection/unprotect endpoint."""
    response = client.post("/protection/unprotect", json={"data": {"encrypted": True}})
    assert response.status_code == 200
    data = response.json()
    assert data["unprotected_data"] == "test"


def test_assessment(client, mock_dp_service):
    """Test the /assessment endpoint."""
    from enterprise.compliance.data_protection_service import (
        DataCategory,
        DataProcessingActivity,
        LawfulBasis,
        ProcessingPurpose,
    )

    activity = DataProcessingActivity(
        activity_id="test",
        name="test",
        description="test",
        controller="test",
        processor="test",
        data_categories=[DataCategory.PERSONAL_DATA],
        lawful_basis=LawfulBasis.CONSENT,
        purposes=[ProcessingPurpose.SERVICE_PROVISION],
        data_subjects=["test"],
        retention_period="test",
        international_transfers=False,
        automated_decision_making=False,
        profiling=False,
    )
    response = client.post("/protection/assessment", json=activity.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert data["compliance_status"] == "Fully Compliant"


def test_export_user_data(client, mock_consent_service, mock_dp_service):
    """Test the /users/{user_lid}/export endpoint."""
    response = client.get("/users/gonzo/export")
    assert response.status_code == 200
    data = response.json()
    assert data["user_lid"] == "gonzo"


def test_delete_user_data(client, mock_consent_service, mock_dp_service):
    """Test the DELETE /users/{user_lid} endpoint."""
    response = client.delete("/users/gonzo")
    assert response.status_code == 200
    data = response.json()
    assert data["deleted_consent_grants"] == 1


def test_update_user_data(client, mock_consent_service, mock_dp_service):
    """Test the PUT /users/{user_lid} endpoint."""
    response = client.put("/users/gonzo", json={"updates": {"data": "new_data"}})
    assert response.status_code == 200
    data = response.json()
    assert data["updated_consent_grants"]["status"] == "success"
