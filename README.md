# WordPress MCP Server 🚀

[![CI Status](https://github.com/Breuk-AI/wordpress-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/Breuk-AI/wordpress-mcp/actions)
[![Version](https://img.shields.io/badge/version-1.0.1-blue.svg)](https://github.com/Breuk-AI/wordpress-mcp/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.org)

Comprehensive WordPress and WooCommerce control via Model Context Protocol (MCP). Manage posts, pages, media, templates, and products through natural language with Claude Desktop.

## ✨ Features

- 📝 **Complete WordPress Control** - Posts, pages, media, users
- 🛒 **WooCommerce Integration** - Products, orders, customers
- 📄 **Template Editing** - Direct theme file editing with backups
- 🔒 **Security First** - Application passwords, rate limiting, input sanitization
- ⚡ **Async Operations** - Fast, non-blocking API calls
- 🔄 **Bulk Operations** - Update multiple items efficiently

## 🚀 Quick Start

### Prerequisites

- WordPress 5.6+ with Application Passwords enabled
- Python 3.8+
- Claude Desktop

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Breuk-AI/wordpress-mcp.git
cd wordpress-mcp
```

2. **Install the WordPress plugin:**
   - Upload `wp-mcp-plugin` folder to `/wp-content/plugins/`
   - Activate "WordPress MCP Integration" in WordPress admin

3. **Configure the MCP server:**

   Use for easy 1-click installation and configuration
```dxt install https://github.com/Breuk-AI/wordpress-mcp``` 
  
   or
```bash
cd mcp-server
cp .env.example .env
# Edit .env with your WordPress credentials
```

4. **Add to Claude Desktop config:**
```json
{
  "wordpress": {
    "command": "python",
    "args": ["E:\\path\\to\\wordpress-mcp\\mcp-server\\server.py"],
    "env": {
      "WP_SITE_URL": "https://your-site.com",
      "WP_USERNAME": "your-username",
      "WP_APP_PASSWORD": "xxxx xxxx xxxx xxxx xxxx xxxx"
    }
  }
}
```

## 🛠️ Available Tools

### WordPress Tools (30+ operations)

- **Posts** - Create, read, update, delete, search posts
- **Pages** - Full page management
- **Media** - Upload and manage media library
- **Templates** - Edit theme files with automatic backups
- **Users** - User management and capabilities
- **System** - WordPress configuration and status

### WooCommerce Tools

- **Products** - Complete product management
- **Orders** - Order processing and updates
- **Customers** - Customer data management
- **Bulk Operations** - Update prices, stock, etc.

## 🔒 Security Features

- ✅ **Path Traversal Protection** - Validated file access
- ✅ **Authentication Security** - Hashed password storage
- ✅ **Rate Limiting** - Prevents API abuse
- ✅ **Input Sanitization** - Protects against injection
- ✅ **HTTPS Enforcement** - Secure connections required
- ✅ **File Extension Validation** - Only .php files editable

## 📋 Requirements

### WordPress
- WordPress 5.6 or higher
- PHP 7.4 or higher
- Application Passwords enabled
- SSL certificate (recommended)

### Python Dependencies
```bash
pip install -r mcp-server/requirements.txt
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Model Context Protocol](https://modelcontextprotocol.org)
- Powered by WordPress REST API
- Created with Claude AI assistance

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/Breuk-AI/wordpress-mcp/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Breuk-AI/wordpress-mcp/discussions)
- **Security:** See [SECURITY.md](SECURITY.md) for reporting vulnerabilities

## 🚦 Status

- ✅ **Production Ready** (v1.1.1)
- ✅ **Security Audited**
- ✅ **CI/CD Pipeline Active**
- ✅ **Documentation Complete**

---

**Made with ❤️ by Breuk & Claude**
