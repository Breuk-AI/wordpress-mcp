@echo off
echo ========================================
echo Double-checking GitHub Connection
echo ========================================
echo.

echo Fetching latest from GitHub...
git fetch origin
echo.

echo Checking if we're in sync...
git status
echo.

echo Showing last 3 commits on GitHub:
git log --oneline -3
echo.

echo Remote branches available:
git branch -r
echo.

echo ========================================
echo If no errors above, everything is perfect!
echo Repository: https://github.com/Breuk-AI/wordpress-mcp
echo ========================================
pause
