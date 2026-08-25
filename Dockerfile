# ==========================================
# Etapa 1: Builder
# ==========================================
FROM python:3.14-slim AS builder

# Copiar uv directamente desde su imagen oficial (ultrarrápido)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

# Copiar dependencias primero para optimizar la caché de Docker
COPY pyproject.toml uv.lock README.md ./

# Instalar dependencias de producción (sin compilar el código fuente todavía)
RUN uv sync --frozen --no-install-project --no-dev

# Copiar el código fuente y sincronizar el proyecto final
COPY src/ /app/src/
RUN uv sync --frozen --no-dev

# ==========================================
# Etapa 2: Runner
# ==========================================
FROM python:3.14-slim AS runner

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Crear usuario sin privilegios por seguridad
RUN useradd --create-home appuser
WORKDIR /app

# Copiar el entorno virtual y el código fuente desde el builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --chown=appuser:appuser src/ /app/src/

# Cambiar al usuario seguro
USER appuser

# Ejecutar la API
CMD ["python", "-m", "uvicorn", "sre_agent_metrics_api.main:app", "--host", "0.0.0.0", "--port", "8000"]