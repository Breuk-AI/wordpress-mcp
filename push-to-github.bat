@echo off
echo Fixing branch name and pushing to GitHub...
echo.

REM Rename master to main
git branch -M main

REM Add remote if not already added
git remote remove origin 2>nul
git remote add origin https://github.com/BREUK24/wordpress-mcp.git

REM Push to GitHub
echo.
echo 🚀 Pushing your first open source project to GitHub...
echo.
git push -u origin main

echo.
echo ✅ Success! Your code is now live on GitHub!
echo.
echo 🎉 Visit your repository: https://github.com/BREUK24/wordpress-mcp
echo.
pause
