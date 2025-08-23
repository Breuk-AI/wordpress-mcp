# WordPress MCP - Technical Documentation

## Architecture Overview

WordPress MCP implements a Model Context Protocol server that bridges Claude Desktop with WordPress installations via REST API and custom endpoints.

### System Architecture

```
┌─────────────────┐     MCP Protocol    ┌──────────────────┐
│  Claude Desktop │◄────────────────────►│  MCP Server      │
│                 │     JSON-RPC         │  (Python 3.8+)   │
└─────────────────┘                      └──────────────────┘
                                                 │
                                          REST API + Custom
                                                 │
                                                 ▼
                                      ┌──────────────────────┐
                                      │  WordPress Site      │
                                      │  - WP REST API       │
                                      │  - MCP Plugin (PHP)  │
                                      └──────────────────────┘
```

## Technical Stack

### MCP Server (Python)
- **Core**: Python 3.8+ with asyncio
- **Protocol**: MCP (Model Context Protocol) via stdio
- **HTTP**: aiohttp for async REST calls
- **Auth**: WordPress Application Passwords
- **Config**: Environment variables (.env)

### WordPress Plugin (PHP)
- **Min Version**: WordPress 5.6 (Application Passwords)
- **PHP**: 7.4+ with JSON support
- **Endpoints**: Custom REST routes at `/wp-json/mcp/v1/`
- **Security**: Nonce verification, capability checks
- **Backups**: Automatic file versioning

## API Endpoints

### WordPress Core Operations

| Tool | Endpoint | Method | Description |
|------|----------|--------|-------------|
| `wp_get_posts` | `/wp/v2/posts` | GET | Retrieve posts with filtering |
| `wp_create_post` | `/wp/v2/posts` | POST | Create new post |
| `wp_update_post` | `/wp/v2/posts/{id}` | PUT | Update existing post |
| `wp_delete_post` | `/wp/v2/posts/{id}` | DELETE | Delete post |
| `wp_upload_media` | `/wp/v2/media` | POST | Upload media files |

### WooCommerce Operations

| Tool | Endpoint | Method | Description |
|------|----------|--------|-------------|
| `wc_get_products` | `/wc/v3/products` | GET | List products |
| `wc_update_product` | `/wc/v3/products/{id}` | PUT | Update product |
| `wc_bulk_update_prices` | `/wc/v3/products/batch` | POST | Bulk price updates |
| `wc_get_orders` | `/wc/v3/orders` | GET | Retrieve orders |

### Custom MCP Operations

| Tool | Endpoint | Method | Description |
|------|----------|--------|-------------|
| `wp_read_template` | `/mcp/v1/template` | GET | Read theme file |
| `wp_update_template` | `/mcp/v1/template` | POST | Update with backup |
| `wp_list_templates` | `/mcp/v1/templates` | GET | List editable files |

## Security Implementation

### Authentication Flow

```python
# Application Password Format
WP_APP_PASSWORD = "xxxx xxxx xxxx xxxx xxxx xxxx"

# Base64 Encoding
auth_string = base64.b64encode(f"{username}:{app_password}".encode())
headers = {"Authorization": f"Basic {auth_string}"}
```

### Security Layers

1. **Path Traversal Protection**
   ```python
   def validate_template_path(path):
       # Prevent directory traversal
       if "../" in path or path.startswith("/"):
           raise SecurityError("Invalid path")
   ```

2. **Rate Limiting**
   ```python
   # Default: 60 requests per minute
   rate_limiter = RateLimiter(max_requests=60, window=60)
   ```

3. **Input Sanitization**
   ```python
   def sanitize_input(data):
       # Strip tags, escape special chars
       return wp.esc_html(wp.strip_tags(data))
   ```

## Testing Infrastructure

### Unit Tests (pytest)
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=mcp-server --cov-report=html

# Run specific test file
pytest tests/unit/test_wp_client.py
```

### Test Categories
- **Unit Tests**: Pure functions, no external dependencies
- **Integration Tests**: WordPress API interaction (requires test site)
- **Security Tests**: Input validation, auth, sanitization
- **Performance Tests**: Bulk operations, memory usage

### CI/CD Pipeline

```yaml
# GitHub Actions Workflow
- Validate: Structure and manifest checks
- Syntax: Python compilation check
- Unit Tests: pytest with coverage
- Quality: ruff, bandit, safety
- Security: Dependency scanning
```

## Performance Optimizations

### Connection Pooling
```python
# Reuse HTTP connections
connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
session = aiohttp.ClientSession(connector=connector)
```

### Async Operations
```python
# Parallel requests for bulk operations
async def bulk_update(items):
    tasks = [update_item(item) for item in items]
    return await asyncio.gather(*tasks)
```

### Caching Strategy
```python
# Template caching with TTL
template_cache = TTLCache(maxsize=100, ttl=300)  # 5 min cache
```

## Development Setup

### Environment Setup
```bash
# Clone repository
git clone https://github.com/Breuk-AI/wordpress-mcp.git
cd wordpress-mcp

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r mcp-server/requirements.txt
pip install -r requirements-dev.txt  # Dev tools

# Configure environment
cp mcp-server/.env.example mcp-server/.env
# Edit .env with your credentials
```

### Local Testing
```bash
# Test server directly
python mcp-server/server.py

# Test with mock WordPress
python tests/mock_wordpress_server.py

# Run specific tool
python -m mcp_server.tools.posts --test
```

## Debugging

### Enable Debug Logging
```python
# In .env
DEBUG=true
LOG_LEVEL=DEBUG

# In code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Tools not appearing | Cache issue | Restart Claude, new conversation |
| Auth failures | Wrong password format | Check spaces in app password |
| 404 errors | Wrong site URL | Remove trailing slash from URL |
| Timeout errors | Large operations | Increase timeout, use pagination |

## Plugin Development

### Adding New Tools

1. Create tool module in `mcp-server/tools/`
```python
# tools/custom.py
async def custom_operation(params):
    # Implementation
    return result
```

2. Register in server
```python
# server.py
@server.tool()
async def wp_custom_tool(params):
    return await custom_operation(params)
```

3. Add WordPress endpoint if needed
```php
// WordPress plugin
add_action('rest_api_init', function() {
    register_rest_route('mcp/v1', '/custom', [
        'methods' => 'POST',
        'callback' => 'handle_custom',
        'permission_callback' => 'check_permissions'
    ]);
});
```

## API Rate Limits

### WordPress.com
- 100 requests per minute (authenticated)
- 5 requests per second burst

### WooCommerce
- No hard limits, but respect server resources
- Batch operations recommended for bulk updates

### Self-Hosted
- Depends on server configuration
- Default plugin limit: 60/minute (configurable)

## Contributing

### Code Style
```bash
# Format with black
black mcp-server/

# Lint with ruff
ruff check mcp-server/

# Type checking
mypy mcp-server/
```

### Pull Request Process
1. Fork repository
2. Create feature branch
3. Add tests for new features
4. Ensure CI passes
5. Update documentation
6. Submit PR with description

## License

MIT License - See [LICENSE](LICENSE) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/Breuk-AI/wordpress-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Breuk-AI/wordpress-mcp/discussions)
- **Security**: [SECURITY.md](SECURITY.md)

---

**Technical questions?** Open a discussion. We love talking shop!