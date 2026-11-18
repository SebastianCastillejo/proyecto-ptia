$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $raiz 'backend'
$frontend = Join-Path $raiz 'frontend'
$python = Join-Path $backend '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { $python = (Get-Command python).Source }
$npm = (Get-Command npm.cmd).Source
$api = Start-Process -FilePath $python -ArgumentList '-m','uvicorn','app.main:app','--reload','--port','8000' -WorkingDirectory $backend -WindowStyle Hidden -PassThru
$web = Start-Process -FilePath $npm -ArgumentList 'run','dev','--','--host','127.0.0.1' -WorkingDirectory $frontend -WindowStyle Hidden -PassThru
Write-Host 'API: http://localhost:8000/api/salud | Front: http://localhost:5173'
Write-Host "Para detenerlos: Stop-Process -Id $($api.Id),$($web.Id)"
