@echo off
echo ================================
echo Running WordPress MCP Tests
echo ================================
echo.

REM Check if pytest is installed
python -m pytest --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pytest...
    pip install pytest
)

echo Running structure tests...
python tests/test_structure.py
if %errorlevel% neq 0 (
    echo ❌ Structure tests failed!
    exit /b 1
)

echo.
echo Running manifest tests...
python tests/test_manifest.py
if %errorlevel% neq 0 (
    echo ❌ Manifest tests failed!
    exit /b 1
)

echo.
echo Running configuration tests...
python tests/test_config.py
if %errorlevel% neq 0 (
    echo ❌ Configuration tests failed!
    exit /b 1
)

echo.
echo Running pytest suite...
python -m pytest tests/ -v
if %errorlevel% neq 0 (
    echo ❌ Pytest suite failed!
    exit /b 1
)

echo.
echo ================================
echo ✅ All tests passed!
echo Ready to push to GitHub!
echo ================================
echo.
echo Run: git add . ^&^& git commit -m "Add comprehensive test suite" ^&^& git push
