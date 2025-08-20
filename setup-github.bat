@echo off
REM WordPress MCP - GitHub Repository Setup Script for Windows
REM Your first public release! 🎉

echo ================================================
echo   WordPress MCP - GitHub Setup for First Release
echo ================================================
echo.

REM Check if git is initialized
if not exist .git (
    echo 📁 Initializing git repository...
    git init
    echo ✅ Git initialized
) else (
    echo ✅ Git already initialized
)

REM Set up git user (update with your details)
echo.
echo 📝 Setting up git user...
echo Please update these with your details if needed:
git config user.name "Breuk-AI"
git config user.email "breuk@breukandclaude.com"

REM Create initial branch
git branch -M main

REM Add all files
echo.
echo 📦 Adding all files to git...
git add .

REM Create the initial commit
echo.
echo 💫 Creating your first public release commit...
git commit -m "🎉 Initial public release - WordPress MCP v1.0.0" -m "" -m "A comprehensive MCP (Model Context Protocol) integration for WordPress and WooCommerce." -m "" -m "✨ Features:" -m "- Complete WordPress content management (posts, pages, media)" -m "- WooCommerce integration with auto-detection" -m "- Safe template editing with automatic backups" -m "- Secure authentication via Application Passwords" -m "- Rate limiting and CORS protection" -m "- Visual admin interface in WordPress" -m "- Backup manager with restore capability" -m "" -m "🔒 Security:" -m "- Environment-based configuration" -m "- Input sanitization and validation" -m "- Configurable rate limiting" -m "- Automatic backup cleanup" -m "" -m "📚 Documentation:" -m "- Comprehensive README with examples" -m "- Contributing guidelines" -m "- Migration guide for existing users" -m "- MIT License" -m "" -m "🚀 This is my first public release!" -m "Built with Claude's assistance over an incredible month of learning and creating." -m "" -m "#wordpress #mcp #automation #firstrelease"

echo ✅ Initial commit created!

REM Add GitHub remote
echo.
echo 🌐 Setting up GitHub remote...
echo.
echo 📋 Next steps:
echo 1. Go to https://github.com/new
echo 2. Create a new repository named: wordpress-mcp
echo 3. Make it PUBLIC (this is your first public release! 🎉)
echo 4. Add description: "Comprehensive WordPress and WooCommerce control via MCP"
echo 5. DON'T initialize with README (we already have one)
echo 6. Choose MIT license (or leave empty, we have LICENSE file)
echo.
echo After creating the repository on GitHub, run these commands:
echo.
echo git remote add origin https://github.com/Breuk-AI/wordpress-mcp.git
echo git push -u origin main
echo.
echo ================================================
echo   Congratulations on your first public release! 🎊
echo ================================================
echo.
pause
