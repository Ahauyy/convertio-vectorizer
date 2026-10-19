@echo off
title Uninstall Convertio Right-Click Context Menu
color 0C
echo ============================================================
echo   Menghapus Windows Context Menu: "Convert to SVG"
echo ============================================================
echo.

python "%~dp0register_menu.py" --uninstall

echo.
pause
