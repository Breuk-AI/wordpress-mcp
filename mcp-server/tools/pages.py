"""
Page Tools for WordPress MCP
Handles all page-related operations
"""

from typing import List, Dict, Any
from mcp.types import Tool

class PageTools:
    """Tools for managing WordPress pages"""
    
    def __init__(self, wp_client):
        self.wp = wp_client
        self.tools = {
            "wp_get_pages": self.get_pages,
            "wp_create_page": self.create_page,
            "wp_update_page": self.update_page,
            "wp_delete_page": self.delete_page
        }
    
    def get_tools(self) -> List[Tool]:
        """Return list of available tools"""
        return [
            Tool(
                name="wp_get_pages",
                description="Get list of WordPress pages",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "per_page": {
                            "type": "integer",
                            "description": "Number of pages to retrieve",
                            "default": 10
                        },
                        "parent": {
                            "type": "integer",
                            "description": "Get child pages of specific parent",
                            "default": 0
                        }
                    }
                }
            ),
            Tool(
                name="wp_create_page",
                description="Create a new WordPress page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Page title"
                        },
                        "content": {
                            "type": "string",
                            "description": "Page content"
                        },
                        "status": {
                            "type": "string",
                            "description": "Page status",
                            "default": "draft"
                        },
                        "parent": {
                            "type": "integer",
                            "description": "Parent page ID",
                            "default": 0
                        }
                    },
                    "required": ["title", "content"]
                }
            ),
            Tool(
                name="wp_update_page",
                description="Update an existing WordPress page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_id": {
                            "type": "integer",
                            "description": "The page ID to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New page title"
                        },
                        "content": {
                            "type": "string",
                            "description": "New page content"
                        }
                    },
                    "required": ["page_id"]
                }
            ),
            Tool(
                name="wp_delete_page",
                description="Delete a WordPress page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_id": {
                            "type": "integer",
                            "description": "The page ID to delete"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Force delete without trash",
                            "default": False
                        }
                    },
                    "required": ["page_id"]
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
    
    # Tool implementations (simplified for now)
    
    async def get_pages(self, per_page=10, parent=0):
        """Get list of pages"""
        params = {
            "per_page": per_page,
            "parent": parent,
            "type": "page"
        }
        pages = await self.wp.get("pages", params)
        return [{
            "id": page["id"],
            "title": page["title"]["rendered"],
            "slug": page["slug"],
            "status": page["status"],
            "parent": page["parent"],
            "link": page["link"]
        } for page in pages]
    
    async def create_page(self, title: str, content: str, status="draft", parent=0):
        """Create new page"""
        data = {
            "title": title,
            "content": content,
            "status": status,
            "parent": parent,
            "type": "page"
        }
        result = await self.wp.post("pages", data)
        return {
            "success": True,
            "page_id": result["id"],
            "link": result["link"]
        }
    
    async def update_page(self, page_id: int, **kwargs):
        """Update existing page"""
        result = await self.wp.put(f"pages/{page_id}", kwargs)
        return {
            "success": True,
            "page_id": result["id"],
            "link": result["link"]
        }
    
    async def delete_page(self, page_id: int, force=False):
        """Delete page"""
        result = await self.wp.delete(f"pages/{page_id}?force={force}")
        return {
            "success": True,
            "message": f"Page {page_id} deleted"
        }
