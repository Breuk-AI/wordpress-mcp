"""
Post Tools for WordPress MCP
Handles all post-related operations
"""

from typing import List, Dict, Any
from mcp.types import Tool
import json

class PostTools:
    """Tools for managing WordPress posts"""
    
    def __init__(self, wp_client):
        self.wp = wp_client
        self.tools = {
            "wp_get_posts": self.get_posts,
            "wp_get_post": self.get_post,
            "wp_create_post": self.create_post,
            "wp_update_post": self.update_post,
            "wp_delete_post": self.delete_post,
            "wp_search_posts": self.search_posts
        }
    
    def get_tools(self) -> List[Tool]:
        """Return list of available tools"""
        return [
            Tool(
                name="wp_get_posts",
                description="Get list of WordPress posts with optional filters",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "per_page": {
                            "type": "integer",
                            "description": "Number of posts to retrieve",
                            "default": 10
                        },
                        "page": {
                            "type": "integer",
                            "description": "Page number",
                            "default": 1
                        },
                        "status": {
                            "type": "string",
                            "description": "Post status (publish, draft, private, etc.)",
                            "default": "publish"
                        },
                        "orderby": {
                            "type": "string",
                            "description": "Order posts by (date, title, modified, etc.)",
                            "default": "date"
                        },
                        "order": {
                            "type": "string",
                            "description": "Order direction (asc, desc)",
                            "default": "desc"
                        }
                    }
                }
            ),
            Tool(
                name="wp_get_post",
                description="Get a single WordPress post by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "post_id": {
                            "type": "integer",
                            "description": "The post ID"
                        }
                    },
                    "required": ["post_id"]
                }
            ),
            Tool(
                name="wp_create_post",
                description="Create a new WordPress post",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Post title"
                        },
                        "content": {
                            "type": "string",
                            "description": "Post content (HTML allowed)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Post status (publish, draft, private)",
                            "default": "draft"
                        },
                        "slug": {
                            "type": "string",
                            "description": "URL slug for the post"
                        },
                        "categories": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Array of category IDs"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Array of tag IDs"
                        },
                        "featured_media": {
                            "type": "integer",
                            "description": "Featured image ID"
                        }
                    },
                    "required": ["title", "content"]
                }
            ),
            Tool(
                name="wp_update_post",
                description="Update an existing WordPress post",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "post_id": {
                            "type": "integer",
                            "description": "The post ID to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New post title"
                        },
                        "content": {
                            "type": "string",
                            "description": "New post content"
                        },
                        "status": {
                            "type": "string",
                            "description": "New post status"
                        },
                        "slug": {
                            "type": "string",
                            "description": "New URL slug"
                        }
                    },
                    "required": ["post_id"]
                }
            ),
            Tool(
                name="wp_delete_post",
                description="Delete a WordPress post",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "post_id": {
                            "type": "integer",
                            "description": "The post ID to delete"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Whether to bypass trash and force delete",
                            "default": False
                        }
                    },
                    "required": ["post_id"]
                }
            ),
            Tool(
                name="wp_search_posts",
                description="Search WordPress posts by keyword",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "search": {
                            "type": "string",
                            "description": "Search keyword"
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "Number of results",
                            "default": 10
                        }
                    },
                    "required": ["search"]
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
    
    # Tool implementations
    
    async def get_posts(self, per_page=10, page=1, status="publish", 
                       orderby="date", order="desc", **kwargs):
        """Get list of posts"""
        params = {
            "per_page": per_page,
            "page": page,
            "status": status,
            "orderby": orderby,
            "order": order,
            **kwargs
        }
        posts = await self.wp.get_posts(**params)
        
        # Simplify the response
        return [{
            "id": post["id"],
            "title": post["title"]["rendered"],
            "slug": post["slug"],
            "status": post["status"],
            "date": post["date"],
            "modified": post["modified"],
            "link": post["link"],
            "excerpt": post["excerpt"]["rendered"][:200] + "..." if len(post["excerpt"]["rendered"]) > 200 else post["excerpt"]["rendered"]
        } for post in posts]
    
    async def get_post(self, post_id: int):
        """Get single post with full details"""
        post = await self.wp.get_post(post_id)
        return {
            "id": post["id"],
            "title": post["title"]["rendered"],
            "content": post["content"]["rendered"],
            "slug": post["slug"],
            "status": post["status"],
            "date": post["date"],
            "modified": post["modified"],
            "link": post["link"],
            "categories": post.get("categories", []),
            "tags": post.get("tags", []),
            "featured_media": post.get("featured_media", 0)
        }
    
    async def create_post(self, title: str, content: str, status="draft", **kwargs):
        """Create new post"""
        data = {
            "title": title,
            "content": content,
            "status": status,
            **kwargs
        }
        result = await self.wp.create_post(data)
        return {
            "success": True,
            "post_id": result["id"],
            "link": result["link"],
            "message": f"Post created successfully with ID {result['id']}"
        }
    
    async def update_post(self, post_id: int, **kwargs):
        """Update existing post"""
        result = await self.wp.update_post(post_id, kwargs)
        return {
            "success": True,
            "post_id": result["id"],
            "link": result["link"],
            "message": f"Post {post_id} updated successfully"
        }
    
    async def delete_post(self, post_id: int, force=False):
        """Delete post"""
        params = {"force": force}
        result = await self.wp.delete(f"posts/{post_id}?force={force}")
        return {
            "success": True,
            "message": f"Post {post_id} {'permanently deleted' if force else 'moved to trash'}"
        }
    
    async def search_posts(self, search: str, per_page=10):
        """Search posts by keyword"""
        params = {
            "search": search,
            "per_page": per_page
        }
        posts = await self.wp.get_posts(**params)
        
        return {
            "found": len(posts),
            "posts": [{
                "id": post["id"],
                "title": post["title"]["rendered"],
                "link": post["link"],
                "excerpt": post["excerpt"]["rendered"][:200] + "..."
            } for post in posts]
        }
