# WordPress MCP Security Update v1.0.1

## 🔒 Critical Security Patches Applied

This update addresses several critical security vulnerabilities identified during a comprehensive security audit. All issues have been patched and tested.

## Vulnerabilities Fixed

### 1. **Path Traversal Vulnerability (CRITICAL)**
- **Issue**: Template editing could access files outside theme directories using `../` sequences
- **Fix**: Implemented strict path validation with `realpath()` checks and directory boundary enforcement
- **Files Modified**: `wp-mcp-plugin/includes/api-endpoints.php`

### 2. **Authentication Token Exposure (CRITICAL)**
- **Issue**: Application passwords stored in plaintext and potentially exposed in logs
- **Fix**: 
  - Passwords now hashed for verification
  - Custom log formatter removes sensitive data
  - Auth headers never logged
- **Files Modified**: `mcp-server/wp_client.py`

### 3. **Missing Rate Limiting (HIGH)**
- **Issue**: Python server had no rate limiting despite configuration
- **Fix**: Implemented sliding window rate limiter with configurable limits
- **Files Modified**: `mcp-server/wp_client.py`

### 4. **File Extension Validation (HIGH)**
- **Issue**: Template editor could modify non-PHP files
- **Fix**: Strict validation to only allow `.php` file extensions
- **Files Modified**: `wp-mcp-plugin/includes/api-endpoints.php`

### 5. **HTTPS Enforcement (HIGH)**
- **Issue**: No enforcement of secure connections for sensitive operations
- **Fix**: Template updates now require HTTPS unless in debug mode
- **Files Modified**: Both PHP and Python components

## Security Improvements

### Enhanced Features
- ✅ **Input Sanitization**: All inputs sanitized before processing
- ✅ **Error Handling**: Generic error messages prevent information leakage
- ✅ **Backup System**: Automatic backups before template modifications
- ✅ **Dangerous Function Detection**: Blocks templates containing eval, exec, etc.
- ✅ **Request Retry Logic**: Exponential backoff for failed requests
- ✅ **Connection Pooling**: Secure session management with forced SSL
- ✅ **CORS Validation**: Proper origin validation for cross-origin requests

### Testing
- Comprehensive security test suite added (`tests/test_security.py`)
- Tests verify all security patches are properly applied
- Automated testing in CI/CD pipeline

## How to Apply Security Patches

### Option 1: Automatic (Recommended)
```bash
# Windows
apply-security-patches.bat

# Linux/Mac
chmod +x apply-security-patches.sh
./apply-security-patches.sh
```

### Option 2: Manual
1. Backup existing files
2. Copy `wp_client_secure.py` to `wp_client.py`
3. Copy `api-endpoints-secure.php` to `api-endpoints.php`
4. Run security tests: `python tests/test_security.py`

## Configuration

### Environment Variables
```env
# Security Settings
WP_SITE_URL=https://your-site.com  # HTTPS required
WP_ALLOW_HTTP=false                 # Set to true only for local development
RATE_LIMIT=60                       # Requests per minute
API_TIMEOUT=30                      # Request timeout in seconds
MCP_DEBUG=false                     # Never enable in production
```

### WordPress Settings
- Ensure Application Passwords are enabled
- Use strong, unique passwords (min 24 characters)
- Regularly rotate application passwords
- Monitor access logs for suspicious activity

## Security Best Practices

1. **Always use HTTPS** in production
2. **Rotate credentials** regularly
3. **Monitor logs** for suspicious activity
4. **Keep WordPress** and plugins updated
5. **Regular backups** of templates and database
6. **Principle of least privilege** for user permissions
7. **Regular security audits** of the codebase

## Vulnerability Disclosure

If you discover a security vulnerability, please email security@your-domain.com with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

Please do NOT create public issues for security vulnerabilities.

## Changelog

### Version 1.0.1 (Security Update)
- Fixed critical path traversal vulnerability
- Secured authentication token handling
- Implemented rate limiting in Python server
- Added file extension validation
- Enforced HTTPS for sensitive operations
- Enhanced input sanitization
- Improved error handling to prevent info leakage
- Added comprehensive security test suite

### Version 1.0.0
- Initial release

## Credits

Security audit and patches by Claude AI team.

## License

MIT License - See LICENSE file for details
