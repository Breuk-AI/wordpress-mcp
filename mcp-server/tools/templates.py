"""
Template Tools for WordPress MCP
Handles theme template editing and management
"""

from typing import List, Dict, Any
from mcp.types import Tool

class TemplateTools:
    """Tools for managing WordPress templates"""
    
    def __init__(self, wp_client):
        self.wp = wp_client
        self.tools = {
            "wp_list_templates": self.list_templates,
            "wp_read_template": self.read_template,
            "wp_update_template": self.update_template,
            "wp_create_child_theme": self.create_child_theme
        }
    
    def get_tools(self) -> List[Tool]:
        """Return list of available tools"""
        return [
            Tool(
                name="wp_list_templates",
                description="List all theme template files",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "include_child": {
                            "type": "boolean",
                            "description": "Include child theme templates",
                            "default": True
                        }
                    }
                }
            ),
            Tool(
                name="wp_read_template",
                description="Read template file content",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "template_path": {
                            "type": "string",
                            "description": "Path to template file (e.g., 'header.php')"
                        }
                    },
                    "required": ["template_path"]
                }
            ),
            Tool(
                name="wp_update_template",
                description="Update template file content (creates backup)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "template_path": {
                            "type": "string",
                            "description": "Path to template file"
                        },
                        "content": {
                            "type": "string",
                            "description": "New template content"
                        }
                    },
                    "required": ["template_path", "content"]
                }
            ),
            Tool(
                name="wp_create_child_theme",
                description="Create a child theme (placeholder)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "child_theme_name": {
                            "type": "string",
                            "description": "Name for the child theme"
                        }
                    },
                    "required": ["child_theme_name"]
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
    
    async def list_templates(self, include_child=True):
        """List all template files"""
        templates = await self.wp.get_template_files()
        
        # Organize by type
        organized = {
            "parent_theme": [],
            "child_theme": [],
            "template_parts": []
        }
        
        for template in templates:
            if template["type"] == "parent":
                organized["parent_theme"].append(template["path"])
            elif template["type"] == "child":
                organized["child_theme"].append(template["path"])
            elif template["type"] == "part":
                organized["template_parts"].append(template["path"])
        
        return organized
    
    async def read_template(self, template_path: str):
        """Read template content"""
        result = await self.wp.read_template(template_path)
        
        return {
            "path": result["path"],
            "content": result["content"],
            "writable": result["writable"],
            "length": len(result["content"]),
            "preview": result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"]
        }
    
    async def update_template(self, template_path: str, content: str):
        """Update template with automatic backup"""
        result = await self.wp.update_template(template_path, content)
        
        return {
            "success": result["success"],
            "message": result["message"],
            "backup_created": result.get("backup_path", ""),
            "template_path": template_path
        }
    
    async def create_child_theme(self, child_theme_name: str):
        """Create child theme - placeholder"""
        # This would require more complex implementation
        return {
            "success": False,
            "message": "Child theme creation not yet implemented - requires server-side file operations"
        }
