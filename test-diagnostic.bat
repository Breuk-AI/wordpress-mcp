@echo off
echo ================================
echo Quick Test Diagnostic
echo ================================
echo.

echo Testing Python availability...
python --version

echo.
echo Testing if pytest is installed...
python -m pytest --version 2>nul
if %errorlevel% neq 0 (
    echo pytest NOT installed - this might be the issue!
    echo Installing pytest...
    pip install pytest
)

echo.
echo Testing individual test files directly...
echo.
echo 1. Testing manifest...
python tests\test_manifest.py
echo.
echo 2. Testing structure...
python tests\test_structure.py
echo.
echo 3. Testing config...
python tests\test_config.py

echo.
echo ================================
echo Diagnostic Complete
echo ================================
pause
