
import datetime
import unittest
from unittest.mock import ANY, patch

from lukhas.memory.index import EmbeddingIndex


class TestSoftDelete(unittest.TestCase):

    def setUp(self):
        self.index = EmbeddingIndex()
        self.index.add("vec1", [1.0, 2.0], {"meta": "data1"})
        self.index.add("vec2", [3.0, 4.0], {"meta": "data2"})

    def test_soft_delete(self):
        self.assertFalse(self.index.is_deleted("vec1"))
        self.assertIsNone(self.index.get_deleted_at("vec1"))

        # Use ANY to ignore the now() call and focus on the logic
        with patch('lukhas.memory.soft_delete.datetime') as mock_dt:
            now = datetime.datetime.now(datetime.timezone.utc)
            mock_dt.datetime.now.return_value = now

            self.index.soft_delete("vec1")

            self.assertTrue(self.index.is_deleted("vec1"))
            # The actual datetime object is created inside the method,
            # so we can either check that the mock was called or
            # check that the returned value is a datetime object.
            self.assertIsInstance(self.index.get_deleted_at("vec1"), datetime.datetime)

    def test_restore(self):
        self.index.soft_delete("vec1")
        self.assertTrue(self.index.is_deleted("vec1"))

        self.index.restore("vec1")
        self.assertFalse(self.index.is_deleted("vec1"))
        self.assertIsNone(self.index.get_deleted_at("vec1"))

    def test_search_excludes_deleted(self):
        self.index.soft_delete("vec1")
        results = self.index.search([1.0, 2.0])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "vec2")

    def test_search_includes_restored(self):
        self.index.soft_delete("vec1")
        self.index.restore("vec1")
        results = self.index.search([1.0, 2.0])
        # The order is not guaranteed, so check for both IDs
        self.assertEqual(len(results), 2)
        self.assertIn(results[0]["id"], ["vec1", "vec2"])
        self.assertIn(results[1]["id"], ["vec1", "vec2"])


if __name__ == '__main__':
    unittest.main()
