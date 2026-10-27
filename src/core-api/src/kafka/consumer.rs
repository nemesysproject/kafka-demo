use rdkafka::config::ClientConfig;
use rdkafka::consumer::{Consumer, StreamConsumer};
use rdkafka::message::Message;
use std::sync::Arc;
use tokio::sync::broadcast;
use tracing::{error, info, warn};

use crate::config::AppConfig;
use crate::engine::{FraudAlert, FraudRuleEngine, OllamaClient, Transaction};
use crate::kafka::producer::AlertProducer;
use crate::network::ws_server::DashboardEvent;

pub struct TransactionConsumer {
    consumer: StreamConsumer,
    engine: FraudRuleEngine,
    ollama: Arc<OllamaClient>,
    producer: AlertProducer,
    event_tx: broadcast::Sender<DashboardEvent>,
}

impl TransactionConsumer {
    pub fn new(
        config: &AppConfig,
        engine: FraudRuleEngine,
        ollama: Arc<OllamaClient>,
        producer: AlertProducer,
        event_tx: broadcast::Sender<DashboardEvent>,
    ) -> Result<Self, rdkafka::error::KafkaError> {
        let consumer: StreamConsumer = ClientConfig::new()
            .set("group.id", &config.consumer_group_id)
            .set("bootstrap.servers", &config.kafka_brokers)
            .set("enable.partition.eof", "false")
            .set("session.timeout.ms", "6000")
            .set("enable.auto.commit", "true")
            .set("auto.offset.reset", "latest")
            .create()?;

        consumer.subscribe(&[&config.transactions_topic])?;
        info!("Suscrito al tópico de transacciones: {}", config.transactions_topic);

        Ok(Self {
            consumer,
            engine,
            ollama,
            producer,
            event_tx,
        })
    }

    pub async fn start(self: Arc<Self>) {
        info!("Iniciando bucle de consumo de eventos de transacciones...");
        loop {
            match self.consumer.recv().await {
                Ok(msg) => {
                    if let Some(payload) = msg.payload() {
                        match serde_json::from_slice::<Transaction>(payload) {
                            Ok(tx) => {
                                // 1. Notificar transacción procesada al dashboard
                                let _ = self.event_tx.send(DashboardEvent::NewTransaction(tx.clone()));

                                // 2. Evaluar reglas de fraude de baja latencia (< 2ms)
                                if let Some(mut alert) = self.engine.evaluate(&tx) {
                                    warn!("¡Fraude preliminar detectado por reglas! Alerta: {:?}", alert);

                                    let ollama_client = self.ollama.clone();
                                    let prod = self.producer.clone();
                                    let event_tx = self.event_tx.clone();
                                    let tx_clone = tx.clone();

                                    // Enriquecimiento cognitivo asíncrono con Ollama (Qwen 2.5 1.5B)
                                    tokio::spawn(async move {
                                        if let Some(ai_analysis) = ollama_client.analyze_transaction(&tx_clone, Some(&alert.reason)).await {
                                            info!("Análisis IA (Qwen 2.5) generado para TX {}: {}", tx_clone.id, ai_analysis.explanation);
                                            alert.ai_analysis = Some(format!("[Qwen 2.5 IA]: {}", ai_analysis.explanation));
                                            if ai_analysis.confidence > 0.85 {
                                                alert.score = std::cmp::max(alert.score, (ai_analysis.confidence * 100.0) as u8);
                                            }
                                        }

                                        // 3. Emitir a Kafka topic 'fraud-alerts'
                                        if let Err(e) = prod.send_alert(&alert).await {
                                            error!("Fallo al enviar alerta a Kafka: {}", e);
                                        }

                                        // 4. Emitir alerta enriquecida al WebSocket del dashboard
                                        let _ = event_tx.send(DashboardEvent::FraudAlertDetected(alert));
                                    });
                                } else {
                                    // 3. Capa de Seguridad Cognitiva para transacciones dudosas en zona gris
                                    // Si no disparó reglas duras pero tiene monto moderado (> $1500)
                                    if tx.amount >= 1500.0 && self.ollama.enabled {
                                        let ollama_client = self.ollama.clone();
                                        let prod = self.producer.clone();
                                        let event_tx = self.event_tx.clone();
                                        let tx_clone = tx.clone();

                                        tokio::spawn(async move {
                                            if let Some(ai_analysis) = ollama_client.analyze_transaction(&tx_clone, None).await {
                                                if ai_analysis.is_fraud && ai_analysis.confidence >= 0.80 {
                                                    warn!("¡Fraude interceptado por IA (Qwen 2.5)! TX {}: {}", tx_clone.id, ai_analysis.explanation);
                                                    let ai_alert = FraudAlert {
                                                        alert_id: uuid::Uuid::new_v4().to_string(),
                                                        transaction_id: tx_clone.id.clone(),
                                                        user_id: tx_clone.user_id.clone(),
                                                        amount: tx_clone.amount,
                                                        currency: tx_clone.currency.clone(),
                                                        reason: "Detección cognitiva IA: Anomalía de comportamiento fuera de patrón".to_string(),
                                                        severity: ai_analysis.risk_level,
                                                        score: (ai_analysis.confidence * 100.0) as u8,
                                                        timestamp: chrono::Utc::now().timestamp(),
                                                        ai_analysis: Some(format!("[Qwen 2.5 IA]: {}", ai_analysis.explanation)),
                                                    };

                                                    let _ = prod.send_alert(&ai_alert).await;
                                                    let _ = event_tx.send(DashboardEvent::FraudAlertDetected(ai_alert));
                                                }
                                            }
                                        });
                                    }
                                }
                            }
                            Err(e) => {
                                error!("Error al deserializar transacción JSON: {:?}", e);
                            }
                        }
                    }
                }
                Err(e) => {
                    error!("Error en consumidor de Kafka: {:?}", e);
                    tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
                }
            }
        }
    }
}
