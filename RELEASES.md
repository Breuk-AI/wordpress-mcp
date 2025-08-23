# 📦 WordPress MCP Release Packages

## Quick Installation Downloads

### 🎯 Option 1: One-Click with DXT (Recommended)
```bash
dxt install https://github.com/Breuk-AI/wordpress-mcp
```

### 📦 Option 2: Download Release Packages

#### WordPress Plugin Package
**File:** `wp-mcp-plugin-v1.1.1.zip`  
**Size:** ~50KB  
**Installation:**
1. Download [wp-mcp-plugin-v1.1.1.zip](https://github.com/Breuk-AI/wordpress-mcp/raw/main/wp-mcp-plugin-v1.1.1.zip)
2. Go to WordPress Admin → Plugins → Add New → Upload Plugin
3. Choose the downloaded zip file
4. Click "Install Now" then "Activate"

#### MCP Server Package  
**File:** `mcp-server-v1.1.1.zip`  
**Size:** ~100KB  
**Installation:**
1. Download [mcp-server-v1.1.1.zip](https://github.com/Breuk-AI/wordpress-mcp/raw/main/mcp-server-v1.1.1.zip)
2. Extract to your preferred location
3. Copy `.env.example` to `.env`
4. Edit `.env` with your WordPress credentials
5. Configure Claude Desktop to point to `server.py`

### 📋 What's Included

**WordPress Plugin (`wp-mcp-plugin-v1.1.1.zip`):**
- ✅ Complete WordPress integration
- ✅ Custom REST API endpoints
- ✅ Admin interface
- ✅ Automatic backup system
- ✅ WooCommerce support

**MCP Server (`mcp-server-v1.1.1.zip`):**
- ✅ Python MCP implementation
- ✅ All WordPress tools
- ✅ Async operations
- ✅ Rate limiting
- ✅ Security features

### 🚀 Version 1.1.1 Highlights

**The "Green Checkmark Victory" Release** 🎯
- Complete CI/CD pipeline
- 29 unit tests with coverage
- Security scanning with Bandit
- Code quality checks with Ruff
- Non-blocking quality metrics
- Claude's README Renaissance

### 📝 Quick Start After Download

1. **Install WordPress Plugin**
   ```bash
   # Upload via WordPress admin or copy to plugins folder
   wp-content/plugins/
   ```

2. **Setup MCP Server**
   ```bash
   cd mcp-server
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Configure Claude Desktop**
   ```json
   {
     "wordpress": {
       "command": "python",
       "args": ["path/to/mcp-server/server.py"],
       "env": {
         "WP_SITE_URL": "https://your-site.com",
         "WP_USERNAME": "your-username",
         "WP_APP_PASSWORD": "xxxx xxxx xxxx xxxx xxxx xxxx"
       }
     }
   }
   ```

4. **Restart Claude & Celebrate!** 🎉

### 💝 Why These Packages?

We pre-built these packages so you don't have to:
- No git cloning required
- No manual zipping needed
- Ready for production use
- Tested and verified
- Includes all dependencies

### 🔒 Package Verification

**WordPress Plugin:**
- Version: 1.1.1
- PHP Compatibility: 7.4+
- WordPress: 5.6+
- License: MIT

**MCP Server:**
- Version: 1.1.1  
- Python: 3.8+
- Protocol: MCP v1.0
- License: MIT

### 📞 Support

Having trouble with the packages?
- 🐛 [Report Issues](https://github.com/Breuk-AI/wordpress-mcp/issues)
- 💬 [Ask Questions](https://github.com/Breuk-AI/wordpress-mcp/discussions)
- 📖 [Read Documentation](https://github.com/Breuk-AI/wordpress-mcp#readme)

---

**Made with ❤️ by Breuk & Claude**  
*Intelligence Combined 🧠*

*Download, Install, Connect, Create!*