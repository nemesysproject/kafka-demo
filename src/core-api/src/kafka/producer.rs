use rdkafka::config::ClientConfig;
use rdkafka::producer::{FutureProducer, FutureRecord};
use std::time::Duration;
use tracing::{error, info};
use crate::engine::{FraudAlert, Transaction};

#[derive(Clone)]
pub struct AlertProducer {
    producer: FutureProducer,
    fraud_topic: String,
    #[allow(dead_code)]
    pub tx_topic: String,
}

impl AlertProducer {
    pub fn new(brokers: &str, fraud_topic: &str, tx_topic: &str) -> Result<Self, rdkafka::error::KafkaError> {
        let producer: FutureProducer = ClientConfig::new()
            .set("bootstrap.servers", brokers)
            .set("message.timeout.ms", "5000")
            .set("acks", "1")
            .create()?;

        Ok(Self {
            producer,
            fraud_topic: fraud_topic.to_string(),
            tx_topic: tx_topic.to_string(),
        })
    }

    /// Publica una alerta de fraude en el tópico de Kafka
    pub async fn send_alert(&self, alert: &FraudAlert) -> Result<(), String> {
        let payload = match serde_json::to_string(alert) {
            Ok(p) => p,
            Err(e) => return Err(format!("Error serializando alerta de fraude: {}", e)),
        };

        let record = FutureRecord::to(&self.fraud_topic)
            .key(&alert.transaction_id)
            .payload(&payload);

        match self.producer.send(record, Duration::from_secs(2)).await {
            Ok(_) => {
                info!("Alerta de fraude publicada en Kafka [{}]", alert.alert_id);
                Ok(())
            }
            Err((e, _)) => {
                error!("Error publicando alerta de fraude en Kafka: {:?}", e);
                Err(e.to_string())
            }
        }
    }

    /// Publica una transacción simulada en el tópico 'transactions'
    #[allow(dead_code)]
    pub async fn send_transaction(&self, tx: &Transaction) -> Result<(), String> {
        let payload = match serde_json::to_string(tx) {
            Ok(p) => p,
            Err(e) => return Err(format!("Error serializando transacción: {}", e)),
        };

        let record = FutureRecord::to(&self.tx_topic)
            .key(&tx.id)
            .payload(&payload);

        match self.producer.send(record, Duration::from_secs(2)).await {
            Ok(_) => Ok(()),
            Err((e, _)) => {
                error!("Error enviando transacción simulada: {:?}", e);
                Err(e.to_string())
            }
        }
    }
}
