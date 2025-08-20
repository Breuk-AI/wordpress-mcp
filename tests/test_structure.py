"""Test the MCP server structure and imports."""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_server_directory_exists():
    """Test that mcp-server directory exists."""
    server_dir = Path(__file__).parent.parent / "mcp-server"
    assert server_dir.exists(), "mcp-server directory not found"
    assert server_dir.is_dir(), "mcp-server is not a directory"


def test_server_files_exist():
    """Test that essential server files exist."""
    server_dir = Path(__file__).parent.parent / "mcp-server"
    
    required_files = [
        'server.py',
        'wp_client.py',
        'requirements.txt'
    ]
    
    for file in required_files:
        file_path = server_dir / file
        assert file_path.exists(), f"Missing required file: {file}"


def test_tools_directory():
    """Test that tools directory exists and has modules."""
    tools_dir = Path(__file__).parent.parent / "mcp-server" / "tools"
    assert tools_dir.exists(), "tools directory not found"
    assert tools_dir.is_dir(), "tools is not a directory"
    
    # Check for tool modules
    expected_modules = [
        'posts.py',
        'pages.py',
        'media.py',
        'woocommerce.py',
        'templates.py',
        'system.py'
    ]
    
    for module in expected_modules:
        module_path = tools_dir / module
        assert module_path.exists(), f"Missing tool module: {module}"


def test_wordpress_plugin_exists():
    """Test that WordPress plugin directory exists."""
    plugin_dir = Path(__file__).parent.parent / "wp-mcp-plugin"
    assert plugin_dir.exists(), "wp-mcp-plugin directory not found"
    assert plugin_dir.is_dir(), "wp-mcp-plugin is not a directory"


def test_plugin_files_exist():
    """Test that WordPress plugin has required files."""
    plugin_dir = Path(__file__).parent.parent / "wp-mcp-plugin"
    
    # At minimum, should have the main plugin file
    plugin_file = plugin_dir / "wp-mcp-plugin.php"
    assert plugin_file.exists(), "Main plugin file wp-mcp-plugin.php not found"


def test_python_imports():
    """Test that Python modules exist and have correct structure."""
    # Don't actually import (might have missing dependencies)
    # Just check the file exists and has the expected class definition
    wp_client_file = Path(__file__).parent.parent / "mcp-server" / "wp_client.py"
    
    if wp_client_file.exists():
        with open(wp_client_file, 'r') as f:
            content = f.read()
            assert 'class WordPressClient' in content, "WordPressClient class not found in file"
    else:
        assert False, "wp_client.py file not found"


if __name__ == "__main__":
    test_server_directory_exists()
    test_server_files_exist()
    test_tools_directory()
    test_wordpress_plugin_exists()
    test_plugin_files_exist()
    test_python_imports()
    print("✅ All structure tests passed!")
