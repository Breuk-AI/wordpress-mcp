#!/usr/bin/env python3
"""
Deployment Helper for WordPress MCP Security Fixes
Automates the application of security patches
"""

import os
import sys
import shutil
import json
from pathlib import Path
import re

def create_modules():
    """Create the security module files"""
    print("Creating security modules...")
    
    modules_to_create = {
        'mcp-server/secure_auth.py': create_secure_auth_module(),
        'mcp-server/rate_limiter.py': create_rate_limiter_module(),
        'mcp-server/validators.py': create_validators_module(),
        'mcp-server/session_manager.py': create_session_manager_module(),
    }
    
    for file_path, content in modules_to_create.items():
        Path(file_path).parent.mkdir(exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Created {file_path}")
    
    return True

def apply_patches():
    """Apply security patches to existing files"""
    print("Applying security patches...")
    
    # Update server.py with security fixes
    if os.path.exists('mcp-server/server_secure.py'):
        shutil.copy('mcp-server/server_secure.py', 'mcp-server/server.py')
        print("  ✅ Updated server.py with security fixes")
    
    # Update wp_client.py with security fixes
    if os.path.exists('mcp-server/wp_client_secure.py'):
        shutil.copy('mcp-server/wp_client_secure.py', 'mcp-server/wp_client.py')
        print("  ✅ Updated wp_client.py with security fixes")
    
    # Update monitoring module if exists
    if os.path.exists('mcp-server/monitoring.py'):
        print("  ✅ Monitoring module already exists")
    
    return True

def update_plugin():
    """Update WordPress plugin with security fixes"""
    print("Updating WordPress plugin...")
    
    # Create secure API endpoints file
    api_endpoints_secure = create_secure_api_endpoints()
    with open('wp-mcp-plugin/includes/api-endpoints-secure.php', 'w', encoding='utf-8') as f:
        f.write(api_endpoints_secure)
    print("  ✅ Created secure API endpoints")
    
    # Update auth.php with rate limiting
    auth_secure = create_secure_auth_php()
    with open('wp-mcp-plugin/includes/auth-secure.php', 'w', encoding='utf-8') as f:
        f.write(auth_secure)
    print("  ✅ Created secure auth module")
    
    return True

def create_secure_auth_module():
    """Create the secure authentication module"""
    return '''"""
Secure authentication management for WordPress MCP
"""

import os
import hashlib
import base64
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

class SecureAuthManager:
    """Manages authentication credentials securely"""
    
    def __init__(self):
        self._encryption_key = self._get_or_create_key()
        self._cipher = Fernet(self._encryption_key)
        self._auth_cache = {}
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key for auth storage"""
        key_file = os.path.expanduser("~/.mcp_auth_key")
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        
        # Generate new key
        key = Fernet.generate_key()
        
        # Save with restricted permissions
        old_umask = os.umask(0o077)
        try:
            with open(key_file, 'wb') as f:
                f.write(key)
        finally:
            os.umask(old_umask)
        
        return key
    
    def store_credentials(self, username: str, app_password: str) -> str:
        """Securely store credentials and return encrypted token"""
        credentials = f"{username}:{app_password}"
        encrypted = self._cipher.encrypt(credentials.encode())
        
        # Generate unique token
        token = base64.urlsafe_b64encode(
            hashlib.sha256(encrypted + os.urandom(16)).digest()
        ).decode()
        
        self._auth_cache[token] = encrypted
        return token
    
    def get_auth_header(self, token: str) -> str:
        """Get auth header from token"""
        if token not in self._auth_cache:
            raise ValueError("Invalid or expired token")
        
        encrypted = self._auth_cache[token]
        credentials = self._cipher.decrypt(encrypted).decode()
        
        auth_bytes = base64.b64encode(credentials.encode()).decode()
        return f"Basic {auth_bytes}"
    
    def clear_token(self, token: str):
        """Clear a token from cache"""
        self._auth_cache.pop(token, None)
    
    def clear_all(self):
        """Clear all cached tokens"""
        self._auth_cache.clear()
'''

def create_rate_limiter_module():
    """Create the rate limiter module"""
    return '''"""
Production-ready rate limiting for WordPress MCP
"""

import time
import asyncio
from collections import defaultdict, deque
from typing import Dict, Tuple, Optional
import hashlib

class RateLimiter:
    """Token bucket rate limiter with sliding window"""
    
    def __init__(self, requests_per_minute: int = 60, burst_size: int = 10, block_duration: int = 300):
        self.rpm = requests_per_minute
        self.burst_size = burst_size
        self.block_duration = block_duration
        self._buckets: Dict[str, Tuple[float, float, deque]] = {}
        self._blocked: Dict[str, float] = {}
        asyncio.create_task(self._cleanup_loop())
    
    async def check_rate_limit(self, identifier: str) -> Tuple[bool, Optional[int]]:
        """Check if request is allowed"""
        now = time.time()
        
        if identifier in self._blocked:
            if now < self._blocked[identifier]:
                retry_after = int(self._blocked[identifier] - now)
                return False, retry_after
            else:
                del self._blocked[identifier]
        
        if identifier not in self._buckets:
            self._buckets[identifier] = (float(self.burst_size), now, deque(maxlen=self.rpm))
        
        tokens, last_refill, request_times = self._buckets[identifier]
        
        time_passed = now - last_refill
        tokens_to_add = time_passed * (self.rpm / 60.0)
        tokens = min(self.burst_size, tokens + tokens_to_add)
        
        cutoff = now - 60
        while request_times and request_times[0] < cutoff:
            request_times.popleft()
        
        if len(request_times) >= self.rpm:
            self._blocked[identifier] = now + self.block_duration
            return False, self.block_duration
        
        if tokens < 1:
            retry_after = int((1 - tokens) * (60.0 / self.rpm))
            return False, retry_after
        
        tokens -= 1
        request_times.append(now)
        self._buckets[identifier] = (tokens, now, request_times)
        
        return True, None
    
    async def _cleanup_loop(self):
        """Cleanup old entries periodically"""
        while True:
            await asyncio.sleep(300)
            now = time.time()
            
            expired_blocks = [k for k, v in self._blocked.items() if v < now]
            for k in expired_blocks:
                del self._blocked[k]
            
            inactive_cutoff = now - 3600
            inactive_buckets = [
                k for k, (_, last_refill, _) in self._buckets.items()
                if last_refill < inactive_cutoff
            ]
            for k in inactive_buckets:
                del self._buckets[k]
    
    def get_identifier(self, request_context) -> str:
        """Get unique identifier for rate limiting"""
        user_id = request_context.get('user_id', 'anonymous')
        ip_address = request_context.get('ip_address', '0.0.0.0')
        combined = f"{user_id}:{ip_address}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
'''

def create_validators_module():
    """Create the input validators module"""
    return '''"""
Comprehensive input validation for WordPress MCP
"""

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

class ValidationError(Exception):
    """Raised when validation fails"""
    pass

class InputValidator:
    """Validates and sanitizes all inputs"""
    
    RULES = {
        'post_title': {'max_length': 200, 'min_length': 1, 'strip_html': True, 'required': True},
        'post_content': {'max_length': 100000, 'sanitize_js': True},
        'post_status': {'allowed_values': ['publish', 'draft', 'private', 'pending'], 'required': True},
        'template_path': {'pattern': r'^[a-zA-Z0-9\-_/]+\.(php|css|js|html)$', 'max_length': 255, 'no_traversal': True},
        'url': {'valid_url': True, 'allowed_schemes': ['http', 'https'], 'max_length': 2048},
        'username': {'pattern': r'^[a-zA-Z0-9_\-]+$', 'max_length': 60},
        'id': {'type': 'int', 'min_value': 1},
        'param': {'max_length': 1000}
    }
    
    @classmethod
    def validate(cls, field_name: str, value: Any, rules: Optional[Dict] = None) -> Any:
        """Validate a single field"""
        if rules is None:
            rules = cls.RULES.get(field_name, {})
        
        if value is None:
            if rules.get('required', False):
                raise ValidationError(f"{field_name} is required")
            return None
        
        if 'type' in rules:
            value = cls._convert_type(value, rules['type'])
        
        if isinstance(value, str):
            value = cls._validate_string(value, field_name, rules)
        elif isinstance(value, (int, float)):
            value = cls._validate_number(value, field_name, rules)
        
        return value
    
    @classmethod
    def _validate_string(cls, value: str, field_name: str, rules: Dict) -> str:
        """Validate string input"""
        if 'min_length' in rules and len(value) < rules['min_length']:
            raise ValidationError(f"{field_name} must be at least {rules['min_length']} characters")
        
        if 'max_length' in rules and len(value) > rules['max_length']:
            raise ValidationError(f"{field_name} must not exceed {rules['max_length']} characters")
        
        if 'pattern' in rules:
            if not re.match(rules['pattern'], value):
                raise ValidationError(f"{field_name} format is invalid")
        
        if rules.get('no_traversal', False):
            if '..' in value or value.startswith('/'):
                raise ValidationError(f"{field_name} contains invalid path")
        
        if rules.get('strip_html', False):
            value = re.sub('<[^<]+?>', '', value)
        
        if rules.get('sanitize_js', False):
            value = cls._remove_javascript(value)
        
        if rules.get('valid_url', False):
            parsed = urlparse(value)
            if not parsed.scheme or not parsed.netloc:
                raise ValidationError(f"{field_name} must be a valid URL")
            
            if 'allowed_schemes' in rules:
                if parsed.scheme not in rules['allowed_schemes']:
                    raise ValidationError(f"{field_name} scheme must be one of {rules['allowed_schemes']}")
        
        if 'allowed_values' in rules:
            if value not in rules['allowed_values']:
                raise ValidationError(f"{field_name} must be one of {rules['allowed_values']}")
        
        return value
    
    @classmethod
    def _validate_number(cls, value: float, field_name: str, rules: Dict) -> float:
        """Validate numeric input"""
        if 'min_value' in rules and value < rules['min_value']:
            raise ValidationError(f"{field_name} must be at least {rules['min_value']}")
        
        if 'max_value' in rules and value > rules['max_value']:
            raise ValidationError(f"{field_name} must not exceed {rules['max_value']}")
        
        return value
    
    @classmethod
    def _remove_javascript(cls, content: str) -> str:
        """Remove JavaScript from content"""
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'\bon\w+\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
        content = re.sub(r'javascript\s*:', '', content, flags=re.IGNORECASE)
        return content
    
    @classmethod
    def _convert_type(cls, value: Any, target_type: str) -> Any:
        """Convert value to target type"""
        if target_type == 'int':
            try:
                return int(value)
            except (ValueError, TypeError):
                raise ValidationError(f"Value must be an integer")
        return value
'''

def create_session_manager_module():
    """Create the session manager module"""
    return '''"""
Secure session management with connection pooling
"""

import asyncio
import aiohttp
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
import time
import logging
import uuid

logger = logging.getLogger(__name__)

class SecureSessionManager:
    """Manages HTTP sessions with proper pooling and cleanup"""
    
    def __init__(self, max_connections: int = 20, max_per_host: int = 10, 
                 timeout: int = 30, keepalive_timeout: int = 30):
        self.max_connections = max_connections
        self.max_per_host = max_per_host
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.keepalive_timeout = keepalive_timeout
        self._session: Optional[aiohttp.ClientSession] = None
        self._session_created: float = 0
        self._request_count: int = 0
        self._lock = asyncio.Lock()
    
    async def _create_session(self, headers: Dict[str, str]) -> aiohttp.ClientSession:
        """Create a new session with security settings"""
        connector = aiohttp.TCPConnector(
            limit=self.max_connections,
            limit_per_host=self.max_per_host,
            ttl_dns_cache=300,
            enable_cleanup_closed=True,
            force_close=False,
            keepalive_timeout=self.keepalive_timeout,
            ssl=True
        )
        
        secure_headers = {
            **headers,
            'User-Agent': 'WordPress-MCP/1.0 (Secure)',
            'X-Request-ID': str(uuid.uuid4()),
        }
        
        logged_headers = {k: v for k, v in secure_headers.items() 
                         if 'auth' not in k.lower()}
        logger.debug(f"Creating session with headers: {logged_headers}")
        
        return aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout,
            headers=secure_headers,
            cookie_jar=aiohttp.DummyCookieJar(),
            trust_env=False
        )
    
    @asynccontextmanager
    async def get_session(self, headers: Dict[str, str]):
        """Get or create a session"""
        async with self._lock:
            now = time.time()
            needs_new = (
                self._session is None or
                self._session.closed or
                (now - self._session_created) > 3600 or
                self._request_count > 1000
            )
            
            if needs_new:
                if self._session and not self._session.closed:
                    await self._session.close()
                    await asyncio.sleep(0.25)
                
                self._session = await self._create_session(headers)
                self._session_created = now
                self._request_count = 0
        
        try:
            yield self._session
        except Exception as e:
            logger.error(f"Session error: {e}")
            self._request_count = 1001
            raise
    
    async def close(self):
        """Close the session properly"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
'''

def create_secure_api_endpoints():
    """Create secure API endpoints PHP file"""
    return '''<?php
/**
 * Secure MCP API Endpoints with Path Validation
 */

// Secure template path validation
function mcp_validate_template_path($template_path) {
    // Remove any directory traversal attempts
    $template_path = str_replace(['..', '\\\\', "\\0"], '', $template_path);
    $template_path = ltrim($template_path, '/');
    
    // Get allowed directories
    $theme_dir = realpath(get_template_directory());
    $child_theme_dir = realpath(get_stylesheet_directory());
    
    // Check both possible paths
    $possible_paths = [
        realpath($child_theme_dir . '/' . $template_path),
        realpath($theme_dir . '/' . $template_path)
    ];
    
    foreach ($possible_paths as $full_path) {
        if ($full_path === false) {
            continue;
        }
        
        // Ensure the path is within allowed directories
        if (strpos($full_path, $theme_dir) === 0 || 
            strpos($full_path, $child_theme_dir) === 0) {
            
            // Additional check: only allow PHP and CSS files
            $allowed_extensions = ['php', 'css', 'js', 'html'];
            $extension = pathinfo($full_path, PATHINFO_EXTENSION);
            
            if (!in_array($extension, $allowed_extensions, true)) {
                return false;
            }
            
            return $full_path;
        }
    }
    
    return false;
}

// Sanitize template content
function mcp_sanitize_template_content($content, $file_type = 'php') {
    // Check for dangerous PHP functions
    $dangerous_functions = [
        'eval', 'exec', 'system', 'shell_exec', 'passthru',
        'proc_open', 'popen', 'curl_exec', 'curl_multi_exec',
        'parse_ini_file', 'show_source', 'file_get_contents',
        'file_put_contents', 'fopen', 'fwrite'
    ];
    
    foreach ($dangerous_functions as $func) {
        if (preg_match('/\\b' . preg_quote($func) . '\\s*\\(/i', $content)) {
            throw new Exception("Dangerous function '$func' detected in template content");
        }
    }
    
    // Check for base64 encoded content
    if (preg_match('/base64_decode\\s*\\(/i', $content)) {
        throw new Exception("Base64 decode detected - potential security risk");
    }
    
    return $content;
}
'''

def create_secure_auth_php():
    """Create secure auth PHP file"""
    return '''<?php
/**
 * Secure Authentication and Rate Limiting for MCP
 */

// Enhanced rate limiting implementation
function mcp_check_rate_limit($user_id) {
    $rate_limit = get_option('mcp_rate_limit', 60);
    $burst_size = get_option('mcp_burst_size', 10);
    $block_duration = get_option('mcp_block_duration', 300);
    
    $transient_key = 'mcp_rate_limit_' . $user_id;
    $burst_key = 'mcp_burst_' . $user_id;
    $block_key = 'mcp_blocked_' . $user_id;
    
    // Check if user is blocked
    if (get_transient($block_key)) {
        return false;
    }
    
    // Check burst limit
    $burst_count = get_transient($burst_key);
    if ($burst_count === false) {
        set_transient($burst_key, 1, 10); // 10 second burst window
    } elseif ($burst_count >= $burst_size) {
        set_transient($block_key, true, $block_duration);
        return false;
    } else {
        set_transient($burst_key, $burst_count + 1, 10);
    }
    
    // Check rate limit
    $requests = get_transient($transient_key);
    if ($requests === false) {
        set_transient($transient_key, 1, 60);
        return true;
    }
    
    if ($requests >= $rate_limit) {
        set_transient($block_key, true, $block_duration);
        return false;
    }
    
    set_transient($transient_key, $requests + 1, 60);
    return true;
}

// CORS security with origin validation
add_action('rest_api_init', function() {
    remove_filter('rest_pre_serve_request', 'rest_send_cors_headers');
    add_filter('rest_pre_serve_request', function($value) {
        $allowed_origins = get_option('mcp_cors_origins', array());
        
        if (empty($allowed_origins)) {
            return $value;
        }
        
        $origin = isset($_SERVER['HTTP_ORIGIN']) ? $_SERVER['HTTP_ORIGIN'] : '';
        
        // Validate origin format
        if ($origin && filter_var($origin, FILTER_VALIDATE_URL)) {
            if (in_array($origin, $allowed_origins, true)) {
                header('Access-Control-Allow-Origin: ' . $origin);
                header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
                header('Access-Control-Allow-Headers: Authorization, Content-Type, X-WP-Nonce');
                header('Access-Control-Allow-Credentials: true');
                header('Access-Control-Max-Age: 3600');
            }
        }
        
        return $value;
    });
}, 15);

// Add nonce verification
function mcp_verify_request_nonce($request) {
    $nonce = $request->get_header('X-WP-Nonce');
    
    if ($nonce && !wp_verify_nonce($nonce, 'wp_rest')) {
        return new WP_Error('invalid_nonce', 'Invalid nonce', array('status' => 403));
    }
    
    return true;
}
'''

def main():
    """Main deployment function"""
    if len(sys.argv) < 2:
        print("Usage: deploy_helper.py [create_modules|apply_patches|update_plugin]")
        return 1
    
    command = sys.argv[1]
    
    try:
        if command == 'create_modules':
            return 0 if create_modules() else 1
        elif command == 'apply_patches':
            return 0 if apply_patches() else 1
        elif command == 'update_plugin':
            return 0 if update_plugin() else 1
        else:
            print(f"Unknown command: {command}")
            return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
