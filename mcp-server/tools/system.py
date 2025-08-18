"""
System Tools for WordPress MCP
Handles system information and advanced operations
"""

from typing import List, Dict, Any
from mcp.types import Tool

class SystemTools:
    """Tools for system operations"""
    
    def __init__(self, wp_client):
        self.wp = wp_client
        self.tools = {
            "wp_get_system_info": self.get_system_info,
            "wp_get_plugins": self.get_plugins,
            "wp_get_themes": self.get_themes,
            "wp_clear_cache": self.clear_cache
        }
    
    def get_tools(self) -> List[Tool]:
        """Return list of available tools"""
        return [
            Tool(
                name="wp_get_system_info",
                description="Get WordPress system information",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="wp_get_plugins",
                description="Get list of installed plugins",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Filter by status (active, inactive)",
                            "default": "active"
                        }
                    }
                }
            ),
            Tool(
                name="wp_get_themes",
                description="Get list of installed themes",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="wp_clear_cache",
                description="Clear various caches (placeholder)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "cache_type": {
                            "type": "string",
                            "description": "Type of cache to clear",
                            "default": "all"
                        }
                    }
                }
            )
        ]
    
    def handles_tool(self, tool_name: str) -> bool:
        """Check if this module handles the given tool"""
        return tool_name in self.tools
    
    async def execute_tool(self, tool_name: str, arguments: Dict) -> Any:
        """Execute a tool with given arguments"""
        if tool_name in self.tools:
            return await self.tools[tool_name](**arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def get_system_info(self):
        """Get system information"""
        info = await self.wp.get("mcp/system/info")
        
        # Format the response nicely
        formatted = {
            "wordpress": {
                "version": info["wordpress"]["version"],
                "site_url": info["wordpress"]["site_url"],
                "active_theme": info["wordpress"]["active_theme"],
                "is_multisite": info["wordpress"]["is_multisite"]
            },
            "php": {
                "version": info["php"]["version"],
                "memory_limit": info["php"]["memory_limit"],
                "max_execution_time": info["php"]["max_execution_time"]
            },
            "server": info["server"]
        }
        
        # Add WooCommerce if present
        if "woocommerce" in info:
            formatted["woocommerce"] = info["woocommerce"]
        
        return formatted
    
    async def get_plugins(self, status="active"):
        """Get installed plugins"""
        # This uses standard WP REST API
        plugins = await self.wp.get("plugins")
        
        # Filter by status if requested
        if status == "active":
            plugins = [p for p in plugins if p["status"] == "active"]
        elif status == "inactive":
            plugins = [p for p in plugins if p["status"] == "inactive"]
        
        return [{
            "name": p["name"],
            "slug": p["plugin"],
            "version": p["version"],
            "status": p["status"],
            "author": p["author"]
        } for p in plugins]
    
    async def get_themes(self):
        """Get installed themes"""
        themes = await self.wp.get("themes")
        
        return [{
            "name": t["name"]["rendered"],
            "slug": t["stylesheet"],
            "version": t["version"],
            "status": t["status"],
            "author": t["author"]["rendered"] if "author" in t else "Unknown"
        } for t in themes]
    
    async def clear_cache(self, cache_type="all"):
        """Clear caches - placeholder"""
        # This would need implementation based on what cache plugins are installed
        return {
            "success": False,
            "message": "Cache clearing not yet implemented - depends on installed cache plugins"
        }
