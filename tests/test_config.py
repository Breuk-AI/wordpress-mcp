"""Test configuration and environment setup."""
import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_requirements_file_valid():
    """Test that requirements.txt is valid."""
    req_file = Path(__file__).parent.parent / "mcp-server" / "requirements.txt"
    assert req_file.exists(), "requirements.txt not found"
    
    with open(req_file, 'r') as f:
        lines = f.readlines()
    
    # Should have at least some requirements
    non_empty_lines = [l.strip() for l in lines if l.strip() and not l.strip().startswith('#')]
    assert len(non_empty_lines) > 0, "requirements.txt is empty"


def test_config_example_exists():
    """Test that configuration examples exist."""
    server_dir = Path(__file__).parent.parent / "mcp-server"
    
    # Should have at least one config example
    config_examples = [
        'config.json.example',
        '.env.example'
    ]
    
    found_example = False
    for example in config_examples:
        if (server_dir / example).exists():
            found_example = True
            break
    
    assert found_example, "No configuration examples found"


def test_documentation_exists():
    """Test that basic documentation exists."""
    root_dir = Path(__file__).parent.parent
    
    required_docs = ['README.md']
    for doc in required_docs:
        doc_path = root_dir / doc
        assert doc_path.exists(), f"Missing documentation: {doc}"


def test_license_exists():
    """Test that LICENSE file exists."""
    license_file = Path(__file__).parent.parent / "LICENSE"
    assert license_file.exists(), "LICENSE file not found"


def test_gitignore_exists():
    """Test that .gitignore exists."""
    gitignore_file = Path(__file__).parent.parent / ".gitignore"
    assert gitignore_file.exists(), ".gitignore file not found"


if __name__ == "__main__":
    test_requirements_file_valid()
    test_config_example_exists()
    test_documentation_exists()
    test_license_exists()
    test_gitignore_exists()
    print("✅ All configuration tests passed!")
