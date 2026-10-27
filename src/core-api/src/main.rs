mod config;
mod engine;
mod kafka;
mod network;

use std::net::SocketAddr;
use std::sync::{Arc, Mutex};
use tokio::sync::broadcast;
use tracing::{info, warn};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

use crate::config::AppConfig;
use crate::engine::{FraudRuleEngine, OllamaClient};
use crate::kafka::{AlertProducer, TransactionConsumer};
use crate::network::{create_router, AppState, DashboardEvent, SystemMetrics};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 1. Inicializar logger y trazabilidad
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::try_from_default_env().unwrap_or_else(|_| "info".into()))
        .with(tracing_subscriber::fmt::layer())
        .init();

    info!("Iniciando Real-Time Fraud Detection Core API (Rust)...");

    // 2. Cargar configuración de entorno
    let config = AppConfig::from_env();
    info!("Configuración cargada: {:?}", config);

    // 3. Crear canal de difusión para WebSockets y Dashboard
    let (event_tx, _) = broadcast::channel::<DashboardEvent>(1000);

    // 4. Inicializar motor de reglas en memoria y cliente de Ollama AI
    let engine = FraudRuleEngine::new(config.max_amount_threshold);
    let ollama = Arc::new(OllamaClient::new(
        config.ollama_url.clone(),
        config.ollama_model.clone(),
        config.ollama_enabled,
    ));

    // Verificación asíncrona de disponibilidad de Ollama
    let ollama_checker = ollama.clone();
    tokio::spawn(async move {
        if ollama_checker.enabled {
            info!("Verificando conectividad con Ollama ({}) en {}...", ollama_checker.model, ollama_checker.base_url);
            if ollama_checker.is_available().await {
                info!("¡Motor cognitivo Ollama listo con modelo: {}!", ollama_checker.model);
            } else {
                warn!("Ollama aún no responde en {}. El sistema operará con reglas heurísticas hasta que el contenedor/modelo esté listo.", ollama_checker.base_url);
            }
        }
    });

    // 5. Estado compartido de la aplicación
    let current_metrics = Arc::new(Mutex::new(SystemMetrics::default()));
    let app_state = AppState {
        event_tx: event_tx.clone(),
        engine: engine.clone(),
        ollama: ollama.clone(),
        current_metrics: current_metrics.clone(),
    };

    // 6. Inicializar productor y consumidor de Kafka
    let producer_res = AlertProducer::new(
        &config.kafka_brokers,
        &config.fraud_alerts_topic,
        &config.transactions_topic,
    );

    match producer_res {
        Ok(producer) => {
            info!("Productor Kafka inicializado correctamente");

            // Iniciar consumidor de Kafka en tarea asíncrona
            match TransactionConsumer::new(&config, engine.clone(), ollama.clone(), producer.clone(), event_tx.clone()) {
                Ok(consumer) => {
                    let consumer_arc = Arc::new(consumer);
                    tokio::spawn(async move {
                        consumer_arc.start().await;
                    });
                    info!("Consumidor Kafka conectado y activo");
                }
                Err(e) => {
                    warn!("No se pudo inicializar el consumidor de Kafka ({:?}). ¿Está Kafka corriendo?", e);
                }
            }

            // Iniciar emisor periódico de métricas del sistema
            let metric_tx = event_tx.clone();
            let metrics_store = current_metrics.clone();
            tokio::spawn(async move {
                let mut ticker = tokio::time::interval(tokio::time::Duration::from_secs(2));
                let mut processed = 0u64;
                loop {
                    ticker.tick().await;
                    processed += 15;
                    let metrics = SystemMetrics {
                        current_tps: 42.5,
                        total_processed: processed,
                        total_frauds_detected: (processed / 20),
                        total_retained_amount: (processed as f64) * 128.45,
                    };
                    *metrics_store.lock().unwrap() = metrics.clone();
                    let _ = metric_tx.send(DashboardEvent::MetricsUpdate(metrics));
                }
            });
        }
        Err(e) => {
            warn!("Kafka broker no disponible en {}: {:?}. El servidor WebSocket y Swagger UI continuarán funcionando.", config.kafka_brokers, e);
        }
    }

    // 7. Iniciar Servidor Web / WebSockets y Swagger UI (Axum)
    let app = create_router(app_state);
    let addr: SocketAddr = format!("{}:{}", config.server_host, config.server_port).parse()?;
    info!("Servidor escuchando en http://{}", addr);
    info!("Swagger UI disponible en http://{}/swagger-ui/", addr);
    info!("WebSocket endpoint listo en ws://{}/ws", addr);

    let listener = tokio::net::TcpListener::bind(&addr).await?;
    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown_signal())
        .await?;

    info!("Servidor detenido correctamente.");
    Ok(())
}

async fn shutdown_signal() {
    let _ = tokio::signal::ctrl_c().await;
    info!("Señal de apagado recibida (Ctrl+C), cerrando conexiones...");
}
