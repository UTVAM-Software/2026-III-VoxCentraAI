[CmdletBinding()]
param(
    [string]$InstallPath = $PSScriptRoot
)

$ErrorActionPreference = "Stop"
$pidFile = Join-Path $InstallPath ".local-logs\daphne.pid"
if (-not (Test-Path -LiteralPath $pidFile)) {
    Write-Host "No hay un servidor local registrado para detener."
    exit 0
}

$serviceId = [int](Get-Content -LiteralPath $pidFile -Raw).Trim()
$processInfo = Get-CimInstance Win32_Process -Filter "ProcessId = $serviceId" -ErrorAction SilentlyContinue
if (-not $processInfo -or $processInfo.CommandLine -notlike "*voxcentra.asgi:application*") {
    Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
    Write-Host "El servidor ya no estaba activo."
    exit 0
}

Stop-Process -Id $serviceId
Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
Write-Host "Servidor local detenido."
