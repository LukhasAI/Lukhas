"""
Test suite for qi.safety.provenance_links - Presigned URL generation for provenance artifacts
"""
import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from candidate.qi.safety.provenance_links import (
    _parse_storage_url,
    _load_record_by_sha,
    _file_link,
    presign_url,
    presign_for_record,
)


class TestProvenanceLinks(unittest.TestCase):
    
    def test_parse_storage_url_s3(self):
        """Test S3 URL parsing"""
        cases = [
            ("s3://bucket/key.txt", ("s3", "bucket", "key.txt")),
            ("s3://my-bucket/path/to/file.pdf", ("s3", "my-bucket", "path/to/file.pdf")),
            ("s3://bucket.name/deep/nested/path.json", ("s3", "bucket.name", "deep/nested/path.json")),
        ]
        for url, expected in cases:
            with self.subTest(url=url):
                result = _parse_storage_url(url)
                self.assertEqual(result, expected)
    
    def test_parse_storage_url_gcs(self):
        """Test GCS URL parsing"""
        cases = [
            ("gs://bucket/key.txt", ("gs", "bucket", "key.txt")),
            ("gs://my-bucket/path/to/file.pdf", ("gs", "my-bucket", "path/to/file.pdf")),
            ("gs://bucket.name/deep/nested/path.json", ("gs", "bucket.name", "deep/nested/path.json")),
        ]
        for url, expected in cases:
            with self.subTest(url=url):
                result = _parse_storage_url(url)
                self.assertEqual(result, expected)
    
    def test_parse_storage_url_file(self):
        """Test file:// URL parsing"""
        cases = [
            ("file:///tmp/test.txt", ("file", "/tmp", "test.txt")),
            ("file:///Users/test/file.pdf", ("file", "/Users/test", "file.pdf")),
            ("file:///home/user/doc.json", ("file", "/home/user", "doc.json")),
        ]
        for url, expected in cases:
            with self.subTest(url=url):
                result = _parse_storage_url(url)
                self.assertEqual(result, expected)
    
    def test_parse_storage_url_invalid(self):
        """Test invalid URL parsing raises error"""
        invalid_urls = [
            "http://example.com/file.txt",
            "https://example.com/file.txt",
            "ftp://server/file.txt",
            "/local/path/file.txt",
            "relative/path.txt",
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                with self.assertRaises(ValueError) as ctx:
                    _parse_storage_url(url)
                self.assertIn("Unsupported storage_url", str(ctx.exception))
    
    def test_file_link(self):
        """Test local file link generation"""
        result = _file_link("/tmp", "test.txt")
        self.assertTrue(result.startswith("file://"))
        self.assertIn("test.txt", result)
        
        result = _file_link("/Users/test", "artifact.pdf")
        self.assertTrue(result.startswith("file://"))
        self.assertIn("artifact.pdf", result)
    
    def test_presign_url_file(self):
        """Test presign_url for local files"""
        result = presign_url(
            "file:///tmp/test.txt",
            expires=600,
            filename="download.txt"
        )
        self.assertEqual(result["backend"], "file")
        self.assertTrue(result["url"].startswith("file://"))
        self.assertIsNone(result["expires_in"])
        self.assertIn("Local file link", result.get("note", ""))
    
    @patch('boto3.client')
    def test_presign_url_s3(self, mock_boto3_client):
        """Test S3 presigned URL generation (mocked)"""
        # Mock S3 client
        mock_s3 = MagicMock()
        mock_boto3_client.return_value = mock_s3
        mock_s3.generate_presigned_url.return_value = "https://s3.amazonaws.com/signed-url"
        
        result = presign_url(
            "s3://my-bucket/path/to/file.pdf",
            expires=300,
            filename="report.pdf",
            content_type="application/pdf"
        )
        
        self.assertEqual(result["backend"], "s3")
        self.assertEqual(result["url"], "https://s3.amazonaws.com/signed-url")
        self.assertEqual(result["expires_in"], 300)
        
        # Verify S3 client was called correctly
        mock_s3.generate_presigned_url.assert_called_once()
        call_args = mock_s3.generate_presigned_url.call_args
        self.assertEqual(call_args[1]["ClientMethod"], "get_object")
        self.assertEqual(call_args[1]["Params"]["Bucket"], "my-bucket")
        self.assertEqual(call_args[1]["Params"]["Key"], "path/to/file.pdf")
        self.assertIn("ResponseContentDisposition", call_args[1]["Params"])
    
    def test_presign_url_gcs_missing_library(self):
        """Test GCS presigned URL generation fails without google-cloud-storage"""
        # Since google-cloud-storage is not installed, this should raise RuntimeError
        with self.assertRaises(RuntimeError) as ctx:
            presign_url(
                "gs://my-bucket/path/to/file.json",
                expires=600,
                filename="data.json",
                content_type="application/json"
            )
        self.assertIn("google-cloud-storage", str(ctx.exception))
    
    def test_presign_for_record_with_dict(self):
        """Test presign_for_record with record dictionary"""
        record = {
            "artifact_sha256": "abc123",
            "storage_url": "file:///tmp/test.txt",
            "mime_type": "text/plain",
            "size_bytes": 100
        }
        
        result = presign_for_record(record, expires=300, filename="custom.txt")
        self.assertEqual(result["backend"], "file")
        self.assertTrue(result["url"].startswith("file://"))
    
    def test_presign_for_record_no_storage_url(self):
        """Test presign_for_record fails without storage_url"""
        record = {
            "artifact_sha256": "abc123",
            "size_bytes": 100
        }
        
        with self.assertRaises(ValueError) as ctx:
            presign_for_record(record)
        self.assertIn("no storage_url", str(ctx.exception))
    
    def test_presign_for_record_auto_filename(self):
        """Test automatic filename generation from SHA and extension"""
        record = {
            "artifact_sha256": "abc123def456",
            "storage_url": "file:///tmp/artifact.pdf",
            "mime_type": "application/pdf"
        }
        
        with patch('qi.safety.provenance_links.presign_url') as mock_presign:
            mock_presign.return_value = {"backend": "file", "url": "file:///tmp/artifact.pdf"}
            
            presign_for_record(record)
            
            # Check that filename was auto-generated with .pdf extension
            call_args = mock_presign.call_args
            self.assertIn("abc123def456.pdf", call_args[1]["filename"])
    
    @patch('os.path.exists')
    @patch('builtins.open')
    def test_load_record_by_sha(self, mock_open, mock_exists):
        """Test loading provenance record by SHA"""
        mock_exists.return_value = True
        mock_record = {
            "artifact_sha256": "abc123",
            "storage_url": "file:///tmp/test.txt"
        }
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_record)
        
        # Mock json.load to return our record
        with patch('json.load', return_value=mock_record):
            result = _load_record_by_sha("abc123")
            self.assertEqual(result["artifact_sha256"], "abc123")
    
    def test_load_record_by_sha_not_found(self):
        """Test loading non-existent record raises error"""
        with self.assertRaises(FileNotFoundError):
            _load_record_by_sha("nonexistent_sha")


if __name__ == "__main__":
    unittest.main()