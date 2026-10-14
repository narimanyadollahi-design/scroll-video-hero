@echo off
title Local site
cd /d "%~dp0"
echo Starting the site...
if exist "node\node.exe" (
  "node\node.exe" server.js
) else (
  where node >nul 2>nul && (node server.js) || (echo Node.js was not found. See README.txt & pause)
)
pause
