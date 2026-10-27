# Real-Time E-Commerce Fraud Detection System

Este proyecto es un **Motor de Detección de Fraude en Tiempo Real** para transacciones de e-commerce y banca con **Arquitectura Híbrida de Dos Capas**: combina un núcleo de altísimo rendimiento en **Rust (< 2ms)** para reglas duras con un **Modelo de Inteligencia Artificial Local (Ollama + Qwen 2.5 1.5B)** para evaluación cognitiva, análisis de patrones en "zona gris" y explicabilidad de alertas (Explainable AI - XAI), todo orquestado en Docker sin necesidad de GPU dedicada.

---

## 🏗️ Arquitectura del Sistema

El sistema implementa una arquitectura reactiva y orientada a eventos con desacoplamiento total:

*   **Infraestructura de Mensajería (Docker + Kafka KRaft):** Broker de eventos distribuido de baja latencia sin dependencia de ZooKeeper.
*   **Core API (Rust + Axum + Tokio):** Backend concurrente que evalúa transacciones a través de un motor de reglas en memoria (< 2ms). Expone WebSocket para el tablero y Swagger UI interactivo.
*   **Motor Cognitivo de IA (Ollama + Qwen 2.5 1.5B):** Microservicio en contenedor local ejecutando un Small Language Model (SLM) en **modo CPU**. Analiza el comportamiento del usuario, audita transacciones dudosas y redacta una explicación analítica contextual para los auditores.
*   **Tablero de Monitoreo (Angular 21):** Single Page Application (SPA) reactiva con *Angular Signals* y WebSockets que muestra métricas financieras en tiempo real y el feed de alertas enriquecido por la IA.

```text
                               ┌────────────────────────────────────────┐
                               │       E-Commerce Transactions Stream   │
                               └───────────────────┬────────────────────┘
                                                   │
                                                   ▼
                                       ┌───────────────────────┐
                                       │   Apache Kafka KRaft  │
                                       │ (topic: transactions) │
                                       └───────────┬───────────┘
                                                   │
                                                   ▼
                                ┌───────────────────────────────────────┐
                                │        fraud-core-api (Rust)          │
                                │                                       │
                                │  [Tier 1: Fast-Path Heurístico <2ms]  │
                                └───┬───────────────────────────────┬───┘
                                    │                               │
                      (Sospecha / Zona Gris)            (Fraude Inmediato / Alerta)
                                    │                               │
                                    ▼                               ▼
                      ┌───────────────────────────┐   ┌───────────────────────────┐
                      │ fraud-ollama (Docker)     │   │   Apache Kafka KRaft      │
                      │ Qwen 2.5 1.5B (CPU Mode)  ├──►│ (topic: fraud-alerts)     │
                      │ [Tier 2: Análisis y XAI]  │   └─────────────┬─────────────┘
                      └───────────────────────────┘                 │
                                    │                               │
                                    └───────────────┬───────────────┘
                                                    ▼
                                      ┌───────────────────────────┐
                                      │ WebSocket Event Broadcast │
                                      └─────────────┬─────────────┘
                                                    ▼
                                      ┌───────────────────────────┐
                                      │ fraud-dashboard (Angular) │
                                      │ Feed + Razonamiento IA    │
                                      └───────────────────────────┘
```

### Estructura del Repositorio

```text
fraud-detection-system/
├── .gitignore
├── README.md
├── docker-compose.yml               # Orquestación de Kafka, Ollama, Core API, Dashboard y Kafka UI
├── build-and-deploy.ps1             # Script unificado de automatización (PowerShell)
├── build-and-deploy.sh              # Script unificado de automatización (Bash)
├── docs/
│   └── diagrams/
│       ├── README.md                # Guía de apertura, edición y paleta de colores
│       ├── arquitectura.drawio      # Diagrama de arquitectura e infraestructura
│       ├── procesos.drawio          # Diagrama de flujo de detección y evaluación en dos capas
│       └── sistema-completo.drawio  # Versión multipágina unificada (ambos diagramas)
├── scripts/
│   ├── build.ps1                    # Compilación local de Rust y Angular (PowerShell)
│   ├── build.sh                     # Compilación local de Rust y Angular (Bash)
│   ├── deploy.ps1                   # Despliegue, descarga de modelo Qwen 2.5 y gestión (PowerShell)
│   ├── deploy.sh                    # Despliegue, descarga de modelo Qwen 2.5 y gestión (Bash)
│   └── generate_diagrams.py         # Generador/validador programático de diagramas Draw.io
└── src/
    ├── infra/                       # Configuración y scripts de infraestructura
    │   └── kafka/
    │       └── cluster-id.sh        # Script auxiliar para inicializar KRaft
    │
    ├── core-api/                    # Backend en Rust
    │   ├── Dockerfile               # Contenedor multi-stage optimizado
    │   ├── Cargo.toml               # Dependencias (rdkafka, tokio, axum, reqwest, serde, utoipa)
    │   └── src/
    │       ├── main.rs              # Punto de entrada y orquestador del servicio
    │       ├── config.rs            # Configuración de Kafka, Ollama y variables de entorno
    │       ├── kafka/
    │       │   ├── mod.rs
    │       │   ├── consumer.rs      # Consumo de transacciones e inferencia asíncrona
    │       │   └── producer.rs      # Productor para alertas hacia Kafka
    │       ├── engine/
    │       │   ├── mod.rs
    │       │   ├── fraud_rules.rs   # Motor algorítmico y reglas heurísticas en memoria
    │       │   └── ollama.rs        # Cliente HTTP del modelo IA (Qwen 2.5 1.5B)
    │       └── network/
    │           ├── mod.rs
    │           └── ws_server.rs     # Servidor Axum, WebSockets, endpoints IA y Swagger UI
    │
    └── dashboard/                   # Frontend en Angular 21
        ├── Dockerfile               # Contenedor multi-stage con Nginx
        ├── package.json             # Dependencias del proyecto Angular
        └── src/app/
            ├── core/services/
            │   └── websocket.service.ts # Conexión reactiva con soporte para análisis IA
            └── features/monitoring/
                ├── components/alert-feed/ # Tarjetas con badge y razonamiento cognitivo Qwen 2.5
                └── monitoring.component.ts
```

---

## 📊 Diagramas del Sistema (Draw.io)

El proyecto incluye diagramas técnicos en formato nativo **Draw.io (`.drawio`)**, compatibles con [diagrams.net](https://app.diagrams.net/) y la extensión [Draw.io Integration de VS Code](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio):

*   **[Diagrama de Arquitectura](./docs/diagrams/arquitectura.drawio):** Topología integral de contenedores Docker, red `fraud-network`, puertos de host e internos, broker Kafka KRaft (tópicos `transactions` y `fraud-alerts`), backend Core API en Rust (Tokio/Axum), motor local Ollama (`qwen2.5:1.5b`) y frontend Angular 21.
*   **[Diagrama de Procesos](./docs/diagrams/procesos.drawio):** Flujo de decisión end-to-end con filtrado heurístico en memoria (**Tier 1 < 2ms**), bifurcación de transacciones en zona gris (>=$1500), auditoría cognitiva asíncrona y explicabilidad (XAI) con Ollama (**Tier 2**), publicación en Kafka y streaming WebSocket al dashboard.
*   **[Diagrama Multipágina Unificado](./docs/diagrams/sistema-completo.drawio):** Archivo Draw.io con ambas vistas en pestañas para edición y exportación rápida.

> Consulta [docs/diagrams/README.md](./docs/diagrams/README.md) para más detalles sobre cómo visualizarlos, editarlos en VS Code o regenerarlos con `python scripts/generate_diagrams.py`.

---

## 🚀 Prerrequisitos

*   **Para despliegue con Docker (Recomendado):**
    *   [Docker](https://docs.docker.com/get-docker/) (v24+) y [Docker Compose](https://docs.docker.com/compose/) (v2+).
    *   ~3-4 GB de memoria RAM libre (para soportar Kafka, Ollama con el modelo Qwen 2.5 1.5B y el Core API en CPU).
*   **Para desarrollo y compilación local:**
    *   **Rust & Cargo:** (v1.80+) con `cmake` y compiladores C/C++ instalados.
    *   **Node.js:** (v20+ o v22+) y `npm` (v10+).

---

## ⚡ Automatización con Scripts (Recomendado)

Los scripts automatizados gestionan todo el ciclo de vida, incluyendo el arranque de Docker y la descarga automática del modelo `qwen2.5:1.5b`:

### Despliegue completo en 1 paso
```powershell
# En Windows (PowerShell)
.\build-and-deploy.ps1

# En Linux / macOS / Git Bash
./build-and-deploy.sh
```
> **Nota:** En el primer arranque, el script descargará el modelo ligero `qwen2.5:1.5b` (~1.0 GB) dentro del contenedor de Ollama. Esta descarga es persistente mediante el volumen `ollama_data`.

### Gestión y monitoreo
```powershell
# Ver estado de los contenedores
.\build-and-deploy.ps1 -Action status

# Seguir logs unificados en vivo
.\build-and-deploy.ps1 -Action logs

# Detener los servicios
.\build-and-deploy.ps1 -Action down

# Detener y limpiar volúmenes de Kafka y Ollama
.\build-and-deploy.ps1 -Action down -Clean
```

---

## 🐳 Despliegue Manual con Docker Compose

Si prefieres orquestar manualmente con `docker compose`:

### 1. Construir e iniciar todos los servicios
```bash
docker compose up --build -d
```

### 2. Descargar el modelo en Ollama (Primera vez)
```bash
docker exec -it fraud-ollama ollama pull qwen2.5:1.5b
```

### 3. Verificar contenedores activos
```bash
docker compose ps
```

Deberás ver los 5 contenedores saludables:
*   `fraud-kafka-kraft`: Broker Kafka en KRaft (puertos `9092` y `9094`).
*   `fraud-kafka-ui`: Interfaz Web para inspección de tópicos.
*   `fraud-ollama`: Motor de inferencia local con `qwen2.5:1.5b`.
*   `fraud-core-api`: Motor de reglas y orquestador IA en Rust.
*   `fraud-dashboard`: Tablero de control SPA servido con Nginx.

---

## 🌐 URLs de Acceso

| Servicio | URL | Descripción |
| :--- | :--- | :--- |
| **Dashboard de Monitoreo** | [http://localhost:4200](http://localhost:4200) | Frontend Angular 21 con visualización reactiva y análisis IA |
| **Swagger UI (OpenAPI)** | [http://localhost:3000/swagger-ui/](http://localhost:3000/swagger-ui/) | Consola interactiva para simular transacciones y probar la IA |
| **Kafka UI** | [http://localhost:8085](http://localhost:8085) | Explorador web de eventos y tópicos de Kafka |
| **Ollama Local AI API** | [http://localhost:11434](http://localhost:11434) | Motor de inferencia del modelo SLM `qwen2.5:1.5b` |
| **Core API Health Check** | [http://localhost:3000/health](http://localhost:3000/health) | Chequeo de estado del motor de Rust y WebSocket (`ws://localhost:3000/ws`) |
| **Estado del Motor IA** | [http://localhost:3000/api/ai/status](http://localhost:3000/api/ai/status) | Diagnóstico de conectividad y estado del modelo local |

---

## 🧪 Pruebas y Simulación de Detección

### 1. Evaluación directa con el modelo IA (Ollama Qwen 2.5)

Puedes invocar el endpoint cognitivo expuesto por el backend en Rust para obtener el razonamiento del modelo en formato JSON:

```bash
curl -X POST http://localhost:3000/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "id": "tx-ai-991",
    "user_id": "usr-501",
    "amount": 3400.00,
    "currency": "USD",
    "card_number_masked": "4111-XXXX-XXXX-9901",
    "merchant": "CryptoExchange Global",
    "location_country": "NG",
    "ip_address": "102.89.23.11",
    "timestamp": 1700000000
  }'
```

**Respuesta estructurada del modelo:**
```json
{
  "status": "success",
  "model": "qwen2.5:1.5b",
  "available": true,
  "analysis": {
    "is_fraud": true,
    "confidence": 0.88,
    "risk_level": "HIGH",
    "explanation": "Transacción de alto riesgo: monto considerable hacia exchange de criptomonedas con geolocalización IP atípica.",
    "model": "qwen2.5:1.5b"
  }
}
```

### 2. Simular flujo completo en el Pipeline de Kafka

Envía un mensaje al tópico `transactions` mediante la consola de Kafka:

```bash
docker exec -it fraud-kafka-kraft /opt/kafka/bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic transactions
```

Pega la transacción:
```json
{"id":"tx-8812","user_id":"usr-902","amount":6200.00,"currency":"USD","card_number_masked":"5500-XXXX-XXXX-4433","merchant":"Electronics MegaStore","location_country":"US","ip_address":"198.51.100.4","timestamp":1700000000}
```

1. **Capa Heurística (< 2ms):** Rust detecta de inmediato la violación del umbral de monto permitido ($5,000.00).
2. **Capa Cognitiva IA:** En segundo plano, Rust consulta asíncronamente a Ollama (`qwen2.5:1.5b`), generando un razonamiento en lenguaje natural.
3. **Kafka & Dashboard:** La alerta se publica en el tópico `fraud-alerts` y aparece con una tarjeta visual con el chip `🤖 Qwen 2.5 1.5B (Ollama)` en el dashboard Angular.

---

## 🛑 Detención y Limpieza de Recursos

```bash
# Detener contenedores manteniendo volúmenes
docker compose down

# Detener y eliminar volúmenes persistentes (Kafka y modelos de Ollama)
docker compose down -v
```