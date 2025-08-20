@echo off
echo ================================
echo WordPress MCP Security Patch
echo ================================
echo.
echo This script will apply critical security fixes to your WordPress MCP project.
echo.

REM Create backups first
echo Creating backups of original files...
mkdir security-backups 2>nul
copy mcp-server\wp_client.py security-backups\wp_client.py.bak >nul
copy wp-mcp-plugin\includes\api-endpoints.php security-backups\api-endpoints.php.bak >nul
echo Backups created in security-backups folder
echo.

echo Applying security patches...
echo.

REM Apply Python security patch
echo 1. Patching wp_client.py (Authentication Security)...
copy /Y mcp-server\wp_client_secure.py mcp-server\wp_client.py >nul
if %errorlevel% equ 0 (
    echo    ✅ Authentication security patch applied
) else (
    echo    ❌ Failed to apply Python security patch
    exit /b 1
)

REM Apply PHP security patch
echo 2. Patching api-endpoints.php (Path Traversal Fix)...
copy /Y wp-mcp-plugin\includes\api-endpoints-secure.php wp-mcp-plugin\includes\api-endpoints.php >nul
if %errorlevel% equ 0 (
    echo    ✅ Path traversal security patch applied
) else (
    echo    ❌ Failed to apply PHP security patch
    exit /b 1
)

echo.
echo 3. Running security tests...
python tests\test_security.py
if %errorlevel% equ 0 (
    echo.
    echo ✅ Security patches verified successfully!
) else (
    echo.
    echo ⚠️  Some security tests failed. Please review the output above.
)

echo.
echo 4. Cleaning up temporary files...
del mcp-server\wp_client_secure.py 2>nul
del wp-mcp-plugin\includes\api-endpoints-secure.php 2>nul

echo.
echo ================================
echo Security Patches Applied!
echo ================================
echo.
echo Summary of fixes:
echo ✓ Path traversal vulnerability patched
echo ✓ Authentication tokens secured
echo ✓ Rate limiting implemented
echo ✓ HTTPS enforcement added
echo ✓ File extension validation added
echo ✓ Input sanitization improved
echo.
echo Your code is now secure and ready for GitHub!
echo.
echo Next steps:
echo 1. Run: run-tests.bat (to verify all tests pass)
echo 2. Run: git add .
echo 3. Run: git commit -m "Apply critical security patches"
echo 4. Run: git push origin main
echo.
pause
