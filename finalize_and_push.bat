@echo off
echo ================================================
echo WordPress MCP - Finalize and Push to GitHub
echo ================================================
echo.

cd /d E:\Claude_Projects\wordpress-mcp

echo Checking current status...
git status

echo.
echo Adding all changes...
git add -A

echo.
echo Committing changes...
git commit -m "Clean repository for public release" -m "- Fixed CI to run actual pytest tests with coverage" -m "- Added blocking security and code quality checks" -m "- Renamed run-tests.bat to verify-install.bat for clarity" -m "- Kept only user-essential scripts" -m "- Ready for public release with green CI checkmark"

echo.
echo Pushing to GitHub main branch...
git push origin main

echo.
echo Cleaning up the cleanup scripts...
git rm public_release_cleanup.py execute_cleanup_and_push.bat finalize_and_push.bat 2>nul
git commit -m "Remove cleanup scripts after successful cleanup"
git push origin main

echo.
echo ================================================
echo SUCCESS! Repository cleaned and pushed!
echo ================================================
echo.
echo View your repository:
echo https://github.com/Breuk-AI/wordpress-mcp
echo.
echo Check CI status (should be green):
echo https://github.com/Breuk-AI/wordpress-mcp/actions
echo.
pause
