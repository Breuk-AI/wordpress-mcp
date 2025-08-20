@echo off
echo ========================================
echo Checking GitHub Connection Status
echo ========================================
echo.

echo 1. Current Remote URL:
git remote -v
echo.

echo 2. Testing connection to GitHub:
git ls-remote --heads origin
echo.

echo 3. Current branch:
git branch --show-current
echo.

echo 4. Last commit:
git log --oneline -1
echo.

echo ========================================
echo If you see branches and commits above,
echo everything is working correctly!
echo ========================================
echo.
pause
