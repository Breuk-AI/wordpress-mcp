"""
WordPress API Client
Handles all communication with WordPress REST API and WooCommerce API
"""

import aiohttp
import base64
import json
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
import asyncio
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class WordPressClient:
    """Client for WordPress REST API communication"""
    
    def __init__(self, site_url: str, username: str, app_password: str, timeout: int = 30):
        self.site_url = site_url.rstrip('/')
        self.username = username
        self.app_password = app_password.replace(' ', '')  # Remove spaces from app password
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        
        # Create auth header
        credentials = f"{username}:{app_password}"
        self.auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"
        
        # API endpoints
        self.wp_api = f"{self.site_url}/wp-json/wp/v2"
        self.wc_api = f"{self.site_url}/wp-json/wc/v3"
        self.custom_api = f"{self.site_url}/wp-json/mcp/v1"  # Our custom endpoints
        
        # Session for connection pooling
        self.session: Optional[aiohttp.ClientSession] = None
    
    @asynccontextmanager
    async def get_session(self):
        """Get or create an aiohttp session with proper cleanup"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": self.auth_header,
                    "Content-Type": "application/json",
                    "User-Agent": "WordPress-MCP/1.0"
                },
                timeout=self.timeout,
                connector=aiohttp.TCPConnector(limit=30, limit_per_host=10)
            )
        try:
            yield self.session
        except Exception as e:
            logger.error(f"Session error: {e}")
            raise
    
    async def close(self):
        """Close the session properly"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def test_connection(self) -> bool:
        """Test if we can connect to WordPress"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.wp_api}/users/me",
                    headers={"Authorization": self.auth_header},
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        user = await response.json()
                        logger.info(f"Connected as: {user.get('name', 'Unknown')}")
                        logger.info(f"User capabilities: {user.get('capabilities', {})}")
                        return True
                    else:
                        text = await response.text()
                        logger.error(f"Connection failed: {response.status} - {text}")
                        return False
        except asyncio.TimeoutError:
            logger.error("Connection timed out")
            return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """GET request to API"""
        async with self.get_session() as session:
            url = self._build_url(endpoint)
            logger.debug(f"GET {url} with params {params}")
            
            try:
                async with session.get(url, params=params) as response:
                    return await self._handle_response(response)
            except asyncio.TimeoutError:
                logger.error(f"Request timed out: GET {url}")
                raise Exception(f"Request timed out after {self.timeout.total} seconds")
    
    async def post(self, endpoint: str, data: Dict) -> Any:
        """POST request to API"""
        async with self.get_session() as session:
            url = self._build_url(endpoint)
            logger.debug(f"POST {url}")
            
            try:
                async with session.post(url, json=data) as response:
                    return await self._handle_response(response)
            except asyncio.TimeoutError:
                logger.error(f"Request timed out: POST {url}")
                raise Exception(f"Request timed out after {self.timeout.total} seconds")
    
    async def put(self, endpoint: str, data: Dict) -> Any:
        """PUT request to API"""
        async with self.get_session() as session:
            url = self._build_url(endpoint)
            logger.debug(f"PUT {url}")
            
            try:
                async with session.put(url, json=data) as response:
                    return await self._handle_response(response)
            except asyncio.TimeoutError:
                logger.error(f"Request timed out: PUT {url}")
                raise Exception(f"Request timed out after {self.timeout.total} seconds")
    
    async def delete(self, endpoint: str) -> Any:
        """DELETE request to API"""
        async with self.get_session() as session:
            url = self._build_url(endpoint)
            logger.debug(f"DELETE {url}")
            
            try:
                async with session.delete(url) as response:
                    return await self._handle_response(response)
            except asyncio.TimeoutError:
                logger.error(f"Request timed out: DELETE {url}")
                raise Exception(f"Request timed out after {self.timeout.total} seconds")
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        if endpoint.startswith('http'):
            return endpoint
        elif endpoint.startswith('/wp-json/'):
            return f"{self.site_url}{endpoint}"
        elif endpoint.startswith('wp/'):
            return f"{self.wp_api}/{endpoint[3:]}"
        elif endpoint.startswith('wc/'):
            return f"{self.wc_api}/{endpoint[3:]}"
        elif endpoint.startswith('mcp/'):
            return f"{self.custom_api}/{endpoint[4:]}"
        else:
            # Default to WP API
            return f"{self.wp_api}/{endpoint}"
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Any:
        """Handle API response"""
        if response.status == 204:
            return {"success": True}
        
        content_type = response.headers.get('Content-Type', '')
        
        try:
            if 'application/json' in content_type:
                data = await response.json()
            else:
                data = await response.text()
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            data = {"error": "Failed to parse response", "status": response.status}
        
        if response.status >= 400:
            error_message = data
            if isinstance(data, dict):
                error_message = data.get('message', data.get('error', str(data)))
            
            logger.error(f"API Error {response.status}: {error_message}")
            
            # Provide more helpful error messages
            if response.status == 401:
                raise Exception(f"Authentication failed. Please check your application password.")
            elif response.status == 403:
                raise Exception(f"Permission denied. User may lack required capabilities.")
            elif response.status == 404:
                raise Exception(f"Endpoint not found. The API endpoint may not exist.")
            else:
                raise Exception(f"API Error {response.status}: {error_message}")
        
        return data
    
    # Convenience methods for common operations
    
    async def get_posts(self, **params) -> List[Dict]:
        """Get posts with optional filters"""
        return await self.get("posts", params)
    
    async def get_post(self, post_id: int) -> Dict:
        """Get single post"""
        return await self.get(f"posts/{post_id}")
    
    async def create_post(self, data: Dict) -> Dict:
        """Create new post"""
        return await self.post("posts", data)
    
    async def update_post(self, post_id: int, data: Dict) -> Dict:
        """Update existing post"""
        return await self.put(f"posts/{post_id}", data)
    
    async def delete_post(self, post_id: int, force: bool = False) -> Dict:
        """Delete post"""
        endpoint = f"posts/{post_id}"
        if force:
            endpoint += "?force=true"
        return await self.delete(endpoint)
    
    # Pages
    async def get_pages(self, **params) -> List[Dict]:
        """Get pages with optional filters"""
        return await self.get("pages", params)
    
    async def get_page(self, page_id: int) -> Dict:
        """Get single page"""
        return await self.get(f"pages/{page_id}")
    
    async def create_page(self, data: Dict) -> Dict:
        """Create new page"""
        return await self.post("pages", data)
    
    async def update_page(self, page_id: int, data: Dict) -> Dict:
        """Update existing page"""
        return await self.put(f"pages/{page_id}", data)
    
    async def delete_page(self, page_id: int, force: bool = False) -> Dict:
        """Delete page"""
        endpoint = f"pages/{page_id}"
        if force:
            endpoint += "?force=true"
        return await self.delete(endpoint)
    
    # Media
    async def get_media(self, **params) -> List[Dict]:
        """Get media items"""
        return await self.get("media", params)
    
    # WooCommerce specific methods
    
    async def get_products(self, **params) -> List[Dict]:
        """Get WooCommerce products"""
        return await self.get("wc/products", params)
    
    async def get_orders(self, **params) -> List[Dict]:
        """Get WooCommerce orders"""
        return await self.get("wc/orders", params)
    
    async def get_customers(self, **params) -> List[Dict]:
        """Get WooCommerce customers"""
        return await self.get("wc/customers", params)
    
    # Custom endpoint methods (for our plugin)
    
    async def get_template_files(self) -> List[Dict]:
        """Get list of theme template files"""
        return await self.get("mcp/templates")
    
    async def read_template(self, template_path: str) -> Dict:
        """Read template file content"""
        return await self.post("mcp/templates/read", {"path": template_path})
    
    async def update_template(self, template_path: str, content: str) -> Dict:
        """Update template file content"""
        return await self.post("mcp/templates/update", {
            "path": template_path,
            "content": content
        })
    
    async def get_system_info(self) -> Dict:
        """Get WordPress system information"""
        return await self.get("mcp/system/info")
    
    async def execute_wp_cli(self, command: str) -> Dict:
        """Execute WP-CLI command (if available)"""
        return await self.post("mcp/cli", {"command": command})
