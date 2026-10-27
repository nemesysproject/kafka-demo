pub mod fraud_rules;
pub mod ollama;

pub use fraud_rules::{FraudAlert, FraudRuleEngine, Transaction};
pub use ollama::{AiFraudAnalysis, OllamaClient};

