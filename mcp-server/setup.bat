@echo off
echo WordPress MCP Server Setup
echo =========================
echo.

REM Check if config.json exists
if not exist config.json (
    echo Creating config.json from template...
    copy config.json.example config.json
    echo.
    echo IMPORTANT: Please edit config.json with your WordPress credentials!
    echo.
    pause
    exit /b
)

echo Installing Python requirements...
pip install -r requirements.txt

echo.
echo Testing WordPress connection...
python test_connection.py

echo.
echo Setup complete!
echo.
echo To run the MCP server:
echo   python server_mcp.py
echo.
echo To add to Claude Desktop, edit:
echo   %%APPDATA%%\Claude\claude_desktop_config.json
echo.
pause
