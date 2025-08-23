@echo off
REM ================================================================
REM WordPress MCP - Quick Environment Setup Helper
REM ================================================================
REM This script helps you create your .env configuration file
REM from the template and guides you through the setup process.
REM Part of WordPress MCP - Control WordPress with AI Assistants!
REM Made with ❤️ by Breuk & Claude
REM ================================================================

echo ================================
echo WordPress MCP - Environment Setup
echo ================================
echo.

if exist mcp-server\.env (
    echo .env file already exists in mcp-server/
    echo.
    choice /C YN /M "Do you want to overwrite it with the template"
    if errorlevel 2 goto :skip_env
)

echo Creating .env file from template...
copy .env.example mcp-server\.env >nul
echo ✓ Created mcp-server\.env

:skip_env
echo.
echo ================================
echo Next Steps:
echo ================================
echo.
echo 1. Edit mcp-server\.env with your WordPress credentials
echo 2. Generate an Application Password in WordPress:
echo    - Go to Users → Your Profile  
echo    - Find "Application Passwords" section
echo    - Create new password named "MCP Server"
echo    - Copy the password to your .env file
echo.
echo 3. Test your connection:
echo    cd mcp-server
echo    python test_connection.py
echo.
echo ================================
pause
