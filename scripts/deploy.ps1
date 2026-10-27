[CmdletBinding()]
param (
    [ValidateSet('up', 'down', 'restart', 'status', 'logs')]
    [string]$Action = 'up',

    [switch]$Clean
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

function Write-WarnMsg {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor Yellow
}

function Write-ErrMsg {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Test-DockerRunning {
    try {
        $prevErrorAction = $ErrorActionPreference
        $ErrorActionPreference = 'SilentlyContinue'
        $null = & docker info 2>$null
        return ($LASTEXITCODE -eq 0)
    }
    catch {
        return $false
    }
    finally {
        $ErrorActionPreference = $prevErrorAction
    }
}

if (-not (Test-DockerRunning)) {
    Write-ErrMsg "El motor de Docker no esta ejecutandose. Por favor inicia Docker Desktop primero."
    exit 1
}

Push-Location $RootDir
try {
    switch ($Action) {
        'down' {
            Write-Step "Deteniendo y eliminando contenedores..."
            $downArgs = @("compose", "down")
            if ($Clean) {
                $downArgs += "-v"
                Write-WarnMsg "Eliminando volumenes persistentes de datos de Kafka..."
            }
            & docker @downArgs
            Write-Success "Servicios detenidos correctamente."
        }

        'restart' {
            Write-Step "Reiniciando el stack de Docker Compose..."
            & docker compose down
            & docker compose up --build -d
            Write-Success "Servicios reiniciados."
        }

        'status' {
            Write-Step "Estado actual de los servicios:"
            & docker compose ps
        }

        'logs' {
            & docker compose logs -f
        }

        'up' {
            Write-Step "Construyendo imagenes y levantando servicios en modo detached..."
            & docker compose up --build -d
            if ($LASTEXITCODE -ne 0) {
                throw "Error al ejecutar 'docker compose up'."
            }

            Write-Step "Esperando a que los servicios completen el chequeo de salud..."
            Start-Sleep -Seconds 6

            Write-Step "Verificando disponibilidad del modelo de IA (qwen2.5:1.5b) en Ollama..."
            try {
                $models = & docker exec fraud-ollama ollama list 2>$null
                if ($models -notmatch "qwen2.5:1.5b") {
                    Write-WarnMsg "Descargando modelo qwen2.5:1.5b en Ollama (~1.0 GB)... Solo se realiza la primera vez."
                    & docker exec fraud-ollama ollama pull qwen2.5:1.5b
                    Write-Success "Modelo qwen2.5:1.5b listo para inferencia."
                } else {
                    Write-Success "Modelo qwen2.5:1.5b ya presente en Ollama."
                }
            } catch {
                Write-WarnMsg "Aviso: Puedes descargar el modelo ejecutando: docker exec -it fraud-ollama ollama pull qwen2.5:1.5b"
            }

            Write-Host ""
            Write-Host "==================================================================" -ForegroundColor Green
            Write-Host "  SISTEMA DE DETECCION DE FRAUDE DESPLEGADO CON EXITO" -ForegroundColor Green
            Write-Host "==================================================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "  Dashboard de Monitoreo:  http://localhost:4200" -ForegroundColor Cyan
            Write-Host "  Swagger UI (OpenAPI):    http://localhost:3000/swagger-ui/" -ForegroundColor Cyan
            Write-Host "  Kafka UI (Broker KRaft): http://localhost:8085" -ForegroundColor Cyan
            Write-Host "  Ollama Local AI (SLM):   http://localhost:11434 (qwen2.5:1.5b)" -ForegroundColor Cyan
            Write-Host "  Core API Health Check:   http://localhost:3000/health" -ForegroundColor Cyan
            Write-Host "  WebSocket Stream:        ws://localhost:3000/ws" -ForegroundColor Cyan
            Write-Host ""

            Write-Host "==================================================================" -ForegroundColor Green
            Write-Host "Comandos utiles:" -ForegroundColor DarkGray
            Write-Host "  Ver logs:              .\scripts\deploy.ps1 -Action logs" -ForegroundColor DarkGray
            Write-Host "  Ver estado:            .\scripts\deploy.ps1 -Action status" -ForegroundColor DarkGray
            Write-Host "  Detener servicios:     .\scripts\deploy.ps1 -Action down" -ForegroundColor DarkGray
            Write-Host "  Limpiar con volumenes: .\scripts\deploy.ps1 -Action down -Clean" -ForegroundColor DarkGray
            Write-Host "==================================================================" -ForegroundColor DarkGray
            Write-Host ""
        }
    }
}
catch {
    Write-ErrMsg $_.Exception.Message
    exit 1
}
finally {
    Pop-Location
}
