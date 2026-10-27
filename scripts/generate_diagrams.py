import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

def create_cell(root, cell_id, value, style, x=None, y=None, width=None, height=None, parent="1", is_edge=False, source=None, target=None):
    attribs = {"id": cell_id, "parent": parent}
    if value is not None:
        attribs["value"] = value
    if style is not None:
        attribs["style"] = style
    if is_edge:
        attribs["edge"] = "1"
        if source:
            attribs["source"] = source
        if target:
            attribs["target"] = target
    else:
        attribs["vertex"] = "1"
    
    cell = ET.SubElement(root, "mxCell", attribs)
    
    if not is_edge and x is not None and y is not None and width is not None and height is not None:
        geo = ET.SubElement(cell, "mxGeometry", {
            "x": str(x),
            "y": str(y),
            "width": str(width),
            "height": str(height),
            "as": "geometry"
        })
    elif is_edge:
        geo = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    return cell

def build_architecture_diagram():
    root = ET.Element("root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    # Canvas Header Banner
    create_cell(
        root, "hdr_banner",
        "<b>SISTEMA DE DETECCIÓN DE FRAUDE EN TIEMPO REAL</b><br/><font style='font-size:12px;font-weight:normal;color:#94A3B8;'>Arquitectura de Componentes, Flujos de Eventos e Infraestructura Contenerizada</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#0F172A;strokeColor=#1E293B;fontColor=#F8FAFC;fontSize=16;align=center;verticalAlign=middle;shadow=1;",
        x=40, y=20, width=1280, height=60
    )

    # -------------------------------------------------------------
    # 1. External Layer (Left side)
    # -------------------------------------------------------------
    create_cell(
        root, "c_ext_layer",
        "<b>🌍 CAPA EXTERNA / CLIENTES & ACTORES</b>",
        "swimlane;whiteSpace=wrap;html=1;collapsible=0;dropTarget=0;fillColor=#F8FAFC;strokeColor=#64748B;strokeWidth=2;fontColor=#1E293B;fontSize=12;fontStyle=1;startSize=30;arcSize=6;",
        x=40, y=100, width=230, height=720
    )

    create_cell(
        root, "ext_ecommerce",
        "<b>🛍️ E-Commerce Checkout</b><br/><font style='font-size:11px;color:#475569;'>Pasarela de Pagos / API de Transacciones<br/>(id, user, amount, card, ip, country)</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=10;fillColor=#FFFFFF;strokeColor=#0284C7;strokeWidth=2;fontColor=#0F172A;fontSize=11;align=center;shadow=1;",
        x=55, y=150, width=200, height=80
    )

    create_cell(
        root, "ext_simulator",
        "<b>⚡ Generador de Carga / CLI</b><br/><font style='font-size:11px;color:#475569;'>Simulador de Transacciones<br/>kafka-console-producer / Scripts</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=10;fillColor=#FFFFFF;strokeColor=#0284C7;strokeWidth=1.5;fontColor=#0F172A;fontSize=11;align=center;shadow=1;",
        x=55, y=260, width=200, height=70
    )

    create_cell(
        root, "ext_analyst",
        "<b>👤 Analista de Fraude / Ops</b><br/><font style='font-size:11px;color:#475569;'>Monitoreo de Alertas en Vivo<br/>Explicabilidad IA (XAI)</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=10;fillColor=#FFFFFF;strokeColor=#475569;strokeWidth=1.5;fontColor=#0F172A;fontSize=11;align=center;shadow=1;",
        x=55, y=520, width=200, height=70
    )

    create_cell(
        root, "ext_devops",
        "<b>👨‍💻 Desarrollador / Auditor</b><br/><font style='font-size:11px;color:#475569;'>Swagger UI (:3000)<br/>Kafka UI (:8085)</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=10;fillColor=#FFFFFF;strokeColor=#475569;strokeWidth=1.5;fontColor=#0F172A;fontSize=11;align=center;shadow=1;",
        x=55, y=660, width=200, height=70
    )

    # -------------------------------------------------------------
    # 2. Docker Compose Environment (Center-Right)
    # -------------------------------------------------------------
    create_cell(
        root, "c_docker_env",
        "<b>🐳 ENTORNO DOCKER COMPOSE &nbsp;|&nbsp; Red Bridge: <code>fraud-network</code></b>",
        "swimlane;whiteSpace=wrap;html=1;collapsible=0;dropTarget=0;fillColor=#F8FAFC;strokeColor=#0284C7;strokeWidth=2;fontColor=#0369A1;fontSize=13;fontStyle=1;startSize=32;arcSize=6;shadow=1;",
        x=290, y=100, width=1030, height=720
    )

    # --- 2.1 Kafka Cluster KRaft ---
    create_cell(
        root, "c_kafka",
        "<b>📦 Broker Apache Kafka (KRaft Mode)</b><br/><font style='font-size:10px;font-weight:normal;color:#7C2D12;'>Contenedor: <code>fraud-kafka-kraft</code> (apache/kafka:3.8.0)<br/>Sin ZooKeeper | Node ID: 1 | Puertos: 9092 (interno) / 9094 (host)</font>",
        "swimlane;whiteSpace=wrap;html=1;collapsible=0;dropTarget=0;fillColor=#FFF7ED;strokeColor=#EA580C;strokeWidth=2;fontColor=#9A3412;fontSize=11;fontStyle=1;startSize=40;arcSize=6;",
        x=310, y=145, width=370, height=265
    )

    create_cell(
        root, "kafka_topic_tx",
        "<b>📨 Topic: <code>transactions</code></b><br/><font style='font-size:10px;color:#9A3412;'>Stream de Eventos Financieros Crudos (JSON)</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#FFEDD5;strokeColor=#EA580C;strokeWidth=1.5;fontColor=#7C2D12;fontSize=11;align=center;",
        x=330, y=200, width=330, height=48
    )

    create_cell(
        root, "kafka_topic_alerts",
        "<b>🚨 Topic: <code>fraud-alerts</code></b><br/><font style='font-size:10px;color:#9A3412;'>Alertas de Fraude Evaluadas & Enriquecidas con IA</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#FEE2E2;strokeColor=#DC2626;strokeWidth=1.5;fontColor=#991B1B;fontSize=11;align=center;",
        x=330, y=260, width=330, height=48
    )

    create_cell(
        root, "kafka_vol",
        "💾 <b>Volumen Docker:</b> <code>kafka_data</code> (/var/lib/kafka/data)",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=6;fillColor=#FED7AA;strokeColor=#C2410C;strokeWidth=1;fontColor=#7C2D12;fontSize=10;align=center;",
        x=330, y=320, width=330, height=30
    )

    create_cell(
        root, "kafka_features",
        "⚡ <i>Auto-creación de tópicos | Group ID: fraud-detection-core | Min ISR: 1</i>",
        "text;html=1;align=center;verticalAlign=middle;fontSize=9;fontColor=#9A3412;",
        x=330, y=355, width=330, height=20
    )

    # --- 2.2 Kafka UI ---
    create_cell(
        root, "c_kafka_ui",
        "<b>🖥️ Kafka UI Dashboard</b><br/><font style='font-size:10px;font-weight:normal;color:#3730A3;'>Contenedor: <code>fraud-kafka-ui</code><br/>provectuslabs/kafka-ui:latest<br/><b>Puerto: 8085:8080</b></font><br/><br/><font style='font-size:10px;color:#4338CA;'>• Telemetría de Brokers<br/>• Explorador de Mensajes<br/>• Métricas de Consumidores</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#EEF2FF;strokeColor=#6366F1;strokeWidth=1.5;fontColor=#312E81;fontSize=11;align=center;shadow=1;",
        x=710, y=145, width=230, height=130
    )

    # --- 2.3 Ollama Local AI Engine ---
    create_cell(
        root, "c_ollama",
        "<b>🧠 Motor Cognitivo de IA (Ollama Local)</b><br/><font style='font-size:10px;font-weight:normal;color:#581C87;'>Contenedor: <code>fraud-ollama</code> (ollama/ollama:latest)<br/>Puerto: 11434:11434 | <b>Ejecución en CPU (Sin GPU)</b></font>",
        "swimlane;whiteSpace=wrap;html=1;collapsible=0;dropTarget=0;fillColor=#FAF5FF;strokeColor=#9333EA;strokeWidth=2;fontColor=#6B21A8;fontSize=11;fontStyle=1;startSize=40;arcSize=6;",
        x=960, y=145, width=340, height=265
    )

    create_cell(
        root, "ollama_model",
        "<b>🔬 Small Language Model (SLM)</b><br/><b><code>qwen2.5:1.5b</code></b> (~1.0 GB RAM)<br/><font style='font-size:10px;color:#581C87;'>• Análisis de 'Zona Gris' (Monto >= $1500)<br/>• Explicabilidad XAI en Lenguaje Natural<br/>• Inferencia Estructurada JSON (risk, confidence)</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#F3E8FF;strokeColor=#A855F7;strokeWidth=1.5;fontColor=#4C1D95;fontSize=10;align=center;",
        x=975, y=200, width=310, height=75
    )

    create_cell(
        root, "ollama_vol",
        "💾 <b>Volumen Docker:</b> <code>ollama_data</code> (/root/.ollama)<br/><font style='font-size:9px;color:#6B21A8;'>Persistencia local del modelo descargado</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=6;fillColor=#E9D5FF;strokeColor=#9333EA;strokeWidth=1;fontColor=#581C87;fontSize=10;align=center;",
        x=975, y=285, width=310, height=35
    )

    create_cell(
        root, "ollama_keepalive",
        "⚡ <i>OLLAMA_KEEP_ALIVE=24h (Modelo caliente en memoria)</i>",
        "text;html=1;align=center;verticalAlign=middle;fontSize=9;fontColor=#6B21A8;",
        x=975, y=325, width=310, height=20
    )

    # --- 2.4 Rust Core API ---
    create_cell(
        root, "c_core_api",
        "<b>⚙️ Core API - Motor de Detección de Fraude (Rust + Axum + Tokio)</b><br/><font style='font-size:10px;font-weight:normal;color:#065F46;'>Contenedor: <code>fraud-core-api</code> | Puerto: 3000:3000 | Concurrencia Asíncrona de Alto Rendimiento</font>",
        "swimlane;whiteSpace=wrap;html=1;collapsible=0;dropTarget=0;fillColor=#ECFDF5;strokeColor=#059669;strokeWidth=2;fontColor=#064E3B;fontSize=11;fontStyle=1;startSize=40;arcSize=6;shadow=1;",
        x=310, y=430, width=630, height=370
    )

    create_cell(
        root, "rust_consumer",
        "<b>📥 Kafka Consumer</b><br/><font style='font-size:10px;color:#064E3B;'>StreamConsumer (rdkafka)<br/>Suscrito a: <code>transactions</code></font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#D1FAE5;strokeColor=#10B981;strokeWidth=1.5;fontColor=#064E3B;fontSize=10;align=center;",
        x=330, y=490, width=170, height=65
    )

    create_cell(
        root, "rust_engine",
        "<b>⚡ Tier 1: Motor Heurístico (&lt; 2ms)</b><br/><font style='font-size:10px;color:#713F12;'><b>Evaluación de Reglas en Memoria:</b><br/>• Monto Excesivo (&gt;= $5,000)<br/>• Velocidad Anormal (&gt;3 tx en 30s)<br/>• Países Alto Riesgo (NK, SY, IR, RU)<br/>• Card Testing (Micro &lt;= $1.00)</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#FEF08A;strokeColor=#CA8A04;strokeWidth=2;fontColor=#713F12;fontSize=10;align=center;shadow=1;",
        x=330, y=570, width=280, height=95
    )

    create_cell(
        root, "rust_producer",
        "<b>📤 Kafka Producer</b><br/><font style='font-size:10px;color:#064E3B;'>FutureProducer (rdkafka)<br/>Emite a: <code>fraud-alerts</code></font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#D1FAE5;strokeColor=#10B981;strokeWidth=1.5;fontColor=#064E3B;fontSize=10;align=center;",
        x=330, y=685, width=170, height=60
    )

    create_cell(
        root, "rust_ollama_client",
        "<b>🤖 Ollama HTTP Client</b><br/><font style='font-size:10px;color:#4C1D95;'>Reqwest Async + Tokio Spawn<br/>• Auditoría 'Zona Gris' (&gt;=$1500)<br/>• Generación de XAI Explicativa<br/>• Recalibra Score de Riesgo</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#EDE9FE;strokeColor=#8B5CF6;strokeWidth=1.5;fontColor=#4C1D95;fontSize=10;align=center;",
        x=640, y=490, width=270, height=85
    )

    create_cell(
        root, "rust_web_server",
        "<b>🌐 Servidor Web Axum & Endpoints</b><br/><font style='font-size:10px;color:#1E3A8A;'>• <b>WebSocket:</b> <code>ws://localhost:3000/ws</code><br/>• <b>Health:</b> <code>/health</code> | <code>/api/ai/status</code><br/>• <b>Inferencia:</b> <code>POST /api/ai/analyze</code><br/>• <b>Docs:</b> <code>/swagger-ui/</code> (OpenAPI)</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#DBEAFE;strokeColor=#3B82F6;strokeWidth=1.5;fontColor=#1E3A8A;fontSize=10;align=center;",
        x=640, y=600, width=270, height=95
    )

    create_cell(
        root, "rust_metrics_state",
        "📊 <b>Estado de Métricas en Memoria:</b> TPS, Transacciones Totales, Fraudes Detectados, $ Retenido",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=6;fillColor=#F1F5F9;strokeColor=#64748B;strokeWidth=1;fontColor=#334155;fontSize=9;align=center;",
        x=530, y=715, width=380, height=30
    )

    # --- 2.5 Angular 21 Dashboard ---
    create_cell(
        root, "c_dashboard",
        "<b>📊 Tablero de Monitoreo Reactivo (Angular 21)</b><br/><font style='font-size:10px;font-weight:normal;color:#1E3A8A;'>Contenedor: <code>fraud-dashboard</code> | Nginx Alpine Multi-stage | <b>Puerto: 4200:80</b></font>",
        "swimlane;whiteSpace=wrap;html=1;collapsible=0;dropTarget=0;fillColor=#EFF6FF;strokeColor=#2563EB;strokeWidth=2;fontColor=#1E40AF;fontSize=11;fontStyle=1;startSize=40;arcSize=6;shadow=1;",
        x=960, y=430, width=340, height=370
    )

    create_cell(
        root, "dash_ws_service",
        "<b>⚡ WebSocket Service (Angular Signals)</b><br/><font style='font-size:10px;color:#1E3A8A;'>Subscripción reactiva a stream <code>/ws</code><br/>Actualización instantánea sin recarga</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#DBEAFE;strokeColor=#3B82F6;strokeWidth=1.5;fontColor=#1E3A8A;fontSize=10;align=center;",
        x=975, y=490, width=310, height=55
    )

    create_cell(
        root, "dash_metrics_cards",
        "<b>📈 KPIs Financieros en Tiempo Real</b><br/><font style='font-size:10px;color:#1E3A8A;'>• Medidor de TPS en Vivo<br/>• Total Operaciones Procesadas<br/>• Monto Retenido USD / Total Alertas</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#DBEAFE;strokeColor=#3B82F6;strokeWidth=1.5;fontColor=#1E3A8A;fontSize=10;align=center;",
        x=975, y=560, width=310, height=65
    )

    create_cell(
        root, "dash_alert_feed",
        "<b>🚨 Feed de Alertas & Explicabilidad IA</b><br/><font style='font-size:10px;color:#1E3A8A;'>• Badges de Severidad (CRITICAL, HIGH, MED)<br/>• Chip explicativo: <b>🤖 Qwen 2.5 1.5B (Ollama)</b><br/>• Modal de detalle con Score de riesgo</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#DBEAFE;strokeColor=#3B82F6;strokeWidth=1.5;fontColor=#1E3A8A;fontSize=10;align=center;",
        x=975, y=640, width=310, height=75
    )

    create_cell(
        root, "dash_tech_stack",
        "💻 <i>Angular 21 + TypeScript + Tailwind CSS / Vanilla CSS + Nginx</i>",
        "text;html=1;align=center;verticalAlign=middle;fontSize=9;fontColor=#1E40AF;",
        x=975, y=730, width=310, height=20
    )

    # -------------------------------------------------------------
    # 3. Connectors & Edges
    # -------------------------------------------------------------
    # Ext E-Commerce -> Kafka transactions
    create_cell(
        root, "e_tx_in", "Transacciones JSON (Port 9094)",
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#EA580C;strokeWidth=2;fontSize=10;fontColor=#7C2D12;labelBackgroundColor=#FFFFFF;",
        is_edge=True, source="ext_ecommerce", target="kafka_topic_tx"
    )

    # Ext Simulator -> Kafka transactions
    create_cell(
        root, "e_sim_in", "Simulación CLI",
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#EA580C;strokeWidth=1.5;dashed=1;fontSize=9;fontColor=#7C2D12;labelBackgroundColor=#FFFFFF;",
        is_edge=True, source="ext_simulator", target="kafka_topic_tx"
    )

    # Kafka transactions -> Rust Consumer
    create_cell(
        root, "e_k_to_consumer", "Consumo Stream Kafka",
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#EA580C;strokeWidth=2;fontSize=10;fontColor=#7C2D12;labelBackgroundColor=#FFFFFF;",
        is_edge=True, source="kafka_topic_tx", target="rust_consumer"
    )

    # Rust Consumer -> Tier 1 Heuristic Engine
    create_cell(
        root, "e_cons_to_engine", "Deserializa & Evalúa (&lt; 2ms)",
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=2;fontSize=10;fontColor=#064E3B;labelBackgroundColor=#FFFFFF;",
        is_edge=True, source="rust_consumer", target="rust_engine"
    )

    # Tier 1 Engine -> Ollama Client (Async trigger)
    create_cell(
        root, "e_engine_to_ollama_cli", "Zona Gris (&gt;=$1500) o Enriquecimiento XAI",
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#8B5CF6;strokeWidth=2;fontSize=9;fontColor=#4C1D95;labelBackgroundColor=#FFFFFF;",
        is_edge=True, source="rust_engine", target="rust_ollama_client"
    )

    # Ollama Client -> Ollama Container
    create_cell(
        root, "e_ollama_req", "HTTP POST /api/generate<br/>(JSON prompt & schema)",
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#9333EA;strokeWidth=2;fontSize=10;fontColor=#581C87;labelBackgroundColor=#FFFFFF;",
        is_edge=True, source="rust_ollama_client", target="ollama_model"
    )

    # Ollama Client -> Rust Producer
    create_cell(
        root, "e_ollama_to_prod", "Alerta enriquecida",
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=1.5;fontSize=9;fontColor=#064E3B;labelBackgroundColor=#FFFFFF;",
        is_edge=True, source="rust_ollama_client", target="rust_producer"
    )

    # Tier 1 Engine directly to Producer (Fast-path if Ollama disabled or sync alert)
    create_cell(
        root, "e_engine_to_prod", "Alerta Regla Dura",
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#CA8A04;strokeWidth=1.5;fontSize=9;fontColor=#713F12;labelBackgroundColor=#FFFFFF;",
        is_edge=True, source="rust_engine", target="rust_producer"
    )

    # Rust Producer -> Kafka fraud-alerts topic
    create_cell(
        root, "e_prod_to_k_alerts", "Publica en 'fraud-alerts'",
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#DC2626;strokeWidth=2;fontSize=10;fontColor=#991B1B;labelBackgroundColor=#FFFFFF;",
        is_edge=True, source="rust_producer", target="kafka_topic_alerts"
    )

    # Rust Web Server -> Dashboard WS Service
    create_cell(
        root, "e_ws_stream", "WebSocket Broadcast: ws://.../ws<br/>(NewTransaction, FraudAlert, Metrics)",
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#2563EB;strokeWidth=2.5;fontSize=10;fontColor=#1E40AF;labelBackgroundColor=#FFFFFF;",
        is_edge=True, source="rust_web_server", target="dash_ws_service"
    )

    # Kafka Broker -> Kafka UI
    create_cell(
        root, "e_k_to_kui", "bootstrap: kafka:9092",
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#6366F1;strokeWidth=1.5;dashed=1;fontSize=9;fontColor=#3730A3;labelBackgroundColor=#FFFFFF;",
        is_edge=True, source="c_kafka", target="c_kafka_ui"
    )

    # Analyst -> Dashboard
    create_cell(
        root, "e_analyst_dash", "HTTP :4200 (Dashboard)",
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#2563EB;strokeWidth=1.5;dashed=1;fontSize=9;fontColor=#1E40AF;labelBackgroundColor=#FFFFFF;",
        is_edge=True, source="ext_analyst", target="c_dashboard"
    )

    # DevOps -> Kafka UI & Swagger UI
    create_cell(
        root, "e_devops_access", "HTTP :8085 / :3000 (Swagger)",
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#64748B;strokeWidth=1.5;dashed=1;fontSize=9;fontColor=#334155;labelBackgroundColor=#FFFFFF;",
        is_edge=True, source="ext_devops", target="rust_web_server"
    )

    return root

def build_process_diagram():
    root = ET.Element("root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    # Title Banner
    create_cell(
        root, "proc_banner",
        "<b>DIAGRAMA DE PROCESOS: DETECCIÓN Y EVALUACIÓN DE FRAUDE EN DOS CAPAS</b><br/><font style='font-size:12px;font-weight:normal;color:#94A3B8;'>Flujo de Eventos: Ingesta Kafka KRaft ➔ Filtro Heurístico Ultrarrápido (&lt;2ms) ➔ Análisis Cognitivo IA (Qwen 2.5) ➔ Alerta & Dashboard</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#0F172A;strokeColor=#1E293B;fontColor=#F8FAFC;fontSize=15;align=center;verticalAlign=middle;shadow=1;",
        x=40, y=20, width=1280, height=60
    )

    # Swimlanes / Lanes
    # Lane 1: Ingesta & Streaming (Kafka)
    create_cell(
        root, "lane_ingest",
        "<b>1. INGESTA &amp; STREAMING</b><br/><font style='font-size:10px;font-weight:normal;'>Pasarelas de Pago &amp; Apache Kafka KRaft</font>",
        "swimlane;whiteSpace=wrap;html=1;collapsible=0;dropTarget=0;fillColor=#FFF7ED;strokeColor=#EA580C;strokeWidth=2;fontColor=#7C2D12;fontSize=11;fontStyle=1;startSize=40;arcSize=6;",
        x=40, y=95, width=280, height=880
    )

    # Lane 2: Tier 1 Fast-Path Heurístico (Rust Core API)
    create_cell(
        root, "lane_tier1",
        "<b>2. TIER 1: FAST-PATH HEURÍSTICO (&lt; 2ms)</b><br/><font style='font-size:10px;font-weight:normal;'>Motor en Memoria (Rust Tokio + rdkafka)</font>",
        "swimlane;whiteSpace=wrap;html=1;collapsible=0;dropTarget=0;fillColor=#ECFDF5;strokeColor=#059669;strokeWidth=2;fontColor=#064E3B;fontSize=11;fontStyle=1;startSize=40;arcSize=6;",
        x=330, y=95, width=340, height=880
    )

    # Lane 3: Tier 2 Análisis Cognitivo IA (Ollama Qwen 2.5)
    create_cell(
        root, "lane_tier2",
        "<b>3. TIER 2: EVALUACIÓN COGNITIVA IA</b><br/><font style='font-size:10px;font-weight:normal;'>Ollama + Qwen 2.5 1.5B (Inferencia CPU Local)</font>",
        "swimlane;whiteSpace=wrap;html=1;collapsible=0;dropTarget=0;fillColor=#FAF5FF;strokeColor=#9333EA;strokeWidth=2;fontColor=#581C87;fontSize=11;fontStyle=1;startSize=40;arcSize=6;",
        x=680, y=95, width=320, height=880
    )

    # Lane 4: Notificación & Auditoría (Dashboard & Kafka)
    create_cell(
        root, "lane_notify",
        "<b>4. DIFUSIÓN &amp; AUDITORÍA EN VIVO</b><br/><font style='font-size:10px;font-weight:normal;'>Kafka Topic <code>fraud-alerts</code> &amp; Dashboard Angular</font>",
        "swimlane;whiteSpace=wrap;html=1;collapsible=0;dropTarget=0;fillColor=#EFF6FF;strokeColor=#2563EB;strokeWidth=2;fontColor=#1E40AF;fontSize=11;fontStyle=1;startSize=40;arcSize=6;",
        x=1010, y=95, width=310, height=880
    )

    # --- Lane 1 Items ---
    create_cell(
        root, "p_start",
        "<b>INICIO</b><br/><font style='font-size:10px;'>Cliente realiza compra en E-Commerce</font>",
        "ellipse;whiteSpace=wrap;html=1;fillColor=#DCFCE7;strokeColor=#16A34A;strokeWidth=2;fontColor=#14532D;fontSize=11;align=center;",
        x=80, y=150, width=200, height=60
    )

    create_cell(
        root, "p_publish_kafka",
        "<b>Publicación a Kafka</b><br/><font style='font-size:10px;color:#7C2D12;'>Evento JSON serializado al tópico:<br/><code>transactions</code></font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#FFEDD5;strokeColor=#EA580C;strokeWidth=1.5;fontColor=#7C2D12;fontSize=11;align=center;",
        x=80, y=240, width=200, height=65
    )

    create_cell(
        root, "p_kafka_broker",
        "<b>Broker Kafka KRaft</b><br/><font style='font-size:10px;color:#7C2D12;'>Partición asignada &amp; Offset persistido</font>",
        "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=10;fillColor=#FED7AA;strokeColor=#C2410C;strokeWidth=1.5;fontColor=#7C2D12;fontSize=10;align=center;",
        x=115, y=340, width=130, height=70
    )

    # --- Lane 2 Items ---
    create_cell(
        root, "p_rust_consume",
        "<b>Consumo Asíncrono de Stream</b><br/><font style='font-size:10px;color:#064E3B;'><code>StreamConsumer::recv().await</code><br/>Deserialización en <code>Transaction</code> struct</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#D1FAE5;strokeColor=#059669;strokeWidth=1.5;fontColor=#064E3B;fontSize=10;align=center;",
        x=350, y=240, width=300, height=55
    )

    create_cell(
        root, "p_notify_new_tx",
        "<b>Notificación de Ingreso</b><br/><font style='font-size:10px;color:#1E3A8A;'>Emite <code>DashboardEvent::NewTransaction</code><br/>Actualiza TPS y contador de transacciones</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#DBEAFE;strokeColor=#3B82F6;strokeWidth=1.5;fontColor=#1E3A8A;fontSize=10;align=center;",
        x=350, y=320, width=300, height=50
    )

    create_cell(
        root, "p_eval_rules",
        "<b>Evaluación Tier 1 en Memoria (&lt; 2ms)</b><br/><font style='font-size:9.5px;color:#713F12;'><b><code>FraudRuleEngine::evaluate(&amp;tx)</code></b><br/>1. Monto &gt;= $5,000 (Monto Excesivo)<br/>2. Historial de usuario &gt; 3 ops en 30s (Velocidad)<br/>3. País en [NK, SY, IR, RU] (Geo Riesgo)<br/>4. Monto &lt;= $1.00 (Prueba de Tarjeta)</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#FEF08A;strokeColor=#CA8A04;strokeWidth=2;fontColor=#713F12;fontSize=10;align=center;shadow=1;",
        x=350, y=395, width=300, height=95
    )

    create_cell(
        root, "d_rule_triggered",
        "¿Se activó<br/>alguna regla?",
        "rhombus;whiteSpace=wrap;html=1;fillColor=#FEF9C3;strokeColor=#CA8A04;strokeWidth=2;fontColor=#713F12;fontSize=11;fontStyle=1;align=center;",
        x=420, y=520, width=160, height=80
    )

    create_cell(
        root, "p_create_alert_obj",
        "<b>Genera Alerta Base</b><br/><font style='font-size:9.5px;color:#991B1B;'>• Asigna UUID Alerta<br/>• Severidad: CRITICAL / HIGH / MED<br/>• Score inicial: 65 - 95<br/>• Despacha <code>tokio::spawn</code> asíncrono</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#FEE2E2;strokeColor=#DC2626;strokeWidth=1.5;fontColor=#991B1B;fontSize=10;align=center;",
        x=350, y=640, width=300, height=65
    )

    create_cell(
        root, "d_gray_zone",
        "¿Transacción en<br/>Zona Gris?<br/><font style='font-size:9px;'>(Monto &gt;= $1500 &amp; IA Activa)</font>",
        "rhombus;whiteSpace=wrap;html=1;fillColor=#F3E8FF;strokeColor=#9333EA;strokeWidth=1.5;fontColor=#581C87;fontSize=10;fontStyle=1;align=center;",
        x=420, y=745, width=160, height=80
    )

    create_cell(
        root, "p_tx_approved",
        "<b>✅ Transacción Aprobada</b><br/><font style='font-size:10px;color:#14532D;'>Sin indicios de fraude.<br/>Tiempo de decisión: &lt; 2ms</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#DCFCE7;strokeColor=#16A34A;strokeWidth=2;fontColor=#14532D;fontSize=11;align=center;",
        x=400, y=870, width=200, height=55
    )

    # --- Lane 3 Items ---
    create_cell(
        root, "p_ai_enrich_req",
        "<b>Solicitud de Explicabilidad (XAI)</b><br/><font style='font-size:10px;color:#581C87;'><code>tokio::spawn</code> envía prompt estructurado:<br/>Transacción + Regla Heurística disparada</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#F3E8FF;strokeColor=#9333EA;strokeWidth=1.5;fontColor=#581C87;fontSize=10;align=center;",
        x=700, y=630, width=280, height=60
    )

    create_cell(
        root, "p_ollama_inference",
        "<b>Inferencia en Ollama (CPU)</b><br/><font style='font-size:10px;color:#4C1D95;'><b>Modelo: <code>qwen2.5:1.5b</code></b><br/>Genera JSON estructurado:<br/><code>{is_fraud, confidence, risk_level, explanation}</code></font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#EDE9FE;strokeColor=#7C3AED;strokeWidth=2;fontColor=#4C1D95;fontSize=10;align=center;shadow=1;",
        x=700, y=715, width=280, height=75
    )

    create_cell(
        root, "p_ai_audit_req",
        "<b>Auditoría Cognitiva de Anomalías</b><br/><font style='font-size:10px;color:#581C87;'>Evalúa coherencia de Merchant vs IP,<br/>país del emisor y monto moderado</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#F3E8FF;strokeColor=#9333EA;strokeWidth=1.5;fontColor=#581C87;fontSize=10;align=center;",
        x=700, y=810, width=280, height=55
    )

    create_cell(
        root, "d_ai_decision",
        "¿IA clasifica Fraude<br/>con Confianza &gt;= 80%?",
        "rhombus;whiteSpace=wrap;html=1;fillColor=#EDE9FE;strokeColor=#7C3AED;strokeWidth=1.5;fontColor=#4C1D95;fontSize=10;fontStyle=1;align=center;",
        x=760, y=880, width=160, height=75
    )

    # --- Lane 4 Items ---
    create_cell(
        root, "p_enrich_alert",
        "<b>Enriquecimiento de Alerta</b><br/><font style='font-size:10px;color:#991B1B;'>• Se adjunta explicación: <code>[Qwen 2.5 IA]: ...</code><br/>• Si confianza &gt; 85%, eleva score final</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#FEE2E2;strokeColor=#DC2626;strokeWidth=1.5;fontColor=#991B1B;fontSize=10;align=center;",
        x=1030, y=630, width=270, height=60
    )

    create_cell(
        root, "p_kafka_publish_alert",
        "<b>Publicación a Kafka</b><br/><font style='font-size:10px;color:#7C2D12;'>Emite al topic: <code>fraud-alerts</code><br/>Para sistemas de bloqueo / auditoría externa</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#FFEDD5;strokeColor=#EA580C;strokeWidth=1.5;fontColor=#7C2D12;fontSize=10;align=center;",
        x=1030, y=715, width=270, height=55
    )

    create_cell(
        root, "p_ws_broadcast",
        "<b>WebSocket Broadcast al Dashboard</b><br/><font style='font-size:10px;color:#1E3A8A;'>Emite <code>DashboardEvent::FraudAlertDetected</code></font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#DBEAFE;strokeColor=#3B82F6;strokeWidth=1.5;fontColor=#1E3A8A;fontSize=10;align=center;",
        x=1030, y=795, width=270, height=50
    )

    create_cell(
        root, "p_dashboard_render",
        "<b>Visualización en Tablero Angular 21</b><br/><font style='font-size:9.5px;color:#1E3A8A;'>• Tarjeta animada en feed de alertas<br/>• Badge de severidad (CRITICAL / HIGH)<br/>• Recuadro con chip 🤖 <b>Qwen 2.5 1.5B (Ollama)</b><br/>• Incremento reactivo de $ Retenido acumulado</font>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#EFF6FF;strokeColor=#1D4ED8;strokeWidth=2;fontColor=#1E3A8A;fontSize=10;align=center;shadow=1;",
        x=1030, y=865, width=270, height=75
    )

    # --- Connections (Process Edges) ---
    # Start -> Publish Kafka
    create_cell(root, "pe_1", "POST Tx", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#EA580C;strokeWidth=2;", is_edge=True, source="p_start", target="p_publish_kafka")
    # Publish Kafka -> Kafka Broker
    create_cell(root, "pe_2", "Stream", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#EA580C;strokeWidth=2;", is_edge=True, source="p_publish_kafka", target="p_kafka_broker")
    # Kafka Broker -> Rust Consume
    create_cell(root, "pe_3", "rdkafka recv()", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#EA580C;strokeWidth=2;fontSize=9;labelBackgroundColor=#FFFFFF;", is_edge=True, source="p_kafka_broker", target="p_rust_consume")
    # Rust Consume -> Notify New Tx
    create_cell(root, "pe_4", "Evento", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#059669;strokeWidth=2;", is_edge=True, source="p_rust_consume", target="p_notify_new_tx")
    # Notify New Tx -> Eval Rules
    create_cell(root, "pe_5", "Inicia Reglas", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#059669;strokeWidth=2;", is_edge=True, source="p_notify_new_tx", target="p_eval_rules")
    # Eval Rules -> Decision 1
    create_cell(root, "pe_6", "", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#CA8A04;strokeWidth=2;", is_edge=True, source="p_eval_rules", target="d_rule_triggered")
    
    # Decision 1 -> SÍ -> Create Alert Base
    create_cell(root, "pe_7_yes", "<b>SÍ (Fraude Detectado)</b>", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#DC2626;strokeWidth=2.5;fontColor=#DC2626;fontSize=10;labelBackgroundColor=#FFFFFF;", is_edge=True, source="d_rule_triggered", target="p_create_alert_obj")
    
    # Decision 1 -> NO -> Decision Gray Zone
    create_cell(root, "pe_7_no", "<b>NO (Pasa reglas)</b>", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#64748B;strokeWidth=2;fontColor=#475569;fontSize=10;labelBackgroundColor=#FFFFFF;", is_edge=True, source="d_rule_triggered", target="d_gray_zone")

    # Create Alert Base -> AI Enrich Request
    create_cell(root, "pe_8", "tokio::spawn", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#9333EA;strokeWidth=2;fontColor=#581C87;fontSize=9;labelBackgroundColor=#FFFFFF;", is_edge=True, source="p_create_alert_obj", target="p_ai_enrich_req")

    # AI Enrich Req -> Ollama Inference
    create_cell(root, "pe_9", "HTTP POST", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#7C3AED;strokeWidth=2;", is_edge=True, source="p_ai_enrich_req", target="p_ollama_inference")

    # Ollama Inference -> Enrich Alert
    create_cell(root, "pe_10", "JSON XAI", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#9333EA;strokeWidth=2;fontSize=9;labelBackgroundColor=#FFFFFF;", is_edge=True, source="p_ollama_inference", target="p_enrich_alert")

    # Enrich Alert -> Kafka Publish Alert
    create_cell(root, "pe_11", "Alerta Completa", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#EA580C;strokeWidth=2;", is_edge=True, source="p_enrich_alert", target="p_kafka_publish_alert")

    # Kafka Publish Alert -> WS Broadcast
    create_cell(root, "pe_12", "rdkafka OK", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#2563EB;strokeWidth=2;", is_edge=True, source="p_kafka_publish_alert", target="p_ws_broadcast")

    # WS Broadcast -> Dashboard Render
    create_cell(root, "pe_13", "WebSocket Push", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#2563EB;strokeWidth=2.5;fontColor=#1E40AF;fontSize=9;labelBackgroundColor=#FFFFFF;", is_edge=True, source="p_ws_broadcast", target="p_dashboard_render")

    # Decision Gray Zone -> SÍ -> AI Audit Req
    create_cell(root, "pe_14_gray_yes", "<b>SÍ (Auditar)</b>", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#9333EA;strokeWidth=2;fontColor=#581C87;fontSize=9;labelBackgroundColor=#FFFFFF;", is_edge=True, source="d_gray_zone", target="p_ai_audit_req")

    # Decision Gray Zone -> NO -> Approved
    create_cell(root, "pe_14_gray_no", "<b>NO (&lt; $1500)</b>", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#16A34A;strokeWidth=2;fontColor=#16A34A;fontSize=9;labelBackgroundColor=#FFFFFF;", is_edge=True, source="d_gray_zone", target="p_tx_approved")

    # AI Audit Req -> AI Decision
    create_cell(root, "pe_15", "Ollama Inferencia", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#7C3AED;strokeWidth=2;", is_edge=True, source="p_ai_audit_req", target="d_ai_decision")

    # AI Decision -> SÍ -> Enrich Alert (or direct alert)
    create_cell(root, "pe_16_ai_yes", "<b>SÍ (Fraude Cognitivo)</b>", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#DC2626;strokeWidth=2;fontColor=#DC2626;fontSize=9;labelBackgroundColor=#FFFFFF;", is_edge=True, source="d_ai_decision", target="p_enrich_alert")

    # AI Decision -> NO -> Approved
    create_cell(root, "pe_16_ai_no", "<b>NO (Legítimo)</b>", "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#16A34A;strokeWidth=2;fontColor=#16A34A;fontSize=9;labelBackgroundColor=#FFFFFF;", is_edge=True, source="d_ai_decision", target="p_tx_approved")

    return root

def serialize_diagram(root_element, diagram_id, diagram_name, width=1350, height=900):
    model = ET.Element("mxGraphModel", {
        "dx": "1422", "dy": "794", "grid": "1", "gridSize": "10",
        "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1",
        "fold": "1", "page": "1", "pageScale": "1",
        "pageWidth": str(width), "pageHeight": str(height),
        "background": "#F8FAFC", "math": "0", "shadow": "0"
    })
    model.append(root_element)
    
    diagram = ET.Element("diagram", {"id": diagram_id, "name": diagram_name})
    diagram.append(model)
    return diagram

def prettify_xml(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

def main():
    target_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "diagrams")
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"Directorio de salida para diagramas: {target_dir}")
    
    # 1. Arquitectura
    arch_root = build_architecture_diagram()
    arch_diagram = serialize_diagram(arch_root, "diag_arch", "Arquitectura del Sistema", width=1360, height=860)
    
    mxfile_arch = ET.Element("mxfile", {
        "host": "app.diagrams.net",
        "modified": "2026-10-26T21:00:00.000Z",
        "agent": "Antigravity",
        "version": "24.0.0",
        "type": "device"
    })
    mxfile_arch.append(arch_diagram)
    
    arch_file = os.path.join(target_dir, "arquitectura.drawio")
    with open(arch_file, "w", encoding="utf-8") as f:
        f.write(prettify_xml(mxfile_arch))
    print(f"Generado exitosamente: {arch_file}")
    
    # 2. Procesos
    proc_root = build_process_diagram()
    proc_diagram = serialize_diagram(proc_root, "diag_proc", "Flujo de Procesos y Detección de Fraude", width=1360, height=1020)
    
    mxfile_proc = ET.Element("mxfile", {
        "host": "app.diagrams.net",
        "modified": "2026-10-26T21:00:00.000Z",
        "agent": "Antigravity",
        "version": "24.0.0",
        "type": "device"
    })
    mxfile_proc.append(proc_diagram)
    
    proc_file = os.path.join(target_dir, "procesos.drawio")
    with open(proc_file, "w", encoding="utf-8") as f:
        f.write(prettify_xml(mxfile_proc))
    print(f"Generado exitosamente: {proc_file}")
    
    # 3. Archivo Combinado (Multi-page drawio: Arquitectura + Procesos)
    # Reconstruir elementos para evitar duplicados en el árbol
    arch_root_comb = build_architecture_diagram()
    arch_diag_comb = serialize_diagram(arch_root_comb, "diag_arch_comb", "Arquitectura del Sistema", width=1360, height=860)
    
    proc_root_comb = build_process_diagram()
    proc_diag_comb = serialize_diagram(proc_root_comb, "diag_proc_comb", "Flujo de Procesos", width=1360, height=1020)
    
    mxfile_comb = ET.Element("mxfile", {
        "host": "app.diagrams.net",
        "modified": "2026-10-26T21:00:00.000Z",
        "agent": "Antigravity",
        "version": "24.0.0",
        "type": "device"
    })
    mxfile_comb.append(arch_diag_comb)
    mxfile_comb.append(proc_diag_comb)
    
    comb_file = os.path.join(target_dir, "sistema-completo.drawio")
    with open(comb_file, "w", encoding="utf-8") as f:
        f.write(prettify_xml(mxfile_comb))
    print(f"Generado exitosamente: {comb_file}")

if __name__ == "__main__":
    main()
