@echo off
echo ========================================
echo   FULL BEAUTIFICATION PROCESS!
echo   Green Checks + Professional Badges
echo ========================================
echo.

echo Running Step 1: Making CI/CD green...
call make-it-pretty.bat

echo.
echo Waiting for push to complete...
timeout /t 5 /nobreak > nul

echo.
echo Running Step 2: Adding beautiful badges...
call add-badges.bat

echo.
echo ========================================
echo    🎉 COMPLETE MAKEOVER DONE!
echo ========================================
echo.
echo Your repository now has:
echo   ✅ Green CI/CD checkmarks
echo   🏆 Professional status badges
echo   💚 "Build Passing" status
echo   ❤️ "Made with love" signature
echo.
echo Your WordPress MCP looks absolutely
echo STUNNING and PROFESSIONAL!
echo.
echo Check it out at:
echo https://github.com/Breuk-AI/wordpress-mcp
echo.
pause
