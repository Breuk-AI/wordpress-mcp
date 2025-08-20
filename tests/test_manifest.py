"""Test the manifest.json file structure and validity."""
import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_manifest_exists():
    """Test that manifest.json exists."""
    manifest_path = Path(__file__).parent.parent / "manifest.json"
    assert manifest_path.exists(), "manifest.json not found"


def test_manifest_valid_json():
    """Test that manifest.json is valid JSON."""
    manifest_path = Path(__file__).parent.parent / "manifest.json"
    with open(manifest_path, 'r') as f:
        data = json.load(f)
    assert data, "manifest.json is empty"


def test_manifest_required_fields():
    """Test that manifest has all required fields."""
    manifest_path = Path(__file__).parent.parent / "manifest.json"
    with open(manifest_path, 'r') as f:
        data = json.load(f)
    
    required_fields = ['name', 'version', 'description', 'mcp']
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"


def test_mcp_configuration():
    """Test MCP configuration in manifest."""
    manifest_path = Path(__file__).parent.parent / "manifest.json"
    with open(manifest_path, 'r') as f:
        data = json.load(f)
    
    assert 'mcp' in data, "Missing mcp configuration"
    assert data['mcp']['type'] == 'python', "MCP type should be python"
    assert 'main' in data['mcp'], "Missing main entry point"
    assert 'requirements' in data['mcp'], "Missing requirements file"


if __name__ == "__main__":
    test_manifest_exists()
    test_manifest_valid_json()
    test_manifest_required_fields()
    test_mcp_configuration()
    print("✅ All manifest tests passed!")
