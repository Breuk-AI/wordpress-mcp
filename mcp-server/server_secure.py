#!/usr/bin/env python3
"""
WordPress MCP Server - Secure Production Version
Comprehensive security, monitoring, and error handling
"""

import asyncio
import json
import logging
import os
import sys
import hashlib
import time
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# MCP imports
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.shared.context import RequestContext
from mcp.types import Tool, TextContent, Resource

# Security imports
from .wp_client_secure import SecureWordPressClient
from .rate_limiter import RateLimiter
from .validators import InputValidator, ValidationError
from .monitoring import MetricsCollector, HealthChecker

# Tool imports
from .tools.posts import PostTools
from .tools.pages import PageTools
from .tools.media import MediaTools
from .tools.woocommerce import WooCommerceTools
from .tools.templates import TemplateTools
from .tools.system import SystemTools

# Load environment variables
load_dotenv()

# Configure secure logging
class SecureLogger(logging.Logger):
    """Logger that filters sensitive information"""
    SENSITIVE_PATTERNS = [
        'authorization', 'password', 'token', 'secret', 'api_key', 'app_password'
    ]
    
    def _log(self, level, msg, args, **kwargs):
        msg_lower = str(msg).lower()
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in msg_lower:
                msg = "[REDACTED - Contains sensitive data]"
                break
        super()._log(level, msg, args, **kwargs)

logging.setLoggerClass(SecureLogger)

# Setup logging with rotation
from logging.handlers import RotatingFileHandler

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

handler = RotatingFileHandler(
    log_dir / "wordpress_mcp.log",
    maxBytes=10_000_000,  # 10MB
    backupCount=5
)

handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if os.getenv('MCP_DEBUG', 'false').lower() == 'true' else logging.INFO)
logger.addHandler(handler)

class SecureWordPressMCPServer:
    """Production-ready MCP server with comprehensive security"""
    
    def __init__(self):
        self.wp_client: Optional[SecureWordPressClient] = None
        self.tools = {}
        self.initialized = False
        
        # Security components
        self.rate_limiter = RateLimiter(
            requests_per_minute=int(os.getenv('RATE_LIMIT', '60')),
            burst_size=int(os.getenv('BURST_SIZE', '10')),
            block_duration=int(os.getenv('BLOCK_DURATION', '300'))
        )
        
        # Monitoring
        self.metrics = MetricsCollector()
        self.health_checker = HealthChecker()
        
        # Configuration
        self.config = self._load_secure_config()
        
        # Start background tasks
        asyncio.create_task(self._background_tasks())
    
    def _load_secure_config(self) -> Dict[str, Any]:
        """Load configuration with validation"""
        config = {}
        
        # Required environment variables
        required_vars = ['WP_SITE_URL', 'WP_USERNAME', 'WP_APP_PASSWORD']
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            else:
                # Validate based on type
                if var == 'WP_SITE_URL':
                    try:
                        config['site_url'] = InputValidator.validate('url', value.rstrip('/'))
                    except ValidationError as e:
                        logger.error(f"Invalid {var}: {e}")
                        missing_vars.append(var)
                else:
                    config[var.lower()] = value
        
        if missing_vars:
            logger.error(f"Missing required configuration: {', '.join(missing_vars)}")
            raise Exception("Configuration incomplete. Please check environment variables.")
        
        # Optional configuration with defaults
        config['timeout'] = int(os.getenv('API_TIMEOUT', '30'))
        config['rate_limit'] = int(os.getenv('RATE_LIMIT', '60'))
        config['cors_origins'] = self._parse_cors_origins(os.getenv('CORS_ALLOWED_ORIGINS', ''))
        config['backup_retention'] = int(os.getenv('BACKUP_RETENTION_DAYS', '7'))
        config['max_request_size'] = int(os.getenv('MAX_REQUEST_SIZE', '10485760'))  # 10MB
        config['enable_monitoring'] = os.getenv('ENABLE_MONITORING', 'true').lower() == 'true'
        
        return config
    
    def _parse_cors_origins(self, origins_str: str) -> List[str]:
        """Parse and validate CORS origins"""
        if not origins_str:
            return []
        
        origins = []
        for origin in origins_str.split(','):
            origin = origin.strip()
            if origin:
                try:
                    validated = InputValidator.validate('url', origin)
                    origins.append(validated)
                except ValidationError:
                    logger.warning(f"Invalid CORS origin ignored: {origin}")
        
        return origins
    
    async def initialize(self, options: InitializationOptions) -> None:
        """Initialize server with security measures"""
        logger.info("Initializing Secure WordPress MCP Server...")
        
        try:
            # Initialize WordPress client with security
            self.wp_client = SecureWordPressClient(
                site_url=self.config['site_url'],
                username=self.config['wp_username'],
                app_password=self.config['wp_app_password'],
                timeout=self.config['timeout'],
                rate_limit=self.config['rate_limit']
            )
            
            # Test connection
            if not await self.wp_client.test_connection():
                raise Exception("WordPress connection failed")
            
            logger.info(f"Connected to WordPress site: [REDACTED]")
            
            # Initialize tool modules with dependency injection
            self.tools = {
                'posts': PostTools(self.wp_client),
                'pages': PageTools(self.wp_client),
                'media': MediaTools(self.wp_client),
                'templates': TemplateTools(self.wp_client),
                'system': SystemTools(self.wp_client)
            }
            
            # Check for WooCommerce
            try:
                wc_check = await self.wp_client.get("wc/v3/system_status")
                if wc_check:
                    self.tools['woocommerce'] = WooCommerceTools(self.wp_client)
                    logger.info("WooCommerce detected and tools enabled")
            except Exception:
                logger.info("WooCommerce not detected")
            
            self.initialized = True
            self.health_checker.set_healthy(True)
            logger.info("WordPress MCP Server initialized successfully")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            self.health_checker.set_healthy(False, str(e))
            raise
    
    async def list_tools(self) -> List[Tool]:
        """List available tools"""
        if not self.initialized:
            return []
        
        all_tools = []
        for module in self.tools.values():
            all_tools.extend(module.get_tools())
        
        return all_tools
    
    async def call_tool(self, name: str, arguments: Any, context: RequestContext) -> List[TextContent]:
        """Execute tool with comprehensive security"""
        if not self.initialized:
            return [TextContent(type="text", text=json.dumps({
                "error": "Server not initialized"
            }))]
        
        # Extract request context for rate limiting
        request_id = context.meta.get('request_id', 'unknown')
        user_context = {
            'user_id': context.meta.get('user_id', 'anonymous'),
            'ip_address': context.meta.get('ip_address', '0.0.0.0'),
            'user_agent': context.meta.get('user_agent', 'unknown')
        }
        
        # Check rate limit
        identifier = self.rate_limiter.get_identifier(user_context)
        allowed, retry_after = await self.rate_limiter.check_rate_limit(identifier)
        
        if not allowed:
            self.metrics.increment('rate_limited')
            return [TextContent(type="text", text=json.dumps({
                "error": "Rate limit exceeded",
                "retry_after": retry_after
            }))]
        
        # Validate request size
        request_size = len(json.dumps(arguments))
        if request_size > self.config['max_request_size']:
            self.metrics.increment('oversized_requests')
            return [TextContent(type="text", text=json.dumps({
                "error": "Request too large",
                "max_size": self.config['max_request_size']
            }))]
        
        # Log request (without sensitive data)
        logger.info(f"Tool request: {name} from {identifier[:8]}...")
        
        # Find and execute tool
        start_time = time.time()
        
        try:
            # Input validation based on tool
            validated_args = self._validate_tool_arguments(name, arguments)
            
            # Find handler
            for module in self.tools.values():
                if module.handles_tool(name):
                    result = await module.execute_tool(name, validated_args)
                    
                    # Track metrics
                    elapsed = time.time() - start_time
                    self.metrics.record_request(name, elapsed, True)
                    
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            # Tool not found
            self.metrics.increment('unknown_tools')
            return [TextContent(type="text", text=json.dumps({
                "error": f"Unknown tool: {name}"
            }))]
            
        except ValidationError as e:
            # Validation failed
            elapsed = time.time() - start_time
            self.metrics.record_request(name, elapsed, False)
            
            return [TextContent(type="text", text=json.dumps({
                "error": "Validation failed",
                "message": str(e)
            }))]
            
        except Exception as e:
            # Execution failed
            elapsed = time.time() - start_time
            self.metrics.record_request(name, elapsed, False)
            
            # Log error (sanitized)
            logger.error(f"Tool execution failed: {name} - {type(e).__name__}")
            
            # Return sanitized error
            return [TextContent(type="text", text=json.dumps({
                "error": "Tool execution failed",
                "tool": name,
                "type": type(e).__name__
            }))]
    
    def _validate_tool_arguments(self, tool_name: str, arguments: Any) -> Any:
        """Validate tool arguments based on tool schema"""
        # Tool-specific validation
        if 'template' in tool_name.lower():
            # Extra validation for template operations
            if 'path' in arguments:
                arguments['path'] = InputValidator.validate('template_path', arguments['path'])
            if 'content' in arguments:
                # Check for dangerous content
                arguments['content'] = self._validate_template_content(arguments['content'])
        
        elif 'post' in tool_name.lower() or 'page' in tool_name.lower():
            # Validate post/page operations
            if 'title' in arguments:
                arguments['title'] = InputValidator.validate('post_title', arguments['title'])
            if 'content' in arguments:
                arguments['content'] = InputValidator.validate('post_content', arguments['content'])
            if 'status' in arguments:
                arguments['status'] = InputValidator.validate('post_status', arguments['status'])
        
        return arguments
    
    def _validate_template_content(self, content: str) -> str:
        """Validate template content for security"""
        dangerous_patterns = [
            'eval(', 'exec(', 'system(', 'shell_exec(', 'passthru(',
            'base64_decode(', 'file_get_contents(', 'file_put_contents(',
            'fopen(', 'include(', 'require(', 'include_once(', 'require_once('
        ]
        
        for pattern in dangerous_patterns:
            if pattern in content:
                raise ValidationError(f"Dangerous pattern detected: {pattern}")
        
        return content
    
    async def list_resources(self) -> List[Resource]:
        """List available resources with caching"""
        # Could cache and return recent items
        return []
    
    async def _background_tasks(self):
        """Run background maintenance tasks"""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Update health status
                if self.initialized and self.wp_client:
                    is_healthy = await self.wp_client.test_connection()
                    self.health_checker.set_healthy(is_healthy)
                
                # Log metrics
                if self.config['enable_monitoring']:
                    metrics = self.metrics.get_summary()
                    logger.info(f"Metrics: {json.dumps(metrics)}")
                
            except Exception as e:
                logger.error(f"Background task error: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get server health status"""
        return {
            "healthy": self.health_checker.is_healthy(),
            "initialized": self.initialized,
            "uptime": self.health_checker.get_uptime(),
            "last_check": self.health_checker.last_check,
            "metrics": self.metrics.get_summary() if self.config['enable_monitoring'] else {}
        }
    
    async def shutdown(self):
        """Clean shutdown"""
        logger.info("Shutting down WordPress MCP Server...")
        
        if self.wp_client:
            await self.wp_client.close()
        
        # Save metrics
        if self.config['enable_monitoring']:
            metrics = self.metrics.get_summary()
            logger.info(f"Final metrics: {json.dumps(metrics)}")

async def main():
    """Main entry point with proper error handling"""
    logger.info("Starting Secure WordPress MCP Server...")
    
    # Verify configuration
    required_vars = ['WP_SITE_URL', 'WP_USERNAME', 'WP_APP_PASSWORD']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        logger.error(f"""
        ================================================================================
        Configuration Error!
        
        Missing required environment variables: {', '.join(missing)}
        
        Please create a .env file with:
        WP_SITE_URL=https://your-site.com
        WP_USERNAME=your-username
        WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
        
        For security, never commit credentials to version control.
        ================================================================================
        """)
        sys.exit(1)
    
    # Create server
    server = SecureWordPressMCPServer()
    
    try:
        # Run server
        async with stdio_server() as (read_stream, write_stream):
            await run_server(server, read_stream, write_stream)
    finally:
        await server.shutdown()

async def run_server(server, read_stream, write_stream):
    """Run the MCP server with error handling"""
    from mcp.server import Server
    
    mcp_server = Server(
        server.list_tools,
        server.call_tool,
        server.list_resources
    )
    
    mcp_server.on_initialize(server.initialize)
    
    try:
        await mcp_server.run(read_stream, write_stream)
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
