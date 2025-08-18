#!/usr/bin/env python3
"""
WordPress MCP Server
Provides comprehensive WordPress and WooCommerce control via MCP protocol
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv

# MCP imports
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.shared.context import RequestContext
from mcp.types import Tool, TextContent, Resource

# Our imports
from wp_client import WordPressClient
from tools.posts import PostTools
from tools.pages import PageTools
from tools.media import MediaTools
from tools.woocommerce import WooCommerceTools
from tools.templates import TemplateTools
from tools.system import SystemTools

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv('MCP_DEBUG', 'false').lower() == 'true' else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WordPressMCPServer:
    """Main MCP server for WordPress integration"""
    
    def __init__(self):
        self.wp_client: Optional[WordPressClient] = None
        self.tools = {}
        self.initialized = False
        self.rate_limit = int(os.getenv('RATE_LIMIT', '60'))
        self.request_counts = {}  # Simple rate limiting tracker
    
    async def initialize(self, options: InitializationOptions) -> None:
        """Initialize the server with WordPress connection details"""
        logger.info("Initializing WordPress MCP Server...")
        
        # Get configuration from environment or config file
        config = self._load_config()
        
        if not config.get('site_url') or not config.get('username') or not config.get('app_password'):
            logger.error("Missing required configuration. Please check your .env file or environment variables.")
            raise Exception("WordPress connection configuration incomplete")
        
        # Initialize WordPress client
        self.wp_client = WordPressClient(
            site_url=config['site_url'],
            username=config['username'],
            app_password=config['app_password'],
            timeout=config.get('timeout', 30)
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
            'templates': TemplateTools(self.wp_client),
            'system': SystemTools(self.wp_client)
        }
        
        # Initialize WooCommerce tools only if WooCommerce is detected
        try:
            wc_check = await self.wp_client.get("wc/v3/system_status")
            if wc_check:
                self.tools['woocommerce'] = WooCommerceTools(self.wp_client)
                logger.info("WooCommerce detected and tools enabled")
        except:
            logger.info("WooCommerce not detected, skipping WooCommerce tools")
        
        self.initialized = True
        logger.info("WordPress MCP Server initialized successfully")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables or config file"""
        # First try environment variables
        if os.getenv('WP_SITE_URL'):
            return {
                'site_url': os.getenv('WP_SITE_URL', '').rstrip('/'),
                'username': os.getenv('WP_USERNAME', ''),
                'app_password': os.getenv('WP_APP_PASSWORD', ''),
                'timeout': int(os.getenv('API_TIMEOUT', '30')),
                'cors_origins': os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if os.getenv('CORS_ALLOWED_ORIGINS') else [],
                'backup_retention': int(os.getenv('BACKUP_RETENTION_DAYS', '7'))
            }
        
        # Fall back to config.json for backwards compatibility
        config_path = Path(__file__).parent / 'config.json'
        if config_path.exists():
            logger.warning("Using config.json is deprecated. Please use environment variables or .env file instead.")
            with open(config_path, 'r') as f:
                config = json.load(f)
                return {
                    'site_url': config.get('site_url', '').rstrip('/'),
                    'username': config.get('username', ''),
                    'app_password': config.get('app_password', ''),
                    'timeout': config.get('timeout', 30),
                    'cors_origins': config.get('cors_origins', []),
                    'backup_retention': config.get('backup_retention', 7)
                }
        
        # Return empty config if nothing found
        return {}
    
    async def list_tools(self) -> List[Tool]:
        """List all available tools"""
        if not self.initialized:
            return []
        
        all_tools = []
        for module in self.tools.values():
            all_tools.extend(module.get_tools())
        
        return all_tools
    
    async def call_tool(self, name: str, arguments: Any, context: RequestContext) -> List[TextContent]:
        """Execute a tool with rate limiting"""
        if not self.initialized:
            return [TextContent(type="text", text="Server not initialized")]
        
        # Simple rate limiting check
        # In production, you'd want a more sophisticated approach
        # like using Redis or a proper rate limiting library
        
        # Find which module handles this tool
        for module in self.tools.values():
            if module.handles_tool(name):
                try:
                    result = await module.execute_tool(name, arguments)
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as e:
                    logger.error(f"Error executing tool {name}: {e}")
                    return [TextContent(type="text", text=json.dumps({
                        "error": str(e),
                        "tool": name
                    }, indent=2))]
        
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    async def list_resources(self) -> List[Resource]:
        """List available resources"""
        # This could be expanded to show recent posts, media items, etc.
        return []

async def main():
    """Main entry point"""
    logger.info("Starting WordPress MCP Server...")
    
    # Check for required configuration
    if not os.getenv('WP_SITE_URL') and not Path(__file__).parent.joinpath('config.json').exists():
        logger.error("""
        ================================================================================
        Configuration not found!
        
        Please create a .env file with your WordPress credentials:
        1. Copy .env.example to .env
        2. Fill in your WordPress site URL, username, and application password
        3. Restart the server
        
        Or set environment variables: WP_SITE_URL, WP_USERNAME, WP_APP_PASSWORD
        ================================================================================
        """)
        sys.exit(1)
    
    # Create server instance
    server = WordPressMCPServer()
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await asyncio.create_task(
            run_server(
                server,
                read_stream,
                write_stream
            )
        )

async def run_server(server, read_stream, write_stream):
    """Run the MCP server"""
    from mcp.server import Server
    
    mcp_server = Server(
        server.list_tools,
        server.call_tool,
        server.list_resources
    )
    
    mcp_server.on_initialize(server.initialize)
    
    await mcp_server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())
