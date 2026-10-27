# 📐 Diagramas del Sistema en Formato Draw.io

Este directorio contiene los diagramas de arquitectura técnica y flujo de procesos del **Sistema de Detección de Fraude en Tiempo Real**, creados en formato XML nativo de **[Draw.io](https://app.diagrams.net/)** (diagrams.net).

---

## 📁 Archivos Disponibles

| Archivo | Tipo | Descripción |
| :--- | :--- | :--- |
| **[`arquitectura.drawio`](./arquitectura.drawio)** | Arquitectura Técnica | Vista detallada de componentes, contenedores Docker Compose (`fraud-network`), puertos, volúmenes de persistencia, tópicos de Apache Kafka KRaft, endpoints del Core API en Rust, motor local de IA Ollama y Tablero en Angular 21. |
| **[`procesos.drawio`](./procesos.drawio)** | Flujo de Procesos (BPMN) | Diagrama de flujo paso a paso desde el checkout del cliente, ingesta en Kafka, filtrado heurístico ultrarrápido (**Tier 1 en memoria < 2ms**), auditoría cognitiva de zona gris y explicabilidad XAI (**Tier 2 Ollama Qwen 2.5**), hasta la difusión en Kafka y el feed reactivo con WebSocket. |
| **[`sistema-completo.drawio`](./sistema-completo.drawio)** | Multipágina Unificado | Archivo unificado de Draw.io con ambas páginas para facilitar la visualización, navegación y exportación consolidada en una sola sesión. |

---

## 🛠️ Cómo Visualizar y Editar los Diagramas

### Opción 1: En Visual Studio Code (Recomendado)
1. Instala la extensión oficial **[Draw.io Integration](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio)** de Henning Dieterichs.
2. Abre cualquiera de los archivos `.drawio` directamente en el editor. Se abrirá la interfaz gráfica interactiva dentro de VS Code.

### Opción 2: Draw.io Web (diagrams.net)
1. Ingresa a **[app.diagrams.net](https://app.diagrams.net/)**.
2. Selecciona **Open Existing Diagram** (Abrir diagrama existente).
3. Selecciona cualquiera de los archivos `.drawio` de esta carpeta.

### Opción 3: Draw.io Desktop App
1. Descarga e instala [Draw.io Desktop](https://www.drawio.com/).
2. Abre los archivos `.drawio` directamente.

---

## 🔄 Regeneración Automatizada

Los diagramas están construidos con un script generador en Python que garantiza precisión en las coordenadas, estilos coherentes y validación XML estricta.

Para regenerar o modificar los diagramas programáticamente:
```bash
python scripts/generate_diagrams.py
```

---

## 🎨 Paleta Visual y Convenciones

* **Infraestructura Docker:** Contenedor azul slate (`#0284C7`), red bridge `fraud-network`.
* **Mensajería Kafka KRaft:** Naranja cálido (`#EA580C`), tópicos `transactions` y `fraud-alerts`.
* **Motor Core API (Rust):** Esmeralda (`#059669`), subcomponentes de Tokio, rdkafka y Axum.
* **Tier 1 Heurístico:** Amarillo / Ámbar (`#CA8A04`), reglas duras evaluadas en memoria (< 2ms).
* **Tier 2 Motor IA (Ollama):** Púrpura / Violeta (`#9333EA`), inferencia del modelo SLM `qwen2.5:1.5b`.
* **Dashboard (Angular 21):** Azul eléctrico (`#2563EB`), Angular Signals y cliente WebSocket.
