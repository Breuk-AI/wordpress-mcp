# WordPress MCP Server

[![CI](https://github.com/Breuk-AI/wordpress-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/Breuk-AI/wordpress-mcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that provides comprehensive WordPress and WooCommerce control through natural language commands.

## Features

- 📝 **Content Management** - Create, read, update, and delete posts and pages
- 🖼️ **Media Library** - Manage images and media files
- 🎨 **Template Editing** - Edit theme templates with automatic backups
- 🛒 **WooCommerce** - Full product and order management (if WooCommerce is active)
- 👥 **User Management** - Manage WordPress users and permissions
- 🔍 **System Monitoring** - Get WordPress system information and status

## Requirements

- WordPress 5.6 or higher
- PHP 7.4 or higher  
- Python 3.8 or higher
- WordPress Application Passwords enabled

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Breuk-AI/wordpress-mcp.git
cd wordpress-mcp
```

### 2. Install WordPress Plugin
1. Copy the `wp-mcp-plugin` folder to your WordPress `wp-content/plugins/` directory
2. Activate "WordPress MCP Integration" in WordPress admin

### 3. Configure MCP Server
```bash
# Run setup script
python setup.py

# Or manually:
cp .env.example mcp-server/.env
# Edit mcp-server/.env with your WordPress credentials
```

### 4. Generate WordPress Application Password
1. Go to WordPress Admin → Users → Your Profile
2. Scroll to "Application Passwords"
3. Enter "MCP Server" as the name
4. Click "Add New Application Password"
5. Copy the password to your `.env` file

### 5. Install Dependencies & Test
```bash
cd mcp-server
pip install -r requirements.txt
python test_connection.py
```

### 6. Run the Server
```bash
python server.py
```

## Configuration

Edit `mcp-server/.env` with your settings:

```env
# WordPress Connection
WP_SITE_URL=https://your-site.com
WP_USERNAME=admin
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx

# Optional Settings
API_TIMEOUT=30
RATE_LIMIT=60
MCP_DEBUG=false
```

## Available Tools

The MCP server provides these tools:

### Posts & Pages
- `wp_get_posts` - List posts with filters
- `wp_create_post` - Create new post
- `wp_update_post` - Update existing post
- `wp_delete_post` - Delete post
- `wp_search_posts` - Search posts

### Media
- `wp_get_media` - List media items
- `wp_upload_media` - Upload new media
- `wp_delete_media` - Delete media

### Templates
- `wp_get_templates` - List theme templates
- `wp_read_template` - Read template content
- `wp_update_template` - Update template (with backup)

### WooCommerce (if active)
- `wp_get_products` - List products
- `wp_create_product` - Create product
- `wp_update_product` - Update product
- `wp_get_orders` - List orders

## Security Features

- ✅ Secure authentication via Application Passwords
- ✅ Rate limiting to prevent abuse
- ✅ Permission-based access control
- ✅ Automatic backup before template edits
- ✅ Input validation and sanitization
- ✅ CORS configuration support

## Testing

Run the test suite:
```bash
pytest tests/
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://github.com/Breuk-AI/wordpress-mcp/wiki)
- 🐛 [Issue Tracker](https://github.com/Breuk-AI/wordpress-mcp/issues)
- 💬 [Discussions](https://github.com/Breuk-AI/wordpress-mcp/discussions)

## Acknowledgments

Built with the Model Context Protocol (MCP) by Anthropic.
