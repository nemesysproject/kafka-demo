use chrono::Utc;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, VecDeque};
use std::sync::{Arc, Mutex};
use uuid::Uuid;

use utoipa::ToSchema;

#[derive(Clone, Debug, Serialize, Deserialize, ToSchema)]
pub struct Transaction {
    /// Identificador único de la transacción
    #[schema(example = "tx-98234")]
    pub id: String,
    /// Identificador del usuario o cliente
    #[schema(example = "usr-4019")]
    pub user_id: String,
    /// Monto numérico de la transacción
    #[schema(example = 1250.50)]
    pub amount: f64,
    /// Moneda en formato ISO (ej. USD, EUR)
    #[schema(example = "USD")]
    pub currency: String,
    /// Número de tarjeta ofuscado
    #[schema(example = "4111-XXXX-XXXX-1234")]
    pub card_number_masked: String,
    /// Nombre del comercio o merchant
    #[schema(example = "TechStore Online")]
    pub merchant: String,
    /// Código ISO de país donde se origina la operación
    #[schema(example = "US")]
    pub location_country: String,
    /// Dirección IP del cliente
    #[schema(example = "192.168.1.100")]
    pub ip_address: String,
    /// Marca de tiempo Unix en segundos
    #[schema(example = 1700000000)]
    pub timestamp: i64,
}

#[derive(Clone, Debug, Serialize, Deserialize, ToSchema)]
pub struct FraudAlert {
    /// Identificador único de la alerta de fraude
    #[schema(example = "alt-b293c04")]
    pub alert_id: String,
    /// Identificador de la transacción que originó la alerta
    #[schema(example = "tx-98234")]
    pub transaction_id: String,
    /// Identificador del usuario implicado
    #[schema(example = "usr-4019")]
    pub user_id: String,
    /// Monto de la transacción
    #[schema(example = 1250.50)]
    pub amount: f64,
    /// Moneda
    #[schema(example = "USD")]
    pub currency: String,
    /// Motivo o regla de detección disparada
    #[schema(example = "Monto excesivo superior al umbral permitido")]
    pub reason: String,
    /// Nivel de criticidad: LOW, MEDIUM, HIGH, CRITICAL
    #[schema(example = "CRITICAL")]
    pub severity: String,
    /// Puntaje de riesgo (0-100)
    #[schema(example = 95)]
    pub score: u8,
    /// Marca de tiempo Unix de la detección
    #[schema(example = 1700000000)]
    pub timestamp: i64,
    /// Explicación analítica o razonamiento generado por el modelo de IA local (Ollama Qwen 2.5)
    #[schema(example = "Patrón anómalo: compra repetitiva con IP no habitual.")]
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub ai_analysis: Option<String>,
}

#[derive(Clone)]
pub struct FraudRuleEngine {
    max_amount: f64,
    // Tracks timestamp history per user for velocity checks
    user_history: Arc<Mutex<HashMap<String, VecDeque<i64>>>>,
}

impl FraudRuleEngine {
    pub fn new(max_amount: f64) -> Self {
        Self {
            max_amount,
            user_history: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    /// Evaluates transaction rules in < 2ms memory execution
    pub fn evaluate(&self, tx: &Transaction) -> Option<FraudAlert> {
        let now = Utc::now().timestamp();

        // 1. High Amount Rule
        if tx.amount >= self.max_amount {
            return Some(FraudAlert {
                alert_id: Uuid::new_v4().to_string(),
                transaction_id: tx.id.clone(),
                user_id: tx.user_id.clone(),
                amount: tx.amount,
                currency: tx.currency.clone(),
                reason: format!("Monto excesivo superior al umbral permitido (${:.2})", self.max_amount),
                severity: "CRITICAL".to_string(),
                score: 95,
                timestamp: now,
                ai_analysis: None,
            });
        }

        // 2. Velocity Check (> 3 transacciones en 30 segundos)
        {
            let mut history = self.user_history.lock().unwrap();
            let timestamps = history.entry(tx.user_id.clone()).or_insert_with(VecDeque::new);

            // Clean older than 30s
            while let Some(&oldest) = timestamps.front() {
                if now - oldest > 30 {
                    timestamps.pop_front();
                } else {
                    break;
                }
            }

            timestamps.push_back(now);

            if timestamps.len() > 3 {
                return Some(FraudAlert {
                    alert_id: Uuid::new_v4().to_string(),
                    transaction_id: tx.id.clone(),
                    user_id: tx.user_id.clone(),
                    amount: tx.amount,
                    currency: tx.currency.clone(),
                    reason: format!(
                        "Alta frecuencia de transacciones (Velocidad anormal: {} ops en 30s)",
                        timestamps.len()
                    ),
                    severity: "HIGH".to_string(),
                    score: 85,
                    timestamp: now,
                    ai_analysis: None,
                });
            }
        }

        // 3. High Risk Location Check
        let high_risk_locations = ["NK", "SY", "IR", "RU"];
        if high_risk_locations.contains(&tx.location_country.to_uppercase().as_str()) {
            return Some(FraudAlert {
                alert_id: Uuid::new_v4().to_string(),
                transaction_id: tx.id.clone(),
                user_id: tx.user_id.clone(),
                amount: tx.amount,
                currency: tx.currency.clone(),
                reason: format!("Transacción originada en zona de alto riesgo: {}", tx.location_country),
                severity: "HIGH".to_string(),
                score: 80,
                timestamp: now,
                ai_analysis: None,
            });
        }

        // 4. Micro-amount Card Testing Rule (repetitive amounts < $1.00)
        if tx.amount <= 1.0 && tx.amount > 0.0 {
            return Some(FraudAlert {
                alert_id: Uuid::new_v4().to_string(),
                transaction_id: tx.id.clone(),
                user_id: tx.user_id.clone(),
                amount: tx.amount,
                currency: tx.currency.clone(),
                reason: "Posible prueba automatizada de tarjeta (Micro-transacción sospechosa)".to_string(),
                severity: "MEDIUM".to_string(),
                score: 65,
                timestamp: now,
                ai_analysis: None,
            });
        }


        None
    }
}
