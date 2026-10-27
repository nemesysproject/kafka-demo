use axum::{
    extract::{
        ws::{Message, WebSocket, WebSocketUpgrade},
        State,
    },
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use futures_util::{sink::SinkExt, stream::StreamExt};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};
use tokio::sync::broadcast;
use tower_http::cors::{Any, CorsLayer};
use tracing::info;
use utoipa::{OpenApi, ToSchema};
use utoipa_swagger_ui::SwaggerUi;

use crate::engine::{AiFraudAnalysis, FraudAlert, FraudRuleEngine, OllamaClient, Transaction};

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(tag = "type", content = "data")]
pub enum DashboardEvent {
    NewTransaction(Transaction),
    FraudAlertDetected(FraudAlert),
    MetricsUpdate(SystemMetrics),
}

#[derive(Clone, Debug, Serialize, Deserialize, Default, ToSchema)]
pub struct SystemMetrics {
    /// Rendimiento actual en transacciones por segundo (TPS)
    #[schema(example = 42.5)]
    pub current_tps: f64,
    /// Total de transacciones financieras procesadas
    #[schema(example = 15200)]
    pub total_processed: u64,
    /// Total de eventos de fraude interceptados y bloqueados
    #[schema(example = 76)]
    pub total_frauds_detected: u64,
    /// Monto acumulado retenido en USD
    #[schema(example = 97622.0)]
    pub total_retained_amount: f64,
}

#[derive(Clone, Debug, Serialize, Deserialize, ToSchema)]
pub struct HealthResponse {
    /// Estado del servicio
    #[schema(example = "UP")]
    pub status: String,
    /// Nombre descriptivo del componente
    #[schema(example = "Fraud Detection Core API (Rust)")]
    pub service: String,
    /// Marca de tiempo ISO-8601
    #[schema(example = "2026-10-22T18:00:00Z")]
    pub timestamp: String,
}

#[derive(Clone, Debug, Serialize, Deserialize, ToSchema)]
pub struct SimulateResponse {
    /// Estado de la simulación
    #[schema(example = "success")]
    pub status: String,
    /// Mensaje explicativo
    #[schema(example = "Transacción procesada por el motor de reglas")]
    pub message: String,
    /// Indica si la transacción disparó una alerta de fraude
    #[schema(example = true)]
    pub fraud_detected: bool,
    /// Detalle de la alerta en caso de detección positiva
    pub alert: Option<FraudAlert>,
}

#[derive(Clone, Debug, Serialize, Deserialize, ToSchema)]
pub struct AiAnalyzeResponse {
    /// Estado de la consulta al modelo IA
    #[schema(example = "success")]
    pub status: String,
    /// Modelo utilizado
    #[schema(example = "qwen2.5:1.5b")]
    pub model: String,
    /// Disponibilidad del servicio Ollama
    #[schema(example = true)]
    pub available: bool,
    /// Resultado del análisis cognitivo
    pub analysis: Option<AiFraudAnalysis>,
}

#[derive(Clone, Debug, Serialize, Deserialize, ToSchema)]
pub struct AiStatusResponse {
    /// Estado del motor IA: ONLINE u OFFLINE
    #[schema(example = "ONLINE")]
    pub status: String,
    /// Nombre del modelo configurado
    #[schema(example = "qwen2.5:1.5b")]
    pub model: String,
    /// Endpoint base de Ollama
    #[schema(example = "http://ollama:11434")]
    pub base_url: String,
    /// Habilitado en la configuración
    #[schema(example = true)]
    pub enabled: bool,
    /// Conectividad confirmada con el servidor
    #[schema(example = true)]
    pub available: bool,
}

#[derive(Clone)]
pub struct AppState {
    pub event_tx: broadcast::Sender<DashboardEvent>,
    pub engine: FraudRuleEngine,
    pub ollama: Arc<OllamaClient>,
    pub current_metrics: Arc<Mutex<SystemMetrics>>,
}

#[derive(OpenApi)]
#[openapi(
    paths(
        health_check,
        get_metrics,
        simulate_transaction,
        analyze_transaction_ai,
        get_ai_status
    ),
    components(
        schemas(
            HealthResponse,
            Transaction,
            FraudAlert,
            SystemMetrics,
            SimulateResponse,
            AiFraudAnalysis,
            AiAnalyzeResponse,
            AiStatusResponse
        )
    ),
    tags(
        (name = "Monitoreo", description = "Verificación de salud y telemetría en tiempo real"),
        (name = "Simulación", description = "Inyección manual de transacciones para testing de reglas"),
        (name = "Inteligencia Artificial", description = "Evaluación cognitiva con modelo Qwen 2.5 1.5B (Ollama)")
    ),
    info(
        title = "Real-Time Fraud Detection System - Core API",
        version = "1.1.0",
        description = "Documentación OpenAPI y consola Swagger UI para el motor concurrente de detección de fraude en tiempo real (Rust + Kafka KRaft + Ollama Qwen 2.5 + WebSockets)."
    )
)]
pub struct ApiDoc;

pub fn create_router(state: AppState) -> Router {
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    Router::new()
        .merge(SwaggerUi::new("/swagger-ui").url("/api-docs/openapi.json", ApiDoc::openapi()))
        .route("/health", get(health_check))
        .route("/api/metrics", get(get_metrics))
        .route("/api/simulate", post(simulate_transaction))
        .route("/api/ai/analyze", post(analyze_transaction_ai))
        .route("/api/ai/status", get(get_ai_status))
        .route("/ws", get(ws_handler))
        .layer(cors)
        .with_state(state)
}

/// Verificación del estado de salud del servicio
#[utoipa::path(
    get,
    path = "/health",
    tag = "Monitoreo",
    responses(
        (status = 200, description = "El servicio se encuentra operativo", body = HealthResponse)
    )
)]
async fn health_check() -> impl IntoResponse {
    Json(HealthResponse {
        status: "UP".to_string(),
        service: "Fraud Detection Core API (Rust)".to_string(),
        timestamp: chrono::Utc::now().to_rfc3339(),
    })
}

/// Obtener las métricas actuales del motor de fraude
#[utoipa::path(
    get,
    path = "/api/metrics",
    tag = "Monitoreo",
    responses(
        (status = 200, description = "Métricas consolidadas de rendimiento y fraude", body = SystemMetrics)
    )
)]
async fn get_metrics(
    State(state): State<AppState>,
) -> impl IntoResponse {
    let metrics = state.current_metrics.lock().unwrap().clone();
    Json(metrics)
}

/// Simular e inyectar una transacción en el motor de reglas y validación IA
#[utoipa::path(
    post,
    path = "/api/simulate",
    tag = "Simulación",
    request_body = Transaction,
    responses(
        (status = 200, description = "Transacción evaluada con éxito", body = SimulateResponse)
    )
)]
async fn simulate_transaction(
    State(state): State<AppState>,
    Json(tx): Json<Transaction>,
) -> impl IntoResponse {
    // 1. Notificar transacción al dashboard
    let _ = state.event_tx.send(DashboardEvent::NewTransaction(tx.clone()));

    // 2. Evaluar mediante el motor de reglas de fraude (< 2ms)
    let mut alert = state.engine.evaluate(&tx);
    let fraud_detected = alert.is_some();

    if let Some(ref mut a) = alert {
        // Enriquecer con Ollama Qwen 2.5 si está disponible
        if state.ollama.enabled {
            if let Some(ai_analysis) = state.ollama.analyze_transaction(&tx, Some(&a.reason)).await {
                a.ai_analysis = Some(format!("[Qwen 2.5 IA]: {}", ai_analysis.explanation));
                if ai_analysis.confidence > 0.85 {
                    a.score = std::cmp::max(a.score, (ai_analysis.confidence * 100.0) as u8);
                }
            }
        }

        // Emitir alerta a WebSocket
        let _ = state.event_tx.send(DashboardEvent::FraudAlertDetected(a.clone()));

        // Actualizar métricas acumuladas
        let mut metrics = state.current_metrics.lock().unwrap();
        metrics.total_processed += 1;
        metrics.total_frauds_detected += 1;
        metrics.total_retained_amount += a.amount;
    } else {
        let mut metrics = state.current_metrics.lock().unwrap();
        metrics.total_processed += 1;
    }

    Json(SimulateResponse {
        status: "success".to_string(),
        message: if fraud_detected {
            "¡Alerta de Fraude detectada por el motor algorítmico y enriquecida con IA!".to_string()
        } else {
            "Transacción legítima aprobada".to_string()
        },
        fraud_detected,
        alert,
    })
}

/// Analizar una transacción directamente con el modelo cognitivo Qwen 2.5 1.5B en Ollama
#[utoipa::path(
    post,
    path = "/api/ai/analyze",
    tag = "Inteligencia Artificial",
    request_body = Transaction,
    responses(
        (status = 200, description = "Evaluación cognitiva realizada por el modelo Qwen 2.5 local", body = AiAnalyzeResponse)
    )
)]
async fn analyze_transaction_ai(
    State(state): State<AppState>,
    Json(tx): Json<Transaction>,
) -> impl IntoResponse {
    let available = state.ollama.is_available().await;
    let analysis = state.ollama.analyze_transaction(&tx, None).await;

    Json(AiAnalyzeResponse {
        status: if analysis.is_some() { "success".to_string() } else { "unavailable_or_error".to_string() },
        model: state.ollama.model.clone(),
        available,
        analysis,
    })
}

/// Verificar el estado y conectividad del servicio de inferencia local Ollama
#[utoipa::path(
    get,
    path = "/api/ai/status",
    tag = "Inteligencia Artificial",
    responses(
        (status = 200, description = "Estado de conectividad y configuración de Ollama", body = AiStatusResponse)
    )
)]
async fn get_ai_status(
    State(state): State<AppState>,
) -> impl IntoResponse {
    let available = state.ollama.is_available().await;
    Json(AiStatusResponse {
        status: if available { "ONLINE".to_string() } else { "OFFLINE_OR_UNAVAILABLE".to_string() },
        model: state.ollama.model.clone(),
        base_url: state.ollama.base_url.clone(),
        enabled: state.ollama.enabled,
        available,
    })
}

async fn ws_handler(
    ws: WebSocketUpgrade,
    State(state): State<AppState>,
) -> impl IntoResponse {
    ws.on_upgrade(move |socket| handle_socket(socket, state))
}

async fn handle_socket(socket: WebSocket, state: AppState) {
    let (mut sender, mut receiver) = socket.split();
    let mut rx = state.event_tx.subscribe();

    info!("Nuevo cliente conectado al dashboard WebSocket");

    let mut send_task = tokio::spawn(async move {
        while let Ok(event) = rx.recv().await {
            if let Ok(msg_text) = serde_json::to_string(&event) {
                if sender.send(Message::Text(msg_text.into())).await.is_err() {
                    break;
                }
            }
        }
    });

    let mut recv_task = tokio::spawn(async move {
        while let Some(Ok(msg)) = receiver.next().await {
            if let Message::Close(_) = msg {
                break;
            }
        }
    });

    tokio::select! {
        _ = (&mut send_task) => recv_task.abort(),
        _ = (&mut recv_task) => send_task.abort(),
    };

    info!("Cliente desconectado del WebSocket");
}
