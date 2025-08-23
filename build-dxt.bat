@echo off
REM ================================================================
REM WordPress MCP - DXT Package Builder
REM ================================================================
REM Creates a .dxt file for submission to Anthropic's Desktop Extensions
REM This packages everything needed for one-click Claude Desktop installation
REM Made with ❤️ by Breuk & Claude
REM ================================================================

echo =====================================
echo 📦 Building WordPress MCP DXT Package
echo =====================================
echo.

set VERSION=1.1.1
set OUTPUT_NAME=wordpress-mcp-v%VERSION%.dxt
set TEMP_DIR=dxt-build

REM Clean up any previous build
if exist %TEMP_DIR% rmdir /s /q %TEMP_DIR%
if exist %OUTPUT_NAME% del %OUTPUT_NAME%

REM Create temp directory structure
echo Creating package structure...
mkdir %TEMP_DIR%
mkdir %TEMP_DIR%\mcp-server
mkdir %TEMP_DIR%\wp-mcp-plugin

REM Copy manifest (rename dxt-manifest.json to manifest.json)
echo Copying manifest...
copy dxt-manifest.json %TEMP_DIR%\manifest.json >nul

REM Copy MCP server files
echo Copying MCP server files...
xcopy mcp-server\*.py %TEMP_DIR%\mcp-server\ /s /q >nul
copy mcp-server\requirements.txt %TEMP_DIR%\mcp-server\ >nul
copy mcp-server\.env.example %TEMP_DIR%\mcp-server\ >nul

REM Copy WordPress plugin
echo Copying WordPress plugin...
xcopy wp-mcp-plugin\*.php %TEMP_DIR%\wp-mcp-plugin\ /s /q >nul
xcopy wp-mcp-plugin\includes %TEMP_DIR%\wp-mcp-plugin\includes\ /s /q >nul 2>nul
xcopy wp-mcp-plugin\admin %TEMP_DIR%\wp-mcp-plugin\admin\ /s /q >nul 2>nul
copy wp-mcp-plugin\readme.txt %TEMP_DIR%\wp-mcp-plugin\ >nul 2>nul

REM Copy documentation
echo Copying documentation...
copy README.md %TEMP_DIR%\ >nul
copy LICENSE %TEMP_DIR%\ >nul
copy QUICKSTART.md %TEMP_DIR%\ >nul
copy CHANGELOG.md %TEMP_DIR%\ >nul

REM Create the DXT package (using tar if available)
echo.
echo Creating DXT package...
where tar >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Using tar to create package...
    cd %TEMP_DIR%
    tar -czf ..\%OUTPUT_NAME% *
    cd ..
    echo ✅ Created %OUTPUT_NAME% using tar
) else (
    echo ⚠️  tar not found. Please install tar or use WSL/Git Bash to create the package:
    echo.
    echo    cd %TEMP_DIR%
    echo    tar -czf ../wordpress-mcp-v%VERSION%.dxt *
    echo.
    echo Or use PowerShell:
    echo    Compress-Archive -Path %TEMP_DIR%\* -DestinationPath wordpress-mcp-v%VERSION%.zip
    echo    Then rename .zip to .dxt
)

REM Cleanup
echo.
echo Cleaning up temporary files...
rmdir /s /q %TEMP_DIR%

echo.
echo =====================================
echo 📦 DXT Package Build Complete!
echo =====================================
echo.
echo Package: %OUTPUT_NAME%
echo Version: %VERSION%
echo.
echo Next steps:
echo 1. Test locally: dxt install %OUTPUT_NAME%
echo 2. Submit to Anthropic via their submission process
echo 3. Share with the community!
echo.
echo "Intelligence Combined 🧠"
echo =====================================
pause