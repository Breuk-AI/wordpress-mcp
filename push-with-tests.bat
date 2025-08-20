@echo off
echo ================================
echo WordPress MCP - Pre-push Checks
echo ================================
echo.

REM Run tests first
echo Step 1: Running tests...
call run-tests.bat
if %errorlevel% neq 0 (
    echo.
    echo ❌ Tests failed! Fix issues before pushing.
    exit /b 1
)

echo.
echo Step 2: Checking git status...
git status

echo.
echo Step 3: Adding test files...
git add tests/
git add .github/workflows/ci.yml
git add requirements-dev.txt
git add run-tests.bat

echo.
echo Step 4: Creating commit...
git commit -m "✅ Add comprehensive test suite for CI/CD" -m "- Added pytest test suite with manifest, structure, and config tests" -m "- Updated CI workflow to run tests on multiple Python versions" -m "- Added requirements-dev.txt for development dependencies" -m "- Created run-tests.bat for local testing"

echo.
echo Step 5: Pushing to GitHub...
git push origin main

echo.
echo ================================
echo ✅ Successfully pushed to GitHub!
echo Check your green checkmark at:
echo https://github.com/Breuk-AI/wordpress-mcp/actions
echo ================================
