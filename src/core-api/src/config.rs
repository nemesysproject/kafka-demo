use std::env;

#[derive(Clone, Debug)]
pub struct AppConfig {
    pub kafka_brokers: String,
    pub transactions_topic: String,
    pub fraud_alerts_topic: String,
    pub consumer_group_id: String,
    pub server_host: String,
    pub server_port: u16,
    pub max_amount_threshold: f64,
    pub ollama_url: String,
    pub ollama_model: String,
    pub ollama_enabled: bool,
}

impl AppConfig {
    pub fn from_env() -> Self {
        Self {
            kafka_brokers: env::var("KAFKA_BROKERS").unwrap_or_else(|_| "localhost:9094".to_string()),
            transactions_topic: env::var("TRANSACTIONS_TOPIC").unwrap_or_else(|_| "transactions".to_string()),
            fraud_alerts_topic: env::var("FRAUD_ALERTS_TOPIC").unwrap_or_else(|_| "fraud-alerts".to_string()),
            consumer_group_id: env::var("KAFKA_GROUP_ID").unwrap_or_else(|_| "fraud-detection-core".to_string()),
            server_host: env::var("SERVER_HOST").unwrap_or_else(|_| "0.0.0.0".to_string()),
            server_port: env::var("PORT")
                .ok()
                .and_then(|p| p.parse::<u16>().ok())
                .unwrap_or(3000),
            max_amount_threshold: env::var("MAX_AMOUNT_THRESHOLD")
                .ok()
                .and_then(|a| a.parse::<f64>().ok())
                .unwrap_or(5000.0),
            ollama_url: env::var("OLLAMA_URL").unwrap_or_else(|_| "http://localhost:11434".to_string()),
            ollama_model: env::var("OLLAMA_MODEL").unwrap_or_else(|_| "qwen2.5:1.5b".to_string()),
            ollama_enabled: env::var("OLLAMA_ENABLED")
                .map(|v| v.to_lowercase() != "false" && v != "0")
                .unwrap_or(true),
        }
    }
}

