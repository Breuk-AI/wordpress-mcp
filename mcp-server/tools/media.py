"""
Media Tools for WordPress MCP
Handles media library operations
"""

from typing import List, Dict, Any
from mcp.types import Tool

class MediaTools:
    """Tools for managing WordPress media"""
    
    def __init__(self, wp_client):
        self.wp = wp_client
        self.tools = {
            "wp_get_media": self.get_media,
            "wp_upload_media": self.upload_media,
            "wp_delete_media": self.delete_media
        }
    
    def get_tools(self) -> List[Tool]:
        """Return list of available tools"""
        return [
            Tool(
                name="wp_get_media",
                description="Get media library items",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "per_page": {
                            "type": "integer",
                            "description": "Number of items to retrieve",
                            "default": 20
                        },
                        "media_type": {
                            "type": "string",
                            "description": "Filter by type (image, video, audio)",
                            "default": "image"
                        }
                    }
                }
            ),
            Tool(
                name="wp_upload_media",
                description="Upload media file (placeholder - needs implementation)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Local file path to upload"
                        },
                        "title": {
                            "type": "string",
                            "description": "Media title"
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="wp_delete_media",
                description="Delete media item",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "media_id": {
                            "type": "integer",
                            "description": "Media ID to delete"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Force delete",
                            "default": True
                        }
                    },
                    "required": ["media_id"]
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
    
    async def get_media(self, per_page=20, media_type="image"):
        """Get media library items"""
        params = {"per_page": per_page}
        if media_type:
            params["media_type"] = media_type
            
        media_items = await self.wp.get("media", params)
        return [{
            "id": item["id"],
            "title": item["title"]["rendered"],
            "url": item["source_url"],
            "type": item["media_type"],
            "mime_type": item["mime_type"],
            "date": item["date"]
        } for item in media_items]
    
    async def upload_media(self, file_path: str, title=""):
        """Upload media file - placeholder"""
        # This would need actual file upload implementation
        return {
            "success": False,
            "message": "Media upload not yet implemented - requires file handling"
        }
    
    async def delete_media(self, media_id: int, force=True):
        """Delete media item"""
        result = await self.wp.delete(f"media/{media_id}?force={force}")
        return {
            "success": True,
            "message": f"Media {media_id} deleted"
        }
