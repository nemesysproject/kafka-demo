#!/usr/bin/env bash
# ==============================================================================
# Docker Deployment Script for Real-Time Fraud Detection System
# ==============================================================================

set -euo pipefail

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

ACTION="${1:-up}"
CLEAN="${2:-}"

# Check Docker
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}[ERROR] Docker no está ejecutándose o no está instalado.${NC}"
    exit 1
fi

cd "${ROOT_DIR}"

case "${ACTION}" in
    down)
        echo -e "${CYAN}[+] Deteniendo contenedores...${NC}"
        if [ "${CLEAN}" = "-v" ] || [ "${CLEAN}" = "--clean" ]; then
            echo -e "${YELLOW}[!] Eliminando volúmenes persistentes de Kafka...${NC}"
            docker compose down -v
        else
            docker compose down
        fi
        echo -e "${GREEN}[OK] Servicios detenidos.${NC}"
        ;;
    status)
        docker compose ps
        ;;
    logs)
        docker compose logs -f
        ;;
    restart)
        echo -e "${CYAN}[+] Reiniciando stack...${NC}"
        docker compose down
        docker compose up --build -d
        ;;
    up|*)
        echo -e "${CYAN}[+] Construyendo y desplegando stack con Docker Compose...${NC}"
        docker compose up --build -d

        echo -e "${CYAN}[+] Esperando inicialización de servicios...${NC}"
        sleep 6

        echo -e "${CYAN}[+] Verificando disponibilidad del modelo de IA (qwen2.5:1.5b) en Ollama...${NC}"
        if docker exec fraud-ollama ollama list 2>/dev/null | grep -q "qwen2.5:1.5b"; then
            echo -e "${GREEN}[OK] Modelo qwen2.5:1.5b ya presente en Ollama.${NC}"
        else
            echo -e "${YELLOW}[!] Descargando modelo qwen2.5:1.5b en Ollama (~1.0 GB)... Solo la primera vez.${NC}"
            docker exec fraud-ollama ollama pull qwen2.5:1.5b || echo -e "${YELLOW}[!] Aviso: Puedes descargar el modelo luego con 'docker exec -it fraud-ollama ollama pull qwen2.5:1.5b'${NC}"
        fi

        echo -e "\n${GREEN}==================================================================${NC}"
        echo -e "${GREEN}  🚀 SISTEMA DE DETECCIÓN DE FRAUDE DESPLEGADO CON ÉXITO${NC}"
        echo -e "${GREEN}==================================================================${NC}"
        echo -e "  🌐 Dashboard de Monitoreo:  ${CYAN}http://localhost:4200${NC}"
        echo -e "  📖 Swagger UI (OpenAPI):    ${CYAN}http://localhost:3000/swagger-ui/${NC}"
        echo -e "  📊 Kafka UI (Broker KRaft): ${CYAN}http://localhost:8085${NC}"
        echo -e "  🤖 Ollama Local AI (SLM):   ${CYAN}http://localhost:11434 (qwen2.5:1.5b)${NC}"
        echo -e "  🩺 Core API Health Check:   ${CYAN}http://localhost:3000/health${NC}"
        echo -e "  ⚡ WebSocket Stream:        ${CYAN}ws://localhost:3000/ws${NC}"
        echo -e "${GREEN}==================================================================${NC}\n"
        ;;
esac

