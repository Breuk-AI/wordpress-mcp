# WordPress MCP (Model Context Protocol) Integration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![WordPress](https://img.shields.io/badge/WordPress-5.6%2B-blue)](https://wordpress.org)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green)](https://python.org)

A powerful MCP server that provides comprehensive control over WordPress sites through Claude Desktop or any MCP-compatible client. Manage posts, pages, media, WooCommerce products, and even edit theme templates - all through natural language commands.

## 🌟 Features

### Core WordPress Management
- **Posts & Pages**: Create, read, update, delete, and search
- **Media Library**: List, upload, and manage media files
- **Templates**: Edit theme files with automatic backups
- **System Info**: Monitor WordPress and server status

### WooCommerce Integration (Auto-detected)
- Product management (CRUD operations)
- Order processing and status updates
- Customer management
- Bulk price and stock updates

### Security & Safety
- Application Password authentication (WordPress 5.6+)
- Rate limiting to prevent API abuse
- Automatic backups before template edits
- Configurable CORS policies
- Input sanitization and validation

## 📋 Requirements

### WordPress Site
- WordPress 5.6 or higher
- PHP 7.4 or higher
- Application Passwords enabled
- Administrator account access

### MCP Server
- Python 3.8 or higher
- Claude Desktop or MCP-compatible client
- Internet connection to your WordPress site

## 🚀 Quick Start

### Step 1: Install the WordPress Plugin

1. Download the `wp-mcp-plugin` folder
2. Upload to `/wp-content/plugins/` on your WordPress site
3. Activate "WordPress MCP Integration" from the Plugins page
4. Navigate to MCP Integration in your WordPress admin

### Step 2: Create Application Password

1. Go to **Users → Your Profile** in WordPress admin
2. Scroll to "Application Passwords" section
3. Enter "MCP Server" as the application name
4. Click "Add New Application Password"
5. **Copy the password immediately** (it won't be shown again!)

### Step 3: Configure MCP Server

1. Clone this repository:
```bash
git clone https://github.com/Breuk-AI/wordpress-mcp.git
cd wordpress-mcp/mcp-server
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Copy and configure environment:
```bash
cp .env.example .env
```

4. Edit `.env` with your details:
```env
WP_SITE_URL=https://your-site.com
WP_USERNAME=your_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

### Step 4: Add to Claude Desktop

Edit your Claude Desktop configuration:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

Add to the `mcpServers` section:
```json
{
  "wordpress": {
    "command": "python",
    "args": ["/path/to/wordpress-mcp/mcp-server/server.py"],
    "env": {
      "PYTHONUNBUFFERED": "1"
    }
  }
}
```

### Step 5: Restart Claude Desktop

The WordPress tools should now appear in Claude!

## 🛠️ Available Tools

### Post Management
- `wp_get_posts` - List posts with filters
- `wp_create_post` - Create new post
- `wp_update_post` - Update existing post
- `wp_delete_post` - Delete post
- `wp_search_posts` - Search posts by keyword

### Page Management
- `wp_get_pages` - List pages
- `wp_create_page` - Create new page
- `wp_update_page` - Update page
- `wp_delete_page` - Delete page

### Media Management
- `wp_get_media` - List media library items
- `wp_upload_media` - Upload new media
- `wp_delete_media` - Delete media item

### Template Management
- `wp_list_templates` - List theme templates
- `wp_read_template` - Read template content
- `wp_update_template` - Update template (with backup)

### WooCommerce (if installed)
- `wc_get_products` - List products
- `wc_create_product` - Create product
- `wc_update_product` - Update product
- `wc_get_orders` - List orders
- `wc_update_order` - Update order status
- `wc_bulk_update_prices` - Bulk price updates
- `wc_bulk_update_stock` - Bulk stock updates

### System Tools
- `wp_get_system_info` - Get WordPress/server info
- `wp_get_plugins` - List installed plugins
- `wp_get_themes` - List installed themes

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `mcp-server` directory:

```env
# Required
WP_SITE_URL=https://your-site.com
WP_USERNAME=your_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx

# Optional
MCP_DEBUG=false                    # Enable debug logging
RATE_LIMIT=60                      # Requests per minute
API_TIMEOUT=30                     # Seconds
BACKUP_RETENTION_DAYS=7            # Days to keep backups
CORS_ALLOWED_ORIGINS=              # Comma-separated origins
```

### WordPress Plugin Settings

Access via **MCP Integration → Settings** in WordPress admin:

- **Rate Limit**: API requests per minute per user
- **Backup Retention**: Days to keep template backups
- **CORS Origins**: Allowed origins for cross-origin requests
- **Debug Mode**: Enable detailed logging

## 🔒 Security Considerations

1. **Application Passwords**: Use unique passwords for each integration
2. **User Permissions**: Use an account with appropriate permissions
3. **CORS Policy**: Configure allowed origins carefully
4. **Rate Limiting**: Adjust based on your server capacity
5. **Backups**: Regularly clean old backups to save space
6. **HTTPS**: Always use HTTPS for production sites

## 🐛 Troubleshooting

### "Connection failed"
- Verify site URL (no trailing slash)
- Check username and application password
- Ensure Application Passwords are enabled
- Check if user has admin permissions

### "401 Unauthorized"
- Application password might be incorrect
- User might lack required permissions
- Check WordPress admin → MCP Integration page

### Tools not showing in Claude
- Restart Claude Desktop
- Verify configuration path is correct
- Check Claude's developer console for errors
- Test connection with `python server.py`

### Rate limit errors
- Increase rate limit in settings
- Reduce request frequency
- Check for infinite loops in automations

## 📝 Example Usage in Claude

Once configured, you can use natural language commands:

- "List my recent blog posts"
- "Create a new draft post about AI technology"
- "Update the homepage template to add a newsletter signup"
- "Show me all products that are out of stock"
- "Bulk update prices for products in the 'Electronics' category"
- "Get system information about my WordPress site"

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for use with [Claude Desktop](https://claude.ai) by Anthropic
- Uses the [MCP (Model Context Protocol)](https://github.com/anthropics/mcp)
- WordPress REST API and Application Passwords

## 🔗 Links

- [Documentation](https://github.com/Breuk-AI/wordpress-mcp/wiki)
- [Issue Tracker](https://github.com/Breuk-AI/wordpress-mcp/issues)
- [MCP Protocol Spec](https://github.com/anthropics/mcp)
- [WordPress REST API](https://developer.wordpress.org/rest-api/)

## ⚠️ Disclaimer

This tool provides powerful access to your WordPress site. Always:
- Test in a staging environment first
- Keep regular backups of your site
- Use appropriate user permissions
- Monitor API usage and logs

---

Made with ❤️ by Breuk & Claude
