#!/usr/bin/env python3
"""
WordPress MCP Server
Provides comprehensive WordPress and WooCommerce control via MCP protocol
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import sys
import os

# Set up logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # MCP imports
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, Resource, ServerCapabilities
except ImportError:
    logger.error("MCP library not found! Please install it with: pip install mcp")
    logger.error("Or install all requirements: pip install -r requirements.txt")
    sys.exit(1)

# Our imports
from wp_client import WordPressClient
from tools.posts import PostTools
from tools.pages import PageTools
from tools.media import MediaTools
from tools.woocommerce import WooCommerceTools
from tools.templates import TemplateTools
from tools.system import SystemTools

class WordPressMCPServer:
    """Main MCP server for WordPress integration"""
    
    def __init__(self):
        self.wp_client: Optional[WordPressClient] = None
        self.tools = {}
        self.initialized = False
        self.server = Server("wordpress-mcp")
        
        # Register handlers
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            return await self.list_tools()
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Any) -> List[TextContent]:
            return await self.call_tool(name, arguments)
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            return await self.list_resources()
    
    async def initialize(self, options: InitializationOptions) -> None:
        """Initialize the server with WordPress connection details"""
        logger.info("Initializing WordPress MCP Server...")
        
        # Get configuration from environment or config file
        config = self._load_config()
        
        if not config.get('username') or config.get('username') == 'your_wordpress_username':
            logger.error("Please update config.json with your WordPress credentials!")
            raise Exception("Configuration not set up")
        
        # Initialize WordPress client
        self.wp_client = WordPressClient(
            site_url=config['site_url'],
            username=config['username'],
            app_password=config['app_password']
        )
        
        # Test connection
        if await self.wp_client.test_connection():
            logger.info(f"Connected to WordPress site: {config['site_url']}")
        else:
            logger.error("Failed to connect to WordPress site")
            raise Exception("WordPress connection failed")
        
        # Initialize tool modules
        self.tools = {
            'posts': PostTools(self.wp_client),
            'pages': PageTools(self.wp_client),
            'media': MediaTools(self.wp_client),
            'woocommerce': WooCommerceTools(self.wp_client),
            'templates': TemplateTools(self.wp_client),
            'system': SystemTools(self.wp_client)
        }
        
        self.initialized = True
        logger.info("WordPress MCP Server initialized successfully")
    
    def _load_config(self) -> Dict[str, str]:
        """Load configuration from file or environment"""
        # Try to load from config file first
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Fall back to environment variables
        return {
            'site_url': os.environ.get('WP_SITE_URL', 'https://monopolygowin.com'),
            'username': os.environ.get('WP_USERNAME', ''),
            'app_password': os.environ.get('WP_APP_PASSWORD', '')
        }
    
    async def list_tools(self) -> List[Tool]:
        """List all available tools"""
        if not self.initialized:
            return []
        
        all_tools = []
        for module in self.tools.values():
            all_tools.extend(module.get_tools())
        
        logger.info(f"Listing {len(all_tools)} tools")
        return all_tools
    
    async def call_tool(self, name: str, arguments: Any) -> List[TextContent]:
        """Execute a tool"""
        logger.info(f"Calling tool: {name}")
        
        if not self.initialized:
            return [TextContent(type="text", text="Server not initialized")]
        
        try:
            # Find which module handles this tool
            for module in self.tools.values():
                if module.handles_tool(name):
                    result = await module.execute_tool(name, arguments)
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def list_resources(self) -> List[Resource]:
        """List available resources"""
        return []
    
    async def run(self):
        """Run the server"""
        # Check for config
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        if not os.path.exists(config_path):
            logger.error("config.json not found!")
            logger.error("Please copy config.json.example to config.json and update with your credentials.")
            sys.exit(1)
        
        # Initialize the server with proper capabilities
        init_options = InitializationOptions(
            server_name="wordpress-mcp",
            server_version="1.0.0",
            capabilities=ServerCapabilities(
                tools={"listChanged": True},
                resources={"listChanged": True}
            )
        )
        await self.initialize(init_options)
        
        # Run with stdio
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                init_options
            )

async def main():
    """Main entry point"""
    logger.info("Starting WordPress MCP Server...")
    
    server = WordPressMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
