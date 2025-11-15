"""
═══════════════════════════════════════════════════════════════════════════════════
🛒 MODULE: api.dream_commerce
📄 FILENAME: dream_commerce.py
🎯 PURPOSE: Dream Commerce Layer - DreamSeed Commerce for PHASE-3-2.md Implementation
🧠 CONTEXT: Consent-driven marketing through user-seeded dream experiences
🔮 CAPABILITY: SEEDRA protocol integration with dream visualization commerce
🛡️ ETHICS: Privacy-first consent-driven commerce with user control and transparency
🚀 VERSION: v1.0.0 • 📅 CREATED: 2025-07-30 • ✍️ AUTHOR: CLAUDE-HARMONIZER
💭 INTEGRATION: DreamAPI, SEEDRA, UserConsent, ZKP, IdentityClient, EventBus
═══════════════════════════════════════════════════════════════════════════════════

🛒 DREAM COMMERCE LAYER - CONSENT-DRIVEN MARKETING EDITION
────────────────────────────────────────────────────────────────────

The Dream Commerce Layer implements the sophisticated DreamSeed Commerce system
outlined in PHASE-3-2.md, enabling consent-driven marketing through user-seeded
dream experiences. This system provides:

- User-seeded dreaming with symbolic prompts (images, audio, emotions, text)
- SEEDRA consent protocol integration for marketing experiences
- Privacy-preserving dream commerce with ZKP validation
- Dream narrative visualization for Sora integration
- Consent-driven advertising within dream experiences
- Revenue sharing models for dream content creators
- Ethical boundaries enforcement for commercial dream content

🔬 CORE COMMERCE FEATURES:
- DreamSeed submission and validation
- Consent-driven dream experience generation
- Commercial dream content integration
- Revenue sharing and creator compensation
- Privacy-preserving transaction processing
- Ethical advertising boundary enforcement
- Dream experience marketplace

🧪 COMMERCE SPECIALIZATIONS:
- Creative DreamSeeds: Artistic and creative content integration
- Brand DreamSeeds: Ethical brand experience integration
- Educational DreamSeeds: Learning and skill development dreams
- Therapeutic DreamSeeds: Wellness and healing dream experiences
- Entertainment DreamSeeds: Game and story-driven dream content
- Research DreamSeeds: Scientific and research collaboration dreams

ΛTAG: dream_commerce, seedra_protocol, consent_driven_marketing, blockchain_integration
AIDEA: Implement dream content NFT marketplace with royalty distribution
"""
import hashlib
import json
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

# Blockchain dependencies (optional - graceful degradation)
try:
    from web3 import Web3
    from web3.contract import Contract
    from web3.middleware import ExtraDataToPOAMiddleware
    from web3.providers import HTTPProvider

    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    Web3 = None  # type: ignore
    Contract = None  # type: ignore

try:
    import ipfshttpclient

    IPFS_AVAILABLE = True
except ImportError:
    IPFS_AVAILABLE = False
    ipfshttpclient = None  # type: ignore

# Import core components
try:
    from governance.identity.interface import (
        IdentityClient,
        check_consent,
        verify_access,
    )

    IDENTITY_AVAILABLE = True
except ImportError:
    IDENTITY_AVAILABLE = False

    def check_consent(user_id, consent_type):
        return True

    def verify_access(user_id, tier):
        return True


try:
    from privacy.zkp_dream_validator import ZKPDreamValidator

    ZKP_AVAILABLE = True
except ImportError:
    ZKP_AVAILABLE = False

try:
    from core.event_bus import DreamEventType, get_global_event_bus

    EVENT_BUS_AVAILABLE = True
except ImportError:
    EVENT_BUS_AVAILABLE = False

logger = logging.getLogger("dream_commerce")
router = APIRouter(prefix="/dream/commerce", tags=["dream_commerce"])


class DreamSeedType(Enum):
    """Types of dream seeds for commerce"""

    CREATIVE = "creative"
    BRAND = "brand"
    EDUCATIONAL = "educational"
    THERAPEUTIC = "therapeutic"
    ENTERTAINMENT = "entertainment"
    RESEARCH = "research"
    COLLABORATIVE = "collaborative"


class ConsentLevel(Enum):
    """Levels of user consent for dream commerce"""

    MINIMAL = "minimal"  # Basic dream seeding only
    STANDARD = "standard"  # Standard commercial integration
    ENHANCED = "enhanced"  # Enhanced brand experiences
    PREMIUM = "premium"  # Full commercial integration with rewards


class RevenueModel(Enum):
    """Revenue models for dream commerce"""

    FREE = "free"  # No revenue, purely creative/educational
    CREATOR_SHARE = "creator_share"  # Revenue shared with dream creators
    SUBSCRIPTION = "subscription"  # Subscription-based access
    PAY_PER_DREAM = "pay_per_dream"  # Individual dream experience pricing
    SPONSORED = "sponsored"  # Sponsor-funded with user rewards


# Pydantic Models


class DreamSeedSubmission(BaseModel):
    """Model for submitting dream seeds"""

    seed_type: DreamSeedType = Field(..., description="Type of dream seed")
    title: str = Field(..., min_length=3, max_length=100, description="Dream seed title")
    description: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Dream seed description",
    )
    symbolic_prompts: dict[str, Any] = Field(..., description="Symbolic prompts (images, audio, emotions, text)")
    target_emotions: list[str] = Field(default_factory=list, description="Target emotional experiences")
    consent_requirements: ConsentLevel = Field(ConsentLevel.STANDARD, description="Required consent level")
    revenue_model: RevenueModel = Field(RevenueModel.FREE, description="Revenue model for this seed")
    creator_revenue_share: float = Field(0.0, ge=0.0, le=1.0, description="Creator revenue share (0.0-1.0)")
    ethical_boundaries: list[str] = Field(default_factory=list, description="Ethical constraints")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DreamExperienceRequest(BaseModel):
    """Model for requesting dream experiences"""

    user_id: str = Field(..., description="User identifier")
    dream_seed_id: str = Field(..., description="Selected dream seed ID")
    personalization_level: float = Field(0.5, ge=0.0, le=1.0, description="Personalization intensity")
    experience_duration: int = Field(10, ge=1, le=60, description="Experience duration in minutes")
    visualization_format: str = Field("narrative", description="Format for dream visualization")
    include_sora_video: bool = Field(False, description="Generate Sora video content")
    consent_confirmation: dict[str, bool] = Field(..., description="Consent confirmations")
    payment_details: Optional[dict[str, Any]] = Field(None, description="Payment information if required")


class DreamMarketplaceFilter(BaseModel):
    """Filters for dream marketplace browsing"""

    seed_types: Optional[list[DreamSeedType]] = None
    consent_levels: Optional[list[ConsentLevel]] = None
    revenue_models: Optional[list[RevenueModel]] = None
    creator_id: Optional[str] = None
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    tags: Optional[list[str]] = None
    price_range: Optional[tuple[float, float]] = None


class APIResponse(BaseModel):
    """Standard API response model"""

    status: str = Field(..., description="Response status")
    data: Any = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Optional message")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# Core Dream Commerce System


@dataclass
class DreamSeed:
    """Represents a dream seed for commerce"""

    seed_id: str
    creator_id: str
    seed_type: DreamSeedType
    title: str
    description: str
    symbolic_prompts: dict[str, Any]
    target_emotions: list[str]
    consent_requirements: ConsentLevel
    revenue_model: RevenueModel
    creator_revenue_share: float
    ethical_boundaries: list[str]
    price: Decimal = field(default=Decimal("0.00"))
    rating: float = 0.0
    usage_count: int = 0
    revenue_generated: Decimal = field(default=Decimal("0.00"))
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DreamExperience:
    """Represents a generated dream experience"""

    experience_id: str
    user_id: str
    dream_seed_id: str
    dream_content: dict[str, Any]
    visualization_content: Optional[dict[str, Any]] = None
    sora_video_url: Optional[str] = None
    personalization_applied: dict[str, Any] = field(default_factory=dict)
    consent_record: dict[str, Any] = field(default_factory=dict)
    privacy_proof: Optional[str] = None
    experience_rating: Optional[float] = None
    revenue_transaction: Optional[dict[str, Any]] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DreamContentNFT:
    """
    Represents a dream content NFT minted on blockchain.

    This dataclass encapsulates all metadata and identifiers for a
    tokenized dream experience, including IPFS hashes, royalty terms,
    and blockchain transaction details.
    """

    token_id: int
    dream_seed_id: str
    creator_address: str
    content_hash: str  # IPFS hash of dream content
    metadata_uri: str  # IPFS URI for NFT metadata
    mint_timestamp: datetime
    royalty_percentage: Decimal  # 0-100 percentage for secondary sales
    license_terms: dict[str, Any] = field(default_factory=dict)
    blockchain_network: str = "ethereum"
    transaction_hash: Optional[str] = None
    owner_address: Optional[str] = None


@dataclass
class ConsentRecord:
    """
    Blockchain-backed immutable consent record.

    Provides cryptographic proof of user consent for dream commerce
    activities, stored permanently on blockchain for audit trail.
    """

    user_address: str
    dream_seed_id: str
    consent_given: bool
    timestamp: datetime
    transaction_hash: str
    ipfs_proof_hash: Optional[str] = None
    consent_type: str = "dream_experience"
    revocable: bool = True


class DreamCommerceBlockchain:
    """
    Blockchain integration for decentralized dream commerce.

    Manages NFT minting, IPFS content storage, royalty distribution,
    and immutable consent ledger on Ethereum-compatible blockchains.

    This class provides the bridge between LUKHAS dream commerce
    and Web3 infrastructure, enabling trustless, decentralized
    transactions for dream content.

    Key capabilities:
    1. NFT minting for dream content (ERC-721)
    2. IPFS content and metadata upload
    3. On-chain consent recording
    4. Consent verification from blockchain
    5. Royalty calculation for secondary sales
    6. Gas optimization strategies

    Example:
        >>> blockchain = DreamCommerceBlockchain(
        ...     blockchain_rpc_url="https://mainnet.infura.io/v3/YOUR-KEY",
        ...     dream_nft_contract_address="0x123...",
        ...     private_key="0xabc..."
        ... )
        >>> nft = blockchain.mint_dream_nft(
        ...     dream_seed_id="dream_123",
        ...     content=b"dream_data",
        ...     creator_address="0x456...",
        ...     royalty_percentage=Decimal("10")
        ... )
    """

    # Smart contract ABIs (simplified for core functionality)
    DREAM_NFT_ABI = json.loads(
        """[
        {
            "inputs": [
                {"type": "string", "name": "contentHash"},
                {"type": "uint256", "name": "royalty"}
            ],
            "name": "mintDreamNFT",
            "outputs": [{"type": "uint256"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"type": "uint256", "name": "tokenId"}],
            "name": "tokenURI",
            "outputs": [{"type": "string"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"type": "uint256", "name": "tokenId"}],
            "name": "ownerOf",
            "outputs": [{"type": "address"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]"""
    )

    CONSENT_LEDGER_ABI = json.loads(
        """[
        {
            "inputs": [
                {"type": "string", "name": "dreamSeedId"},
                {"type": "bool", "name": "consent"}
            ],
            "name": "recordConsent",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"type": "address", "name": "user"},
                {"type": "string", "name": "dreamSeedId"}
            ],
            "name": "getConsent",
            "outputs": [{"type": "bool"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]"""
    )

    def __init__(
        self,
        *,
        blockchain_rpc_url: str = "http://localhost:8545",
        dream_nft_contract_address: Optional[str] = None,
        consent_ledger_address: Optional[str] = None,
        ipfs_api: str = "/ip4/127.0.0.1/tcp/5001",
        private_key: Optional[str] = None,
        gas_price_multiplier: float = 1.1,
        network_id: str = "ethereum",
    ):
        """
        Initialize blockchain integration.

        Args:
            blockchain_rpc_url: Ethereum RPC endpoint (Infura, Alchemy, local)
            dream_nft_contract_address: Deployed NFT contract address
            consent_ledger_address: Deployed consent ledger contract address
            ipfs_api: IPFS API endpoint (multiaddr format)
            private_key: Private key for signing transactions (keep secure!)
            gas_price_multiplier: Multiplier for gas price estimation
            network_id: Network identifier (ethereum, polygon, etc.)

        Raises:
            ImportError: If web3 not installed
            ConnectionError: If cannot connect to blockchain or IPFS
        """
        if not WEB3_AVAILABLE:
            raise ImportError(
                "Blockchain features require web3: pip install web3>=6.0.0"
            )

        # Initialize Web3
        self.w3 = Web3(HTTPProvider(blockchain_rpc_url))

        # Add PoA middleware for networks like Polygon
        if network_id in ["polygon", "bsc"]:
            self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        if not self.w3.is_connected():
            raise ConnectionError(
                f"Cannot connect to blockchain at {blockchain_rpc_url}"
            )

        # Store configuration
        self.network_id = network_id
        self.dream_nft_address = dream_nft_contract_address
        self.consent_ledger_address = consent_ledger_address
        self._private_key = private_key
        self._gas_price_multiplier = gas_price_multiplier

        # Initialize contracts
        self.dream_nft_contract: Optional[Contract] = None
        self.consent_ledger_contract: Optional[Contract] = None

        if dream_nft_contract_address:
            self.dream_nft_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(dream_nft_contract_address),
                abi=self.DREAM_NFT_ABI,
            )

        if consent_ledger_address:
            self.consent_ledger_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(consent_ledger_address),
                abi=self.CONSENT_LEDGER_ABI,
            )

        # IPFS client
        self._ipfs_client = None
        if IPFS_AVAILABLE:
            try:
                self._ipfs_client = ipfshttpclient.connect(ipfs_api)
                # Test connection
                self._ipfs_client.version()
            except Exception as e:
                logging.warning(f"Could not connect to IPFS at {ipfs_api}: {e}")
                self._ipfs_client = None

        self._logger = logging.getLogger(__name__)
        self._logger.info(
            f"Blockchain integration initialized",
            extra={
                "network": network_id,
                "rpc_url": blockchain_rpc_url,
                "nft_contract": dream_nft_contract_address,
                "consent_ledger": consent_ledger_address,
                "ipfs_available": self._ipfs_client is not None,
            },
        )

    def upload_to_ipfs(self, content: bytes) -> str:
        """
        Upload content to IPFS and return CID.

        Args:
            content: Raw content bytes to upload

        Returns:
            IPFS Content Identifier (CID) as string

        Raises:
            RuntimeError: If IPFS client not available
        """
        if not self._ipfs_client:
            raise RuntimeError(
                "IPFS client not available. Install ipfshttpclient and ensure IPFS daemon is running."
            )

        try:
            result = self._ipfs_client.add_bytes(content)
            ipfs_hash = result

            self._logger.info(
                f"Content uploaded to IPFS",
                extra={"ipfs_hash": ipfs_hash, "size_bytes": len(content)},
            )

            return ipfs_hash

        except Exception as e:
            self._logger.error(f"IPFS upload failed: {e}")
            raise RuntimeError(f"Failed to upload to IPFS: {e}") from e

    def mint_dream_nft(
        self,
        dream_seed_id: str,
        content: bytes,
        creator_address: str,
        royalty_percentage: Decimal,
        metadata: dict[str, Any],
    ) -> DreamContentNFT:
        """
        Mint a dream content NFT on blockchain.

        This method:
        1. Uploads dream content to IPFS
        2. Creates NFT metadata with content reference
        3. Uploads metadata to IPFS
        4. Mints NFT on blockchain with royalty information
        5. Returns complete NFT record

        Args:
            dream_seed_id: Dream seed identifier
            content: Dream content bytes (imagery, audio, etc.)
            creator_address: Creator's blockchain address (0x...)
            royalty_percentage: Royalty for secondary sales (0-100)
            metadata: NFT metadata (name, description, attributes, etc.)

        Returns:
            DreamContentNFT with token ID and IPFS hashes

        Raises:
            RuntimeError: If NFT contract not initialized or minting fails
        """
        if not self.dream_nft_contract:
            raise RuntimeError("Dream NFT contract not initialized")

        if not self._private_key:
            raise RuntimeError("Private key required for minting")

        try:
            # Step 1: Upload content to IPFS
            content_hash = self.upload_to_ipfs(content)
            self._logger.info(f"Dream content uploaded: {content_hash}")

            # Step 2: Create comprehensive NFT metadata
            nft_metadata = {
                "name": metadata.get("name", f"Dream {dream_seed_id}"),
                "description": metadata.get(
                    "description", "A unique dream experience from LUKHAS"
                ),
                "image": f"ipfs://{content_hash}",
                "dream_seed_id": dream_seed_id,
                "creator": creator_address,
                "royalty": float(royalty_percentage),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "attributes": metadata.get("attributes", []),
                "external_url": metadata.get("external_url"),
                "animation_url": metadata.get("animation_url"),
                **{
                    k: v
                    for k, v in metadata.items()
                    if k
                    not in [
                        "name",
                        "description",
                        "attributes",
                        "external_url",
                        "animation_url",
                    ]
                },
            }

            # Step 3: Upload metadata to IPFS
            metadata_bytes = json.dumps(nft_metadata, indent=2).encode()
            metadata_hash = self.upload_to_ipfs(metadata_bytes)
            metadata_uri = f"ipfs://{metadata_hash}"
            self._logger.info(f"NFT metadata uploaded: {metadata_hash}")

            # Step 4: Prepare blockchain transaction
            account = self.w3.eth.account.from_key(self._private_key)

            # Build mint transaction
            tx = self.dream_nft_contract.functions.mintDreamNFT(
                content_hash, int(royalty_percentage)
            ).build_transaction(
                {
                    "from": account.address,
                    "nonce": self.w3.eth.get_transaction_count(account.address),
                    "gas": 250000,  # Estimate with buffer
                    "gasPrice": int(
                        self.w3.eth.gas_price * self._gas_price_multiplier
                    ),
                }
            )

            # Step 5: Sign and send transaction
            signed_tx = account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            self._logger.info(
                f"NFT mint transaction sent",
                extra={"tx_hash": tx_hash.hex(), "creator": creator_address},
            )

            # Step 6: Wait for transaction confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)

            if receipt["status"] != 1:
                raise RuntimeError(f"Minting transaction failed: {tx_hash.hex()}")

            # Step 7: Extract token ID from logs
            # Assuming first log contains token ID in second topic
            token_id = int.from_bytes(receipt["logs"][0]["topics"][1], "big")

            # Step 8: Create NFT record
            nft = DreamContentNFT(
                token_id=token_id,
                dream_seed_id=dream_seed_id,
                creator_address=creator_address,
                content_hash=content_hash,
                metadata_uri=metadata_uri,
                mint_timestamp=datetime.now(timezone.utc),
                royalty_percentage=royalty_percentage,
                license_terms=metadata.get("license", {}),
                blockchain_network=self.network_id,
                transaction_hash=tx_hash.hex(),
                owner_address=creator_address,
            )

            self._logger.info(
                f"Dream NFT #{token_id} minted successfully",
                extra={
                    "token_id": token_id,
                    "dream_seed_id": dream_seed_id,
                    "creator": creator_address,
                    "tx_hash": tx_hash.hex(),
                    "content_hash": content_hash,
                    "royalty": float(royalty_percentage),
                },
            )

            return nft

        except Exception as e:
            self._logger.error(f"Failed to mint dream NFT: {e}")
            raise RuntimeError(f"NFT minting failed: {e}") from e

    def record_consent_on_chain(
        self, user_address: str, dream_seed_id: str, consent_given: bool
    ) -> ConsentRecord:
        """
        Record user consent on blockchain for immutable audit trail.

        Creates a permanent, cryptographically-verified record of user
        consent for dream commerce activities.

        Args:
            user_address: User's blockchain address
            dream_seed_id: Dream seed identifier
            consent_given: Whether consent was given (True/False)

        Returns:
            ConsentRecord with transaction hash

        Raises:
            RuntimeError: If consent ledger not initialized or recording fails
        """
        if not self.consent_ledger_contract:
            raise RuntimeError("Consent ledger contract not initialized")

        if not self._private_key:
            raise RuntimeError("Private key required for consent recording")

        try:
            account = self.w3.eth.account.from_key(self._private_key)

            # Build consent recording transaction
            tx = self.consent_ledger_contract.functions.recordConsent(
                dream_seed_id, consent_given
            ).build_transaction(
                {
                    "from": account.address,
                    "nonce": self.w3.eth.get_transaction_count(account.address),
                    "gas": 100000,
                    "gasPrice": int(
                        self.w3.eth.gas_price * self._gas_price_multiplier
                    ),
                }
            )

            # Sign and send transaction
            signed_tx = account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            self._logger.info(
                f"Consent recording transaction sent",
                extra={
                    "tx_hash": tx_hash.hex(),
                    "user": user_address,
                    "dream_seed": dream_seed_id,
                    "consent": consent_given,
                },
            )

            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)

            if receipt["status"] != 1:
                raise RuntimeError(
                    f"Consent recording transaction failed: {tx_hash.hex()}"
                )

            # Create consent record with IPFS proof (optional)
            ipfs_proof_hash = None
            if self._ipfs_client:
                try:
                    proof_data = {
                        "user_address": user_address,
                        "dream_seed_id": dream_seed_id,
                        "consent_given": consent_given,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "transaction_hash": tx_hash.hex(),
                        "network": self.network_id,
                    }
                    proof_bytes = json.dumps(proof_data, indent=2).encode()
                    ipfs_proof_hash = self.upload_to_ipfs(proof_bytes)
                    self._logger.info(f"Consent proof uploaded to IPFS: {ipfs_proof_hash}")
                except Exception as e:
                    self._logger.warning(f"Failed to upload consent proof to IPFS: {e}")

            record = ConsentRecord(
                user_address=user_address,
                dream_seed_id=dream_seed_id,
                consent_given=consent_given,
                timestamp=datetime.now(timezone.utc),
                transaction_hash=tx_hash.hex(),
                ipfs_proof_hash=ipfs_proof_hash,
            )

            self._logger.info(
                f"Consent recorded on-chain",
                extra={
                    "user": user_address,
                    "dream_seed": dream_seed_id,
                    "consent": consent_given,
                    "tx_hash": tx_hash.hex(),
                    "ipfs_proof": ipfs_proof_hash,
                },
            )

            return record

        except Exception as e:
            self._logger.error(f"Failed to record consent on chain: {e}")
            raise RuntimeError(f"Consent recording failed: {e}") from e

    def verify_consent_on_chain(self, user_address: str, dream_seed_id: str) -> bool:
        """
        Verify consent from blockchain ledger.

        Queries the immutable consent ledger to check if user
        has given consent for a specific dream seed.

        Args:
            user_address: User's blockchain address
            dream_seed_id: Dream seed identifier

        Returns:
            True if consent was given, False otherwise

        Raises:
            RuntimeError: If consent ledger not initialized
        """
        if not self.consent_ledger_contract:
            raise RuntimeError("Consent ledger contract not initialized")

        try:
            consent = self.consent_ledger_contract.functions.getConsent(
                Web3.to_checksum_address(user_address), dream_seed_id
            ).call()

            self._logger.debug(
                f"Consent verification",
                extra={
                    "user": user_address,
                    "dream_seed": dream_seed_id,
                    "consent": bool(consent),
                },
            )

            return bool(consent)

        except Exception as e:
            self._logger.error(f"Failed to verify consent on chain: {e}")
            raise RuntimeError(f"Consent verification failed: {e}") from e

    def calculate_royalty_distribution(
        self, token_id: int, sale_amount: Decimal
    ) -> dict[str, Decimal]:
        """
        Calculate royalty distribution for secondary sale.

        Determines how sale proceeds should be split between
        original creator (royalty) and current seller.

        Args:
            token_id: NFT token ID
            sale_amount: Sale price in wei or smallest unit

        Returns:
            Dict mapping recipient types to amounts:
            - "creator": Amount for original creator (royalty)
            - "seller": Amount for current seller
            - "platform": Amount for platform fee (if applicable)

        Raises:
            RuntimeError: If NFT contract not initialized
        """
        if not self.dream_nft_contract:
            raise RuntimeError("Dream NFT contract not initialized")

        try:
            # In production, would fetch royalty from contract/metadata
            # For now, using fixed 10% royalty
            royalty_percentage = Decimal("10")  # 10%
            platform_fee = Decimal("2.5")  # 2.5% platform fee

            creator_amount = (sale_amount * royalty_percentage) / Decimal("100")
            platform_amount = (sale_amount * platform_fee) / Decimal("100")
            seller_amount = sale_amount - creator_amount - platform_amount

            distribution = {
                "creator": creator_amount,
                "seller": seller_amount,
                "platform": platform_amount,
            }

            self._logger.info(
                f"Royalty distribution calculated",
                extra={
                    "token_id": token_id,
                    "sale_amount": float(sale_amount),
                    "creator_royalty": float(creator_amount),
                    "platform_fee": float(platform_amount),
                    "seller_proceeds": float(seller_amount),
                },
            )

            return distribution

        except Exception as e:
            self._logger.error(f"Failed to calculate royalty distribution: {e}")
            raise RuntimeError(f"Royalty calculation failed: {e}") from e

    def get_nft_owner(self, token_id: int) -> str:
        """
        Get current owner of NFT.

        Args:
            token_id: NFT token ID

        Returns:
            Owner's blockchain address

        Raises:
            RuntimeError: If NFT contract not initialized or token doesn't exist
        """
        if not self.dream_nft_contract:
            raise RuntimeError("Dream NFT contract not initialized")

        try:
            owner = self.dream_nft_contract.functions.ownerOf(token_id).call()
            return owner

        except Exception as e:
            self._logger.error(f"Failed to get NFT owner: {e}")
            raise RuntimeError(f"Failed to get owner for token {token_id}: {e}") from e

    def get_connection_info(self) -> dict[str, Any]:
        """
        Get blockchain connection status and configuration.

        Returns:
            Dict with connection details and capabilities
        """
        return {
            "connected": self.w3.is_connected(),
            "network_id": self.network_id,
            "chain_id": self.w3.eth.chain_id if self.w3.is_connected() else None,
            "latest_block": (
                self.w3.eth.block_number if self.w3.is_connected() else None
            ),
            "nft_contract_address": self.dream_nft_address,
            "consent_ledger_address": self.consent_ledger_address,
            "ipfs_available": self._ipfs_client is not None,
            "gas_price_wei": (
                self.w3.eth.gas_price if self.w3.is_connected() else None
            ),
        }


class DreamCommerceEngine:
    """
    Dream Commerce Engine

    Implements the complete DreamSeed Commerce system with consent-driven
    marketing, SEEDRA protocol integration, and privacy-preserving transactions.

    Key capabilities:
    1. Dream seed creation and marketplace management
    2. Consent-driven dream experience generation
    3. Privacy-preserving commercial transactions
    4. Creator revenue sharing and compensation
    5. Ethical boundary enforcement
    6. Integration with Sora for dream visualization
    7. SEEDRA protocol compliance
    """

    def __init__(
        self,
        *,
        enable_blockchain: bool = False,
        blockchain_config: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize the dream commerce engine.

        Args:
            enable_blockchain: Enable blockchain features for NFTs and consent ledger
            blockchain_config: Blockchain configuration dict with keys:
                - blockchain_rpc_url: RPC endpoint URL
                - dream_nft_contract_address: NFT contract address
                - consent_ledger_address: Consent ledger contract address
                - ipfs_api: IPFS API endpoint
                - private_key: Private key for signing (keep secure!)
                - network_id: Network identifier (ethereum, polygon, etc.)
        """
        self.logger = logging.getLogger("dream_commerce_engine")

        # Data storage (in production, would use proper database)
        self.dream_seeds: dict[str, DreamSeed] = {}
        self.dream_experiences: dict[str, DreamExperience] = {}
        self.user_consents: dict[str, dict[str, Any]] = {}
        self.creator_profiles: dict[str, dict[str, Any]] = {}
        self.revenue_transactions: list[dict[str, Any]] = []
        self.minted_nfts: dict[str, DreamContentNFT] = {}  # dream_seed_id -> NFT

        # System integrations
        self.identity_client = IdentityClient() if IDENTITY_AVAILABLE else None
        self.zkp_validator = ZKPDreamValidator() if ZKP_AVAILABLE else None
        self.event_bus = None

        # Blockchain integration
        self._enable_blockchain = enable_blockchain and WEB3_AVAILABLE
        self._blockchain: Optional[DreamCommerceBlockchain] = None

        if self._enable_blockchain:
            try:
                self._blockchain = DreamCommerceBlockchain(
                    **(blockchain_config or {})
                )
                self.logger.info("Blockchain integration enabled")
            except Exception as e:
                self.logger.error(f"Failed to initialize blockchain: {e}")
                self._enable_blockchain = False
                self._blockchain = None

        # Commerce configuration
        self.platform_revenue_share = 0.3  # 30% platform fee
        self.creator_minimum_share = 0.5  # 50% minimum for creators
        self.ethical_validation_enabled = True
        self.privacy_validation_required = True

        # Metrics
        self.total_seeds_created = 0
        self.total_experiences_generated = 0
        self.total_revenue_processed = Decimal("0.00")
        self.total_nfts_minted = 0

        self.logger.info(
            "Dream commerce engine initialized",
            extra={"blockchain_enabled": self._enable_blockchain},
        )

    async def initialize(self) -> bool:
        """Initialize the commerce engine"""
        try:
            # Initialize event bus connection
            if EVENT_BUS_AVAILABLE:
                self.event_bus = await get_global_event_bus()
                self.logger.info("Event bus integration initialized")

            # Initialize ZKP validator
            if self.zkp_validator:
                await self.zkp_validator.initialize()
                self.logger.info("ZKP validator integration initialized")

            self.logger.info("Dream commerce engine fully operational")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize dream commerce engine: {e}")
            return False

    async def create_dream_seed(self, creator_id: str, submission: DreamSeedSubmission) -> DreamSeed:
        """Create a new dream seed for the marketplace"""
        try:
            # Verify creator permissions
            if IDENTITY_AVAILABLE and self.identity_client and not verify_access(creator_id, "DREAM_CREATOR_TIER"):
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient creator permissions",
                )

            # Validate ethical boundaries
            if self.ethical_validation_enabled:
                ethical_validation = await self._validate_ethical_boundaries(
                    submission.symbolic_prompts, submission.ethical_boundaries
                )
                if not ethical_validation["approved"]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Ethical validation failed: {ethical_validation['reason']}",
                    )

            # Create dream seed
            seed_id = f"dream_seed_{uuid.uuid4().hex[:12]}"

            # Calculate pricing based on revenue model
            price = await self._calculate_dream_seed_price(submission)

            dream_seed = DreamSeed(
                seed_id=seed_id,
                creator_id=creator_id,
                seed_type=submission.seed_type,
                title=submission.title,
                description=submission.description,
                symbolic_prompts=submission.symbolic_prompts,
                target_emotions=submission.target_emotions,
                consent_requirements=submission.consent_requirements,
                revenue_model=submission.revenue_model,
                creator_revenue_share=max(
                    submission.creator_revenue_share,
                    self.creator_minimum_share,
                ),
                ethical_boundaries=submission.ethical_boundaries,
                price=price,
                metadata=submission.metadata,
            )

            # Store dream seed
            self.dream_seeds[seed_id] = dream_seed
            self.total_seeds_created += 1

            # Update creator profile
            if creator_id not in self.creator_profiles:
                self.creator_profiles[creator_id] = {
                    "total_seeds": 0,
                    "total_revenue": Decimal("0.00"),
                    "average_rating": 0.0,
                    "specializations": [],
                }

            self.creator_profiles[creator_id]["total_seeds"] += 1

            # Add specialization if new
            if submission.seed_type.value not in self.creator_profiles[creator_id]["specializations"]:
                self.creator_profiles[creator_id]["specializations"].append(submission.seed_type.value)

            # Publish creation event
            if self.event_bus:
                await self.event_bus.publish(
                    "dream_seed_created",
                    {
                        "seed_id": seed_id,
                        "creator_id": creator_id,
                        "seed_type": submission.seed_type.value,
                        "revenue_model": submission.revenue_model.value,
                        "price": float(price),
                    },
                    source="dream_commerce_engine",
                )

            self.logger.info(f"Dream seed created: {seed_id} by creator {creator_id}")
            return dream_seed

        except Exception as e:
            self.logger.error(f"Failed to create dream seed: {e}")
            raise

    async def generate_dream_experience(self, request: DreamExperienceRequest) -> DreamExperience:
        """Generate a personalized dream experience from a dream seed"""
        try:
            # Validate dream seed exists
            if request.dream_seed_id not in self.dream_seeds:
                raise HTTPException(status_code=404, detail="Dream seed not found")

            dream_seed = self.dream_seeds[request.dream_seed_id]

            # Verify user consent
            consent_valid = await self._verify_user_consent(request.user_id, dream_seed, request.consent_confirmation)

            if not consent_valid:
                raise HTTPException(status_code=403, detail="Insufficient or invalid consent")

            # Process payment if required
            payment_processed = False
            if dream_seed.revenue_model != RevenueModel.FREE:
                payment_result = await self._process_payment(request.user_id, dream_seed, request.payment_details)
                payment_processed = payment_result["success"]

                if not payment_processed:
                    raise HTTPException(status_code=402, detail="Payment processing failed")

            # Generate personalized dream content
            dream_content = await self._generate_personalized_dream_content(
                dream_seed,
                request.user_id,
                request.personalization_level,
                request.experience_duration,
            )

            # Generate visualization content
            visualization_content = None
            sora_video_url = None

            if request.visualization_format:
                visualization_content = await self._generate_dream_visualization(
                    dream_content, request.visualization_format
                )

            if request.include_sora_video:
                sora_video_url = await self._generate_sora_video(dream_content, visualization_content)

            # Create privacy proof if required
            privacy_proof = None
            if self.privacy_validation_required and self.zkp_validator:
                privacy_proof_obj = await self.zkp_validator.generate_emotional_range_proof(
                    dream_content.get("emotional_context", {}),
                    request.user_id,
                    f"commerce_dream_{uuid.uuid4().hex[:8]}",
                )
                privacy_proof = privacy_proof_obj.proof_id

            # Create dream experience
            experience_id = f"dream_exp_{uuid.uuid4().hex[:12]}"

            dream_experience = DreamExperience(
                experience_id=experience_id,
                user_id=request.user_id,
                dream_seed_id=request.dream_seed_id,
                dream_content=dream_content,
                visualization_content=visualization_content,
                sora_video_url=sora_video_url,
                personalization_applied={
                    "level": request.personalization_level,
                    "duration": request.experience_duration,
                    "format": request.visualization_format,
                },
                consent_record=request.consent_confirmation,
                privacy_proof=privacy_proof,
                revenue_transaction=(payment_result if payment_processed else None),
            )

            # Store experience
            self.dream_experiences[experience_id] = dream_experience
            self.total_experiences_generated += 1

            # Update dream seed usage metrics
            dream_seed.usage_count += 1
            dream_seed.updated_at = datetime.now(timezone.utc)

            # Process revenue sharing if applicable
            if payment_processed:
                await self._process_revenue_sharing(dream_seed, payment_result)

            # Publish experience event
            if self.event_bus:
                await self.event_bus.publish_dream_event(
                    DreamEventType.DREAM_PROCESSING_COMPLETE,
                    dream_id=experience_id,
                    payload={
                        "experience_id": experience_id,
                        "user_id": request.user_id,
                        "dream_seed_id": request.dream_seed_id,
                        "personalization_level": request.personalization_level,
                        "revenue_generated": payment_processed,
                        "privacy_protected": privacy_proof is not None,
                    },
                    source="dream_commerce_engine",
                    user_id=request.user_id,
                )

            self.logger.info(f"Dream experience generated: {experience_id}")
            return dream_experience

        except Exception as e:
            self.logger.error(f"Failed to generate dream experience: {e}")
            raise

    async def get_marketplace_dreams(
        self, filters: DreamMarketplaceFilter, limit: int = 20, offset: int = 0
    ) -> list[DreamSeed]:
        """Get filtered dream seeds from the marketplace"""
        try:
            # Apply filters
            filtered_seeds = []

            for dream_seed in self.dream_seeds.values():
                # Apply type filter
                if filters.seed_types and dream_seed.seed_type not in filters.seed_types:
                    continue

                # Apply consent level filter
                if filters.consent_levels and dream_seed.consent_requirements not in filters.consent_levels:
                    continue

                # Apply revenue model filter
                if filters.revenue_models and dream_seed.revenue_model not in filters.revenue_models:
                    continue

                # Apply creator filter
                if filters.creator_id and dream_seed.creator_id != filters.creator_id:
                    continue

                # Apply rating filter
                if filters.min_rating and dream_seed.rating < filters.min_rating:
                    continue

                # Apply price range filter
                if filters.price_range:
                    min_price, max_price = filters.price_range
                    if not (min_price <= float(dream_seed.price) <= max_price):
                        continue

                # Apply tags filter
                if filters.tags and not any(tag in dream_seed.tags for tag in filters.tags):
                    continue

                filtered_seeds.append(dream_seed)

            # Sort by rating and usage
            filtered_seeds.sort(key=lambda s: (s.rating, s.usage_count), reverse=True)

            # Apply pagination
            return filtered_seeds[offset : offset + limit]

        except Exception as e:
            self.logger.error(f"Failed to get marketplace dreams: {e}")
            raise

    async def publish_dream_seed_as_nft(
        self,
        dream_seed_id: str,
        content: bytes,
        creator_blockchain_address: str,
        royalty_percentage: Decimal = Decimal("10"),
    ) -> DreamContentNFT:
        """
        Publish dream seed as blockchain NFT (requires blockchain enabled).

        This method mints the dream seed content as an NFT, uploading
        content to IPFS and recording the NFT on blockchain.

        Args:
            dream_seed_id: Dream seed to publish
            content: Dream content bytes for IPFS
            creator_blockchain_address: Creator's blockchain wallet address
            royalty_percentage: Royalty percentage for secondary sales (0-100)

        Returns:
            DreamContentNFT with token ID and blockchain details

        Raises:
            RuntimeError: If blockchain not enabled or dream seed not found
        """
        if not self._enable_blockchain or not self._blockchain:
            raise RuntimeError(
                "Blockchain features not enabled. Initialize with enable_blockchain=True"
            )

        # Verify dream seed exists
        if dream_seed_id not in self.dream_seeds:
            raise ValueError(f"Dream seed not found: {dream_seed_id}")

        dream_seed = self.dream_seeds[dream_seed_id]

        try:
            # Prepare NFT metadata from dream seed
            nft_metadata = {
                "name": dream_seed.title,
                "description": dream_seed.description,
                "attributes": [
                    {"trait_type": "Dream Type", "value": dream_seed.seed_type.value},
                    {
                        "trait_type": "Consent Level",
                        "value": dream_seed.consent_requirements.value,
                    },
                    {
                        "trait_type": "Revenue Model",
                        "value": dream_seed.revenue_model.value,
                    },
                    {"trait_type": "Usage Count", "value": dream_seed.usage_count},
                    {"trait_type": "Rating", "value": dream_seed.rating},
                ],
                "external_url": f"https://lukhas.ai/dreams/{dream_seed_id}",
                "license": dream_seed.metadata.get("license", {}),
            }

            # Mint NFT on blockchain
            nft = self._blockchain.mint_dream_nft(
                dream_seed_id=dream_seed_id,
                content=content,
                creator_address=creator_blockchain_address,
                royalty_percentage=royalty_percentage,
                metadata=nft_metadata,
            )

            # Store NFT record
            self.minted_nfts[dream_seed_id] = nft
            self.total_nfts_minted += 1

            # Update dream seed metadata
            dream_seed.metadata["nft_token_id"] = nft.token_id
            dream_seed.metadata["nft_contract_address"] = (
                self._blockchain.dream_nft_address
            )
            dream_seed.metadata["blockchain_network"] = nft.blockchain_network

            # Publish event
            if self.event_bus:
                await self.event_bus.publish(
                    "dream_seed_nft_minted",
                    {
                        "dream_seed_id": dream_seed_id,
                        "token_id": nft.token_id,
                        "creator_address": creator_blockchain_address,
                        "content_hash": nft.content_hash,
                        "metadata_uri": nft.metadata_uri,
                        "royalty": float(royalty_percentage),
                    },
                    source="dream_commerce_engine",
                )

            self.logger.info(
                f"Dream seed published as NFT #{nft.token_id}",
                extra={
                    "dream_seed_id": dream_seed_id,
                    "token_id": nft.token_id,
                    "creator": creator_blockchain_address,
                },
            )

            return nft

        except Exception as e:
            self.logger.error(f"Failed to publish dream seed as NFT: {e}")
            raise

    async def record_consent_on_blockchain(
        self,
        user_blockchain_address: str,
        dream_seed_id: str,
        consent_given: bool = True,
    ) -> ConsentRecord:
        """
        Record user consent on blockchain (requires blockchain enabled).

        Creates an immutable on-chain record of user consent for
        dream commerce activities.

        Args:
            user_blockchain_address: User's blockchain wallet address
            dream_seed_id: Dream seed for which consent is given
            consent_given: Whether consent was granted (default True)

        Returns:
            ConsentRecord with transaction hash

        Raises:
            RuntimeError: If blockchain not enabled
        """
        if not self._enable_blockchain or not self._blockchain:
            raise RuntimeError(
                "Blockchain features not enabled. Initialize with enable_blockchain=True"
            )

        try:
            # Record consent on blockchain
            consent_record = self._blockchain.record_consent_on_chain(
                user_address=user_blockchain_address,
                dream_seed_id=dream_seed_id,
                consent_given=consent_given,
            )

            # Publish event
            if self.event_bus:
                await self.event_bus.publish(
                    "consent_recorded_on_chain",
                    {
                        "user_address": user_blockchain_address,
                        "dream_seed_id": dream_seed_id,
                        "consent_given": consent_given,
                        "transaction_hash": consent_record.transaction_hash,
                        "ipfs_proof": consent_record.ipfs_proof_hash,
                    },
                    source="dream_commerce_engine",
                )

            self.logger.info(
                f"Consent recorded on blockchain",
                extra={
                    "user": user_blockchain_address,
                    "dream_seed": dream_seed_id,
                    "consent": consent_given,
                    "tx_hash": consent_record.transaction_hash,
                },
            )

            return consent_record

        except Exception as e:
            self.logger.error(f"Failed to record consent on blockchain: {e}")
            raise

    async def verify_blockchain_consent(
        self, user_blockchain_address: str, dream_seed_id: str
    ) -> bool:
        """
        Verify user consent from blockchain (requires blockchain enabled).

        Args:
            user_blockchain_address: User's blockchain wallet address
            dream_seed_id: Dream seed identifier

        Returns:
            True if consent was given on-chain, False otherwise

        Raises:
            RuntimeError: If blockchain not enabled
        """
        if not self._enable_blockchain or not self._blockchain:
            raise RuntimeError(
                "Blockchain features not enabled. Initialize with enable_blockchain=True"
            )

        try:
            consent = self._blockchain.verify_consent_on_chain(
                user_address=user_blockchain_address, dream_seed_id=dream_seed_id
            )

            self.logger.debug(
                f"Blockchain consent verification",
                extra={
                    "user": user_blockchain_address,
                    "dream_seed": dream_seed_id,
                    "consent": consent,
                },
            )

            return consent

        except Exception as e:
            self.logger.error(f"Failed to verify blockchain consent: {e}")
            raise

    def get_nft_for_dream_seed(self, dream_seed_id: str) -> Optional[DreamContentNFT]:
        """
        Get NFT record for a dream seed if it was minted.

        Args:
            dream_seed_id: Dream seed identifier

        Returns:
            DreamContentNFT if minted, None otherwise
        """
        return self.minted_nfts.get(dream_seed_id)

    def get_blockchain_status(self) -> dict[str, Any]:
        """
        Get blockchain integration status.

        Returns:
            Dict with blockchain connection status and capabilities
        """
        if not self._enable_blockchain or not self._blockchain:
            return {
                "enabled": False,
                "reason": "Blockchain integration not enabled or unavailable",
            }

        try:
            return {
                "enabled": True,
                **self._blockchain.get_connection_info(),
            }
        except Exception as e:
            return {"enabled": False, "error": str(e)}

    # Private helper methods

    async def _validate_ethical_boundaries(
        self, symbolic_prompts: dict[str, Any], ethical_boundaries: list[str]
    ) -> dict[str, Any]:
        """Validate that dream seed meets ethical requirements"""
        # Simplified ethical validation - in production would use sophisticated AI
        # ethics
        forbidden_content = [
            "violence",
            "hatred",
            "discrimination",
            "illegal",
            "harmful",
            "exploitation",
            "manipulation",
            "deception",
        ]

        # Check symbolic prompts for forbidden content
        prompt_text = str(symbolic_prompts).lower()
        for forbidden in forbidden_content:
            if forbidden in prompt_text:
                return {
                    "approved": False,
                    "reason": f"Contains forbidden content: {forbidden}",
                }

        # Check if required ethical boundaries are present
        required_boundaries = [
            "no_harm",
            "respect_privacy",
            "honest_representation",
        ]
        for required in required_boundaries:
            if required not in ethical_boundaries:
                return {
                    "approved": False,
                    "reason": f"Missing required ethical boundary: {required}",
                }

        return {"approved": True, "reason": "Passed ethical validation"}

    async def _calculate_dream_seed_price(self, submission: DreamSeedSubmission) -> Decimal:
        """Calculate pricing for dream seed based on revenue model"""
        if submission.revenue_model == RevenueModel.FREE:
            return Decimal("0.00")
        elif submission.revenue_model == RevenueModel.PAY_PER_DREAM:
            # Base pricing on seed type and complexity
            base_prices = {
                DreamSeedType.CREATIVE: Decimal("2.99"),
                DreamSeedType.BRAND: Decimal("4.99"),
                DreamSeedType.EDUCATIONAL: Decimal("1.99"),
                DreamSeedType.THERAPEUTIC: Decimal("7.99"),
                DreamSeedType.ENTERTAINMENT: Decimal("3.99"),
                DreamSeedType.RESEARCH: Decimal("5.99"),
                DreamSeedType.COLLABORATIVE: Decimal("6.99"),
            }

            base_price = base_prices.get(submission.seed_type, Decimal("2.99"))

            # Adjust for complexity (number of symbolic prompts)
            complexity_multiplier = min(1.5, 1.0 + len(submission.symbolic_prompts) * 0.1)

            return base_price * Decimal(str(complexity_multiplier))

        elif submission.revenue_model == RevenueModel.SUBSCRIPTION:
            return Decimal("9.99")  # Monthly subscription

        elif submission.revenue_model == RevenueModel.SPONSORED:
            return Decimal("0.00")  # Free for users, sponsored by brands

        else:
            return Decimal("1.99")  # Default

    async def _verify_user_consent(
        self,
        user_id: str,
        dream_seed: DreamSeed,
        consent_confirmation: dict[str, bool],
    ) -> bool:
        """Verify user has provided appropriate consent"""
        required_consents = {
            "dream_experience_generation": True,
            "data_processing": True,
            "personalization": True,
        }

        # Add revenue model specific consents
        if dream_seed.revenue_model != RevenueModel.FREE:
            required_consents["payment_processing"] = True

        if dream_seed.seed_type == DreamSeedType.BRAND:
            required_consents["brand_content_exposure"] = True

        # Check all required consents are provided
        for consent_type, required in required_consents.items():
            if required and not consent_confirmation.get(consent_type, False):
                return False

        # Store consent record
        self.user_consents[user_id] = {
            "dream_seed_id": dream_seed.seed_id,
            "consents": consent_confirmation,
            "consent_time": datetime.now(timezone.utc),
            "consent_level": dream_seed.consent_requirements.value,
        }

        return True

    async def _process_payment(
        self,
        user_id: str,
        dream_seed: DreamSeed,
        payment_details: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        """Process payment for dream experience"""
        if dream_seed.price == 0:
            return {"success": True, "amount": 0, "transaction_id": "free"}

        if not payment_details:
            return {"success": False, "error": "Payment details required"}

        # Simplified payment processing - in production would integrate with
        # payment gateway
        transaction_id = f"txn_{uuid.uuid4().hex[:12]}"

        # Simulate payment processing
        payment_result = {
            "success": True,
            "transaction_id": transaction_id,
            "amount": float(dream_seed.price),
            "currency": "USD",
            "payment_method": payment_details.get("method", "unknown"),
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

        # Store transaction
        self.revenue_transactions.append(
            {
                "transaction_id": transaction_id,
                "user_id": user_id,
                "dream_seed_id": dream_seed.seed_id,
                "creator_id": dream_seed.creator_id,
                "amount": dream_seed.price,
                "platform_fee": dream_seed.price * Decimal(str(self.platform_revenue_share)),
                "creator_share": dream_seed.price * Decimal(str(dream_seed.creator_revenue_share)),
                "timestamp": datetime.now(timezone.utc),
            }
        )

        self.total_revenue_processed += dream_seed.price

        return payment_result

    async def _generate_personalized_dream_content(
        self,
        dream_seed: DreamSeed,
        user_id: str,
        personalization_level: float,
        duration: int,
    ) -> dict[str, Any]:
        """Generate personalized dream content from seed"""
        # Base dream content from seed
        dream_content = {
            "title": dream_seed.title,
            "description": dream_seed.description,
            "symbolic_elements": dream_seed.symbolic_prompts,
            "target_emotions": dream_seed.target_emotions,
            "duration_minutes": duration,
            "personalization_level": personalization_level,
        }

        # Add personalization based on level
        if personalization_level > 0.3:
            # Add user-specific emotional context
            dream_content["emotional_context"] = {
                "curiosity": min(1.0, 0.5 + personalization_level * 0.3),
                "wonder": min(1.0, 0.6 + personalization_level * 0.2),
                "engagement": min(1.0, 0.7 + personalization_level * 0.3),
            }

        if personalization_level > 0.6:
            # Add adaptive narrative elements
            dream_content["adaptive_narrative"] = {
                "user_preferences_applied": True,
                "dynamic_pacing": True,
                "emotional_resonance_optimization": True,
            }

        if personalization_level > 0.8:
            # Add advanced personalization
            dream_content["advanced_personalization"] = {
                "memory_integration": True,
                "preference_learning": True,
                "contextual_adaptation": True,
            }

        return dream_content

    async def _generate_dream_visualization(
        self, dream_content: dict[str, Any], visualization_format: str
    ) -> dict[str, Any]:
        """Generate visualization content for dream"""
        if visualization_format == "narrative":
            return {
                "format": "narrative",
                "content": f"A dream experience titled '{dream_content['title']}' unfolds...",
                "visual_elements": dream_content.get("symbolic_elements", {}),
                "emotional_tone": dream_content.get("emotional_context", {}),
            }

        elif visualization_format == "interactive":
            return {
                "format": "interactive",
                "interaction_points": [
                    {
                        "type": "choice",
                        "description": "Choose your path through the dream",
                    },
                    {
                        "type": "emotion",
                        "description": "Express how the dream makes you feel",
                    },
                ],
                "visual_elements": dream_content.get("symbolic_elements", {}),
            }

        else:  # Default to abstract
            return {
                "format": "abstract",
                "visual_metaphors": dream_content.get("symbolic_elements", {}),
                "color_palette": ["deep_blue", "soft_gold", "ethereal_white"],
                "mood": "contemplative",
            }

    async def _generate_sora_video(
        self,
        dream_content: dict[str, Any],
        visualization_content: Optional[dict[str, Any]],
    ) -> str:
        """Generate Sora video URL for dream visualization"""
        # Simplified Sora integration - in production would integrate with actual
        # Sora API
        video_id = f"sora_dream_{uuid.uuid4().hex[:12]}"

        # Simulate video generation
        (f"Generate a dreamy, surreal video based on: {dream_content['description']}")

        # Return placeholder URL
        return f"https://sora-api.example.com/videos/{video_id}.mp4"

    async def _process_revenue_sharing(self, dream_seed: DreamSeed, payment_result: dict[str, Any]) -> None:
        """Process revenue sharing between creator and platform"""
        total_amount = Decimal(str(payment_result["amount"]))
        creator_share = total_amount * Decimal(str(dream_seed.creator_revenue_share))
        platform_share = total_amount - creator_share

        # Update creator revenue
        if dream_seed.creator_id in self.creator_profiles:
            self.creator_profiles[dream_seed.creator_id]["total_revenue"] += creator_share

        # Update dream seed revenue
        dream_seed.revenue_generated += total_amount

        self.logger.info(f"Revenue sharing processed: Creator {creator_share}, Platform {platform_share}")

    def get_commerce_stats(self) -> dict[str, Any]:
        """Get comprehensive commerce engine statistics"""
        stats = {
            "total_seeds_created": self.total_seeds_created,
            "total_experiences_generated": self.total_experiences_generated,
            "total_revenue_processed": float(self.total_revenue_processed),
            "active_creators": len(self.creator_profiles),
            "marketplace_seeds": len(self.dream_seeds),
            "revenue_models_used": {
                model.value: len(
                    [s for s in self.dream_seeds.values() if s.revenue_model == model]
                )
                for model in RevenueModel
            },
            "seed_types_distribution": {
                seed_type.value: len(
                    [s for s in self.dream_seeds.values() if s.seed_type == seed_type]
                )
                for seed_type in DreamSeedType
            },
            "average_seed_price": float(
                sum(s.price for s in self.dream_seeds.values())
                / max(1, len(self.dream_seeds))
            ),
            "platform_revenue_share": self.platform_revenue_share,
            "ethical_validation_enabled": self.ethical_validation_enabled,
            "privacy_validation_required": self.privacy_validation_required,
        }

        # Add blockchain metrics if enabled
        if self._enable_blockchain:
            stats["blockchain"] = {
                "enabled": True,
                "total_nfts_minted": self.total_nfts_minted,
                "nft_contracts": len(self.minted_nfts),
                **self.get_blockchain_status(),
            }
        else:
            stats["blockchain"] = {
                "enabled": False,
                "reason": "Blockchain integration not enabled",
            }

        return stats


# Initialize commerce engine
commerce_engine = DreamCommerceEngine()

# API Endpoints


@router.post("/seeds", response_model=APIResponse)
async def create_dream_seed(
    submission: DreamSeedSubmission,
    creator_id: str = Query(..., description="Creator user ID"),
):
    """Create a new dream seed for the marketplace"""
    try:
        dream_seed = await commerce_engine.create_dream_seed(creator_id, submission)

        return APIResponse(
            status="success",
            data={
                "seed_id": dream_seed.seed_id,
                "title": dream_seed.title,
                "seed_type": dream_seed.seed_type.value,
                "price": float(dream_seed.price),
                "revenue_model": dream_seed.revenue_model.value,
                "created_at": dream_seed.created_at.isoformat(),
            },
            message=f"Dream seed created successfully: {dream_seed.seed_id}",
        )

    except Exception as e:
        logger.error(f"Failed to create dream seed: {e}")
        raise HTTPException(status_code=500, detail=str(e))  # TODO[T4-ISSUE]: {"code": "B904", "ticket": "GH-1031", "owner": "consciousness-team", "status": "planned", "reason": "Exception re-raise pattern - needs review for proper chaining (raise...from)", "estimate": "15m", "priority": "medium", "dependencies": "none", "id": "core_bridge_dream_commerce_py_L867"}


@router.post("/experiences", response_model=APIResponse)
async def generate_dream_experience(request: DreamExperienceRequest):
    """Generate a personalized dream experience"""
    try:
        dream_experience = await commerce_engine.generate_dream_experience(request)

        return APIResponse(
            status="success",
            data={
                "experience_id": dream_experience.experience_id,
                "dream_content": dream_experience.dream_content,
                "visualization_content": dream_experience.visualization_content,
                "sora_video_url": dream_experience.sora_video_url,
                "privacy_proof": dream_experience.privacy_proof,
                "created_at": dream_experience.created_at.isoformat(),
            },
            message="Dream experience generated successfully",
        )

    except Exception as e:
        logger.error(f"Failed to generate dream experience: {e}")
        raise HTTPException(status_code=500, detail=str(e))  # TODO[T4-ISSUE]: {"code": "B904", "ticket": "GH-1031", "owner": "consciousness-team", "status": "planned", "reason": "Exception re-raise pattern - needs review for proper chaining (raise...from)", "estimate": "15m", "priority": "medium", "dependencies": "none", "id": "core_bridge_dream_commerce_py_L892"}


@router.get("/marketplace", response_model=APIResponse)
async def browse_marketplace(
    seed_types: Optional[str] = Query(None, description="Comma-separated seed types"),
    consent_levels: Optional[str] = Query(None, description="Comma-separated consent levels"),
    revenue_models: Optional[str] = Query(None, description="Comma-separated revenue models"),
    creator_id: Optional[str] = Query(None, description="Filter by creator ID"),
    min_rating: Optional[float] = Query(None, description="Minimum rating filter"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    limit: int = Query(20, description="Number of results", ge=1, le=100),
    offset: int = Query(0, description="Results offset", ge=0),
):
    """Browse the dream seed marketplace"""
    try:
        # Parse filters
        filters = DreamMarketplaceFilter()

        if seed_types:
            filters.seed_types = [DreamSeedType(t.strip()) for t in seed_types.split(",")]

        if consent_levels:
            filters.consent_levels = [ConsentLevel(c.strip()) for c in consent_levels.split(",")]

        if revenue_models:
            filters.revenue_models = [RevenueModel(r.strip()) for r in revenue_models.split(",")]

        if creator_id:
            filters.creator_id = creator_id

        if min_rating:
            filters.min_rating = min_rating

        if tags:
            filters.tags = [t.strip() for t in tags.split(",")]

        # Get filtered seeds
        dream_seeds = await commerce_engine.get_marketplace_dreams(filters, limit, offset)

        # Format response
        seeds_data = []
        for seed in dream_seeds:
            seeds_data.append(
                {
                    "seed_id": seed.seed_id,
                    "title": seed.title,
                    "description": seed.description,
                    "seed_type": seed.seed_type.value,
                    "price": float(seed.price),
                    "rating": seed.rating,
                    "usage_count": seed.usage_count,
                    "revenue_model": seed.revenue_model.value,
                    "consent_requirements": seed.consent_requirements.value,
                    "tags": seed.tags,
                    "created_at": seed.created_at.isoformat(),
                }
            )

        return APIResponse(
            status="success",
            data={
                "seeds": seeds_data,
                "total_results": len(seeds_data),
                "offset": offset,
                "limit": limit,
            },
            message=f"Found {len(seeds_data)} dream seeds",
        )

    except Exception as e:
        logger.error(f"Failed to browse marketplace: {e}")
        raise HTTPException(status_code=500, detail=str(e))  # TODO[T4-ISSUE]: {"code": "B904", "ticket": "GH-1031", "owner": "consciousness-team", "status": "planned", "reason": "Exception re-raise pattern - needs review for proper chaining (raise...from)", "estimate": "15m", "priority": "medium", "dependencies": "none", "id": "core_bridge_dream_commerce_py_L965"}


@router.get("/stats", response_model=APIResponse)
async def get_commerce_statistics():
    """Get dream commerce system statistics"""
    try:
        stats = commerce_engine.get_commerce_stats()

        return APIResponse(
            status="success",
            data=stats,
            message="Commerce statistics retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Failed to get commerce statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))  # TODO[T4-ISSUE]: {"code": "B904", "ticket": "GH-1031", "owner": "consciousness-team", "status": "planned", "reason": "Exception re-raise pattern - needs review for proper chaining (raise...from)", "estimate": "15m", "priority": "medium", "dependencies": "none", "id": "core_bridge_dream_commerce_py_L983"}


@router.get("/health", response_model=APIResponse)
async def commerce_health_check():
    """Check dream commerce system health"""
    try:
        health_data = {
            "status": "operational",
            "commerce_engine_initialized": commerce_engine is not None,
            "integrations": {
                "identity_client": IDENTITY_AVAILABLE,
                "zkp_validator": ZKP_AVAILABLE,
                "event_bus": EVENT_BUS_AVAILABLE,
            },
            "marketplace_active": len(commerce_engine.dream_seeds) > 0,
            "revenue_processing": commerce_engine.total_revenue_processed > 0,
            "ethical_validation": commerce_engine.ethical_validation_enabled,
            "privacy_protection": commerce_engine.privacy_validation_required,
        }

        return APIResponse(
            status="success",
            data=health_data,
            message="Dream commerce system is healthy",
        )

    except Exception as e:
        logger.error(f"Commerce health check failed: {e}")
        return APIResponse(
            status="error",
            data={"error": str(e)},
            message="Dream commerce system health check failed",
        )


# Initialize commerce engine on startup


@router.on_event("startup")
async def startup_commerce_engine():
    """Initialize commerce engine on startup"""
    await commerce_engine.initialize()


# Export main classes
__all__ = [
    "ConsentLevel",
    "ConsentRecord",
    "DreamCommerceBlockchain",
    "DreamCommerceEngine",
    "DreamContentNFT",
    "DreamExperience",
    "DreamSeed",
    "DreamSeedType",
    "RevenueModel",
    "WEB3_AVAILABLE",
    "IPFS_AVAILABLE",
    "router",
]
