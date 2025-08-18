# Migration Guide: v0.9 to v1.0

This guide helps existing users migrate from the private version to the public release.

## ⚠️ Breaking Changes

### Configuration Changes

The configuration system has completely changed from `config.json` to environment variables.

#### Old Method (config.json)
```json
{
    "site_url": "https://monopolygowin.com",
    "username": "your_username",
    "app_password": "xxxx xxxx xxxx xxxx xxxx xxxx"
}
```

#### New Method (.env file)
```env
WP_SITE_URL=https://your-site.com
WP_USERNAME=your_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

### Security Changes

1. **CORS Policy**: The wildcard CORS (`*`) has been removed. You must now explicitly configure allowed origins.

2. **Rate Limiting**: Now enforced by default (60 requests/minute). Configure in WordPress admin or via environment variable.

## 📋 Migration Steps

### Step 1: Backup Your Configuration

```bash
cp mcp-server/config.json mcp-server/config.json.backup
```

### Step 2: Update the WordPress Plugin

1. Deactivate the old plugin in WordPress admin
2. Delete the old plugin files
3. Upload the new `wp-mcp-plugin` folder
4. Activate the new plugin
5. Configure settings in **MCP Integration → Settings**

### Step 3: Update the MCP Server

1. Pull the latest code:
```bash
git pull origin main
```

2. Create your `.env` file:
```bash
cd mcp-server
cp .env.example .env
```

3. Edit `.env` with your configuration from the old `config.json`

4. Update Python dependencies:
```bash
pip install -r requirements.txt
```

### Step 4: Configure New Settings

In WordPress admin, go to **MCP Integration → Settings** and configure:

- Rate Limit (default: 60 requests/minute)
- Backup Retention (default: 7 days)
- CORS Origins (if needed)
- Debug Mode (for troubleshooting)

### Step 5: Update Claude Desktop Configuration

No changes needed to your Claude Desktop configuration unless you want to use environment variables there too.

### Step 6: Test the Connection

```bash
cd mcp-server
python server.py
```

You should see:
```
Starting WordPress MCP Server...
Connected to WordPress site: https://your-site.com
WordPress MCP Server initialized successfully
```

## 🔄 Rollback Instructions

If you need to rollback:

1. Restore your old plugin files
2. Rename `config.json.backup` back to `config.json`
3. Checkout the previous version:
```bash
git checkout v0.9.0
```

## 📝 New Features

After migrating, you'll have access to:

- **Admin Interface**: Full settings panel in WordPress admin
- **Backup Manager**: Visual backup management and restoration
- **Rate Limiting**: Protect your API from abuse
- **Better Security**: Proper CORS handling and input validation
- **Environment Variables**: More secure configuration
- **Auto-cleanup**: Old backups are automatically removed

## 🆘 Troubleshooting

### "Configuration not found"
- Ensure `.env` file exists and has correct values
- Check file permissions

### "401 Unauthorized"
- Regenerate your application password
- Update the `.env` file with the new password

### "Rate limit exceeded"
- Increase rate limit in WordPress settings
- Wait 60 seconds and try again

### Tools not appearing in Claude
- Restart Claude Desktop after updating
- Check logs with `MCP_DEBUG=true`

## 📞 Support

- [GitHub Issues](https://github.com/yourusername/wordpress-mcp/issues)
- [Documentation](https://github.com/yourusername/wordpress-mcp/wiki)
- [Discussions](https://github.com/yourusername/wordpress-mcp/discussions)

## 🎉 Thank You!

Thank you for being an early adopter! Your feedback has been invaluable in making this tool better for everyone.
