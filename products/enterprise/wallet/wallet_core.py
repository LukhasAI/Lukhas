#!/usr/bin/env python3
"""
WΛLLET Core - Digital Identity & Wallet System
Self-Sovereign Identity with NFT verification and symbolic currency
"""
from consciousness.qi import qi
import streamlit as st

import asyncio
import hashlib

# Cryptographic imports (simplified for demo)
import secrets
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class CredentialType(Enum):
    """Types of verifiable credentials"""

    DEVELOPER = "developer"
    VERIFIED_USER = "verified_user"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"
    NFT_HOLDER = "nft_holder"
    PREMIUM = "premium"
    LAMBDA_CERTIFIED = "lambda_certified"


class TransactionStatus(Enum):
    """Transaction status types"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ΛiD:
    """Lambda Identity (Decentralized Identifier)"""

    did: str
    public_key: str
    private_key: str  # In production, stored securely
    profile: dict[str, Any]
    credentials: list[str]
    created_at: float
    lambda_signature: str


@dataclass
class Transaction:
    """Blockchain-style transaction"""

    id: str
    from_did: str
    to_did: str
    amount: float
    currency: str
    status: TransactionStatus
    timestamp: float
    memo: Optional[str]
    fee: float
    signature: str


@dataclass
class NFTToken:
    """Non-Fungible Token representation"""

    token_id: str
    contract_address: str
    owner_did: str
    metadata: dict[str, Any]
    verified: bool
    lambda_certified: bool
    created_at: float


class WΛLLET:
    """
    Main WΛLLET engine for digital identity and wallet management
    Powered by LUKHAS consciousness and Lambda branding
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or self._default_config()
        self.lambda_brand = "Λ"

        # Storage (in production, use database)
        self.identities: dict[str, ΛiD] = {}
        self.balances: dict[str, float] = {}
        self.transactions: list[Transaction] = []
        self.nfts: dict[str, NFTToken] = {}
        self.credentials: dict[str, list[str]] = {}

        # Initialize subsystems
        self.identity_manager = IdentityManager(self)
        self.ledger = Ledger(self)
        self.nft_verifier = NFTVerifier(self)
        self.auth_service = AuthService(self)

        # Genesis block for ledger
        self._init_genesis()

    def _default_config(self) -> dict:
        """Default WΛLLET configuration"""
        return {
            "brand": "LUKHAS",
            "symbol": "Λ",
            "currency": "LUK",
            "initial_balance": 100.0,
            "transaction_fee": 0.1,
            "qi_resistant": True,
            "privacy_mode": True,
            "testnet": True,
        }

    def _init_genesis(self):
        """Initialize genesis block/state"""
        # Create system identity
        system_did = "did:lambda:system"
        system_identity = ΛiD(
            did=system_did,
            public_key="SYSTEM_PUBLIC_KEY",
            private_key="SYSTEM_PRIVATE_KEY",
            profile={"name": "LUKHAS System", "type": "system"},
            credentials=["admin", "lambda_certified"],
            created_at=time.time(),
            lambda_signature=f"{self.lambda_brand}-GENESIS",
        )
        self.identities[system_did] = system_identity
        self.balances[system_did] = 1000000.0  # System reserve

    async def create_identity(self, profile: dict[str, Any], credentials: Optional[list[str]] = None) -> ΛiD:
        """
        Create a new Lambda Identity (DID)

        Args:
            profile: User profile information
            credentials: Initial verifiable credentials

        Returns:
            New ΛiD object
        """
        # Generate DID
        did_uuid = str(uuid.uuid4())
        did = f"did:lambda:{did_uuid}"

        # Generate key pair (simplified - use proper crypto in production)
        private_key = secrets.token_hex(32)
        public_key = hashlib.sha256(private_key.encode()).hexdigest()

        # Create Lambda signature
        lambda_signature = f"{self.lambda_brand}-{did_uuid[:8].upper()}"

        # Create identity
        identity = ΛiD(
            did=did,
            public_key=public_key,
            private_key=private_key,
            profile=profile,
            credentials=credentials or [],
            created_at=time.time(),
            lambda_signature=lambda_signature,
        )

        # Store identity
        self.identities[did] = identity
        self.credentials[did] = credentials or []

        # Initialize balance with welcome bonus
        self.balances[did] = self.config["initial_balance"]

        # Create welcome transaction
        await self.ledger.create_transaction(
            from_did="did:lambda:system",
            to_did=did,
            amount=self.config["initial_balance"],
            memo="Welcome to WΛLLET!",
        )

        return identity

    async def get_balance(self, did: str) -> float:
        """Get wallet balance for a DID"""
        return self.balances.get(did, 0.0)

    async def send_transaction(
        self, from_did: str, to_did: str, amount: float, memo: Optional[str] = None
    ) -> Transaction:
        """
        Send a transaction between DIDs

        Args:
            from_did: Sender's DID
            to_did: Recipient's DID
            amount: Amount to send
            memo: Optional transaction memo

        Returns:
            Transaction object
        """
        # Validate identities
        if from_did not in self.identities:
            raise ValueError(f"Unknown sender: {from_did}")
        if to_did not in self.identities:
            raise ValueError(f"Unknown recipient: {to_did}")

        # Check balance
        balance = self.balances.get(from_did, 0.0)
        total_amount = amount + self.config["transaction_fee"]

        if balance < total_amount:
            raise ValueError(f"Insufficient balance: {balance} < {total_amount}")

        # Create transaction
        tx = await self.ledger.create_transaction(from_did=from_did, to_did=to_did, amount=amount, memo=memo)

        # Update balances
        self.balances[from_did] -= total_amount
        self.balances[to_did] += amount
        self.balances["did:lambda:system"] += self.config["transaction_fee"]

        return tx

    async def verify_nft(self, token_id: str, owner_did: str) -> bool:
        """
        Verify NFT ownership

        Args:
            token_id: NFT token ID
            owner_did: Claimed owner's DID

        Returns:
            True if verified, False otherwise
        """
        return await self.nft_verifier.verify(token_id, owner_did)

    async def mint_nft(self, owner_did: str, metadata: dict[str, Any]) -> NFTToken:
        """
        Mint a new Lambda NFT

        Args:
            owner_did: Owner's DID
            metadata: NFT metadata

        Returns:
            New NFTToken object
        """
        # Generate token ID
        token_id = f"lambda-{uuid.uuid4().hex[:16]}"

        # Create NFT
        nft = NFTToken(
            token_id=token_id,
            contract_address="lambda:nft:contract",
            owner_did=owner_did,
            metadata=metadata,
            verified=True,
            lambda_certified=True,
            created_at=time.time(),
        )

        # Store NFT
        self.nfts[token_id] = nft

        return nft

    async def add_credential(self, did: str, credential: str) -> bool:
        """Add a verifiable credential to an identity"""
        if did not in self.identities:
            return False

        if credential not in self.credentials.get(did, []):
            self.credentials[did].append(credential)
            self.identities[did].credentials.append(credential)

        return True

    async def verify_credential(self, did: str, credential: str) -> bool:
        """Verify if an identity has a specific credential"""
        return credential in self.credentials.get(did, [])


class IdentityManager:
    """Manages Lambda identities and DIDs"""

    def __init__(self, wallet: WΛLLET):
        self.wallet = wallet

    async def authenticate(self, did: str, signature: str) -> bool:
        """Authenticate an identity using signature"""
        identity = self.wallet.identities.get(did)
        if not identity:
            return False

        # Simplified signature verification
        expected = hashlib.sha256(f"{did}{identity.public_key}".encode()).hexdigest()

        return signature == expected

    async def rotate_keys(self, did: str) -> tuple[str, str]:
        """Rotate cryptographic keys for an identity"""
        identity = self.wallet.identities.get(did)
        if not identity:
            raise ValueError(f"Unknown identity: {did}")

        # Generate new keys
        new_private = secrets.token_hex(32)
        new_public = hashlib.sha256(new_private.encode()).hexdigest()

        # Update identity
        identity.private_key = new_private
        identity.public_key = new_public

        return new_public, new_private

    async def export_identity(self, did: str) -> dict[str, Any]:
        """Export identity for backup (without private key)"""
        identity = self.wallet.identities.get(did)
        if not identity:
            raise ValueError(f"Unknown identity: {did}")

        return {
            "did": identity.did,
            "public_key": identity.public_key,
            "profile": identity.profile,
            "credentials": identity.credentials,
            "created_at": identity.created_at,
            "lambda_signature": identity.lambda_signature,
        }


class Ledger:
    """Manages the transaction ledger"""

    def __init__(self, wallet: WΛLLET):
        self.wallet = wallet
        self.chain: list[Transaction] = []

    async def create_transaction(
        self, from_did: str, to_did: str, amount: float, memo: Optional[str] = None
    ) -> Transaction:
        """Create and record a transaction"""
        # Generate transaction ID
        tx_id = str(uuid.uuid4())

        # Create signature (simplified)
        signature = hashlib.sha256(f"{tx_id}{from_did}{to_did}{amount}".encode()).hexdigest()

        # Create transaction
        tx = Transaction(
            id=tx_id,
            from_did=from_did,
            to_did=to_did,
            amount=amount,
            currency=self.wallet.config["currency"],
            status=TransactionStatus.CONFIRMED,
            timestamp=time.time(),
            memo=memo,
            fee=self.wallet.config["transaction_fee"],
            signature=signature,
        )

        # Add to ledger
        self.chain.append(tx)
        self.wallet.transactions.append(tx)

        return tx

    async def get_transactions(self, did: str, limit: int = 10) -> list[Transaction]:
        """Get transactions for a DID"""
        user_txs = [tx for tx in self.wallet.transactions if tx.from_did == did or tx.to_did == did]

        # Sort by timestamp descending
        user_txs.sort(key=lambda tx: tx.timestamp, reverse=True)

        return user_txs[:limit]

    async def verify_chain(self) -> bool:
        """Verify the integrity of the transaction chain"""
        for tx in self.chain:
            # Verify signature
            expected_sig = hashlib.sha256(f"{tx.id}{tx.from_did}{tx.to_did}{tx.amount}".encode()).hexdigest()

            if tx.signature != expected_sig:
                return False

        return True


class NFTVerifier:
    """Verifies NFT ownership and authenticity"""

    def __init__(self, wallet: WΛLLET):
        self.wallet = wallet

    async def verify(self, token_id: str, owner_did: str) -> bool:
        """Verify NFT ownership"""
        nft = self.wallet.nfts.get(token_id)

        if not nft:
            # Could check external blockchains here
            return False

        return nft.owner_did == owner_did and nft.verified

    async def transfer_nft(self, token_id: str, from_did: str, to_did: str) -> bool:
        """Transfer NFT ownership"""
        nft = self.wallet.nfts.get(token_id)

        if not nft or nft.owner_did != from_did:
            return False

        # Update ownership
        nft.owner_did = to_did

        # Create transfer record
        await self.wallet.ledger.create_transaction(
            from_did=from_did,
            to_did=to_did,
            amount=0.0,
            memo=f"NFT Transfer: {token_id}",
        )

        return True

    async def get_nfts(self, owner_did: str) -> list[NFTToken]:
        """Get all NFTs owned by a DID"""
        return [nft for nft in self.wallet.nfts.values() if nft.owner_did == owner_did]


class AuthService:
    """Authentication and authorization service"""

    def __init__(self, wallet: WΛLLET):
        self.wallet = wallet
        self.sessions: dict[str, dict] = {}

    async def login(self, did: str, password: str) -> Optional[str]:
        """Login with DID and password"""
        # In production, use proper password hashing
        identity = self.wallet.identities.get(did)

        if not identity:
            return None

        # Create session token
        session_token = secrets.token_urlsafe(32)

        self.sessions[session_token] = {
            "did": did,
            "created_at": time.time(),
            "expires_at": time.time() + 3600,  # 1 hour
        }

        return session_token

    async def verify_session(self, token: str) -> Optional[str]:
        """Verify session token and return DID"""
        session = self.sessions.get(token)

        if not session:
            return None

        if time.time() > session["expires_at"]:
            del self.sessions[token]
            return None

        return session["did"]

    async def logout(self, token: str) -> bool:
        """Logout and invalidate session"""
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False


# Demo usage
if __name__ == "__main__":

    async def demo():
        """Demo WΛLLET functionality"""
        print("💳 WΛLLET - Digital Identity & Wallet Demo")
        print("=" * 50)

        # Initialize wallet
        wallet = WΛLLET()

        # Create identities
        alice = await wallet.create_identity(
            profile={"name": "Alice", "email": "alice@lukhas.ai"},
            credentials=["developer", "verified_user"],
        )

        bob = await wallet.create_identity(
            profile={"name": "Bob", "email": "bob@lukhas.ai"},
            credentials=["verified_user"],
        )

        print("\n✅ Created identities:")
        print(f"  Alice: {alice.did}")
        print(f"  Λ Signature: {alice.lambda_signature}")
        print(f"  Bob: {bob.did}")
        print(f"  Λ Signature: {bob.lambda_signature}")

        # Check balances
        alice_balance = await wallet.get_balance(alice.did)
        bob_balance = await wallet.get_balance(bob.did)

        print("\n💰 Initial balances:")
        print(f"  Alice: {alice_balance} LUK")
        print(f"  Bob: {bob_balance} LUK")

        # Send transaction
        tx = await wallet.send_transaction(
            from_did=alice.did,
            to_did=bob.did,
            amount=25.0,
            memo="Payment for Lambda services",
        )

        print("\n📤 Transaction sent:")
        print(f"  ID: {tx.id}")
        print(f"  Amount: {tx.amount} {tx.currency}")
        print(f"  Fee: {tx.fee} {tx.currency}")

        # Check updated balances
        alice_balance = await wallet.get_balance(alice.did)
        bob_balance = await wallet.get_balance(bob.did)

        print("\n💰 Updated balances:")
        print(f"  Alice: {alice_balance} LUK")
        print(f"  Bob: {bob_balance} LUK")

        # Mint NFT
        nft = await wallet.mint_nft(
            owner_did=alice.did,
            metadata={
                "name": "Lambda Genesis NFT",
                "description": "First NFT in the Lambda ecosystem",
                "image": "ipfs://lambda-genesis.png",
                "attributes": [
                    {"trait": "Rarity", "value": "Legendary"},
                    {"trait": "Power", "value": "100"},
                ],
            },
        )

        print("\n🎨 NFT minted:")
        print(f"  Token ID: {nft.token_id}")
        print(f"  Owner: {alice.did}")
        print(f"  Lambda Certified: {nft.lambda_certified}")

        # Verify NFT ownership
        verified = await wallet.verify_nft(nft.token_id, alice.did)
        print(f"\n✅ NFT verification: {verified}")

        # Verify credentials
        has_dev = await wallet.verify_credential(alice.did, "developer")
        print(f"\n🎓 Alice has 'developer' credential: {has_dev}")

    # Run demo
    asyncio.run(demo())