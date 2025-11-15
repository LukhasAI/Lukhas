"""Comprehensive tests for Blockchain Integration in Dream Commerce."""
import json
import pytest
from decimal import Decimal
from datetime import datetime, timezone
from unittest.mock import Mock, MagicMock, patch, PropertyMock

from core.bridge.dream_commerce import (
    DreamCommerceBlockchain,
    DreamContentNFT,
    ConsentRecord,
    WEB3_AVAILABLE,
    IPFS_AVAILABLE,
    DreamCommerceEngine,
)

# Skip all tests if Web3 not available
pytestmark = pytest.mark.skipif(
    not WEB3_AVAILABLE, reason="Web3 dependencies not available"
)


class TestDreamContentNFTDataclass:
    """Test suite for DreamContentNFT dataclass."""

    def test_create_nft_dataclass(self):
        """Test creating DreamContentNFT instance."""
        nft = DreamContentNFT(
            token_id=1,
            dream_seed_id="dream_123",
            creator_address="0x123",
            content_hash="Qm123",
            metadata_uri="ipfs://Qm456",
            mint_timestamp=datetime.now(timezone.utc),
            royalty_percentage=Decimal("10"),
        )

        assert nft.token_id == 1
        assert nft.dream_seed_id == "dream_123"
        assert nft.creator_address == "0x123"
        assert nft.content_hash == "Qm123"
        assert nft.metadata_uri == "ipfs://Qm456"
        assert nft.royalty_percentage == Decimal("10")
        assert nft.blockchain_network == "ethereum"  # Default

    def test_nft_with_custom_network(self):
        """Test NFT with custom blockchain network."""
        nft = DreamContentNFT(
            token_id=1,
            dream_seed_id="dream_123",
            creator_address="0x123",
            content_hash="Qm123",
            metadata_uri="ipfs://Qm456",
            mint_timestamp=datetime.now(timezone.utc),
            royalty_percentage=Decimal("15"),
            blockchain_network="polygon",
        )

        assert nft.blockchain_network == "polygon"


class TestConsentRecordDataclass:
    """Test suite for ConsentRecord dataclass."""

    def test_create_consent_record(self):
        """Test creating ConsentRecord instance."""
        record = ConsentRecord(
            user_address="0x456",
            dream_seed_id="dream_123",
            consent_given=True,
            timestamp=datetime.now(timezone.utc),
            transaction_hash="0xabc",
        )

        assert record.user_address == "0x456"
        assert record.dream_seed_id == "dream_123"
        assert record.consent_given is True
        assert record.transaction_hash == "0xabc"
        assert record.consent_type == "dream_experience"  # Default
        assert record.revocable is True  # Default

    def test_consent_record_with_ipfs_proof(self):
        """Test consent record with IPFS proof."""
        record = ConsentRecord(
            user_address="0x456",
            dream_seed_id="dream_123",
            consent_given=True,
            timestamp=datetime.now(timezone.utc),
            transaction_hash="0xabc",
            ipfs_proof_hash="Qm789",
        )

        assert record.ipfs_proof_hash == "Qm789"


class TestDreamCommerceBlockchain:
    """Test suite for DreamCommerceBlockchain class."""

    @pytest.fixture
    def mock_web3(self):
        """Mock Web3 instance."""
        with patch("core.bridge.dream_commerce.Web3") as mock_w3_class:
            mock_w3 = MagicMock()
            mock_w3.is_connected.return_value = True
            mock_w3.eth.gas_price = 1000000000
            mock_w3.eth.chain_id = 137  # Polygon
            mock_w3.eth.block_number = 12345
            mock_w3_class.return_value = mock_w3
            mock_w3_class.to_checksum_address = lambda addr: addr
            yield mock_w3

    @pytest.fixture
    def mock_ipfs(self):
        """Mock IPFS client."""
        with patch("core.bridge.dream_commerce.ipfshttpclient") as mock_ipfs_module:
            mock_client = MagicMock()
            mock_client.version.return_value = {"Version": "0.12.0"}
            mock_client.add_bytes.return_value = "Qm123abc"
            mock_ipfs_module.connect.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def blockchain(self, mock_web3, mock_ipfs):
        """Create blockchain instance with mocks."""
        bc = DreamCommerceBlockchain(
            blockchain_rpc_url="http://localhost:8545",
            dream_nft_contract_address="0x" + "1" * 40,
            consent_ledger_address="0x" + "2" * 40,
            private_key="0x" + "a" * 64,
        )
        yield bc

    def test_initialization_success(self, blockchain, mock_web3):
        """Test successful blockchain initialization."""
        assert blockchain.w3 is not None
        assert blockchain.dream_nft_address == "0x" + "1" * 40
        assert blockchain.consent_ledger_address == "0x" + "2" * 40
        assert blockchain.network_id == "ethereum"
        assert mock_web3.is_connected.called

    def test_initialization_without_web3(self):
        """Test initialization fails gracefully without Web3."""
        with patch("core.bridge.dream_commerce.WEB3_AVAILABLE", False):
            with pytest.raises(ImportError, match="web3"):
                DreamCommerceBlockchain()

    def test_initialization_connection_failure(self):
        """Test initialization fails with connection error."""
        with patch("core.bridge.dream_commerce.Web3") as mock_w3_class:
            mock_w3 = MagicMock()
            mock_w3.is_connected.return_value = False
            mock_w3_class.return_value = mock_w3

            with pytest.raises(ConnectionError, match="Cannot connect"):
                DreamCommerceBlockchain(blockchain_rpc_url="http://bad-url")

    def test_upload_to_ipfs_success(self, blockchain):
        """Test successful IPFS upload."""
        content = b"test dream content"
        ipfs_hash = blockchain.upload_to_ipfs(content)

        assert ipfs_hash == "Qm123abc"
        blockchain._ipfs_client.add_bytes.assert_called_once_with(content)

    def test_upload_to_ipfs_without_client(self, blockchain):
        """Test IPFS upload fails without client."""
        blockchain._ipfs_client = None

        with pytest.raises(RuntimeError, match="IPFS client not available"):
            blockchain.upload_to_ipfs(b"content")

    def test_upload_to_ipfs_error_handling(self, blockchain):
        """Test IPFS upload error handling."""
        blockchain._ipfs_client.add_bytes.side_effect = Exception("IPFS error")

        with pytest.raises(RuntimeError, match="Failed to upload to IPFS"):
            blockchain.upload_to_ipfs(b"content")

    def test_mint_dream_nft_success(self, blockchain):
        """Test successful NFT minting."""
        # Mock IPFS uploads
        with patch.object(
            blockchain, "upload_to_ipfs", side_effect=["Qm123content", "Qm456metadata"]
        ):
            # Mock contract transaction
            mock_mint_func = MagicMock()
            mock_build = MagicMock()
            mock_build.build_transaction.return_value = {
                "from": "0xsender",
                "nonce": 0,
                "gas": 250000,
                "gasPrice": 1100000000,
            }
            mock_mint_func.return_value = mock_build
            blockchain.dream_nft_contract.functions.mintDreamNFT = mock_mint_func

            # Mock account and transaction
            mock_account = MagicMock()
            mock_account.address = "0x" + "3" * 40
            mock_signed_tx = MagicMock()
            mock_signed_tx.raw_transaction = b"\x12\x34"

            with patch.object(
                blockchain.w3.eth.account, "from_key", return_value=mock_account
            ):
                with patch.object(
                    mock_account, "sign_transaction", return_value=mock_signed_tx
                ):
                    with patch.object(
                        blockchain.w3.eth, "get_transaction_count", return_value=0
                    ):
                        with patch.object(
                            blockchain.w3.eth,
                            "send_raw_transaction",
                            return_value=b"\xab\xcd",
                        ):
                            mock_receipt = {
                                "status": 1,
                                "logs": [{"topics": [b"", b"\x00" * 31 + b"\x01"]}],
                            }
                            with patch.object(
                                blockchain.w3.eth,
                                "wait_for_transaction_receipt",
                                return_value=mock_receipt,
                            ):
                                nft = blockchain.mint_dream_nft(
                                    dream_seed_id="dream_001",
                                    content=b"dream content",
                                    creator_address="0x" + "3" * 40,
                                    royalty_percentage=Decimal("10"),
                                    metadata={"name": "Test Dream"},
                                )

                                assert isinstance(nft, DreamContentNFT)
                                assert nft.token_id == 1
                                assert nft.dream_seed_id == "dream_001"
                                assert nft.content_hash == "Qm123content"
                                assert nft.metadata_uri == "ipfs://Qm456metadata"
                                assert nft.creator_address == "0x" + "3" * 40
                                assert nft.royalty_percentage == Decimal("10")

    def test_mint_nft_without_contract(self, blockchain):
        """Test minting fails without contract."""
        blockchain.dream_nft_contract = None

        with pytest.raises(RuntimeError, match="Dream NFT contract not initialized"):
            blockchain.mint_dream_nft(
                dream_seed_id="dream_001",
                content=b"content",
                creator_address="0x123",
                royalty_percentage=Decimal("10"),
                metadata={},
            )

    def test_mint_nft_without_private_key(self, blockchain):
        """Test minting fails without private key."""
        blockchain._private_key = None

        with pytest.raises(RuntimeError, match="Private key required"):
            blockchain.mint_dream_nft(
                dream_seed_id="dream_001",
                content=b"content",
                creator_address="0x123",
                royalty_percentage=Decimal("10"),
                metadata={},
            )

    def test_record_consent_on_chain_success(self, blockchain):
        """Test successful consent recording."""
        # Mock contract transaction
        mock_record_func = MagicMock()
        mock_build = MagicMock()
        mock_build.build_transaction.return_value = {
            "from": "0xsender",
            "nonce": 0,
            "gas": 100000,
            "gasPrice": 1100000000,
        }
        mock_record_func.return_value = mock_build
        blockchain.consent_ledger_contract.functions.recordConsent = mock_record_func

        # Mock account and transaction
        mock_account = MagicMock()
        mock_account.address = "0x" + "4" * 40
        mock_signed_tx = MagicMock()
        mock_signed_tx.raw_transaction = b"\xef\xgh"

        with patch.object(
            blockchain.w3.eth.account, "from_key", return_value=mock_account
        ):
            with patch.object(
                mock_account, "sign_transaction", return_value=mock_signed_tx
            ):
                with patch.object(
                    blockchain.w3.eth, "get_transaction_count", return_value=0
                ):
                    with patch.object(
                        blockchain.w3.eth,
                        "send_raw_transaction",
                        return_value=b"\xij\kl",
                    ):
                        mock_receipt = {"status": 1}
                        with patch.object(
                            blockchain.w3.eth,
                            "wait_for_transaction_receipt",
                            return_value=mock_receipt,
                        ):
                            # Mock IPFS upload for proof
                            with patch.object(
                                blockchain, "upload_to_ipfs", return_value="Qmproof"
                            ):
                                record = blockchain.record_consent_on_chain(
                                    user_address="0x" + "4" * 40,
                                    dream_seed_id="dream_001",
                                    consent_given=True,
                                )

                                assert isinstance(record, ConsentRecord)
                                assert record.user_address == "0x" + "4" * 40
                                assert record.dream_seed_id == "dream_001"
                                assert record.consent_given is True
                                assert record.ipfs_proof_hash == "Qmproof"

    def test_record_consent_without_contract(self, blockchain):
        """Test consent recording fails without contract."""
        blockchain.consent_ledger_contract = None

        with pytest.raises(RuntimeError, match="Consent ledger contract not initialized"):
            blockchain.record_consent_on_chain(
                user_address="0x123", dream_seed_id="dream_001", consent_given=True
            )

    def test_verify_consent_on_chain_success(self, blockchain):
        """Test successful consent verification."""
        mock_get_func = MagicMock()
        mock_call = MagicMock()
        mock_call.call.return_value = True
        mock_get_func.return_value = mock_call
        blockchain.consent_ledger_contract.functions.getConsent = mock_get_func

        with patch("core.bridge.dream_commerce.Web3") as mock_w3_class:
            mock_w3_class.to_checksum_address = lambda addr: addr

            consent = blockchain.verify_consent_on_chain(
                user_address="0x" + "4" * 40, dream_seed_id="dream_001"
            )

            assert consent is True

    def test_verify_consent_without_contract(self, blockchain):
        """Test consent verification fails without contract."""
        blockchain.consent_ledger_contract = None

        with pytest.raises(RuntimeError, match="Consent ledger contract not initialized"):
            blockchain.verify_consent_on_chain(
                user_address="0x123", dream_seed_id="dream_001"
            )

    def test_calculate_royalty_distribution(self, blockchain):
        """Test royalty distribution calculation."""
        distribution = blockchain.calculate_royalty_distribution(
            token_id=1, sale_amount=Decimal("1000")
        )

        assert "creator" in distribution
        assert "seller" in distribution
        assert "platform" in distribution

        # With 10% royalty and 2.5% platform fee
        assert distribution["creator"] == Decimal("100")  # 10%
        assert distribution["platform"] == Decimal("25")  # 2.5%
        assert distribution["seller"] == Decimal("875")  # 87.5%

    def test_get_nft_owner_success(self, blockchain):
        """Test getting NFT owner."""
        mock_owner_func = MagicMock()
        mock_owner_func.return_value.call.return_value = "0x" + "5" * 40
        blockchain.dream_nft_contract.functions.ownerOf = lambda token_id: mock_owner_func

        owner = blockchain.get_nft_owner(1)

        assert owner == "0x" + "5" * 40

    def test_get_connection_info(self, blockchain):
        """Test getting connection information."""
        info = blockchain.get_connection_info()

        assert info["connected"] is True
        assert info["network_id"] == "ethereum"
        assert info["chain_id"] == 137
        assert info["latest_block"] == 12345
        assert info["nft_contract_address"] == "0x" + "1" * 40
        assert info["consent_ledger_address"] == "0x" + "2" * 40


class TestDreamCommerceEngineBlockchainIntegration:
    """Test suite for DreamCommerceEngine blockchain integration."""

    @pytest.fixture
    def mock_blockchain(self):
        """Mock blockchain instance."""
        mock_bc = MagicMock()
        mock_bc.dream_nft_address = "0x" + "1" * 40
        mock_bc.get_connection_info.return_value = {
            "connected": True,
            "network_id": "ethereum",
            "chain_id": 1,
        }
        return mock_bc

    @pytest.fixture
    async def engine_with_blockchain(self, mock_blockchain):
        """Create engine with mocked blockchain."""
        with patch("core.bridge.dream_commerce.WEB3_AVAILABLE", True):
            with patch(
                "core.bridge.dream_commerce.DreamCommerceBlockchain",
                return_value=mock_blockchain,
            ):
                engine = DreamCommerceEngine(
                    enable_blockchain=True,
                    blockchain_config={"blockchain_rpc_url": "http://localhost:8545"},
                )
                await engine.initialize()
                yield engine

    def test_engine_initialization_with_blockchain(self):
        """Test engine initializes with blockchain enabled."""
        with patch("core.bridge.dream_commerce.WEB3_AVAILABLE", True):
            with patch("core.bridge.dream_commerce.DreamCommerceBlockchain"):
                engine = DreamCommerceEngine(enable_blockchain=True)

                assert engine._enable_blockchain is True
                assert engine._blockchain is not None
                assert engine.total_nfts_minted == 0

    def test_engine_initialization_without_blockchain(self):
        """Test engine initializes without blockchain."""
        engine = DreamCommerceEngine(enable_blockchain=False)

        assert engine._enable_blockchain is False
        assert engine._blockchain is None

    @pytest.mark.asyncio
    async def test_publish_dream_seed_as_nft(self, engine_with_blockchain):
        """Test publishing dream seed as NFT."""
        # Create a dream seed first
        from core.bridge.dream_commerce import DreamSeedSubmission, DreamSeedType

        submission = DreamSeedSubmission(
            seed_type=DreamSeedType.CREATIVE,
            title="Test Dream",
            description="A test dream seed",
            symbolic_prompts={"image": "test.png"},
            consent_requirements="standard",
            revenue_model="free",
        )

        dream_seed = await engine_with_blockchain.create_dream_seed(
            "creator_001", submission
        )

        # Mock NFT minting
        mock_nft = DreamContentNFT(
            token_id=1,
            dream_seed_id=dream_seed.seed_id,
            creator_address="0x" + "6" * 40,
            content_hash="Qm123",
            metadata_uri="ipfs://Qm456",
            mint_timestamp=datetime.now(timezone.utc),
            royalty_percentage=Decimal("10"),
        )

        engine_with_blockchain._blockchain.mint_dream_nft.return_value = mock_nft

        # Publish as NFT
        nft = await engine_with_blockchain.publish_dream_seed_as_nft(
            dream_seed_id=dream_seed.seed_id,
            content=b"dream content",
            creator_blockchain_address="0x" + "6" * 40,
            royalty_percentage=Decimal("10"),
        )

        assert nft.token_id == 1
        assert nft.dream_seed_id == dream_seed.seed_id
        assert engine_with_blockchain.total_nfts_minted == 1
        assert dream_seed.seed_id in engine_with_blockchain.minted_nfts

    @pytest.mark.asyncio
    async def test_publish_nft_without_blockchain(self):
        """Test publishing NFT fails without blockchain enabled."""
        engine = DreamCommerceEngine(enable_blockchain=False)

        with pytest.raises(RuntimeError, match="Blockchain features not enabled"):
            await engine.publish_dream_seed_as_nft(
                dream_seed_id="dream_001",
                content=b"content",
                creator_blockchain_address="0x123",
            )

    @pytest.mark.asyncio
    async def test_record_consent_on_blockchain(self, engine_with_blockchain):
        """Test recording consent on blockchain."""
        mock_consent_record = ConsentRecord(
            user_address="0x" + "7" * 40,
            dream_seed_id="dream_001",
            consent_given=True,
            timestamp=datetime.now(timezone.utc),
            transaction_hash="0xtxhash",
        )

        engine_with_blockchain._blockchain.record_consent_on_chain.return_value = (
            mock_consent_record
        )

        record = await engine_with_blockchain.record_consent_on_blockchain(
            user_blockchain_address="0x" + "7" * 40,
            dream_seed_id="dream_001",
            consent_given=True,
        )

        assert record.user_address == "0x" + "7" * 40
        assert record.consent_given is True
        assert record.transaction_hash == "0xtxhash"

    @pytest.mark.asyncio
    async def test_verify_blockchain_consent(self, engine_with_blockchain):
        """Test verifying consent from blockchain."""
        engine_with_blockchain._blockchain.verify_consent_on_chain.return_value = True

        consent = await engine_with_blockchain.verify_blockchain_consent(
            user_blockchain_address="0x" + "7" * 40, dream_seed_id="dream_001"
        )

        assert consent is True

    def test_get_blockchain_status_enabled(self, engine_with_blockchain):
        """Test getting blockchain status when enabled."""
        status = engine_with_blockchain.get_blockchain_status()

        assert status["enabled"] is True
        assert "connected" in status
        assert "network_id" in status

    def test_get_blockchain_status_disabled(self):
        """Test getting blockchain status when disabled."""
        engine = DreamCommerceEngine(enable_blockchain=False)
        status = engine.get_blockchain_status()

        assert status["enabled"] is False
        assert "reason" in status

    def test_get_nft_for_dream_seed(self, engine_with_blockchain):
        """Test getting NFT for dream seed."""
        mock_nft = DreamContentNFT(
            token_id=1,
            dream_seed_id="dream_001",
            creator_address="0x123",
            content_hash="Qm123",
            metadata_uri="ipfs://Qm456",
            mint_timestamp=datetime.now(timezone.utc),
            royalty_percentage=Decimal("10"),
        )

        engine_with_blockchain.minted_nfts["dream_001"] = mock_nft

        nft = engine_with_blockchain.get_nft_for_dream_seed("dream_001")

        assert nft is not None
        assert nft.token_id == 1
        assert nft.dream_seed_id == "dream_001"

    def test_get_commerce_stats_with_blockchain(self, engine_with_blockchain):
        """Test getting stats includes blockchain metrics."""
        stats = engine_with_blockchain.get_commerce_stats()

        assert "blockchain" in stats
        assert stats["blockchain"]["enabled"] is True
        assert "total_nfts_minted" in stats["blockchain"]


# Smoke tests
def test_module_imports():
    """Test that all blockchain classes can be imported."""
    from core.bridge.dream_commerce import (
        DreamCommerceBlockchain,
        DreamContentNFT,
        ConsentRecord,
        WEB3_AVAILABLE,
        IPFS_AVAILABLE,
    )

    assert DreamCommerceBlockchain is not None
    assert DreamContentNFT is not None
    assert ConsentRecord is not None
    # WEB3_AVAILABLE and IPFS_AVAILABLE are booleans


@pytest.mark.skipif(not WEB3_AVAILABLE, reason="Web3 not available")
def test_basic_blockchain_workflow():
    """Test basic blockchain workflow (with mocks)."""
    # This test verifies the core workflow without actual blockchain
    with patch("core.bridge.dream_commerce.Web3") as mock_w3_class:
        mock_w3 = MagicMock()
        mock_w3.is_connected.return_value = True
        mock_w3.eth.gas_price = 1000000000
        mock_w3_class.return_value = mock_w3
        mock_w3_class.to_checksum_address = lambda addr: addr

        with patch("core.bridge.dream_commerce.ipfshttpclient"):
            # Create blockchain instance
            blockchain = DreamCommerceBlockchain(
                blockchain_rpc_url="http://localhost:8545",
                dream_nft_contract_address="0x" + "1" * 40,
                consent_ledger_address="0x" + "2" * 40,
                private_key="0x" + "a" * 64,
            )

            # Verify initialization
            assert blockchain.w3 is not None
            assert blockchain.dream_nft_address == "0x" + "1" * 40
            assert blockchain.consent_ledger_address == "0x" + "2" * 40

            # Get connection info
            info = blockchain.get_connection_info()
            assert info["connected"] is True
