@echo off
echo ========================================
echo   Adding Professional Status Badges
echo   Making README Extra Pretty!
echo ========================================
echo.

echo Step 1: Backing up current README...
copy README.md README.backup.md

echo Step 2: Creating new README with badges...
(
echo # WordPress MCP ^(Model Context Protocol^) Integration
echo.
echo ![Build Status](https://github.com/Breuk-AI/wordpress-mcp/actions/workflows/ci.yml/badge.svg^)
echo ![WordPress](https://img.shields.io/badge/WordPress-5.6+-blue^)
echo ![Python](https://img.shields.io/badge/Python-3.8+-green^)
echo ![License](https://img.shields.io/badge/License-MIT-yellow^)
echo ![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-purple^)
echo ![WooCommerce](https://img.shields.io/badge/WooCommerce-Supported-96588A^)
echo.
) > README_header.tmp

:: Skip the first line of original README (the title) and append the rest
more +1 README.md >> README_header.tmp

:: Replace the original README
move /y README_header.tmp README.md

echo.
echo Step 3: Committing the beautiful badges...
git add README.md
git commit -m "🎨 Add professional status badges to README"

echo.
echo Step 4: Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo    ✨ Badges Added Successfully!
echo ========================================
echo.
echo Your README now shows:
echo   ✅ Build Status (green when CI passes)
echo   📘 WordPress 5.6+ requirement
echo   🐍 Python 3.8+ requirement  
echo   📜 MIT License
echo   🟣 MCP Compatible
echo   🛍️ WooCommerce Supported
echo.
echo These badges make your project look
echo SUPER professional!
echo.
pause
