from candidate.governance.identity.core.qrs.qrg_generator import QRGGenerator


def test_generate_and_validate_pairing_code_success():
    generator = QRGGenerator(config={"code_length": 10, "code_ttl": 120})
    device_info = {"os": "λOS", "model": "L-01"}

    pairing = generator.generate_pairing_code("lambda-001", device_info)

    assert len(pairing["code"]) == 10
    validation = generator.validate_pairing_code(pairing["code"], pairing["signature"])
    assert validation["valid"] is True
    assert validation["user_id"] == "lambda-001"
    assert pairing["code"] not in generator.active_codes


def test_validate_pairing_code_with_wrong_signature_then_success():
    generator = QRGGenerator(config={"code_length": 8, "code_ttl": 60})
    device_info = {"os": "λOS", "model": "L-02"}

    pairing = generator.generate_pairing_code("lambda-002", device_info)
    failure = generator.validate_pairing_code(pairing["code"], "INVALID")
    assert failure["valid"] is False
    assert failure["reason"] == "signature_mismatch"

    success = generator.validate_pairing_code(pairing["code"], pairing["signature"])
    assert success["valid"] is True


def test_cleanup_expired_codes_removes_entries():
    generator = QRGGenerator(config={"code_length": 6, "code_ttl": 1})
    device_info = {"os": "λOS", "model": "L-03"}
    pairing = generator.generate_pairing_code("lambda-003", device_info)

    generator.active_codes[pairing["code"]]["expires_at"] = generator._now() - 5
    removed = generator.cleanup_expired_codes()

    assert removed == 1
    assert pairing["code"] not in generator.active_codes
