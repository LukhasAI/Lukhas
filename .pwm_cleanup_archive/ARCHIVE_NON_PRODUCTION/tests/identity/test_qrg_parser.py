import unittest

from identity.utils.qrg_parser import GLYMPHParser, QRGParser

CONFIG = {
    "qr_format": r"^[A-Z0-9|:{}\s]+$",
    "allowed_symbols": {"A", "B", "C"},
    "symbol_map": {"A": "alpha", "B": "beta", "C": "gamma"},
}


class TestQRGParser(unittest.TestCase):
    def setUp(self):
        self.parser = QRGParser(CONFIG)
        self.g_parser = GLYMPHParser(CONFIG)

    def test_parse_qr_code_json(self):
        data = '{"type":"test","payload":"123"}'
        result = self.parser.parse_qr_code(data)
        self.assertEqual(result["type"], "test")

    def test_validate_qr_format(self):
        self.assertTrue(self.parser.validate_qr_format("TEST|DATA"))

    def test_glymph_parse_and_validate(self):
        seq = "A-B-C"
        parsed = self.g_parser.parse_glymph(seq)
        self.assertEqual(parsed["tokens"], ["A", "B", "C"])
        self.assertTrue(self.g_parser.validate_glymph_sequence(seq))
        self.assertEqual(self.g_parser.interpret_symbols(seq), "alpha beta gamma")
