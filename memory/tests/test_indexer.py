
import unittest
from unittest.mock import MagicMock, patch

from memory.indexer import Embeddings, Indexer

class TestEmbeddings(unittest.TestCase):

    def test_initialization_with_default_provider(self):
        """Test that Embeddings initializes with a default provider if none is given."""
        with patch('memory.indexer.OpenAIEmbeddingProvider') as MockProvider:
            embeddings = Embeddings()
            MockProvider.assert_called_once()
            self.assertIs(embeddings.provider, MockProvider.return_value)

    def test_initialization_with_custom_provider(self):
        """Test that Embeddings uses the provider it is initialized with."""
        mock_provider = MagicMock()
        embeddings = Embeddings(provider=mock_provider)
        self.assertIs(embeddings.provider, mock_provider)

    def test_embed_calls_provider(self):
        """Test that the embed method calls the underlying provider."""
        mock_provider = MagicMock()
        mock_provider.embed.return_value = [[0.1, 0.2, 0.3]]
        embeddings = Embeddings(provider=mock_provider)

        result = embeddings.embed("test text")

        mock_provider.embed.assert_called_once_with(["test text"])
        self.assertEqual(result, [0.1, 0.2, 0.3])

    def test_embed_caching(self):
        """Test that the embed method caches results."""
        mock_provider = MagicMock()
        mock_provider.embed.return_value = [[0.1, 0.2, 0.3]]
        embeddings = Embeddings(provider=mock_provider)

        # First call - should call the provider
        result1 = embeddings.embed("test text")
        self.assertEqual(result1, [0.1, 0.2, 0.3])
        mock_provider.embed.assert_called_once_with(["test text"])

        # Second call with the same text - should not call the provider again
        result2 = embeddings.embed("test text")
        self.assertEqual(result2, [0.1, 0.2, 0.3])
        mock_provider.embed.assert_called_once()

    def test_embed_caching_with_different_text(self):
        """Test that the cache distinguishes between different texts."""
        mock_provider = MagicMock()
        mock_provider.embed.side_effect = [[[0.1, 0.2, 0.3]], [[0.4, 0.5, 0.6]]]
        embeddings = Embeddings(provider=mock_provider)

        # First call
        result1 = embeddings.embed("text one")
        self.assertEqual(result1, [0.1, 0.2, 0.3])
        self.assertEqual(mock_provider.embed.call_count, 1)

        # Second call with different text
        result2 = embeddings.embed("text two")
        self.assertEqual(result2, [0.4, 0.5, 0.6])
        self.assertEqual(mock_provider.embed.call_count, 2)

        # Third call, repeating the first text
        result3 = embeddings.embed("text one")
        self.assertEqual(result3, [0.1, 0.2, 0.3])
        self.assertEqual(mock_provider.embed.call_count, 2)
class TestIndexer(unittest.TestCase):
    def test_upsert_duplicate_detection(self):
        """Test that upsert detects and handles duplicates."""
        mock_store = MagicMock()
        mock_store.search.return_value = [("existing_id", 0.99)]

        indexer = Indexer(store=mock_store)

        result_id = indexer.upsert("duplicate text", {})

        self.assertEqual(result_id, "existing_id")
        mock_store.add.assert_not_called()

if __name__ == '__main__':
    unittest.main()
