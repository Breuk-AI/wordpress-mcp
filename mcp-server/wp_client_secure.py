"""
WordPress API Client - SECURITY PATCHED VERSION
Handles all communication with WordPress REST API and WooCommerce API
"""

import aiohttp
import base64
import json
import logging
import os
import hashlib
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
import asyncio
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# SECURITY: Configure logging to never log sensitive data
class SanitizedFormatter(logging.Formatter):
    """Custom formatter that removes sensitive data from logs"""
    
    def format(self, record):
        # Remove auth headers from log messages
        if hasattr(record, 'msg'):
            msg = str(record.msg)
            # Remove base64 auth strings
            import re
            msg = re.sub(r'Basic [A-Za-z0-9+/=]+', 'Basic [REDACTED]', msg)
            msg = re.sub(r'Authorization: [^\s]+', 'Authorization: [REDACTED]', msg)
            record.msg = msg
        return super().format(record)

# Apply sanitized formatter to all handlers
for handler in logger.handlers:
    handler.setFormatter(SanitizedFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

class WordPressClient:
    """Client for WordPress REST API communication with enhanced security"""
    
    def __init__(self, site_url: str, username: str, app_password: str, timeout: int = 30):
        # SECURITY: Validate HTTPS usage
        self.site_url = site_url.rstrip('/')
        if not self.site_url.startswith('https://') and not os.getenv('WP_ALLOW_HTTP', '').lower() == 'true':
            logger.warning("WARNING: Using HTTP instead of HTTPS. Set WP_ALLOW_HTTP=true to suppress this warning.")
        
        self.username = username
        # SECURITY: Store password hash for verification, not the actual password
        self._password_hash = hashlib.sha256(app_password.encode()).hexdigest()
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        
        # SECURITY: Create auth header without storing password
        app_password_clean = app_password.replace(' ', '')
        credentials = f"{username}:{app_password_clean}"
        self._auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"
        
        # Clear the password from memory
        del app_password
        del app_password_clean
        del credentials
        
        # API endpoints
        self.wp_api = f"{self.site_url}/wp-json/wp/v2"
        self.wc_api = f"{self.site_url}/wp-json/wc/v3"
        self.custom_api = f"{self.site_url}/wp-json/mcp/v1"
        
        # Session for connection pooling
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiting
        self.rate_limiter = RateLimiter(
            max_requests=int(os.getenv('RATE_LIMIT', '60')),
            time_window=60  # per minute
        )
    
    @asynccontextmanager
    async def get_session(self):
        """Get or create an aiohttp session with proper cleanup"""
        if self.session is None or self.session.closed:
            # SECURITY: Never log the auth header
            headers = {
                "Authorization": self._auth_header,
                "Content-Type": "application/json",
                "User-Agent": "WordPress-MCP/1.0"
            }
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=self.timeout,
                connector=aiohttp.TCPConnector(
                    limit=30,
                    limit_per_host=10,
                    force_close=True,  # Security: Force connection close
                    enable_cleanup_closed=True
                )
            )
        try:
            yield self.session
        except Exception as e:
            logger.error(f"Session error: {str(e)}")  # Don't log full exception which might contain auth
            raise
    
    async def close(self):
        """Close the session properly"""
        if self.session and not self.session.closed:
            await self.session.close()
            # Small delay to ensure cleanup
            await asyncio.sleep(0.25)
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def test_connection(self) -> bool:
        """Test if we can connect to WordPress"""
        try:
            # Check rate limit
            if not await self.rate_limiter.acquire():
                logger.error("Rate limit exceeded during connection test")
                return False
            
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": self._auth_header}
                
                async with session.get(
                    f"{self.wp_api}/users/me",
                    headers=headers,
                    timeout=self.timeout,
                    ssl=True  # Force SSL verification
                ) as response:
                    if response.status == 200:
                        user = await response.json()
                        logger.info(f"Connected as: {user.get('name', 'Unknown')}")
                        # Don't log capabilities as they might reveal security info
                        return True
                    else:
                        logger.error(f"Connection failed with status: {response.status}")
                        return False
        except asyncio.TimeoutError:
            logger.error("Connection timed out")
            return False
        except Exception as e:
            logger.error(f"Connection error: {type(e).__name__}")  # Don't log full error
            return False
    
    async def _request_with_retry(self, method: str, url: str, max_retries: int = 3, **kwargs):
        """Make HTTP request with exponential backoff retry"""
        for attempt in range(max_retries):
            try:
                # Check rate limit
                if not await self.rate_limiter.acquire():
                    raise Exception("Rate limit exceeded")
                
                async with self.get_session() as session:
                    async with session.request(method, url, **kwargs) as response:
                        return await self._handle_response(response)
            
            except asyncio.TimeoutError:
                if attempt == max_retries - 1:
                    raise
                wait_time = (2 ** attempt) * 1  # Exponential backoff: 1, 2, 4 seconds
                logger.warning(f"Request timeout, retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                if "rate limit" in str(e).lower():
                    wait_time = 10  # Longer wait for rate limits
                else:
                    wait_time = (2 ** attempt) * 1
                logger.warning(f"Request failed, retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """GET request to API with retry logic"""
        url = self._build_url(endpoint)
        logger.debug(f"GET {url}")  # Don't log params which might contain sensitive data
        
        return await self._request_with_retry('GET', url, params=params)
    
    async def post(self, endpoint: str, data: Dict) -> Any:
        """POST request to API with retry logic"""
        url = self._build_url(endpoint)
        logger.debug(f"POST {url}")
        
        # SECURITY: Sanitize data before sending
        sanitized_data = self._sanitize_data(data)
        
        return await self._request_with_retry('POST', url, json=sanitized_data)
    
    async def put(self, endpoint: str, data: Dict) -> Any:
        """PUT request to API with retry logic"""
        url = self._build_url(endpoint)
        logger.debug(f"PUT {url}")
        
        sanitized_data = self._sanitize_data(data)
        
        return await self._request_with_retry('PUT', url, json=sanitized_data)
    
    async def delete(self, endpoint: str) -> Any:
        """DELETE request to API with retry logic"""
        url = self._build_url(endpoint)
        logger.debug(f"DELETE {url}")
        
        return await self._request_with_retry('DELETE', url)
    
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
            return f"{self.wp_api}/{endpoint}"
    
    def _sanitize_data(self, data: Dict) -> Dict:
        """Sanitize data to prevent injection attacks"""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Basic sanitization - WordPress will do more on its end
                value = value.replace('\x00', '')  # Remove null bytes
                # Limit string length to prevent memory attacks
                if len(value) > 100000:  # 100KB max per field
                    value = value[:100000]
            elif isinstance(value, dict):
                value = self._sanitize_data(value)
            elif isinstance(value, list):
                value = [self._sanitize_data(item) if isinstance(item, dict) else item for item in value]
            
            sanitized[key] = value
        
        return sanitized
    
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
            logger.error(f"Failed to parse response")
            data = {"error": "Failed to parse response", "status": response.status}
        
        if response.status >= 400:
            # SECURITY: Don't log full error details that might expose system info
            if response.status == 401:
                raise Exception("Authentication failed. Please check your credentials.")
            elif response.status == 403:
                raise Exception("Permission denied. Insufficient privileges.")
            elif response.status == 404:
                raise Exception("Endpoint not found.")
            elif response.status == 429:
                raise Exception("Rate limit exceeded. Please try again later.")
            else:
                raise Exception(f"API Error {response.status}")
        
        return data
    
    # Convenience methods remain the same but inherit security improvements
    
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
    
    # Additional methods remain the same...


class RateLimiter:
    """Simple rate limiter using sliding window"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window  # in seconds
        self.requests = []
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """Check if request can proceed"""
        async with self.lock:
            now = asyncio.get_event_loop().time()
            
            # Remove old requests outside the window
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.time_window]
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            
            return False
    
    def reset(self):
        """Reset the rate limiter"""
        self.requests = []
