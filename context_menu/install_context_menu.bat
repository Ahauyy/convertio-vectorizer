@echo off
title Install Convertio Right-Click Context Menu
color 0A
echo ============================================================
echo   Memasang Windows Context Menu: "Convert to SVG"
echo ============================================================
echo.

python "%~dp0register_menu.py"

echo.
pause
