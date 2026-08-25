# SRE Agent Metrics API

> API asíncrona y de alto rendimiento para la ingesta de telemetría de sistemas Linux, diseñada para recibir métricas desde el bot `sre-agent` y persistirlas en **VictoriaMetrics**.

Esta aplicación actúa como un intermediario ligero y seguro. Recibe payloads JSON estructurados, valida estrictamente los datos utilizando Pydantic, los formatea a *InfluxDB Line Protocol* y los envía de forma asíncrona a VictoriaMetrics para no bloquear al agente recolector.

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3.11+
* **Gestor de Paquetes:** [uv](https://github.com/astral-sh/uv) (Resolución ultrarrápida en Rust).
* **Framework Web:** [FastAPI](https://fastapi.tiangolo.com/) (Asincronía nativa).
* **Validación:** Pydantic & Pydantic-Settings.
* **Cliente HTTP:** `httpx` (Llamadas asíncronas a la base de datos).
* **Base de Datos:** VictoriaMetrics (Time-Series Database).
* **Infraestructura:** Docker (Multi-stage build) & Docker Compose.

## 📋 Requisitos Previos

* [Docker](https://docs.docker.com/get-docker/) y Docker Compose instalados.
* *(Opcional)* `uv` instalado localmente para desarrollo sin contenedores.

## 📁 Estructura del Proyecto

```text
sre-agent-metrics-api/
├── .pre-commit-config.yaml    # Reglas de Ruff (Linting & Formatting)
├── Dockerfile                 # Multi-stage build (Builder + Runner)
├── docker-compose.yml         # Orquestación de la API + VictoriaMetrics
├── pyproject.toml             # Configuración del proyecto y dependencias
├── uv.lock                    # Dependencias fijadas deterministas
└── src/
    └── sre_agent_metrics_api/
        ├── __init__.py
        └── main.py            # Endpoints y lógica principal

```

## 🚀 Puesta en Marcha (Quick Start)

1. **Clonar y configurar variables de entorno:**
Crea el archivo `.env` en la raíz del proyecto para que `pydantic-settings` lo detecte:

```bash
echo "VM_WRITE_URL=http://victoriametrics:8428/write" > .env

```

1. **Levantar la infraestructura:**
Esto construirá la imagen optimizada de la API y levantará tanto la aplicación como VictoriaMetrics.

```bash
docker compose up -d --build

```

1. **Verificar los servicios:**

* Documentación interactiva de la API (Swagger): `http://localhost:8000/docs`
* Interfaz web de VictoriaMetrics: `http://localhost:8428`

## 🧪 Prueba de Ingesta (Simulando el sre-agent)

Una vez que los contenedores estén corriendo, puedes simular un envío de métricas desde tu terminal usando `curl`:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/metrics' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "hostname": "linux-server-01",
  "cpu_percent": 45.5,
  "ram_mb_used": 2048.0
}'

```

Deberías recibir una respuesta inmediata `{"status": "accepted"}`, mientras la API guarda silenciosamente el dato en VictoriaMetrics de fondo.

## 💻 Desarrollo Local

Para trabajar en el código sin levantar contenedores (requiere una instancia de VictoriaMetrics accesible):

```bash
# Sincronizar el entorno virtual y dependencias
uv sync

# Ejecutar el servidor de desarrollo
uv run fastapi run src/sre_agent_metrics_api/main.py

```
