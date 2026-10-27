[CmdletBinding()]
param (
    [ValidateSet('all', 'backend', 'frontend')]
    [string]$Target = 'all',

    [switch]$Release
)

$ErrorActionPreference = 'Stop'
$RootDir = Split-Path -Parent $PSScriptRoot

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "[+] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Err {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

try {
    # 1. Compilacion del Backend en Rust
    if ($Target -in @('all', 'backend')) {
        Write-Step "Compilando Core API (Rust)..."
        $CoreApiDir = Join-Path $RootDir "src\core-api"
        Push-Location $CoreApiDir

        try {
            $cargoArgs = @("build")
            if ($Release) {
                $cargoArgs += "--release"
                Write-Host "Modo: Release (Optimizado)" -ForegroundColor DarkGray
            } else {
                Write-Host "Modo: Development" -ForegroundColor DarkGray
            }

            & cargo @cargoArgs
            if ($LASTEXITCODE -ne 0) {
                throw "Fallo en la compilacion de Cargo en core-api."
            }
            Write-Success "Core API compilado exitosamente."
        }
        finally {
            Pop-Location
        }
    }

    # 2. Compilacion del Frontend en Angular 21
    if ($Target -in @('all', 'frontend')) {
        Write-Step "Instalando dependencias y compilando Dashboard (Angular 21)..."
        $DashboardDir = Join-Path $RootDir "src\dashboard"
        Push-Location $DashboardDir

        try {
            if (-not (Test-Path "node_modules")) {
                Write-Host "Instalando node_modules..." -ForegroundColor DarkGray
                & npm install --no-audit --prefer-offline --legacy-peer-deps
                if ($LASTEXITCODE -ne 0) {
                    throw "Error ejecutando 'npm install' en dashboard."
                }
            }

            Write-Host "Ejecutando 'npm run build'..." -ForegroundColor DarkGray
            & npm run build
            if ($LASTEXITCODE -ne 0) {
                throw "Error en 'npm run build' en dashboard."
            }
            Write-Success "Dashboard en Angular compilado exitosamente (dist/dashboard)."
        }
        finally {
            Pop-Location
        }
    }

    Write-Host ""
    Write-Host "=======================================================" -ForegroundColor Green
    Write-Host "  Compilacion completada exitosamente!" -ForegroundColor Green
    Write-Host "=======================================================" -ForegroundColor Green
    Write-Host ""
}
catch {
    Write-Err $_.Exception.Message
    exit 1
}
