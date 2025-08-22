"""
Unit tests for wp_client.py - Pure functions only
Phase 3 of CI Enhancement
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

# Import module to test
from wp_client import WordPressClient


class TestWordPressClientPureFunctions:
    """Test WordPressClient pure functions"""
    
    def setup_method(self):
        """Set up test client instance"""
        # Create client with test credentials
        # Note: __init__ has side effects but we need an instance
        with patch('wp_client.hashlib.sha256'):
            self.client = WordPressClient(
                site_url="https://example.com",
                username="testuser",
                app_password="testpass",
                timeout=30
            )
    
    def test_build_url_basic_endpoint(self):
        """Test building URL for basic endpoints"""
        # Simple endpoint
        assert self.client._build_url("posts") == "https://example.com/wp-json/wp/v2/posts"
        assert self.client._build_url("pages") == "https://example.com/wp-json/wp/v2/pages"
        assert self.client._build_url("users") == "https://example.com/wp-json/wp/v2/users"
    
    def test_build_url_with_id(self):
        """Test building URL with resource ID"""
        assert self.client._build_url("posts/123") == "https://example.com/wp-json/wp/v2/posts/123"
        assert self.client._build_url("pages/456") == "https://example.com/wp-json/wp/v2/pages/456"
    
    def test_build_url_wp_prefix(self):
        """Test URL building with wp/ prefix"""
        assert self.client._build_url("wp/posts") == "https://example.com/wp-json/wp/v2/posts"
        assert self.client._build_url("wp/v2/posts") == "https://example.com/wp-json/wp/v2/v2/posts"  # Note: This creates v2/v2
    
    def test_build_url_wc_prefix(self):
        """Test URL building with wc/ prefix (WooCommerce)"""
        assert self.client._build_url("wc/products") == "https://example.com/wp-json/wc/v3/products"
        assert self.client._build_url("wc/orders") == "https://example.com/wp-json/wc/v3/orders"
        assert self.client._build_url("wc/v3/customers") == "https://example.com/wp-json/wc/v3/v3/customers"
    
    def test_build_url_mcp_prefix(self):
        """Test URL building with mcp/ prefix (custom)"""
        assert self.client._build_url("mcp/backup") == "https://example.com/wp-json/mcp/v1/backup"
        assert self.client._build_url("mcp/status") == "https://example.com/wp-json/mcp/v1/status"
    
    def test_build_url_full_url(self):
        """Test that full URLs are returned unchanged"""
        assert self.client._build_url("https://example.com/custom") == "https://example.com/custom"
        assert self.client._build_url("http://other.com/api") == "http://other.com/api"
    
    def test_build_url_wp_json_prefix(self):
        """Test URL building with /wp-json/ prefix"""
        assert self.client._build_url("/wp-json/custom/v1/endpoint") == "https://example.com/wp-json/custom/v1/endpoint"
        assert self.client._build_url("/wp-json/wp/v2/posts") == "https://example.com/wp-json/wp/v2/posts"
    
    def test_sanitize_data_null_bytes(self):
        """Test removal of null bytes from strings"""
        data = {
            "title": "Test\x00Title",
            "content": "Content\x00with\x00nulls"
        }
        
        result = self.client._sanitize_data(data)
        
        assert result["title"] == "TestTitle"
        assert result["content"] == "Contentwithnulls"
    
    def test_sanitize_data_long_strings(self):
        """Test truncation of long strings"""
        data = {
            "content": "x" * 200000  # 200KB string
        }
        
        result = self.client._sanitize_data(data)
        
        assert len(result["content"]) == 100000  # Should be truncated
    
    def test_sanitize_data_nested_dict(self):
        """Test sanitization of nested dictionaries"""
        data = {
            "meta": {
                "key1": "value\x00clean",
                "nested": {
                    "key2": "deep\x00value"
                }
            }
        }
        
        result = self.client._sanitize_data(data)
        
        assert result["meta"]["key1"] == "valueclean"
        assert result["meta"]["nested"]["key2"] == "deepvalue"
    
    def test_sanitize_data_lists(self):
        """Test sanitization of lists"""
        data = {
            "tags": ["tag1\x00", "tag2", "tag\x003"],
            "categories": [
                {"name": "cat\x001"},
                {"name": "cat2"}
            ]
        }
        
        result = self.client._sanitize_data(data)
        
        assert result["tags"] == ["tag1", "tag2", "tag3"]
        assert result["categories"][0]["name"] == "cat1"
        assert result["categories"][1]["name"] == "cat2"
    
    def test_sanitize_data_mixed_types(self):
        """Test sanitization with mixed data types"""
        data = {
            "string": "test\x00string",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "none": None,
            "list": [1, "two\x00", 3],
            "dict": {"key": "value\x00"}
        }
        
        result = self.client._sanitize_data(data)
        
        assert result["string"] == "teststring"
        assert result["number"] == 42
        assert result["float"] == 3.14
        assert result["boolean"] is True
        assert result["none"] is None
        assert result["list"] == [1, "two", 3]
        assert result["dict"]["key"] == "value"
    
    def test_sanitize_data_empty_values(self):
        """Test sanitization with empty values"""
        data = {
            "empty_string": "",
            "empty_list": [],
            "empty_dict": {}
        }
        
        result = self.client._sanitize_data(data)
        
        assert result["empty_string"] == ""
        assert result["empty_list"] == []
        assert result["empty_dict"] == {}
    
    def test_sanitize_data_special_characters(self):
        """Test that normal special characters are preserved"""
        data = {
            "title": "Test & Title <html>",
            "content": "Content with 'quotes' and \"double quotes\"",
            "unicode": "Emoji 🎉 and special chars: é, ñ, ü"
        }
        
        result = self.client._sanitize_data(data)
        
        # These should remain unchanged (only null bytes are removed)
        assert result["title"] == "Test & Title <html>"
        assert result["content"] == "Content with 'quotes' and \"double quotes\""
        assert result["unicode"] == "Emoji 🎉 and special chars: é, ñ, ü"
    
    def test_sanitize_data_not_dict(self):
        """Test sanitization when input is not a dict"""
        # Should return input unchanged if not a dict
        assert self.client._sanitize_data("string") == "string"
        assert self.client._sanitize_data(123) == 123
        assert self.client._sanitize_data([1, 2, 3]) == [1, 2, 3]
        assert self.client._sanitize_data(None) == None


# Run tests with: pytest tests/unit/test_wp_client.py -v
