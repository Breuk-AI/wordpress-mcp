#!/bin/bash
# WordPress MCP - GitHub Repository Setup Script
# Your first public release! 🎉

echo "================================================"
echo "  WordPress MCP - GitHub Setup for First Release"
echo "================================================"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📁 Initializing git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi

# Set up git user (update with your details)
echo ""
echo "📝 Setting up git user..."
echo "Please update these with your details if needed:"
git config user.name "Breuk-AI"
git config user.email "breuk@breukandclaude.com"

# Create initial branch
git branch -M main

# Add all files
echo ""
echo "📦 Adding all files to git..."
git add .

# Create the initial commit
echo ""
echo "💫 Creating your first public release commit..."
git commit -m "🎉 Initial public release - WordPress MCP v1.0.0

A comprehensive MCP (Model Context Protocol) integration for WordPress and WooCommerce.

✨ Features:
- Complete WordPress content management (posts, pages, media)
- WooCommerce integration with auto-detection
- Safe template editing with automatic backups
- Secure authentication via Application Passwords
- Rate limiting and CORS protection
- Visual admin interface in WordPress
- Backup manager with restore capability

🔒 Security:
- Environment-based configuration
- Input sanitization and validation
- Configurable rate limiting
- Automatic backup cleanup

📚 Documentation:
- Comprehensive README with examples
- Contributing guidelines
- Migration guide for existing users
- MIT License

🚀 This is my first public release!
Built with Claude's assistance over an incredible month of learning and creating.

#wordpress #mcp #automation #firstrelease"

echo "✅ Initial commit created!"

# Add GitHub remote (you'll need to create the repo on GitHub first)
echo ""
echo "🌐 Setting up GitHub remote..."
echo ""
echo "📋 Next steps:"
echo "1. Go to https://github.com/new"
echo "2. Create a new repository named: wordpress-mcp"
echo "3. Make it PUBLIC (this is your first public release! 🎉)"
echo "4. Add description: 'Comprehensive WordPress and WooCommerce control via MCP (Model Context Protocol)'"
echo "5. DON'T initialize with README (we already have one)"
echo "6. Choose MIT license (or leave empty, we have LICENSE file)"
echo ""
echo "After creating the repository on GitHub, run these commands:"
echo ""
echo "git remote add origin https://github.com/Breuk-AI/wordpress-mcp.git"
echo "git push -u origin main"
echo ""
echo "================================================"
echo "  Congratulations on your first public release! 🎊"
echo "================================================"
