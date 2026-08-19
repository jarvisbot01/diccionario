# syntax=docker/dockerfile:1
FROM python:3.14-slim

# Evitar prompts interactivos y buffers de Python
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Actualizar sistema e instalar dependencias del sistema
RUN apt update && \
    apt upgrade -y && \
    apt install -y --no-install-recommends \
        procps \
        curl && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# Instalar uv desde la imagen oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Establecer directorio de trabajo
WORKDIR /app

# 1. Copiar manifiestos de dependencias e instalar dependencias (optimiza caché de capas)
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project --no-dev

# 2. Copiar código fuente del proyecto
COPY src/ ./src/

# 3. Sincronizar e instalar el proyecto en el entorno virtual
RUN uv sync --frozen --no-dev

# Añadir el entorno virtual al PATH
ENV PATH="/app/.venv/bin:$PATH"

# Entrada fija al gestor uv
ENTRYPOINT ["uv"]

# Comando por defecto para ejecutar la aplicación
CMD ["run", "diccionario"]
