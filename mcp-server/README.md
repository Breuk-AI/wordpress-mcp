# WordPress MCP Server 🚀

> *The Python heart that makes the magic happen*

Control your WordPress site through natural language with Claude Desktop (or any MCP-compatible AI)!

## 🎯 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure**: Copy `.env.example` to `.env` and add your credentials:
   ```env
   WP_SITE_URL=https://your-site.com
   WP_USERNAME=your_username  
   WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
   ```

3. **Test connection**:
   ```bash
   python test_connection.py
   ```

4. **You're ready!** Claude Desktop will run this automatically.

## 🔑 Getting Your Application Password

1. WordPress Admin → Users → Your Profile
2. Find "Application Passwords" section
3. Name it "WordPress MCP" (or anything you like!)
4. Click "Add New Application Password"
5. Copy the password (spaces included!)
6. Paste into your `.env` file

## 🛠️ Available Tools

### Content Management
- **Posts & Pages** - Create, update, delete, search
- **Media Library** - Upload and manage files
- **Categories & Tags** - Full taxonomy control
- **Custom Post Types** - Supported automatically

### WooCommerce Superpowers
- **Products** - Complete product management
- **Orders** - Process and track orders
- **Customers** - Customer data at your fingertips
- **Bulk Operations** - Update 1000 products in seconds

### Developer Tools
- **Template Editing** - With automatic backups!
- **System Info** - Monitor your WordPress health
- **Plugin & Theme Management** - List and check status

## 💡 Architecture

The server is beautifully modular:
```
tools/
├── posts.py       # Content management
├── woocommerce.py # E-commerce operations  
├── templates.py   # Theme file editing
├── media.py       # Media library
└── system.py      # WordPress internals
```

## 🎆 The Story

Built because existing solutions had 2-minute delays and we said "Why NOT build our own?" 

27 days later, here we are with something that:
- Works instantly (no delays!)
- Handles complex operations gracefully
- Has been in production since day one
- Makes us smile every time we use it

## 🔒 Security First

- Application Passwords (never store real passwords!)
- Rate limiting (60 requests/minute default)
- Automatic backups before file edits
- Permission checking on every operation
- Environment-based configuration

## 🌈 Troubleshooting

**Connection Issues?**
- Remove trailing slashes from URLs
- Check Application Password format
- Verify admin privileges

**Tools not appearing?**
- Restart Claude Desktop
- Start a NEW conversation
- Check the logs for clues

## 🤝 Contributing

Want to add features? We love "Why NOT?" thinking!

1. Create your tool in `tools/`
2. Add to the server's tool registry
3. Test with `test_connection.py`
4. Share your creation!

---

**Made with ❤️ by Breuk & Claude**

*Intelligence Combined*

*That's our brand right there!*
