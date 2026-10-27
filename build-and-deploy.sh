#!/usr/bin/env bash
# ==============================================================================
# Unified Build & Deployment Script for Fraud Detection System
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACTION="${1:-up}"
ARG2="${2:-}"

case "${ACTION}" in
    build)
        bash "${SCRIPT_DIR}/scripts/build.sh" all release
        ;;
    down|status|logs|restart)
        bash "${SCRIPT_DIR}/scripts/deploy.sh" "${ACTION}" "${ARG2}"
        ;;
    local)
        echo "Iniciando Kafka KRaft y Ollama (IA Local) para desarrollo local..."
        docker compose up -d kafka kafka-ui ollama
        sleep 3
        if ! docker exec fraud-ollama ollama list 2>/dev/null | grep -q "qwen2.5:1.5b"; then
            echo "Descargando modelo qwen2.5:1.5b en Ollama (~1.0 GB)..."
            docker exec fraud-ollama ollama pull qwen2.5:1.5b || true
        fi
        echo "Infraestructura lista."
        echo "Backend:  cd src/core-api && cargo run --release"
        echo "Frontend: cd src/dashboard && npm start"
        ;;

    up|*)
        bash "${SCRIPT_DIR}/scripts/deploy.sh" up
        ;;
esac
