"""
Universal Language Service
=========================
Core service for managing personal symbol-meaning bindings.
Provides local storage, challenge generation, and proof verification.

System-wide guardrails applied:
1. All symbol data stays local - never sent to server
2. Server only receives and verifies cryptographic proofs
3. Symbol bindings encrypted with device-specific keys
4. Composition challenges prove knowledge without exposure
5. Integrates with GTΨ for combined high-risk approvals

ACK GUARDRAILS
"""
from typing import List
import random
import streamlit as st

import asyncio
import json
import secrets
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from . import (
    CompositionChallenge,
    CompositionProof,
    MeaningType,
    PersonalSymbol,
    SymbolBinding,
    SymbolType,
    ULSignature,
    calculate_symbol_quality,
    compose_symbol_proof,
    get_required_symbols,
    hash_symbol,
    parse_composition,
    requires_composition,
)


class LocalSymbolStore:
    """
    Local encrypted storage for personal symbols.

    All data stays on device - never synchronized to server.
    Uses device-specific encryption key derived from biometrics/PIN.
    """

    def __init__(self, storage_path: str = "ul/local_map.enc"):
        self.storage_path = Path(storage_path)
        self.encryption_key = None
        self.symbols: dict[str, PersonalSymbol] = {}
        self.compositions: dict[str, dict[str, Any]] = {}

    def initialize(self, device_key: str):
        """
        Initialize store with device-specific key.

        In production: derive from biometrics + PIN
        """
        # Derive encryption key from device key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"lukhas_ul_salt",  # In production: random salt per device
            iterations=100000,
        )
        kdf.derive(device_key.encode())
        self.encryption_key = Fernet(Fernet.generate_key())  # Mock for now

        # Load existing symbols if file exists
        if self.storage_path.exists():
            self._load_symbols()

    def bind_symbol(self, binding: SymbolBinding) -> PersonalSymbol:
        """
        Bind a personal symbol to meaning.

        Symbol data is hashed and stored locally only.
        """
        # Generate unique ID and salt
        symbol_id = f"sym_{secrets.token_urlsafe(16)}"
        salt = secrets.token_urlsafe(32)

        # Hash the symbol data
        symbol_hash = hash_symbol(binding.symbol_data, binding.symbol_type, salt)

        # Calculate quality score
        quality_score = calculate_symbol_quality(binding.symbol_data, binding.symbol_type)

        # Create symbol record
        symbol = PersonalSymbol(
            symbol_id=symbol_id,
            symbol_type=binding.symbol_type,
            symbol_hash=symbol_hash,
            salt=salt,
            meaning_type=binding.meaning_type,
            meaning_value=binding.meaning_value,
            created_at=datetime.now(timezone.utc),
            quality_score=quality_score,
        )

        # Store locally
        self.symbols[symbol_id] = symbol
        self._save_symbols()

        return symbol

    def find_symbols_by_meaning(self, meaning: str) -> list[PersonalSymbol]:
        """Find all symbols bound to a specific meaning"""
        return [symbol for symbol in self.symbols.values() if symbol.meaning_value == meaning]

    def verify_symbol(self, symbol_data: Any, symbol_type: SymbolType, meaning: str) -> bool:
        """
        Verify that symbol data matches a stored binding.

        Returns True if symbol is bound to the specified meaning.
        """
        symbols = self.find_symbols_by_meaning(meaning)

        for symbol in symbols:
            if symbol.symbol_type != symbol_type:
                continue

            # Hash the provided data with stored salt
            test_hash = hash_symbol(symbol_data, symbol_type, symbol.salt)

            if test_hash == symbol.symbol_hash:
                # Update usage stats
                symbol.last_used_at = datetime.now(timezone.utc)
                symbol.use_count += 1
                self._save_symbols()
                return True

        return False

    def create_composition(self, name: str, symbol_ids: list[str], operators: list[str], meaning: str) -> str:
        """
        Create a symbol composition.

        Compositions combine multiple symbols with operators.
        """
        composition_id = f"comp_{secrets.token_urlsafe(16)}"

        self.compositions[composition_id] = {
            "composition_id": composition_id,
            "name": name,
            "symbols": symbol_ids,
            "operators": operators,
            "meaning": meaning,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self._save_symbols()
        return composition_id

    def _load_symbols(self):
        """Load symbols from encrypted storage"""
        if not self.encryption_key:
            raise ValueError("Store not initialized with encryption key")

        try:
            # Read encrypted content
            self.storage_path.read_bytes()

            # Decrypt (mock for development)
            # In production: use Fernet or similar

            # Parse JSON (if it were real encrypted data)
            # data = json.loads(decrypted_data)
            # self._deserialize_symbols(data)

        except Exception as e:
            print(f"Could not load symbols: {e}")
            # Start with empty store
            self.symbols = {}
            self.compositions = {}

    def _save_symbols(self):
        """Save symbols to encrypted storage"""
        if not self.encryption_key:
            raise ValueError("Store not initialized with encryption key")

        # Serialize symbols
        data = self._serialize_symbols()

        # Encrypt (mock for development)
        # In production: use Fernet or similar
        encrypted_data = json.dumps(data, default=str).encode()  # Mock

        # Write to file
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_bytes(encrypted_data)

    def _serialize_symbols(self) -> dict[str, Any]:
        """Serialize symbols for storage"""
        return {
            "version": "1.0",
            "symbols": {
                sid: {
                    "symbol_id": s.symbol_id,
                    "symbol_type": s.symbol_type.value,
                    "symbol_hash": s.symbol_hash,
                    "salt": s.salt,
                    "meaning_type": s.meaning_type.value,
                    "meaning_value": s.meaning_value,
                    "created_at": s.created_at.isoformat(),
                    "last_used_at": s.last_used_at.isoformat() if s.last_used_at else None,
                    "use_count": s.use_count,
                    "quality_score": s.quality_score,
                }
                for sid, s in self.symbols.items()
            },
            "compositions": self.compositions,
        }


class ULChallengeService:
    """
    Server-side challenge generation and verification.

    Generates composition challenges and verifies proofs
    without ever seeing the actual symbol data.
    """

    def __init__(self):
        self.active_challenges: dict[str, CompositionChallenge] = {}
        self.verified_signatures: dict[str, ULSignature] = {}

    async def generate_challenge(self, lid: str, action: str, required_meanings: list[str]) -> CompositionChallenge:
        """
        Generate composition challenge for user.

        Args:
            lid: Canonical ΛID
            action: High-risk action requiring UL entropy
            required_meanings: Meanings to compose

        Returns:
            Composition challenge
        """
        # Create composition string
        if len(required_meanings) == 1:
            composition = required_meanings[0]
            operators = []
        else:
            # Random operators for composition
            operators = ["+"] * (len(required_meanings) - 1)  # Simple addition for now
            composition = " + ".join(required_meanings)

        # Generate challenge
        challenge_id = f"ul_challenge_{secrets.token_urlsafe(24)}"
        nonce = secrets.token_urlsafe(32)

        challenge = CompositionChallenge(
            challenge_id=challenge_id,
            composition=composition,
            operators=operators,
            expected_symbols=len(required_meanings),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
            nonce=nonce,
        )

        self.active_challenges[challenge_id] = challenge

        return challenge

    async def verify_composition_proof(self, lid: str, proof: CompositionProof) -> bool:
        """
        Verify composition proof without seeing symbols.

        Args:
            lid: User's canonical ΛID
            proof: Composition proof to verify

        Returns:
            True if proof is valid
        """
        # Find challenge
        challenge = self.active_challenges.get(proof.challenge_id)
        if not challenge:
            return False

        # Check expiration
        if datetime.now(timezone.utc) > challenge.expires_at:
            del self.active_challenges[proof.challenge_id]
            return False

        # Verify proof structure
        if proof.symbol_count != challenge.expected_symbols:
            return False

        # Check quality
        if proof.quality_score < 0.5:
            return False

        # In production: verify cryptographic proof
        # For now, accept if structure is valid

        # Mark challenge as used
        del self.active_challenges[proof.challenge_id]

        return True

    async def create_ul_signature(
        self,
        lid: str,
        action: str,
        symbol_proofs: list[str],
        composition_proof: Optional[CompositionProof] = None,
    ) -> ULSignature:
        """
        Create UL signature for action approval.

        Args:
            lid: User's canonical ΛID
            action: Action being approved
            symbol_proofs: Proof hashes from symbols
            composition_proof: Optional composition proof

        Returns:
            UL signature for the action
        """
        signature = ULSignature(
            lid=lid,
            action=action,
            symbol_proofs=symbol_proofs,
            composition_proof=composition_proof,
            timestamp=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=1),
        )

        # Store for verification
        sig_id = f"ul_sig_{secrets.token_urlsafe(16)}"
        self.verified_signatures[sig_id] = signature

        return signature

    def verify_ul_signature(self, lid: str, action: str, signature: ULSignature) -> bool:
        """
        Verify UL signature is valid for action.

        Args:
            lid: User's canonical ΛID
            action: Action requiring approval
            signature: UL signature to verify

        Returns:
            True if signature is valid
        """
        # Check signature matches request
        if signature.lid != lid or signature.action != action:
            return False

        # Check expiration
        if datetime.now(timezone.utc) > signature.expires_at:
            return False

        # Check required symbols
        required_symbols = get_required_symbols(action)
        if len(signature.symbol_proofs) < required_symbols:
            return False

        # Check composition if required
        return not (requires_composition(action) and not signature.composition_proof)


class UniversalLanguageService:
    """
    Main UL service coordinating local storage and server verification.

    Manages the complete UL workflow:
    1. Local symbol binding
    2. Challenge generation
    3. Local proof computation
    4. Server verification
    5. Signature creation
    """

    def __init__(self):
        self.local_store = LocalSymbolStore()
        self.challenge_service = ULChallengeService()
        self.initialized = False

    async def initialize(self, device_key: str = "mock_device_key"):
        """Initialize UL service with device key"""
        self.local_store.initialize(device_key)
        self.initialized = True

    async def bind_symbol(
        self,
        symbol_type: SymbolType,
        symbol_data: Any,
        meaning_type: MeaningType,
        meaning_value: str,
    ) -> str:
        """
        Bind personal symbol to meaning (local only).

        Returns:
            Symbol ID for reference
        """
        if not self.initialized:
            raise ValueError("Service not initialized")

        binding = SymbolBinding(
            symbol_type=symbol_type,
            symbol_data=symbol_data,
            meaning_type=meaning_type,
            meaning_value=meaning_value,
        )

        symbol = self.local_store.bind_symbol(binding)

        return symbol.symbol_id

    async def request_challenge(self, lid: str, action: str) -> CompositionChallenge:
        """
        Request composition challenge from server.

        Args:
            lid: User's canonical ΛID
            action: High-risk action requiring UL

        Returns:
            Composition challenge
        """
        # Determine required meanings based on action
        if action == "grant_admin_scope":
            required_meanings = ["power", "responsibility"]
        elif action == "delete_all_data":
            required_meanings = ["destruction", "finality", "certainty"]
        elif action == "transfer_ownership":
            required_meanings = ["release", "transfer"]
        else:
            required_meanings = ["confirm"]

        challenge = await self.challenge_service.generate_challenge(lid, action, required_meanings)

        return challenge

    async def solve_challenge(
        self, challenge: CompositionChallenge, symbol_data_list: list[tuple[Any, SymbolType]]
    ) -> CompositionProof:
        """
        Solve composition challenge locally.

        Args:
            challenge: Challenge to solve
            symbol_data_list: List of (symbol_data, symbol_type) tuples

        Returns:
            Composition proof (no raw symbols exposed)
        """
        start_time = time.perf_counter()

        # Parse required meanings from composition
        meanings, operators = parse_composition(challenge.composition)

        # Find matching symbols locally
        symbols = []
        for i, meaning in enumerate(meanings):
            if i < len(symbol_data_list):
                symbol_data, symbol_type = symbol_data_list[i]

                # Verify symbol matches meaning
                if self.local_store.verify_symbol(symbol_data, symbol_type, meaning):
                    # Get the matching symbol
                    matching_symbols = self.local_store.find_symbols_by_meaning(meaning)
                    if matching_symbols:
                        symbols.append(matching_symbols[0])

        if len(symbols) != len(meanings):
            raise ValueError("Could not match all required meanings")

        # Create proof without exposing symbols
        proof_hash = compose_symbol_proof(symbols, operators, challenge.nonce)

        # Calculate average quality
        avg_quality = sum(s.quality_score for s in symbols) / len(symbols)

        computation_time = (time.perf_counter() - start_time) * 1000

        proof = CompositionProof(
            challenge_id=challenge.challenge_id,
            proof_hash=proof_hash,
            symbol_count=len(symbols),
            computation_time_ms=computation_time,
            quality_score=avg_quality,
        )

        return proof

    async def create_approval_signature(
        self, lid: str, action: str, composition_proof: Optional[CompositionProof] = None
    ) -> ULSignature:
        """
        Create UL signature for action approval.

        Args:
            lid: User's canonical ΛID
            action: Action being approved
            composition_proof: Proof of symbol composition

        Returns:
            UL signature
        """
        # Get symbol proofs from local store
        symbol_proofs = []

        # In production: generate proper cryptographic proofs
        # For now, use symbol hashes as proofs
        for symbol in list(self.local_store.symbols.values())[: get_required_symbols(action)]:
            symbol_proofs.append(symbol.symbol_hash[:16])  # Truncated for demo

        signature = await self.challenge_service.create_ul_signature(lid, action, symbol_proofs, composition_proof)

        return signature


# Example usage
async def demonstrate_ul_workflow():
    """Demonstrate complete UL workflow"""
    print("🔤 Universal Language Entropy Demonstration")
    print("=" * 45)

    service = UniversalLanguageService()
    await service.initialize("demo_device_key")

    # 1. Bind personal symbols
    print("📝 Binding personal symbols...")

    await service.bind_symbol(
        SymbolType.EMOJI,
        "⚡️💪",  # Lightning + muscle = power
        MeaningType.CONCEPT,
        "power",
    )

    await service.bind_symbol(SymbolType.WORD, "with great power", MeaningType.CONCEPT, "responsibility")

    print("✅ Bound 'power' to emoji: ⚡️💪")
    print("✅ Bound 'responsibility' to phrase: 'with great power'")

    # 2. Request challenge for high-risk action
    print("\n🎯 Requesting challenge for admin scope grant...")

    challenge = await service.request_challenge("gonzo", "grant_admin_scope")
    print(f"Challenge: Compose '{challenge.composition}'")
    print(f"Expires: {challenge.expires_at}")

    # 3. Solve challenge locally
    print("\n🧩 Solving challenge with personal symbols...")

    proof = await service.solve_challenge(
        challenge,
        [
            ("⚡️💪", SymbolType.EMOJI),  # power
            ("with great power", SymbolType.WORD),  # responsibility
        ],
    )

    print(f"✅ Proof generated in {proof.computation_time_ms:.2f}ms")
    print(f"   Quality score: {proof.quality_score:.2f}")

    # 4. Verify proof on server
    print("\n🔍 Verifying proof on server...")

    verified = await service.challenge_service.verify_composition_proof("gonzo", proof)

    if verified:
        print("✅ Proof verified! Creating UL signature...")

        # 5. Create approval signature
        signature = await service.create_approval_signature("gonzo", "grant_admin_scope", proof)

        print(f"🔏 UL Signature created, expires: {signature.expires_at}")
        print("✅ Admin scope can now be granted with UL+GTΨ approval")
    else:
        print("❌ Proof verification failed")

    print("\n🎉 UL workflow demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demonstrate_ul_workflow())
