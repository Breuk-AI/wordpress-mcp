# WordPress MCP Server

Control your WordPress site completely through Claude Desktop!

## Quick Start

1. **Run setup**:
   ```bash
   setup.bat
   ```
   Or manually:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure**: Edit `config.json` with your WordPress credentials:
   ```json
   {
       "site_url": "https://monopolygowin.com",
       "username": "your_username",
       "app_password": "xxxx xxxx xxxx xxxx xxxx xxxx"
   }
   ```

3. **Test connection**:
   ```bash
   python test_connection.py
   ```

4. **Run server** (after installing MCP library):
   ```bash
   python server_mcp.py
   ```

## Getting Application Password

1. Log into WordPress admin
2. Go to Users → Your Profile
3. Scroll to "Application Passwords"
4. Enter "MCP Server" as name
5. Click "Add New Application Password"
6. Copy the generated password (spaces are OK)

## Available Tools

### Posts & Pages
- `wp_get_posts` - List posts
- `wp_create_post` - Create post
- `wp_update_post` - Update post
- `wp_delete_post` - Delete post
- `wp_search_posts` - Search posts
- Similar tools for pages

### WooCommerce
- `wc_get_products` - List products
- `wc_create_product` - Create product
- `wc_update_product` - Update product
- `wc_bulk_update_prices` - Bulk price updates
- `wc_bulk_update_stock` - Bulk stock updates
- Order and customer management

### Templates
- `wp_list_templates` - List theme files
- `wp_read_template` - Read template
- `wp_update_template` - Edit template (with backup)

### System
- `wp_get_system_info` - System information
- `wp_get_plugins` - List plugins
- `wp_get_themes` - List themes

## Troubleshooting

### MCP library not found
The MCP protocol library needs to be installed. Check the latest installation method for your system.

### Connection failed
- Check site URL (include https://)
- Verify username is correct
- Check Application Password
- Ensure user has admin privileges

### Tools not showing in Claude
- Restart Claude Desktop after adding to config
- Check Claude Desktop logs for errors

## For Developers

The server is modular - each tool category is in `tools/`:
- `posts.py` - Post management
- `pages.py` - Page management
- `media.py` - Media library
- `woocommerce.py` - WooCommerce operations
- `templates.py` - Theme editing
- `system.py` - System information

Add new tools by:
1. Creating new methods in appropriate module
2. Adding to the tools dict
3. Defining the Tool schema

## Security

- Application Passwords are secure and revocable
- Each password is tracked in WordPress
- Template edits create automatic backups
- User permissions are enforced
