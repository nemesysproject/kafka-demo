use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::time::Duration;
use tracing::{debug, error, warn};
use utoipa::ToSchema;

use crate::engine::fraud_rules::Transaction;

#[derive(Clone, Debug, Serialize, Deserialize, ToSchema)]
pub struct AiFraudAnalysis {
    /// Indica si el modelo clasifica la operación como fraudulenta
    #[schema(example = true)]
    pub is_fraud: bool,
    /// Grado de certeza del modelo (0.0 a 1.0)
    #[schema(example = 0.89)]
    pub confidence: f64,
    /// Nivel de riesgo asignado por la IA: LOW, MEDIUM, HIGH, CRITICAL
    #[schema(example = "HIGH")]
    pub risk_level: String,
    /// Razón explicativa generada en lenguaje natural
    #[schema(example = "Monto elevado con comportamiento de compra atípico y cambio repentino de ubicación geográfica.")]
    pub explanation: String,
    /// Nombre del modelo local de Ollama utilizado
    #[schema(example = "qwen2.5:1.5b")]
    pub model: String,
}

#[derive(Deserialize)]
struct OllamaGenerateResponse {
    response: String,
}

#[derive(Deserialize)]
struct AiStructuredResponse {
    #[serde(default)]
    is_fraud: bool,
    #[serde(default)]
    confidence: f64,
    #[serde(default)]
    risk_level: Option<String>,
    #[serde(default)]
    explanation: String,
}

#[derive(Clone)]
pub struct OllamaClient {
    client: Client,
    pub base_url: String,
    pub model: String,
    pub enabled: bool,
}

impl OllamaClient {
    pub fn new(base_url: String, model: String, enabled: bool) -> Self {
        let client = Client::builder()
            .timeout(Duration::from_secs(8))
            .build()
            .unwrap_or_default();

        Self {
            client,
            base_url,
            model,
            enabled,
        }
    }

    /// Comprueba si la API de Ollama está accesible
    pub async fn is_available(&self) -> bool {
        if !self.enabled {
            return false;
        }

        let url = format!("{}/api/tags", self.base_url);
        match self.client.get(&url).send().await {
            Ok(resp) => resp.status().is_success(),
            Err(_) => false,
        }
    }

    /// Analiza una transacción mediante el modelo SLM (Qwen 2.5 1.5B)
    pub async fn analyze_transaction(
        &self,
        tx: &Transaction,
        preliminary_reason: Option<&str>,
    ) -> Option<AiFraudAnalysis> {
        if !self.enabled {
            debug!("Ollama AI analysis deshabilitado");
            return None;
        }

        let url = format!("{}/api/generate", self.base_url);
        let reason_context = preliminary_reason.unwrap_or("Evaluación heurística preventiva o de zona gris");

        let prompt = format!(
            "Actúa como un motor de IA para detección de fraude financiero y comercio electrónico. \
            Analiza de forma estricta los siguientes datos de la transacción:\n\
            - ID: {id}\n\
            - Usuario: {user}\n\
            - Monto: ${amount:.2} {currency}\n\
            - Comercio: {merchant}\n\
            - País origen: {country}\n\
            - IP del cliente: {ip}\n\
            - Detección previa del motor: {reason}\n\n\
            Instrucciones:\n\
            1. Determina si el evento es fraudulento o anómalo (is_fraud: true/false).\n\
            2. Asigna una confianza numérica entre 0.0 y 1.0 (confidence).\n\
            3. Asigna un nivel de severidad de riesgo (risk_level: 'LOW', 'MEDIUM', 'HIGH' o 'CRITICAL').\n\
            4. Genera una explicación concisa en español (1-2 oraciones) indicando por qué se considera riesgosa o legítima (explanation).\n\
            Devuelve ÚNICAMENTE un JSON con las claves exactas: is_fraud, confidence, risk_level, explanation.",
            id = tx.id,
            user = tx.user_id,
            amount = tx.amount,
            currency = tx.currency,
            merchant = tx.merchant,
            country = tx.location_country,
            ip = tx.ip_address,
            reason = reason_context
        );

        let body = serde_json::json!({
            "model": self.model,
            "prompt": prompt,
            "stream": false,
            "format": "json"
        });

        debug!("Enviando solicitud de inferencia a Ollama ({}) en {}", self.model, url);

        match self.client.post(&url).json(&body).send().await {
            Ok(response) => {
                if !response.status().is_success() {
                    warn!("Ollama devolvió código de error HTTP: {}", response.status());
                    return None;
                }

                match response.json::<OllamaGenerateResponse>().await {
                    Ok(gen_resp) => {
                        match serde_json::from_str::<AiStructuredResponse>(&gen_resp.response) {
                            Ok(structured) => {
                                let risk_level = structured
                                    .risk_level
                                    .unwrap_or_else(|| if structured.is_fraud { "HIGH".to_string() } else { "LOW".to_string() });

                                Some(AiFraudAnalysis {
                                    is_fraud: structured.is_fraud,
                                    confidence: structured.confidence,
                                    risk_level,
                                    explanation: structured.explanation,
                                    model: self.model.clone(),
                                })
                            }
                            Err(e) => {
                                warn!("Error al parsear el JSON estructurado de Ollama: {}. Respuesta cruda: {}", e, gen_resp.response);
                                // Fallback a usar el texto crudo si tiene contenido
                                if !gen_resp.response.trim().is_empty() {
                                    Some(AiFraudAnalysis {
                                        is_fraud: preliminary_reason.is_some(),
                                        confidence: 0.75,
                                        risk_level: "MEDIUM".to_string(),
                                        explanation: gen_resp.response.chars().take(200).collect(),
                                        model: self.model.clone(),
                                    })
                                } else {
                                    None
                                }
                            }
                        }
                    }
                    Err(e) => {
                        error!("Fallo al deserializar la respuesta de Ollama: {:?}", e);
                        None
                    }
                }
            }
            Err(e) => {
                warn!("No se pudo conectar con Ollama en {} ({:?}). Operando en modo degradado (solo reglas).", self.base_url, e);
                None
            }
        }
    }
}
