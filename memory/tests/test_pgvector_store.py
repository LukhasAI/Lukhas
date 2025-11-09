
import unittest
import json
from unittest.mock import MagicMock, call

from memory.backends.pgvector_store import PgVectorStore, VectorDoc

class TestPgVectorStore(unittest.TestCase):

    def setUp(self):
        self.mock_conn = MagicMock()
        self.mock_cursor = self.mock_conn.cursor.return_value.__enter__.return_value
        self.store = PgVectorStore(self.mock_conn, table="test_table", dim=3)

    def test_add_successful(self):
        doc = VectorDoc(id="doc1", text="some text", embedding=[0.1, 0.2, 0.3], meta={"source": "test"})
        self.mock_cursor.fetchone.return_value = ("doc1",)

        result_id = self.store.add(doc)

        self.assertEqual(result_id, "doc1")
        self.mock_cursor.execute.assert_called_once()
        query, params = self.mock_cursor.execute.call_args[0]

        self.assertIn("INSERT INTO test_table", query)
        self.assertIn("ON CONFLICT (id) DO UPDATE", query)
        self.assertEqual(params, ("doc1", [0.1, 0.2, 0.3], json.dumps({"source": "test"}), "some text"))

    def test_add_raises_error_if_no_id_returned(self):
        doc = VectorDoc(id="doc1", text="some text", embedding=[0.1, 0.2, 0.3], meta={})
        self.mock_cursor.fetchone.return_value = None

        with self.assertRaises(ValueError):
            self.store.add(doc)

    def test_bulk_add_successful(self):
        docs = [
            VectorDoc(id="doc1", text="text1", embedding=[0.1, 0.2, 0.3], meta={}),
            VectorDoc(id="doc2", text="text2", embedding=[0.4, 0.5, 0.6], meta={})
        ]
        self.mock_cursor.fetchall.return_value = [("doc1",), ("doc2",)]

        result_ids = self.store.bulk_add(docs)

        self.assertEqual(result_ids, ["doc1", "doc2"])
        self.mock_cursor.execute.assert_called_once()
        query, params = self.mock_cursor.execute.call_args[0]
        self.assertIn("VALUES (%s, %s, %s, %s), (%s, %s, %s, %s)", query)

    def test_bulk_add_with_no_docs(self):
        result = self.store.bulk_add([])
        self.assertEqual(result, [])
        self.mock_cursor.execute.assert_not_called()

    def test_search(self):
        self.mock_cursor.fetchall.return_value = [("doc1", 0.9), ("doc2", 0.8)]

        results = self.store.search(embedding=[0.1, 0.2, 0.3], k=5)

        self.assertEqual(results, [("doc1", 0.9), ("doc2", 0.8)])
        self.mock_cursor.execute.assert_called_once_with(
            "SELECT id, 1 - (embedding <=> %s) AS score FROM test_table ORDER BY score DESC LIMIT %s",
            ([0.1, 0.2, 0.3], 5)
        )

    def test_search_with_filters(self):
        self.mock_cursor.fetchall.return_value = [("doc1", 0.9)]

        results = self.store.search(embedding=[0.1, 0.2, 0.3], k=5, filters={"source": "test"})

        self.assertEqual(results, [("doc1", 0.9)])
        expected_query = "SELECT id, 1 - (embedding <=> %s) AS score FROM test_table WHERE metadata->>'source' = %s ORDER BY score DESC LIMIT %s"
        expected_params = ([0.1, 0.2, 0.3], 5, "test")

        # Unpack the actual call arguments for easier comparison
        actual_query, actual_params = self.mock_cursor.execute.call_args[0]

        # Remove whitespace and compare queries
        self.assertEqual(" ".join(actual_query.split()), " ".join(expected_query.split()))

        # Compare parameters
        self.assertEqual(actual_params, expected_params)

    def test_delete_by_id(self):
        self.mock_cursor.rowcount = 1

        affected_rows = self.store.delete(id="doc1")

        self.assertEqual(affected_rows, 1)
        self.mock_cursor.execute.assert_called_once_with("DELETE FROM test_table WHERE id = %s", ("doc1",))

    def test_delete_by_filter(self):
        self.mock_cursor.rowcount = 2

        affected_rows = self.store.delete(where={"source": "doc.pdf"})

        self.assertEqual(affected_rows, 2)
        # Note: The exact query string depends on dict ordering in older Python,
        # but for a single key it's deterministic.
        self.mock_cursor.execute.assert_called_once_with(
            "DELETE FROM test_table WHERE metadata->>'source' = %s",
            ("doc.pdf",)
        )

    def test_delete_raises_error_if_no_args(self):
        with self.assertRaises(ValueError):
            self.store.delete()

    def test_stats(self):
        self.mock_cursor.fetchone.return_value = (100,)

        stats = self.store.stats()

        self.assertEqual(stats, {"table": "test_table", "dim": 3, "count": 100})
        self.mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM test_table")


if __name__ == '__main__':
    unittest.main()
