# 🚀 WordPress MCP - 60 Second Quick Start

> *"The fastest path from install to awesome"*

## 🎯 Choose Your Adventure

### 🌟 Path 1: The One-Click Wonder (5 seconds)

```bash
dxt install https://github.com/Breuk-AI/wordpress-mcp
```

**Done.** No, seriously, that's it. Go talk to Claude about your WordPress site now.

---

### 🛠️ Path 2: The Manual Installation (60 seconds)

#### 1️⃣ Get The Code (10 seconds)
```bash
git clone https://github.com/Breuk-AI/wordpress-mcp.git
cd wordpress-mcp
```

#### 2️⃣ Install WordPress Plugin (20 seconds)
- Drag `wp-mcp-plugin` folder to your WordPress `/wp-content/plugins/`
- Hit Activate in WordPress admin
- ✅ WordPress side done!

#### 3️⃣ Setup Python Server (15 seconds)
```bash
cd mcp-server
cp .env.example .env
nano .env  # Add your WordPress URL, username, and app password
```

#### 4️⃣ Configure Claude Desktop (10 seconds)
Add to your `claude_desktop_config.json`:
```json
{
  "wordpress": {
    "command": "python",
    "args": ["path/to/wordpress-mcp/mcp-server/server.py"],
    "env": {
      "WP_SITE_URL": "https://your-site.com",
      "WP_USERNAME": "admin",
      "WP_APP_PASSWORD": "xxxx xxxx xxxx xxxx xxxx xxxx"
    }
  }
}
```

#### 5️⃣ Restart Claude & Celebrate (5 seconds)
- Restart Claude Desktop
- Open new chat
- Say: "Show me my WordPress posts"
- 🎉 **BOOM! You're connected!**

---

## 🎭 First Commands to Try

```claude
"Show me my recent posts"
"Create a draft post about AI and creativity"  
"Update all product prices - increase by 10%"
"Fix the typo in my homepage"
"Show me orders from this week"
"Upload this image to my media library"
```

## 🆘 Trouble?

**Claude can't see WordPress tools?**
- Restart Claude Desktop (really, it helps)
- Start a NEW conversation (important!)

**Getting auth errors?**
- Application Password format: `xxxx xxxx xxxx xxxx xxxx xxxx`
- Get it from: WordPress → Users → Your Profile → Application Passwords

**Something else?**
- Check our [Issues](https://github.com/Breuk-AI/wordpress-mcp/issues)
- We respond fast and we actually care!

---

<div align="center">

### You're 60 seconds away from WordPress superpowers! 🚀

**Made with ❤️ by Breuk & Claude**

</div>