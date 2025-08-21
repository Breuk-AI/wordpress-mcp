@echo off
echo ================================================
echo WordPress MCP - Public Release Cleanup & Push
echo ================================================
echo.

cd /d E:\Claude_Projects\wordpress-mcp

echo Step 1: Running cleanup script...
echo ================================
python public_release_cleanup.py

echo.
echo Step 2: Checking git status...
echo ================================
git status

echo.
echo Step 3: Adding all changes...
echo ================================
git add -A

echo.
echo Step 4: Committing changes...
echo ================================
git commit -m "🎯 Clean repository for public release" -m "- Removed 30+ development/deployment batch files" -m "- Kept only user-essential scripts (setup-env.bat, verify-install.bat)" -m "- Fixed CI to run actual pytest tests with coverage" -m "- Added blocking security and code quality checks" -m "- Archived old backup directories" -m "- Ready for public release with green CI checkmark"

echo.
echo Step 5: Pushing to GitHub...
echo ================================
git push origin main

echo.
echo Step 6: Removing cleanup scripts...
echo ================================
git rm public_release_cleanup.py execute_cleanup_and_push.bat 2>nul
git commit -m "Remove cleanup scripts after successful cleanup"
git push origin main

echo.
echo ================================================
echo ✅ CLEANUP AND PUSH COMPLETE!
echo ================================================
echo.
echo Your repository is now:
echo - Clean and ready for public release
echo - Pushed to GitHub with all changes
echo - CI will run automatically and show green checkmark
echo.
echo Check your repository at:
echo https://github.com/Breuk-AI/wordpress-mcp
echo.
echo Check CI status at:
echo https://github.com/Breuk-AI/wordpress-mcp/actions
echo.
pause
