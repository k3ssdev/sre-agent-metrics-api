import httpx
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


# 1. Definimos la clase de configuración
class Settings(BaseSettings):
    vm_write_url: str

    class Config:
        env_file = ".env"


# Instanciamos la configuración (carga el .env automáticamente)
settings = Settings()

app = FastAPI(title="SRE Agent Metrics API")


# Definimos el modelo de datos para las métricas del sistema
class SystemMetrics(BaseModel):
    hostname: str
    cpu_percent: float = Field(..., ge=0, le=100)
    ram_mb_used: float


# Función para enviar métricas a VictoriaMetrics
async def push_to_victoriametrics(metrics: SystemMetrics):
    line_data = (
        f"linux_system,host={metrics.hostname} "
        f"cpu_percent={metrics.cpu_percent},ram_mb_used={metrics.ram_mb_used}"
    )
    # Async evita bloquear el hilo principal mientras se envían las métricas
    async with httpx.AsyncClient() as client:
        try:
            # Carga URL del archivo .env y hace post
            await client.post(settings.vm_write_url, content=line_data)
        except httpx.RequestError as exc:
            print(f"Error enviando métricas: {exc}")


# Endpoint para recibir métricas del sistema
@app.post("/api/v1/metrics")
async def receive_metrics(metrics: SystemMetrics, bg_tasks: BackgroundTasks):
    bg_tasks.add_task(push_to_victoriametrics, metrics)
    return {"status": "accepted"}
