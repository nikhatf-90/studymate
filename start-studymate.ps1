# Starts StudyMate's API and Vite frontend in separate PowerShell windows.
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = "Set-Location -LiteralPath '$projectRoot'; & '$projectRoot\.venv\Scripts\Activate.ps1'; uvicorn backend.main:app --reload --port 8000"
$frontend = "Set-Location -LiteralPath '$projectRoot\frontend'; npm run dev"
Start-Process powershell -ArgumentList '-NoExit', '-Command', $backend
Start-Process powershell -ArgumentList '-NoExit', '-Command', $frontend
