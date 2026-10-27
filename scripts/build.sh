#!/usr/bin/env bash
# ==============================================================================
# Build Script for Real-Time Fraud Detection System (Rust + Angular)
# ==============================================================================

set -euo pipefail

# ANSI Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

TARGET="${1:-all}"
MODE="${2:-debug}"

echo -e "${CYAN}======================================================${NC}"
echo -e "${CYAN} Invocando proceso de compilación local: ${TARGET}${NC}"
echo -e "${CYAN}======================================================${NC}"

# 1. Compile Rust Core API
if [ "$TARGET" = "all" ] || [ "$TARGET" = "backend" ]; then
    echo -e "\n${CYAN}[+] Compilando Core API (Rust)...${NC}"
    cd "${ROOT_DIR}/src/core-api"
    if [ "$MODE" = "release" ]; then
        cargo build --release
    else
        cargo build
    fi
    echo -e "${GREEN}[OK] Core API compilado con éxito.${NC}"
fi

# 2. Compile Angular Dashboard
if [ "$TARGET" = "all" ] || [ "$TARGET" = "frontend" ]; then
    echo -e "\n${CYAN}[+] Compilando Dashboard (Angular 21)...${NC}"
    cd "${ROOT_DIR}/src/dashboard"
    if [ ! -d "node_modules" ]; then
        echo "Instalando paquetes npm..."
        npm install --no-audit --prefer-offline --legacy-peer-deps
    fi
    npm run build
    echo -e "${GREEN}[OK] Dashboard en Angular compilado con éxito.${NC}"
fi

echo -e "\n${GREEN}======================================================${NC}"
echo -e "${GREEN}  ¡Compilación finalizada exitosamente!${NC}"
echo -e "${GREEN}======================================================${NC}"
