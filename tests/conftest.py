"""
Pytest configuration for WordPress MCP tests
"""

import sys
import os
from pathlib import Path

# Add mcp-server to path so we can import modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "mcp-server"))
