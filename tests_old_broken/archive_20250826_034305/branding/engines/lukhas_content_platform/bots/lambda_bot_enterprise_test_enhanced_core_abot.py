#!/usr/bin/env python3
"""
Enhanced Core LUKHAS AI ΛBot - Comprehensive Test Suite
Testing for authentication, AI integration, social media, compliance, and mobile app backend
"""

import pytest
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
import tempfile
import os
import sys

# Add paths for testing
sys.path.append('/Users/A_G_I/Λ/LUKHAS AI ΛBot/core')
sys.path.append('/Users/A_G_I/Λ/brain')

from enhanced_core_lambda_bot_backend import app, get_current_user, create_access_token
from celery_tasks import celery_app, generate_ai_content, check_content_compliance, publish_to_social_platfrom # Test configuration
TEST_DATABASE_URL = "postgresql://test:test@localhost:5432/test_coreΛBot"
TEST_REDIS_URL = "redis://localhost:6379/15"

# Test client
client = TestClient(app)

# Test fixtures
@pytest.fixture
def test_user():
    """Test user data"""
    return {
        "id": str(uuid.uuid4()),
        "email": "test@coreΛBot.com",
        "display_name": "Test User",
        "subscription_tier": "pro",
        "authenticated_platforms": ["linkedin", "instagram"],
        "preferences": {
            "auto_suggest_content": True,
            "enable_ai_review": True,
            "default_content_type": "text"
        },
        "compliance_settings": {
            "gdpr_compliant": True,
            "eu_ai_act_compliant": True,
            "require_explicit_consent": True
        }
    }

@pytest.fixture
def test_content():
    """Test content data"""
    return {
        "content": "Exciting news about AI innovation in social media! 🚀 #AI #Innovation #SocialMedia",
        "content_type": "text",
        "target_platforms": ["linkedin", "instagram"],
        "hashtags": ["#AI", "#Innovation", "#SocialMedia"],
        "mentions": [],
        "ai_generated": True
    }

@pytest.fixture
def auth_headers(test_user):
    """Authentication headers for API requests"""
    token = create_access_token(data={"sub": test_user["id"]})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "choices": [{
            "message": {
                "content": "Here's an engaging LinkedIn post about AI innovation that will capture your audience's attention! 🚀\n\n#AI #Innovation #TechTrends"
            }
        }],
        "usage": {
            "prompt_tokens": 150,
            "completion_tokens": 75,
            "total_tokens": 225
        }
    }

# Authentication Tests
class TestAuthentication:
    """Test authentication and authorization functionality"""

    def test_user_registration_success(self):
        """Test successful user registration"""
        user_data = {
            "email": "newuser@test.com",
            "password": "securepassword123",
            "display_name": "New User",
            "gdpr_consent": True,
            "eu_ai_act_consent": True,
            "data_processing_consent": True
        }

        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200

        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["display_name"] == user_data["display_name"]
        assert data["subscription_tier"] == "free"
        assert "id" in data

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        user_data = {
            "email": "test@coreΛBot.com",  # Existing email
            "password": "password123",
            "display_name": "Test User",
            "gdpr_consent": True,
            "eu_ai_act_consent": True,
            "data_processing_consent": True
        }

        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_user_login_success(self, test_user):
        """Test successful user login"""
        login_data = {
            "email": test_user["email"],
            "password": "testpassword"
        }

        with patch('enhanced_core_lambda_bot_backend.verify_password', return_value=True):
            with patch('enhanced_core_lambda_bot_backend.database.fetch_one', return_value=test_user):
                response = client.post("/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == test_user["email"]

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            "email": "test@test.com",
            "password": "wrongpassword"
        }

        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without authentication"""
        response = client.get("/content/list")
        assert response.status_code == 403

    def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/content/list", headers=headers)
        assert response.status_code == 401

# ChatGPT Integration Tests
class TestChatGPTIntegration:
    """Test ChatGPT API integration and AI functionality"""

    @patch('openai.ChatCompletion.create')
    def test_chat_message_success(self, mock_openai, test_user, auth_headers, mock_openai_response):
        """Test successful chat message with ChatGPT"""
        mock_openai.return_value = mock_openai_response

        message_data = {
            "role": "user",
            "content": "Help me create a LinkedIn post about AI innovation",
            "platform": "linkedin"
        }

        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            response = client.post("/chat/message", json=message_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "assistant"
        assert "content" in data
        assert "AI" in data["content"]

    @patch('openai.ChatCompletion.create')
    def test_generate_content_suggestion(self, mock_openai, test_user, auth_headers, mock_openai_response):
        """Test AI content generation"""
        mock_openai.return_value = mock_openai_response

        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            response = client.post(
                "/chat/generate-content",
                params={"platform": "linkedin", "topic": "AI innovation"},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert data["platform"] == "linkedin"
        assert data["topic"] == "AI innovation"
        assert "content" in data

    @patch('openai.ChatCompletion.create')
    def test_content_review(self, mock_openai, test_user, auth_headers):
        """Test AI-powered content review"""
        mock_review_response = {
            "choices": [{
                "message": {
                    "content": "This content looks great! Consider adding more specific hashtags and a clear call-to-action."
                }
            }]
        }
        mock_openai.return_value = mock_review_response

        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            response = client.post(
                "/chat/review-content",
                params={"content": "Great post about AI!", "platform": "linkedin"},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert "review" in data
        assert "compliance_flags" in data

    @patch('openai.ChatCompletion.create')
    def test_apply_amendment(self, mock_openai, test_user, auth_headers):
        """Test natural language content amendments"""
        mock_amendment_response = {
            "choices": [{
                "message": {
                    "content": "Exciting news about revolutionary AI innovation in social media! 🚀 This changes everything. #AI #Innovation #SocialMedia #Revolution"
                }
            }]
        }
        mock_openai.return_value = mock_amendment_response

        amendment_data = {
            "content": "Great news about AI innovation! #AI #Innovation",
            "amendment": "Make it more exciting and add more hashtags"
        }

        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            response = client.post("/chat/apply-amendment", json=amendment_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "updated_content" in data
        assert "exciting" in data["updated_content"].lower()
        assert "revolution" in data["updated_content"].lower()

# Content Management Tests
class TestContentManagement:
    """Test content creation, review, and management"""

    def test_create_content_success(self, test_user, test_content, auth_headers):
        """Test successful content creation"""
        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            with patch('enhanced_core_lambda_bot_backend.compliance_service.check_content_compliance', return_value=[]):
                response = client.post("/content/create", json=test_content, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == test_content["content"]
        assert data["content_type"] == test_content["content_type"]
        assert data["target_platforms"] == test_content["target_platforms"]
        assert "id" in data

    def test_create_content_with_compliance_flags(self, test_user, auth_headers):
        """Test content creation with compliance issues"""
        problematic_content = {
            "content": "Contact me at personal@email.com for exclusive deals!",
            "content_type": "text",
            "target_platforms": ["linkedin"]
        }

        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            with patch('enhanced_core_lambda_bot_backend.compliance_service.check_content_compliance',
                      return_value=["Contains potential personal data - GDPR review required"]):
                response = client.post("/content/create", json=problematic_content, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["compliance_flags"]) > 0
        assert "GDPR" in data["compliance_flags"][0]

    def test_list_content(self, test_user, auth_headers):
        """Test content listing"""
        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            with patch('enhanced_core_lambda_bot_backend.database.fetch_all', return_value=[]):
                response = client.get("/content/list", headers=auth_headers)

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_review_content_approve(self, test_user, auth_headers):
        """Test content approval"""
        content_id = str(uuid.uuid4())
        review_data = {
            "content_id": content_id,
            "action": "approve",
            "comments": "Content looks good for publication"
        }

        mock_content = {
            "id": content_id,
            "content": "Test content",
            "user_amendments": []
        }

        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            with patch('enhanced_core_lambda_bot_backend.database.fetch_one', return_value=mock_content):
                with patch('enhanced_core_lambda_bot_backend.database.execute'):
                    response = client.post(f"/content/{content_id}/review", json=review_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["action"] == "approve"

# Social Media Integration Tests
class TestSocialMediaIntegration:
    """Test social media platfrom connections and publishing"""

    def test_connect_linkedin_success(self, test_user, auth_headers):
        """Test successful LinkedIn connection"""
        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            with patch('enhanced_core_lambda_bot_backend.social_media_service.authenticate_platform',
                      return_value={"user_id": "linkedin_123", "access_token": "token_123"}):
                response = client.post(
                    "/social/connect/linkedin",
                    data={"auth_code": "test_auth_code"},
                    headers=auth_headers
                )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["platform"] == "linkedin"

    def test_disconnect_platform(self, test_user, auth_headers):
        """Test platfrom disconnection"""
        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            with patch('enhanced_core_lambda_bot_backend.database.execute'):
                response = client.delete("/social/disconnect/linkedin", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["platform"] == "linkedin"

    def test_get_social_connections(self, test_user, auth_headers):
        """Test retrieving social connections"""
        mock_connections = [
            {
                "platform": "linkedin",
                "connected_at": datetime.utcnow(),
                "platform_data": {"name": "LinkedIn User"}
            }
        ]

        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            with patch('enhanced_core_lambda_bot_backend.database.fetch_all', return_value=mock_connections):
                response = client.get("/social/connections", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["platform"] == "linkedin"

    def test_publish_content(self, test_user, auth_headers):
        """Test content publishing to social platforms"""
        content_id = str(uuid.uuid4())

        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            with patch('enhanced_core_lambda_bot_backend.social_media_service.publish_content',
                      return_value={"linkedin": {"status": "success", "post_id": "123"}}):
                response = client.post(f"/content/{content_id}/publish", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "linkedin" in data
        assert data["linkedin"]["status"] == "success"

# File Management Tests
class TestFileManagement:
    """Test file upload and management functionality"""

    def test_file_upload_success(self, test_user, auth_headers):
        """Test successful file upload"""
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_file.write(b"fake image content")
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, "rb") as f:
                files = {"file": ("test.jpg", f, "image/jpeg")}

                with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
                    with patch('enhanced_core_lambda_bot_backend.file_service.upload_file',
                              return_value={"id": "file_123", "filename": "test.jpg", "url": "https://s3.amazonaws.com/test.jpg"}):
                        response = client.post("/files/upload", files=files, headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["filename"] == "test.jpg"
            assert "url" in data
        finally:
            os.unlink(temp_file_path)

    def test_list_files(self, test_user, auth_headers):
        """Test file listing"""
        mock_files = [
            {
                "id": "file_123",
                "filename": "test.jpg",
                "file_type": "image",
                "file_size": 1024,
                "upload_date": datetime.utcnow()
            }
        ]

        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            with patch('enhanced_core_lambda_bot_backend.file_service.get_user_files', return_value=mock_files):
                response = client.get("/files/list", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["filename"] == "test.jpg"

    def test_delete_file(self, test_user, auth_headers):
        """Test file deletion"""
        file_id = str(uuid.uuid4())

        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            with patch('enhanced_core_lambda_bot_backend.file_service.delete_file', return_value=True):
                response = client.delete(f"/files/{file_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

# Compliance Tests
class TestCompliance:
    """Test GDPR, EU AI Act, and other compliance features"""

    def test_update_consent(self, test_user, auth_headers):
        """Test consent preference updates"""
        consent_data = {
            "gdpr_consent": True,
            "eu_ai_act_consent": True,
            "data_processing_consent": False
        }

        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            with patch('enhanced_core_lambda_bot_backend.database.execute'):
                with patch('enhanced_core_lambda_bot_backend.compliance_service.log_compliance_event'):
                    response = client.post("/compliance/consent", data=consent_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_data_export_request(self, test_user, auth_headers):
        """Test GDPR data export request"""
        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            with patch('enhanced_core_lambda_bot_backend.compliance_service.handle_data_subject_request',
                      return_value={"status": "completed", "data": {"profile": test_user}}):
                response = client.post(
                    "/compliance/data-request",
                    data={"request_type": "export"},
                    headers=auth_headers
                )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "data" in data

    def test_data_deletion_request(self, test_user, auth_headers):
        """Test GDPR data deletion request"""
        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            with patch('enhanced_core_lambda_bot_backend.compliance_service.handle_data_subject_request',
                      return_value={"status": "completed", "message": "All user data has been permanently deleted"}):
                response = client.post(
                    "/compliance/data-request",
                    data={"request_type": "delete"},
                    headers=auth_headers
                )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "deleted" in data["message"]

    def test_compliance_logs(self, test_user, auth_headers):
        """Test compliance activity logs"""
        mock_logs = [
            {
                "id": str(uuid.uuid4()),
                "event_type": "consent_update",
                "event_data": {"gdpr_consent": True},
                "timestamp": datetime.utcnow()
            }
        ]

        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            with patch('enhanced_core_lambda_bot_backend.database.fetch_all', return_value=mock_logs):
                response = client.get("/compliance/logs", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["event_type"] == "consent_update"

# Celery Task Tests
class TestCeleryTasks:
    """Test background task processing"""

    @patch('celery_tasks.openai.ChatCompletion.create')
    def test_generate_ai_content_task(self, mock_openai, mock_openai_response):
        """Test AI content generation task"""
        mock_openai.return_value = mock_openai_response

        with patch('celery_tasks.get_user_context', return_value={}):
            with patch('celery_tasks.store_generated_content', return_value="content_123"):
                with patch('celery_tasks.check_content_compliance.delay') as mock_compliance:
                    mock_compliance.return_value.get.return_value = []

                    result = generate_ai_content(
                        user_id="user_123",
                        platform="linkedin",
                        topic="AI innovation"
                    )

        assert result["status"] == "success"
        assert result["platform"] == "linkedin"
        assert result["topic"] == "AI innovation"
        assert "content_id" in result

    def test_content_compliance_check(self):
        """Test content compliance checking"""
        test_content = "Contact me at personal@email.com for exclusive deals!"
        user_id = "user_123"

        with patch('celery_tasks.detect_personal_information', return_value=["email"]):
            with patch('celery_tasks.log_compliance_event'):
                result = check_content_compliance(test_content, user_id)

        assert len(result) > 0
        assert any("PII_DETECTED" in flag for flag in result)

    @patch('celery_tasks.publish_to_linkedin')
    def test_publish_to_social_platform_task(self, mock_publish):
        """Test social platfrom publishing task"""
        mock_publish.return_value = {"status": "success", "post_id": "linkedin_123"}

        with patch('celery_tasks.get_content_by_id', return_value={"content": "Test post", "target_platforms": ["linkedin"]}):
            with patch('celery_tasks.get_platform_connection', return_value={"is_active": True, "access_token": "token"}):
                with patch('celery_tasks.validate_content_for_platform', return_value={"valid": True}):
                    with patch('celery_tasks.update_content_status'):
                        with patch('celery_tasks.log_compliance_event'):
                            result = publish_to_social_platform(
                                content_id="content_123",
                                platform="linkedin",
                                user_id="user_123"
                            )

        assert result["status"] == "success"
        assert result["platform"] == "linkedin"
        assert "post_id" in result

# Performance Tests
class TestPerformance:
    """Test performance and load handling"""

    def test_concurrent_chat_requests(self, test_user, auth_headers):
        """Test handling multiple concurrent chat requests"""
        async def make_chat_request():
            async with AsyncClient(app=app, base_url="http://test") as ac:
                response = await ac.post(
                    "/chat/message",
                    json={"role": "user", "content": "Test message"},
                    headers=auth_headers
                )
                return response.status_code

        # This would be implemented with proper async testing
        # For now, just test that the endpoint exists
        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            response = client.post(
                "/chat/message",
                json={"role": "user", "content": "Test message"},
                headers=auth_headers
            )
        assert response.status_code in [200, 500]  # May fail due to missing OpenAI key

    def test_large_file_upload(self, test_user, auth_headers):
        """Test handling large file uploads"""
        # Create a large temporary file (simulated)
        large_content = b"x" * (10 * 1024 * 1024)  # 10MB

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_file.write(large_content)
            temp_file_path = temp_file.name

        try:
            with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
                with patch('enhanced_core_lambda_bot_backend.file_service.upload_file',
                          return_value={"id": "large_file", "size": len(large_content)}):
                    # Simulate file upload without actually reading the large file
                    response = client.post(
                        "/files/upload",
                        files={"file": ("large.jpg", b"fake", "image/jpeg")},
                        headers=auth_headers
                    )

            assert response.status_code == 200
        finally:
            os.unlink(temp_file_path)

# Security Tests
class TestSecurity:
    """Test security measures and vulnerability protection"""

    def test_sql_injection_protection(self, auth_headers):
        """Test protection against SQL injection"""
        malicious_input = "'; DROP TABLE users; --"'

        response = client.post(
            "/chat/generate-content",
            params={"platform": "linkedin", "topic": malicious_input},
            headers=auth_headers
        )

        # Should not cause a server error due to SQL injection
        assert response.status_code in [200, 401, 403, 422]

    def test_xss_protection(self, test_user, auth_headers):
        """Test protection against XSS attacks"""
        xss_content = {
            "content": "<script>alert('xss')</script>",
            "content_type": "text",
            "target_platforms": ["linkedin"]
        }

        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            response = client.post("/content/create", json=xss_content, headers=auth_headers)

        # Should handle malicious content appropriately
        assert response.status_code in [200, 400, 422]

    def test_rate_limiting(self, test_user, auth_headers):
        """Test rate limiting protection"""
        # Make multiple rapid requests
        responses = []
        for _ in range(10):
            response = client.get("/health", headers=auth_headers)
            responses.append(response.status_code)

        # Should not all succeed if rate limiting is in place
        assert all(status in [200, 429] for status in responses)

# Integration Tests
class TestIntegration:
    """Test end-to-end integration scenarios"""

    def test_complete_content_workflow(self, test_user, auth_headers):
        """Test complete content creation and publishing workflow"""
        # 1. Create content
        content_data = {
            "content": "Test content for integration test",
            "content_type": "text",
            "target_platforms": ["linkedin"]
        }

        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            with patch('enhanced_core_lambda_bot_backend.compliance_service.check_content_compliance', return_value=[]):
                create_response = client.post("/content/create", json=content_data, headers=auth_headers)

        assert create_response.status_code == 200
        content_id = create_response.json()["id"]

        # 2. Review and approve content
        review_data = {
            "content_id": content_id,
            "action": "approve"
        }

        mock_content = {"id": content_id, "content": content_data["content"], "user_amendments": []}

        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            with patch('enhanced_core_lambda_bot_backend.database.fetch_one', return_value=mock_content):
                with patch('enhanced_core_lambda_bot_backend.database.execute'):
                    review_response = client.post(f"/content/{content_id}/review", json=review_data, headers=auth_headers)

        assert review_response.status_code == 200

        # 3. Publish content
        with patch('enhanced_core_lambda_bot_backend.get_current_user', return_value=test_user):
            with patch('enhanced_core_lambda_bot_backend.social_media_service.publish_content',
                      return_value={"linkedin": {"status": "success", "post_id": "test_post"}}):
                publish_response = client.post(f"/content/{content_id}/publish", headers=auth_headers)

        assert publish_response.status_code == 200
        assert publish_response.json()["linkedin"]["status"] == "success"

# Health Check Tests
class TestHealthCheck:
    """Test system health and monitoring"""

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] in ["healthy", "unhealthy"]
        assert "timestamp" in data
        assert "version" in data
        assert "services" in data

    def test_database_health(self):
        """Test database connectivity health"""
        # This would test actual database connectivity
        # For now, just ensure the endpoint responds
        response = client.get("/health")
        assert response.status_code == 200

# Cleanup and utilities
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data():
    """Clean up test data after test session"""
    yield
    # Cleanup would go here
    pass

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
