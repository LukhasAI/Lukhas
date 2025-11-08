"""
Tests for the Dream Commerce Engine.
"""
import sys
from unittest.mock import AsyncMock, MagicMock, patch

# Mock modules that cause import errors before importing the application code
mock_governance_interface = MagicMock()
sys.modules['governance.identity.interface'] = mock_governance_interface
sys.modules['privacy.zkp_dream_validator'] = MagicMock()
sys.modules['core.event_bus'] = MagicMock()

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.bridge.dream_commerce import (
    ConsentLevel,
    DreamCommerceEngine,
    DreamExperienceRequest,
    DreamMarketplaceFilter,
    DreamSeedSubmission,
    DreamSeedType,
    RevenueModel,
    router,
)


@pytest.fixture
def commerce_engine():
    """Provides a DreamCommerceEngine instance with mocked dependencies."""
    # The modules are already mocked via sys.modules, so we can just instantiate the engine.
    engine = DreamCommerceEngine()
    # Reset mocks for each test
    engine.event_bus = AsyncMock()
    return engine

@pytest.fixture
def test_client():
    """Provides a TestClient for the FastAPI router by creating a full app."""
    app = FastAPI()
    app.include_router(router)
    with patch('core.bridge.dream_commerce.commerce_engine', new=DreamCommerceEngine()):
        yield TestClient(app)

@pytest.mark.asyncio
class TestDreamCommerceEngine:
    """Tests for the DreamCommerceEngine class."""

    async def test_create_dream_seed_success(self, commerce_engine: DreamCommerceEngine):
        """Test successful creation of a dream seed."""
        submission = DreamSeedSubmission(
            seed_type=DreamSeedType.CREATIVE,
            title="Test Dream Seed",
            description="A dream seed for testing.",
            symbolic_prompts={"text": "A calm beach at sunset."},
            target_emotions=["calm", "serene"],
            consent_requirements=ConsentLevel.STANDARD,
            revenue_model=RevenueModel.PAY_PER_DREAM,
            creator_revenue_share=0.7,
            ethical_boundaries=["no_harm", "respect_privacy", "honest_representation"],
        )
        creator_id = "creator-123"

        # Mock the ethical validation to return approved
        with patch.object(commerce_engine, '_validate_ethical_boundaries', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {"approved": True}

            dream_seed = await commerce_engine.create_dream_seed(creator_id, submission)

            assert dream_seed is not None
            assert dream_seed.creator_id == creator_id
            assert dream_seed.title == submission.title
            assert dream_seed.seed_id in commerce_engine.dream_seeds
            assert commerce_engine.dream_seeds[dream_seed.seed_id] == dream_seed
            assert commerce_engine.total_seeds_created == 1
            commerce_engine.event_bus.publish.assert_called_once()

    async def test_create_dream_seed_ethical_validation_fails(self, commerce_engine: DreamCommerceEngine):
        """Test dream seed creation failure due to ethical validation."""
        submission = DreamSeedSubmission(
            seed_type=DreamSeedType.CREATIVE,
            title="Unethical Dream Seed",
            description="An unethical dream seed for testing.",
            symbolic_prompts={"text": "A violent and harmful dream."},
            target_emotions=["anger", "fear"],
            consent_requirements=ConsentLevel.STANDARD,
            revenue_model=RevenueModel.FREE,
            creator_revenue_share=0.0,
            ethical_boundaries=[],
        )
        creator_id = "creator-456"

        # Mock the ethical validation to return rejected
        with patch.object(commerce_engine, '_validate_ethical_boundaries', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {"approved": False, "reason": "Contains forbidden content"}

            with pytest.raises(Exception) as excinfo:
                await commerce_engine.create_dream_seed(creator_id, submission)

            assert "Ethical validation failed" in str(excinfo.value)
            assert commerce_engine.total_seeds_created == 0

    async def test_generate_dream_experience_success(self, commerce_engine: DreamCommerceEngine):
        """Test successful generation of a dream experience."""
        # First, create a dream seed
        submission = DreamSeedSubmission(
            seed_type=DreamSeedType.CREATIVE,
            title="Test Dream Seed",
            description="A dream seed for testing.",
            symbolic_prompts={"text": "A calm beach at sunset."},
            target_emotions=["calm", "serene"],
            consent_requirements=ConsentLevel.STANDARD,
            revenue_model=RevenueModel.PAY_PER_DREAM,
            creator_revenue_share=0.7,
            ethical_boundaries=["no_harm", "respect_privacy", "honest_representation"],
        )
        creator_id = "creator-123"
        with patch.object(commerce_engine, '_validate_ethical_boundaries', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {"approved": True}
            dream_seed = await commerce_engine.create_dream_seed(creator_id, submission)

        # Now, generate a dream experience
        request = DreamExperienceRequest(
            user_id="user-789",
            dream_seed_id=dream_seed.seed_id,
            personalization_level=0.7,
            experience_duration=20,
            visualization_format="narrative",
            include_sora_video=True,
            consent_confirmation={"dream_experience_generation": True, "data_processing": True, "personalization": True, "payment_processing": True},
            payment_details={"method": "credit_card"},
        )

        with patch.object(commerce_engine, '_verify_user_consent', new_callable=AsyncMock) as mock_consent, \
             patch.object(commerce_engine, '_process_payment', new_callable=AsyncMock) as mock_payment, \
             patch.object(commerce_engine, '_generate_personalized_dream_content', new_callable=AsyncMock) as mock_content, \
             patch.object(commerce_engine, '_generate_dream_visualization', new_callable=AsyncMock) as mock_viz, \
             patch.object(commerce_engine, '_generate_sora_video', new_callable=AsyncMock) as mock_sora, \
             patch.object(commerce_engine, '_process_revenue_sharing', new_callable=AsyncMock) as mock_revenue:

            mock_consent.return_value = True
            mock_payment.return_value = {"success": True, "amount": 2.99}
            mock_content.return_value = {"title": "Personalized Dream"}
            mock_viz.return_value = {"format": "narrative", "content": "..."}
            mock_sora.return_value = "https://sora.example.com/video.mp4"

            # Configure the ZKP validator mock to be awaitable
            commerce_engine.zkp_validator.generate_emotional_range_proof = AsyncMock(return_value=MagicMock(proof_id="zkp_proof_123"))

            dream_experience = await commerce_engine.generate_dream_experience(request)

            assert dream_experience is not None
            assert dream_experience.user_id == request.user_id
            assert dream_experience.dream_seed_id == dream_seed.seed_id
            assert dream_experience.experience_id in commerce_engine.dream_experiences
            assert commerce_engine.total_experiences_generated == 1
            mock_revenue.assert_called_once()
            commerce_engine.event_bus.publish_dream_event.assert_called_once()

    async def test_generate_dream_experience_consent_fails(self, commerce_engine: DreamCommerceEngine):
        """Test dream experience generation failure due to insufficient consent."""
        # First, create a dream seed
        submission = DreamSeedSubmission(
            seed_type=DreamSeedType.CREATIVE,
            title="Test Dream Seed",
            description="A dream seed for testing.",
            symbolic_prompts={"text": "A calm beach at sunset."},
            target_emotions=["calm", "serene"],
            consent_requirements=ConsentLevel.STANDARD,
            revenue_model=RevenueModel.PAY_PER_DREAM,
            creator_revenue_share=0.7,
            ethical_boundaries=["no_harm", "respect_privacy", "honest_representation"],
        )
        creator_id = "creator-123"
        with patch.object(commerce_engine, '_validate_ethical_boundaries', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {"approved": True}
            dream_seed = await commerce_engine.create_dream_seed(creator_id, submission)

        # Now, generate a dream experience with missing consent
        request = DreamExperienceRequest(
            user_id="user-789",
            dream_seed_id=dream_seed.seed_id,
            personalization_level=0.7,
            experience_duration=20,
            visualization_format="narrative",
            include_sora_video=True,
            consent_confirmation={"dream_experience_generation": True},  # Missing consents
            payment_details={"method": "credit_card"},
        )

        with patch.object(commerce_engine, '_verify_user_consent', new_callable=AsyncMock) as mock_consent:
            mock_consent.return_value = False

            with pytest.raises(Exception) as excinfo:
                await commerce_engine.generate_dream_experience(request)

            assert "Insufficient or invalid consent" in str(excinfo.value)
            assert commerce_engine.total_experiences_generated == 0

    async def test_get_marketplace_dreams_with_filters(self, commerce_engine: DreamCommerceEngine):
        """Test filtering marketplace dreams."""
        # Create some dream seeds
        submission1 = DreamSeedSubmission(
            seed_type=DreamSeedType.CREATIVE,
            title="Creative Dream",
            description="A creative dream.",
            symbolic_prompts={},
            consent_requirements=ConsentLevel.STANDARD,
            revenue_model=RevenueModel.FREE,
            ethical_boundaries=["no_harm", "respect_privacy", "honest_representation"],
        )
        submission2 = DreamSeedSubmission(
            seed_type=DreamSeedType.BRAND,
            title="Brand Dream",
            description="A brand dream.",
            symbolic_prompts={},
            consent_requirements=ConsentLevel.ENHANCED,
            revenue_model=RevenueModel.SPONSORED,
            ethical_boundaries=["no_harm", "respect_privacy", "honest_representation"],
        )
        with patch.object(commerce_engine, '_validate_ethical_boundaries', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {"approved": True}
            await commerce_engine.create_dream_seed("creator-1", submission1)
            await commerce_engine.create_dream_seed("creator-2", submission2)

        # Apply filters
        filters = DreamMarketplaceFilter(seed_types=[DreamSeedType.BRAND])
        filtered_seeds = await commerce_engine.get_marketplace_dreams(filters)

        assert len(filtered_seeds) == 1
        assert filtered_seeds[0].title == "Brand Dream"

        filters = DreamMarketplaceFilter(revenue_models=[RevenueModel.FREE])
        filtered_seeds = await commerce_engine.get_marketplace_dreams(filters)

        assert len(filtered_seeds) == 1
        assert filtered_seeds[0].title == "Creative Dream"

    @pytest.mark.parametrize(
        "prompts, boundaries, expected_approved, expected_reason",
        [
            ({"text": "A peaceful meadow."}, ["no_harm", "respect_privacy", "honest_representation"], True, "Passed ethical validation"),
            ({"text": "A dream of violence."}, ["no_harm", "respect_privacy", "honest_representation"], False, "Contains forbidden content: violence"),
            ({"text": "A peaceful meadow."}, ["respect_privacy"], False, "Missing required ethical boundary: no_harm"),
        ],
    )
    async def test_validate_ethical_boundaries(
        self, commerce_engine: DreamCommerceEngine, prompts, boundaries, expected_approved, expected_reason
    ):
        """Test the _validate_ethical_boundaries method."""
        result = await commerce_engine._validate_ethical_boundaries(prompts, boundaries)
        assert result["approved"] == expected_approved
        assert expected_reason in result["reason"]

    @pytest.mark.parametrize(
        "revenue_model, seed_type, expected_price",
        [
            (RevenueModel.FREE, DreamSeedType.CREATIVE, 0.00),
            (RevenueModel.PAY_PER_DREAM, DreamSeedType.CREATIVE, 2.99),
            (RevenueModel.SUBSCRIPTION, DreamSeedType.CREATIVE, 9.99),
            (RevenueModel.SPONSORED, DreamSeedType.CREATIVE, 0.00),
        ],
    )
    async def test_calculate_dream_seed_price(
        self, commerce_engine: DreamCommerceEngine, revenue_model, seed_type, expected_price
    ):
        """Test the _calculate_dream_seed_price method."""
        submission = DreamSeedSubmission(
            seed_type=seed_type,
            title="Test Price",
            description="Test price calculation.",
            symbolic_prompts={},
            revenue_model=revenue_model,
            ethical_boundaries=["no_harm", "respect_privacy", "honest_representation"],
        )
        price = await commerce_engine._calculate_dream_seed_price(submission)
        assert float(price) == expected_price

    async def test_process_payment(self, commerce_engine: DreamCommerceEngine):
        """Test the _process_payment method."""
        submission = DreamSeedSubmission(
            seed_type=DreamSeedType.CREATIVE,
            title="Test Payment",
            description="Test payment processing.",
            symbolic_prompts={},
            revenue_model=RevenueModel.PAY_PER_DREAM,
            ethical_boundaries=["no_harm", "respect_privacy", "honest_representation"],
        )
        with patch.object(commerce_engine, '_validate_ethical_boundaries', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {"approved": True}
            dream_seed = await commerce_engine.create_dream_seed("creator-1", submission)

        # Test payment with no details
        result = await commerce_engine._process_payment("user-1", dream_seed, None)
        assert not result["success"]

        # Test successful payment
        result = await commerce_engine._process_payment("user-1", dream_seed, {"method": "test"})
        assert result["success"]
        assert result["amount"] > 0

    async def test_generate_personalized_dream_content(self, commerce_engine: DreamCommerceEngine):
        """Test the _generate_personalized_dream_content method."""
        submission = DreamSeedSubmission(
            seed_type=DreamSeedType.CREATIVE,
            title="Test Content",
            description="Test content generation.",
            symbolic_prompts={},
            revenue_model=RevenueModel.FREE,
            ethical_boundaries=["no_harm", "respect_privacy", "honest_representation"],
        )
        with patch.object(commerce_engine, '_validate_ethical_boundaries', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {"approved": True}
            dream_seed = await commerce_engine.create_dream_seed("creator-1", submission)

        content = await commerce_engine._generate_personalized_dream_content(dream_seed, "user-1", 0.9, 10)
        assert "advanced_personalization" in content

    async def test_generate_dream_visualization(self, commerce_engine: DreamCommerceEngine):
        """Test the _generate_dream_visualization method."""
        content = {"title": "Test Viz"}
        viz = await commerce_engine._generate_dream_visualization(content, "interactive")
        assert viz["format"] == "interactive"

    async def test_generate_sora_video(self, commerce_engine: DreamCommerceEngine):
        """Test the _generate_sora_video method."""
        url = await commerce_engine._generate_sora_video({"description": "A test video"}, {})
        assert "sora-api.example.com" in url

    async def test_process_revenue_sharing(self, commerce_engine: DreamCommerceEngine):
        """Test the _process_revenue_sharing method."""
        submission = DreamSeedSubmission(
            seed_type=DreamSeedType.CREATIVE,
            title="Test Revenue",
            description="Test revenue sharing.",
            symbolic_prompts={},
            revenue_model=RevenueModel.PAY_PER_DREAM,
            creator_revenue_share=0.7,
            ethical_boundaries=["no_harm", "respect_privacy", "honest_representation"],
        )
        with patch.object(commerce_engine, '_validate_ethical_boundaries', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {"approved": True}
            dream_seed = await commerce_engine.create_dream_seed("creator-1", submission)

        await commerce_engine._process_revenue_sharing(dream_seed, {"amount": 10.0})
        assert dream_seed.revenue_generated > 0


class TestDreamCommerceEngineSync:
    """Synchronous tests for the DreamCommerceEngine class."""

    def test_get_commerce_stats(self, commerce_engine: DreamCommerceEngine):
        """Test the get_commerce_stats method."""
        stats = commerce_engine.get_commerce_stats()
        assert stats["total_seeds_created"] == 0
        assert stats["total_revenue_processed"] == 0.0

class TestDreamCommerceAPI:
    """Tests for the Dream Commerce FastAPI endpoints."""

    def test_create_dream_seed_endpoint_success(self, test_client: TestClient):
        """Test the POST /seeds endpoint."""
        submission_data = {
            "seed_type": "creative",
            "title": "API Test Dream Seed",
            "description": "A dream seed created via the API.",
            "symbolic_prompts": {"text": "A futuristic city."},
            "target_emotions": ["excitement", "wonder"],
            "consent_requirements": "standard",
            "revenue_model": "pay_per_dream",
            "creator_revenue_share": 0.8,
            "ethical_boundaries": ["no_harm", "respect_privacy", "honest_representation"],
        }

        with patch('core.bridge.dream_commerce.commerce_engine.create_dream_seed', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = MagicMock(seed_id="seed-123", title="API Test Dream Seed", seed_type=MagicMock(value="creative"), price=2.99, revenue_model=MagicMock(value="pay_per_dream"), created_at=MagicMock(isoformat=lambda: "2025-11-06T18:00:00Z"))

            response = test_client.post("/dream/commerce/seeds?creator_id=api-creator", json=submission_data)

            assert response.status_code == 200
            response_data = response.json()
            assert response_data["status"] == "success"
            assert response_data["data"]["seed_id"] == "seed-123"
            mock_create.assert_called_once()

    def test_generate_dream_experience_endpoint_success(self, test_client: TestClient):
        """Test the POST /experiences endpoint."""
        request_data = {
            "user_id": "api-user",
            "dream_seed_id": "seed-123",
            "personalization_level": 0.8,
            "experience_duration": 30,
            "visualization_format": "interactive",
            "include_sora_video": False,
            "consent_confirmation": {"dream_experience_generation": True, "data_processing": True, "personalization": True},
        }

        with patch('core.bridge.dream_commerce.commerce_engine.generate_dream_experience', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = MagicMock(experience_id="exp-456", dream_content={"title": "API Dream"}, visualization_content=None, sora_video_url=None, privacy_proof=None, created_at=MagicMock(isoformat=lambda: "2025-11-06T18:00:00Z"))

            response = test_client.post("/dream/commerce/experiences", json=request_data)

            assert response.status_code == 200
            response_data = response.json()
            assert response_data["status"] == "success"
            assert response_data["data"]["experience_id"] == "exp-456"
            mock_generate.assert_called_once()

    def test_browse_marketplace_endpoint_success(self, test_client: TestClient):
        """Test the GET /marketplace endpoint."""
        with patch('core.bridge.dream_commerce.commerce_engine.get_marketplace_dreams', new_callable=AsyncMock) as mock_browse:
            mock_browse.return_value = [MagicMock(seed_id="seed-123", title="Marketplace Dream", description="...", seed_type=MagicMock(value="creative"), price=2.99, rating=4.5, usage_count=100, revenue_model=MagicMock(value="pay_per_dream"), consent_requirements=MagicMock(value="standard"), tags=[], created_at=MagicMock(isoformat=lambda: "2025-11-06T18:00:00Z"))]

            response = test_client.get("/dream/commerce/marketplace?seed_types=creative")

            assert response.status_code == 200
            response_data = response.json()
            assert response_data["status"] == "success"
            assert len(response_data["data"]["seeds"]) == 1
            assert response_data["data"]["seeds"][0]["seed_id"] == "seed-123"
            mock_browse.assert_called_once()

    def test_get_commerce_statistics_endpoint_success(self, test_client: TestClient):
        """Test the GET /stats endpoint."""
        with patch('core.bridge.dream_commerce.commerce_engine.get_commerce_stats') as mock_stats:
            mock_stats.return_value = {"total_seeds_created": 10, "total_revenue_processed": 123.45}

            response = test_client.get("/dream/commerce/stats")

            assert response.status_code == 200
            response_data = response.json()
            assert response_data["status"] == "success"
            assert response_data["data"]["total_seeds_created"] == 10
            mock_stats.assert_called_once()

    def test_commerce_health_check_endpoint_success(self, test_client: TestClient):
        """Test the GET /health endpoint."""
        response = test_client.get("/dream/commerce/health")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status"] == "success"
        assert response_data["data"]["status"] == "operational"
