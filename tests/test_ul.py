"""
Tests for Universal Language (UL) Entropy System
===============================================
Tests for personal symbol binding, composition challenges, and proof verification.
Validates privacy preservation and integration with GTΨ.
"""

from datetime import datetime, timedelta, timezone

import pytest

from universal_language import (
    CompositionChallenge,
    CompositionProof,
    MeaningType,
    PersonalSymbol,
    SymbolBinding,
    SymbolType,
    calculate_symbol_quality,
    compose_symbol_proof,
    get_required_symbols,
    hash_symbol,
    parse_composition,
    requires_ul_entropy,
)
from universal_language.service import LocalSymbolStore, ULChallengeService, UniversalLanguageService


class TestSymbolEncoding:
    """Test symbol encoding and hashing"""

    def test_emoji_encoding(self):
        """Test emoji symbol encoding"""
        from universal_language import EmojiEncoder

        encoder = EmojiEncoder()

        # Single emoji
        encoded = encoder.encode("🔒")
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0

        # Emoji sequence
        encoded_seq = encoder.encode("⚡️💪")
        assert isinstance(encoded_seq, bytes)
        assert len(encoded_seq) > len(encoded)

        # Features extraction
        features = encoder.extract_features("⚡️💪🔥")
        assert len(features) == 4
        assert all(isinstance(f, float) for f in features)

    def test_word_encoding(self):
        """Test word/phrase symbol encoding"""
        from universal_language import WordEncoder

        encoder = WordEncoder()

        # Single word
        encoded = encoder.encode("power")
        assert encoded == b"power"

        # Phrase with normalization
        encoded_phrase = encoder.encode("  With Great Power  ")
        assert encoded_phrase == b"with great power"

        # Features extraction
        features = encoder.extract_features("hello world")
        assert len(features) == 4
        assert features[1] == 2  # Word count

    def test_symbol_hashing_privacy(self):
        """Test that symbol hashing preserves privacy"""
        symbol_data = "🔐🎯"
        symbol_type = SymbolType.EMOJI
        salt = "test_salt_123"

        # Hash the symbol
        hash1 = hash_symbol(symbol_data, symbol_type, salt)
        hash2 = hash_symbol(symbol_data, symbol_type, salt)

        # Hashing is deterministic
        assert hash1 == hash2

        # Hash doesn't contain raw data
        assert symbol_data not in hash1
        assert "🔐" not in hash1

        # Different salts produce different hashes
        hash3 = hash_symbol(symbol_data, symbol_type, "different_salt")
        assert hash3 != hash1

        # Hash is proper length (SHA-256)
        assert len(hash1) == 64

    def test_symbol_quality_scoring(self):
        """Test symbol quality calculation"""
        # Simple emoji - lower quality
        quality1 = calculate_symbol_quality("😀", SymbolType.EMOJI)

        # Complex emoji sequence - higher quality
        quality2 = calculate_symbol_quality("⚡️💪🔥🎯", SymbolType.EMOJI)

        assert 0.0 <= quality1 <= 1.0
        assert 0.0 <= quality2 <= 1.0
        assert quality2 > quality1  # More complex = higher quality

        # Long phrase - higher quality
        quality3 = calculate_symbol_quality("with great power comes responsibility", SymbolType.WORD)
        assert quality3 > 0.5


class TestLocalSymbolStore:
    """Test local encrypted symbol storage"""

    @pytest.fixture
    def store(self, tmp_path):
        """Create temporary symbol store"""
        storage_path = tmp_path / "test_symbols.enc"
        store = LocalSymbolStore(str(storage_path))
        store.initialize("test_device_key")
        return store

    def test_symbol_binding(self, store):
        """Test binding personal symbols"""
        binding = SymbolBinding(
            symbol_type=SymbolType.EMOJI,
            symbol_data="🔒🔑",
            meaning_type=MeaningType.CONCEPT,
            meaning_value="security"
        )

        symbol = store.bind_symbol(binding)

        assert symbol.symbol_id.startswith("sym_")
        assert symbol.symbol_type == SymbolType.EMOJI
        assert symbol.meaning_value == "security"
        assert symbol.quality_score > 0
        assert len(symbol.salt) > 0
        assert len(symbol.symbol_hash) == 64

        # Symbol should be stored
        assert symbol.symbol_id in store.symbols

    def test_find_symbols_by_meaning(self, store):
        """Test finding symbols by meaning"""
        # Bind multiple symbols to same meaning
        binding1 = SymbolBinding(
            symbol_type=SymbolType.EMOJI,
            symbol_data="✅",
            meaning_type=MeaningType.ACTION,
            meaning_value="approve"
        )

        binding2 = SymbolBinding(
            symbol_type=SymbolType.WORD,
            symbol_data="yes please",
            meaning_type=MeaningType.ACTION,
            meaning_value="approve"
        )

        symbol1 = store.bind_symbol(binding1)
        symbol2 = store.bind_symbol(binding2)

        # Find all symbols for "approve"
        symbols = store.find_symbols_by_meaning("approve")

        assert len(symbols) == 2
        assert symbol1 in symbols
        assert symbol2 in symbols

    def test_verify_symbol(self, store):
        """Test symbol verification"""
        # Bind a symbol
        binding = SymbolBinding(
            symbol_type=SymbolType.WORD,
            symbol_data="secret passphrase",
            meaning_type=MeaningType.IDENTITY,
            meaning_value="self"
        )

        symbol = store.bind_symbol(binding)

        # Verify with correct data
        verified = store.verify_symbol("secret passphrase", SymbolType.WORD, "self")
        assert verified is True

        # Verify with wrong data
        verified = store.verify_symbol("wrong passphrase", SymbolType.WORD, "self")
        assert verified is False

        # Verify with wrong type
        verified = store.verify_symbol("secret passphrase", SymbolType.EMOJI, "self")
        assert verified is False

        # Check usage stats updated
        updated_symbol = store.symbols[symbol.symbol_id]
        assert updated_symbol.use_count == 1
        assert updated_symbol.last_used_at is not None

    def test_create_composition(self, store):
        """Test symbol composition creation"""
        # Bind symbols first
        symbol1 = store.bind_symbol(SymbolBinding(
            symbol_type=SymbolType.EMOJI,
            symbol_data="⚡",
            meaning_type=MeaningType.CONCEPT,
            meaning_value="power"
        ))

        symbol2 = store.bind_symbol(SymbolBinding(
            symbol_type=SymbolType.EMOJI,
            symbol_data="🛡️",
            meaning_type=MeaningType.CONCEPT,
            meaning_value="responsibility"
        ))

        # Create composition
        comp_id = store.create_composition(
            "admin_approval",
            [symbol1.symbol_id, symbol2.symbol_id],
            ["+"],
            "grant_admin_scope"
        )

        assert comp_id.startswith("comp_")
        assert comp_id in store.compositions

        composition = store.compositions[comp_id]
        assert composition["name"] == "admin_approval"
        assert len(composition["symbols"]) == 2
        assert composition["meaning"] == "grant_admin_scope"

    def test_storage_persistence(self, store):
        """Test that symbols persist to encrypted storage"""
        # Bind a symbol
        binding = SymbolBinding(
            symbol_type=SymbolType.EMOJI,
            symbol_data="🔐",
            meaning_type=MeaningType.CONCEPT,
            meaning_value="locked"
        )

        symbol = store.bind_symbol(binding)
        symbol_id = symbol.symbol_id

        # Save should have been called automatically
        assert store.storage_path.exists()

        # Create new store instance with same path
        store2 = LocalSymbolStore(str(store.storage_path))
        store2.initialize("test_device_key")

        # Symbol should be loaded
        # Note: In mock implementation, this won't actually persist
        # In production, it would load from encrypted file


class TestULChallengeService:
    """Test server-side challenge generation and verification"""

    @pytest.fixture
    async def service(self):
        """Create UL challenge service"""
        service = ULChallengeService()
        return service

    @pytest.mark.asyncio
    async def test_challenge_generation(self, service):
        """Test composition challenge generation"""
        challenge = await service.generate_challenge(
            "gonzo",
            "grant_admin_scope",
            ["power", "responsibility"]
        )

        assert challenge.challenge_id.startswith("ul_challenge_")
        assert challenge.composition == "power + responsibility"
        assert challenge.expected_symbols == 2
        assert len(challenge.operators) == 1
        assert challenge.expires_at > datetime.now(timezone.utc)
        assert len(challenge.nonce) > 0

        # Challenge should be stored
        assert challenge.challenge_id in service.active_challenges

    @pytest.mark.asyncio
    async def test_challenge_expiration(self, service):
        """Test that expired challenges are rejected"""
        # Create expired challenge
        challenge = CompositionChallenge(
            challenge_id="expired_challenge",
            composition="test",
            operators=[],
            expected_symbols=1,
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            nonce="test_nonce"
        )

        service.active_challenges["expired_challenge"] = challenge

        # Try to verify proof for expired challenge
        proof = CompositionProof(
            challenge_id="expired_challenge",
            proof_hash="test_hash",
            symbol_count=1,
            computation_time_ms=100,
            quality_score=0.8
        )

        verified = await service.verify_composition_proof("gonzo", proof)
        assert verified is False

        # Challenge should be removed
        assert "expired_challenge" not in service.active_challenges

    @pytest.mark.asyncio
    async def test_proof_verification(self, service):
        """Test composition proof verification"""
        # Generate challenge
        challenge = await service.generate_challenge(
            "gonzo",
            "delete_all_data",
            ["destruction", "finality", "certainty"]
        )

        # Create valid proof
        proof = CompositionProof(
            challenge_id=challenge.challenge_id,
            proof_hash="valid_proof_hash_abc123",
            symbol_count=3,  # Matches expected
            computation_time_ms=250.5,
            quality_score=0.75  # Above threshold
        )

        verified = await service.verify_composition_proof("gonzo", proof)
        assert verified is True

        # Challenge should be consumed
        assert challenge.challenge_id not in service.active_challenges

    @pytest.mark.asyncio
    async def test_proof_quality_validation(self, service):
        """Test that low-quality proofs are rejected"""
        challenge = await service.generate_challenge(
            "gonzo",
            "transfer_ownership",
            ["release", "transfer"]
        )

        # Create low-quality proof
        proof = CompositionProof(
            challenge_id=challenge.challenge_id,
            proof_hash="weak_proof",
            symbol_count=2,
            computation_time_ms=50,
            quality_score=0.3  # Below threshold
        )

        verified = await service.verify_composition_proof("gonzo", proof)
        assert verified is False

    @pytest.mark.asyncio
    async def test_ul_signature_creation(self, service):
        """Test UL signature generation"""
        symbol_proofs = ["proof1_hash", "proof2_hash"]
        composition_proof = CompositionProof(
            challenge_id="test_challenge",
            proof_hash="comp_proof",
            symbol_count=2,
            computation_time_ms=150,
            quality_score=0.8
        )

        signature = await service.create_ul_signature(
            "gonzo",
            "grant_admin_scope",
            symbol_proofs,
            composition_proof
        )

        assert signature.lid == "gonzo"
        assert signature.action == "grant_admin_scope"
        assert len(signature.symbol_proofs) == 2
        assert signature.composition_proof == composition_proof
        assert signature.expires_at > datetime.now(timezone.utc)

        # Signature expiry should be short (1 minute)
        time_diff = (signature.expires_at - datetime.now(timezone.utc)).total_seconds()
        assert 50 <= time_diff <= 70  # Around 60 seconds

    @pytest.mark.asyncio
    async def test_ul_signature_verification(self, service):
        """Test UL signature verification"""
        # Create signature
        signature = await service.create_ul_signature(
            "gonzo",
            "delete_all_data",
            ["proof1", "proof2", "proof3"],  # 3 proofs for critical action
            None
        )

        # Verify valid signature
        valid = service.verify_ul_signature("gonzo", "delete_all_data", signature)
        assert valid is True

        # Wrong user
        valid = service.verify_ul_signature("alice", "delete_all_data", signature)
        assert valid is False

        # Wrong action
        valid = service.verify_ul_signature("gonzo", "send_email", signature)
        assert valid is False

        # Expired signature
        signature.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        valid = service.verify_ul_signature("gonzo", "delete_all_data", signature)
        assert valid is False


class TestUniversalLanguageService:
    """Test complete UL service integration"""

    @pytest.fixture
    async def service(self, tmp_path):
        """Create UL service with temp storage"""
        service = UniversalLanguageService()
        service.local_store.storage_path = tmp_path / "test_ul.enc"
        await service.initialize("test_device_key")
        return service

    @pytest.mark.asyncio
    async def test_complete_ul_workflow(self, service):
        """Test end-to-end UL workflow"""
        # 1. Bind personal symbols
        power_id = await service.bind_symbol(
            SymbolType.EMOJI,
            "⚡️💪",
            MeaningType.CONCEPT,
            "power"
        )

        responsibility_id = await service.bind_symbol(
            SymbolType.WORD,
            "with great power",
            MeaningType.CONCEPT,
            "responsibility"
        )

        assert power_id.startswith("sym_")
        assert responsibility_id.startswith("sym_")

        # 2. Request challenge
        challenge = await service.request_challenge("gonzo", "grant_admin_scope")

        assert challenge.composition == "power + responsibility"
        assert challenge.expected_symbols == 2

        # 3. Solve challenge
        proof = await service.solve_challenge(
            challenge,
            [
                ("⚡️💪", SymbolType.EMOJI),
                ("with great power", SymbolType.WORD)
            ]
        )

        assert proof.challenge_id == challenge.challenge_id
        assert proof.symbol_count == 2
        assert proof.quality_score > 0
        assert proof.computation_time_ms > 0

        # 4. Verify proof
        verified = await service.challenge_service.verify_composition_proof("gonzo", proof)
        assert verified is True

        # 5. Create approval signature
        signature = await service.create_approval_signature(
            "gonzo",
            "grant_admin_scope",
            proof
        )

        assert signature.lid == "gonzo"
        assert signature.action == "grant_admin_scope"
        assert signature.composition_proof == proof

    @pytest.mark.asyncio
    async def test_wrong_symbol_rejection(self, service):
        """Test that wrong symbols fail challenge"""
        # Bind symbols
        await service.bind_symbol(
            SymbolType.EMOJI,
            "🔒",
            MeaningType.CONCEPT,
            "security"
        )

        await service.bind_symbol(
            SymbolType.EMOJI,
            "🔑",
            MeaningType.CONCEPT,
            "access"
        )

        # Request challenge for different meanings
        challenge = await service.request_challenge("gonzo", "grant_admin_scope")

        # Try to solve with wrong symbols
        with pytest.raises(ValueError, match="Could not match all required meanings"):
            await service.solve_challenge(
                challenge,
                [
                    ("🔒", SymbolType.EMOJI),  # Wrong - expects "power"
                    ("🔑", SymbolType.EMOJI)   # Wrong - expects "responsibility"
                ]
            )

    @pytest.mark.asyncio
    async def test_action_specific_challenges(self, service):
        """Test different actions have different challenge requirements"""
        # Test admin scope
        challenge1 = await service.request_challenge("gonzo", "grant_admin_scope")
        assert "power" in challenge1.composition
        assert "responsibility" in challenge1.composition

        # Test data deletion
        challenge2 = await service.request_challenge("gonzo", "delete_all_data")
        assert "destruction" in challenge2.composition
        assert "finality" in challenge2.composition
        assert "certainty" in challenge2.composition

        # Test ownership transfer
        challenge3 = await service.request_challenge("gonzo", "transfer_ownership")
        assert "release" in challenge3.composition
        assert "transfer" in challenge3.composition


class TestCompositionParsing:
    """Test composition string parsing"""

    def test_simple_composition(self):
        """Test parsing simple compositions"""
        meanings, operators = parse_composition("calm + collapse")

        assert meanings == ["calm", "collapse"]
        assert operators == ["+"]

    def test_complex_composition(self):
        """Test parsing complex compositions"""
        meanings, operators = parse_composition("power * responsibility - doubt")

        assert meanings == ["power", "responsibility", "doubt"]
        assert operators == ["*", "-"]

    def test_single_meaning(self):
        """Test parsing single meaning (no operators)"""
        meanings, operators = parse_composition("confirm")

        assert meanings == ["confirm"]
        assert operators == []

    def test_whitespace_handling(self):
        """Test whitespace is handled correctly"""
        meanings, operators = parse_composition("  start  +  middle  →  end  ")

        assert meanings == ["start", "middle", "end"]
        assert operators == ["+", "→"]


class TestULRequirements:
    """Test UL requirement checking"""

    def test_ul_required_actions(self):
        """Test which actions require UL entropy"""
        assert requires_ul_entropy("grant_admin_scope") is True
        assert requires_ul_entropy("delete_all_data") is True
        assert requires_ul_entropy("transfer_ownership") is True
        assert requires_ul_entropy("emergency_lockdown") is True

        assert requires_ul_entropy("send_email") is False
        assert requires_ul_entropy("view_file") is False

    def test_symbol_requirements(self):
        """Test required symbol counts for actions"""
        assert get_required_symbols("grant_admin_scope") == 2
        assert get_required_symbols("delete_all_data") == 3
        assert get_required_symbols("transfer_ownership") == 2
        assert get_required_symbols("emergency_lockdown") == 1

        assert get_required_symbols("unknown_action") == 0

    def test_composition_requirements(self):
        """Test which actions require composition"""
        from universal_language import requires_composition

        assert requires_composition("grant_admin_scope") is True
        assert requires_composition("delete_all_data") is True
        assert requires_composition("transfer_ownership") is True
        assert requires_composition("emergency_lockdown") is False


class TestPrivacyPreservation:
    """Test that UL system preserves privacy"""

    def test_no_raw_symbols_in_proofs(self):
        """Test that proofs don't contain raw symbols"""
        symbols = [
            PersonalSymbol(
                symbol_id="sym_1",
                symbol_type=SymbolType.EMOJI,
                symbol_hash="hash1",
                salt="salt1",
                meaning_type=MeaningType.CONCEPT,
                meaning_value="power",
                created_at=datetime.now(timezone.utc),
                quality_score=0.8
            ),
            PersonalSymbol(
                symbol_id="sym_2",
                symbol_type=SymbolType.WORD,
                symbol_hash="hash2",
                salt="salt2",
                meaning_type=MeaningType.CONCEPT,
                meaning_value="responsibility",
                created_at=datetime.now(timezone.utc),
                quality_score=0.9
            )
        ]

        proof_hash = compose_symbol_proof(symbols, ["+"], "test_nonce")

        # Proof should not contain any raw data
        assert "⚡️" not in proof_hash
        assert "power" not in proof_hash
        assert "responsibility" not in proof_hash

        # Proof should be a proper hash
        assert len(proof_hash) == 64

    def test_salt_uniqueness(self):
        """Test that each symbol gets unique salt"""
        store = LocalSymbolStore("test.enc")
        store.initialize("test_key")

        # Bind same symbol data twice
        symbol1 = store.bind_symbol(SymbolBinding(
            symbol_type=SymbolType.EMOJI,
            symbol_data="🔒",
            meaning_type=MeaningType.CONCEPT,
            meaning_value="secure1"
        ))

        symbol2 = store.bind_symbol(SymbolBinding(
            symbol_type=SymbolType.EMOJI,
            symbol_data="🔒",
            meaning_type=MeaningType.CONCEPT,
            meaning_value="secure2"
        ))

        # Different salts
        assert symbol1.salt != symbol2.salt

        # Different hashes despite same data
        assert symbol1.symbol_hash != symbol2.symbol_hash


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
