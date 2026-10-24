@echo off
chcp 65001 >nul
title LinguaDesk Pro v6.1 - Mohammed Albukeer (mohammedalbukeer@gmail.com)
cd /d "%~dp0"
echo ============================================================================
echo   LinguaDesk Pro v6.1 Ultimate - Native Desktop App ^& Floating Translator
echo   Created by: Mohammed Albukeer (mohammedalbukeer@gmail.com)
echo ============================================================================
echo.
start "" wscript.exe "%~dp0Launch_LinguaDeskPro.vbs"
exit /b 0
