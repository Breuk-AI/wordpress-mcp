@echo off
echo ================================================================================
echo WordPress MCP - Deployment Status Check
echo ================================================================================
echo.

echo Checking deployment readiness...
echo.

set READY=1

echo [✓] Checking for required files...
if not exist mcp-server\server.py (
    echo   ❌ Missing: mcp-server\server.py
    set READY=0
) else (
    echo   ✅ Found: mcp-server\server.py
)

if not exist wp-mcp-plugin\wp-mcp-plugin.php (
    echo   ❌ Missing: wp-mcp-plugin\wp-mcp-plugin.php
    set READY=0
) else (
    echo   ✅ Found: wp-mcp-plugin\wp-mcp-plugin.php
)

if not exist tests\test_security.py (
    echo   ❌ Missing: tests\test_security.py
    set READY=0
) else (
    echo   ✅ Found: tests\test_security.py
)

echo.
echo [✓] Checking Python dependencies...
python -c "import cryptography" 2>nul
if %errorlevel% neq 0 (
    echo   ❌ Missing: cryptography module
    echo   Run: pip install cryptography
    set READY=0
) else (
    echo   ✅ cryptography installed
)

python -c "import aiohttp" 2>nul
if %errorlevel% neq 0 (
    echo   ❌ Missing: aiohttp module
    echo   Run: pip install aiohttp
    set READY=0
) else (
    echo   ✅ aiohttp installed
)

echo.
echo [✓] Checking Git status...
git status --porcelain > temp_git_status.txt
for %%A in (temp_git_status.txt) do (
    if %%~zA==0 (
        echo   ✅ No uncommitted changes
    ) else (
        echo   ⚠️  Uncommitted changes detected
    )
)
del temp_git_status.txt

echo.
echo [✓] Checking GitHub remote...
git remote -v | find "github.com" >nul
if %errorlevel% neq 0 (
    echo   ❌ No GitHub remote configured
    set READY=0
) else (
    echo   ✅ GitHub remote configured
)

echo.
echo ================================================================================
if %READY%==1 (
    echo ✅ READY FOR DEPLOYMENT
    echo.
    echo Run ONE_CLICK_DEPLOY.bat to deploy everything automatically!
) else (
    echo ❌ NOT READY - Fix the issues above first
)
echo ================================================================================
echo.
pause
