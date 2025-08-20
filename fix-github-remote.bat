@echo off
echo Fixing GitHub remote URL to use Breuk-AI...
echo.

REM Remove old remote
git remote remove origin

REM Add new remote with correct username
git remote add origin https://github.com/Breuk-AI/wordpress-mcp.git

REM Verify the change
echo.
echo New remote URL:
git remote -v

echo.
echo Now pushing to the correct repository...
git push -u origin main

echo.
echo ✅ Done! Your repository should now be at:
echo https://github.com/Breuk-AI/wordpress-mcp
echo.
pause
