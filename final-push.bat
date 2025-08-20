@echo off
echo ========================================
echo Final Push to GitHub as Breuk-AI
echo ========================================
echo.

echo Current status:
git status
echo.

echo Pushing to GitHub...
git push origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ SUCCESS! Your repository is now live at:
    echo 🔗 https://github.com/Breuk-AI/wordpress-mcp
    echo.
    echo Next steps:
    echo 1. Visit the URL above to confirm it's live
    echo 2. Submit to Anthropic MCP directory
    echo 3. Post on Product Hunt
    echo 4. Announce on Discord
) else (
    echo.
    echo ❌ Error pushing to GitHub.
    echo.
    echo If authentication failed, create a Personal Access Token:
    echo 1. Go to: https://github.com/settings/tokens
    echo 2. Generate new token (classic^)
    echo 3. Select 'repo' scope
    echo 4. Use the token as your password
)

echo.
pause
