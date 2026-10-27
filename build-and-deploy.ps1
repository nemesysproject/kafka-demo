[CmdletBinding()]
param (
    [ValidateSet('docker', 'local')]
    [string]$Target = 'docker',

    [ValidateSet('up', 'build', 'down', 'status', 'logs')]
    [string]$Action = 'up',

    [switch]$Clean
)

$ErrorActionPreference = 'Stop'
$ScriptDir = $PSScriptRoot

if ($Action -eq 'build' -or $Target -eq 'local') {
    if ($Action -eq 'build') {
        & "$ScriptDir\scripts\build.ps1" -Target all -Release
    } elseif ($Action -eq 'up') {
        Write-Host ""
        Write-Host "[+] Iniciando infraestructura Kafka y Ollama (IA Local) para desarrollo local..." -ForegroundColor Cyan
        & docker compose up -d kafka kafka-ui ollama
        Start-Sleep -Seconds 3
        try {
            $models = & docker exec fraud-ollama ollama list 2>$null
            if ($models -notmatch "qwen2.5:1.5b") {
                Write-Host "[!] Descargando modelo qwen2.5:1.5b en Ollama (~1.0 GB)..." -ForegroundColor Yellow
                & docker exec fraud-ollama ollama pull qwen2.5:1.5b
            }
        } catch {}
        Write-Host ""
        Write-Host "[+] Infraestructura Kafka y Ollama activa." -ForegroundColor Green
        Write-Host "Para iniciar el backend ejecuta:   cd src\core-api && cargo run --release" -ForegroundColor Yellow
        Write-Host "Para iniciar el frontend ejecuta:  cd src\dashboard && npm start" -ForegroundColor Yellow
        Write-Host ""
    }

} else {
    # Docker mode
    & "$ScriptDir\scripts\deploy.ps1" -Action $Action -Clean:$Clean
}
