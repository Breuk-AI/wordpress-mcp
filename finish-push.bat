@echo off
echo ================================
echo Finishing the Push
echo ================================
echo.

echo Current status:
git status --short
echo.

echo Creating commit...
git commit -m "Security Update v1.0.1 + Test Suite" -m "Applied critical security patches and comprehensive testing"

if %errorlevel% neq 0 (
    echo.
    echo No changes to commit or commit failed.
    echo Trying to push existing commits...
)

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo ================================
echo Done! Check the result above.
echo ================================
echo.
echo Visit: https://github.com/Breuk-AI/wordpress-mcp/actions
echo.
pause
