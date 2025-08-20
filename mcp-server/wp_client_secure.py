"""
Secure WordPress Client with all security fixes applied
Production-ready implementation
"""

import aiohttp
import base64
import json
import logging
import os
import hashlib
import time
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin
from contextlib import asynccontextmanager
from cryptography.fernet import Fernet

# Import our security modules
from .secure_auth import SecureAuthManager
from .session_manager import SecureSessionManager
from .rate_limiter import RateLimiter
from .validators import InputValidator, ValidationError

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
logger = logging.getLogger(__name__)

class SecureWordPressClient:
    """Secure WordPress REST API client with comprehensive protection"""
    
    def __init__(self, site_url: str, username: str, app_password: str, 
                 timeout: int = 30, rate_limit: int = 60):
        """
        Initialize secure WordPress client
        
        Args:
            site_url: WordPress site URL
            username: WordPress username
            app_password: Application password
            timeout: Request timeout in seconds
            rate_limit: Requests per minute limit
        """
        # Validate inputs
        self.site_url = InputValidator.validate('url', site_url.rstrip('/'))
        self.username = InputValidator.validate('username', username)
        
        # Secure auth management
        self.auth_manager = SecureAuthManager()
        self.auth_token = self.auth_manager.store_credentials(username, app_password)
        
        # Session management
        self.session_manager = SecureSessionManager(timeout=timeout)
        
        # Rate limiting
        self.rate_limiter = RateLimiter(requests_per_minute=rate_limit)
        
        # API endpoints
        self.wp_api = f"{self.site_url}/wp-json/wp/v2"
        self.wc_api = f"{self.site_url}/wp-json/wc/v3"
        self.custom_api = f"{self.site_url}/wp-json/mcp/v1"
        
        # Request tracking
        self._request_id = 0
        self._metrics = {
            'total_requests': 0,
            'failed_requests': 0,
            'rate_limited': 0
        }
    
    async def test_connection(self) -> bool:
        """Test WordPress connection with secure auth"""
        try:
            # Get auth header securely
            auth_header = self.auth_manager.get_auth_header(self.auth_token)
            
            async with self.session_manager.get_session(
                {"Authorization": auth_header}
            ) as session:
                async with session.get(
                    f"{self.wp_api}/users/me",
                    ssl=True,  # Force SSL
                    allow_redirects=False  # Prevent redirect attacks
                ) as response:
                    if response.status == 200:
                        user = await response.json()
                        # Log without sensitive data
                        logger.info(f"Connected as user ID: {user.get('id', 'Unknown')}")
                        return True
                    else:
                        logger.error(f"Connection failed with status: {response.status}")
                        return False
                        
        except asyncio.TimeoutError:
            logger.error("Connection timed out")
            return False
        except Exception as e:
            logger.error(f"Connection error: {type(e).__name__}")
            return False
    
    async def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting"""
        # Get identifier for rate limiting
        identifier = hashlib.sha256(
            f"{self.username}:{id(self)}".encode()
        ).hexdigest()[:16]
        
        allowed, retry_after = await self.rate_limiter.check_rate_limit(identifier)
        
        if not allowed:
            self._metrics['rate_limited'] += 1
            raise Exception(f"Rate limit exceeded. Retry after {retry_after} seconds")
    
    async def _execute_request(self, method: str, url: str, 
                              **kwargs) -> Any:
        """Execute HTTP request with security measures"""
        # Check rate limit
        await self._check_rate_limit()
        
        # Generate request ID for tracing
        self._request_id += 1
        request_id = f"{self._request_id:06d}-{int(time.time())}"
        
        # Get auth header
        auth_header = self.auth_manager.get_auth_header(self.auth_token)
        
        # Prepare headers
        headers = {
            "Authorization": auth_header,
            "X-Request-ID": request_id,
            "Content-Type": "application/json"
        }
        
        # Add to kwargs
        kwargs.setdefault('headers', {}).update(headers)
        kwargs['ssl'] = True  # Force SSL
        kwargs['allow_redirects'] = False  # Prevent redirect attacks
        
        # Track metrics
        self._metrics['total_requests'] += 1
        
        try:
            async with self.session_manager.get_session(headers) as session:
                async with session.request(method, url, **kwargs) as response:
                    return await self._handle_response(response)
                    
        except asyncio.TimeoutError:
            self._metrics['failed_requests'] += 1
            logger.error(f"Request {request_id} timed out")
            raise Exception("Request timed out")
            
        except Exception as e:
            self._metrics['failed_requests'] += 1
            logger.error(f"Request {request_id} failed: {type(e).__name__}")
            raise
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Any:
        """Handle response with proper error handling"""
        if response.status == 204:
            return {"success": True}
        
        content_type = response.headers.get('Content-Type', '')
        
        try:
            if 'application/json' in content_type:
                data = await response.json()
            else:
                data = await response.text()
        except Exception:
            data = {"error": "Failed to parse response", "status": response.status}
        
        if response.status >= 400:
            # Sanitize error message
            error_message = self._sanitize_error(data)
            
            if response.status == 401:
                raise Exception("Authentication failed")
            elif response.status == 403:
                raise Exception("Permission denied")
            elif response.status == 404:
                raise Exception("Resource not found")
            elif response.status == 429:
                raise Exception("Rate limit exceeded")
            else:
                raise Exception(f"Request failed: {error_message}")
        
        return data
    
    def _sanitize_error(self, error_data: Any) -> str:
        """Sanitize error message to prevent information disclosure"""
        if isinstance(error_data, dict):
            # Only return safe error messages
            return error_data.get('code', 'unknown_error')
        return "Request failed"
    
    def _build_url(self, endpoint: str) -> str:
        """Build and validate URL"""
        if endpoint.startswith('http'):
            # Validate full URL
            return InputValidator.validate('url', endpoint)
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
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Secure GET request"""
        url = self._build_url(endpoint)
        
        # Validate params
        if params:
            validated_params = {}
            for key, value in params.items():
                # Basic validation - extend as needed
                validated_params[key] = InputValidator.validate('param', value)
            params = validated_params
        
        logger.debug(f"GET {endpoint}")
        return await self._execute_request('GET', url, params=params)
    
    async def post(self, endpoint: str, data: Dict) -> Any:
        """Secure POST request"""
        url = self._build_url(endpoint)
        
        # Validate data based on endpoint
        validated_data = self._validate_request_data(endpoint, data)
        
        logger.debug(f"POST {endpoint}")
        return await self._execute_request('POST', url, json=validated_data)
    
    async def put(self, endpoint: str, data: Dict) -> Any:
        """Secure PUT request"""
        url = self._build_url(endpoint)
        
        # Validate data
        validated_data = self._validate_request_data(endpoint, data)
        
        logger.debug(f"PUT {endpoint}")
        return await self._execute_request('PUT', url, json=validated_data)
    
    async def delete(self, endpoint: str) -> Any:
        """Secure DELETE request"""
        url = self._build_url(endpoint)
        
        logger.debug(f"DELETE {endpoint}")
        return await self._execute_request('DELETE', url)
    
    def _validate_request_data(self, endpoint: str, data: Dict) -> Dict:
        """Validate request data based on endpoint"""
        validated = {}
        
        # Endpoint-specific validation
        if 'posts' in endpoint:
            if 'title' in data:
                validated['title'] = InputValidator.validate('post_title', data['title'])
            if 'content' in data:
                validated['content'] = InputValidator.validate('post_content', data['content'])
            if 'status' in data:
                validated['status'] = InputValidator.validate('post_status', data['status'])
            # Add other fields as needed
            for key, value in data.items():
                if key not in validated:
                    validated[key] = value  # Pass through other fields
                    
        elif 'templates' in endpoint:
            if 'path' in data:
                validated['path'] = InputValidator.validate('template_path', data['path'])
            if 'content' in data:
                # Special validation for template content
                validated['content'] = self._validate_template_content(data['content'])
            for key, value in data.items():
                if key not in validated:
                    validated[key] = value
                    
        else:
            # Default validation for other endpoints
            validated = data
        
        return validated
    
    def _validate_template_content(self, content: str) -> str:
        """Validate template content for security"""
        # Check for dangerous PHP functions
        dangerous_functions = [
            'eval', 'exec', 'system', 'shell_exec', 'passthru',
            'proc_open', 'popen', 'curl_exec', 'file_get_contents',
            'file_put_contents', 'fopen', 'fwrite'
        ]
        
        for func in dangerous_functions:
            if f'{func}(' in content:
                raise ValidationError(f"Dangerous function '{func}' not allowed in templates")
        
        # Check for base64 encoded content
        if 'base64_decode' in content:
            raise ValidationError("Base64 decode not allowed in templates")
        
        return content
    
    # Convenience methods with validation
    
    async def get_posts(self, **params) -> List[Dict]:
        """Get posts with validation"""
        return await self.get("posts", params)
    
    async def create_post(self, data: Dict) -> Dict:
        """Create post with validation"""
        return await self.post("posts", data)
    
    async def update_post(self, post_id: int, data: Dict) -> Dict:
        """Update post with validation"""
        post_id = InputValidator.validate('id', post_id)
        return await self.put(f"posts/{post_id}", data)
    
    async def delete_post(self, post_id: int, force: bool = False) -> Dict:
        """Delete post with validation"""
        post_id = InputValidator.validate('id', post_id)
        endpoint = f"posts/{post_id}"
        if force:
            endpoint += "?force=true"
        return await self.delete(endpoint)
    
    async def read_template(self, template_path: str) -> Dict:
        """Read template with path validation"""
        validated_path = InputValidator.validate('template_path', template_path)
        return await self.post("mcp/templates/read", {"path": validated_path})
    
    async def update_template(self, template_path: str, content: str) -> Dict:
        """Update template with full validation"""
        validated_path = InputValidator.validate('template_path', template_path)
        validated_content = self._validate_template_content(content)
        
        return await self.post("mcp/templates/update", {
            "path": validated_path,
            "content": validated_content
        })
    
    def get_metrics(self) -> Dict[str, int]:
        """Get client metrics for monitoring"""
        return self._metrics.copy()
    
    async def close(self):
        """Clean shutdown"""
        await self.session_manager.close()
        self.auth_manager.clear_all()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
