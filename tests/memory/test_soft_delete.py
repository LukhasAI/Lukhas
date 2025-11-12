import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

from lukhas.memory.soft_delete import SoftDeleteEmbeddingIndex


class TestSoftDeleteEmbeddingIndex(unittest.TestCase):
    def setUp(self):
        self.index = SoftDeleteEmbeddingIndex()
        self.vector1 = [1.0, 2.0, 3.0]
        self.vector2 = [4.0, 5.0, 6.0]
        self.index.add("vec1", self.vector1)
        self.index.add("vec2", self.vector2)

    def test_add_initializes_soft_delete_fields(self):
        metadata = self.index._metadata["vec1"]
        self.assertFalse(metadata["is_deleted"])
        self.assertIsNone(metadata["deleted_at"])

    def test_soft_delete(self):
        with patch("lukhas.memory.soft_delete.datetime") as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.utcnow.return_value = mock_now

            self.index.soft_delete("vec1")

            metadata = self.index._metadata["vec1"]
            self.assertTrue(metadata["is_deleted"])
            self.assertEqual(metadata["deleted_at"], mock_now.isoformat())

    def test_restore(self):
        self.index.soft_delete("vec1")
        self.index.restore("vec1")

        metadata = self.index._metadata["vec1"]
        self.assertFalse(metadata["is_deleted"])
        self.assertIsNone(metadata["deleted_at"])

    def test_search_excludes_deleted_by_default(self):
        self.index.soft_delete("vec1")
        results = self.index.search(self.vector1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "vec2")

    def test_search_includes_deleted_when_requested(self):
        self.index.soft_delete("vec1")
        results = self.index.search(self.vector1, include_deleted=True)
        self.assertEqual(len(results), 2)
        self.assertIn("vec1", [r["id"] for r in results])
        self.assertIn("vec2", [r["id"] for r in results])


if __name__ == "__main__":
    unittest.main()
