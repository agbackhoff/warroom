FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primero para aprovechar la caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos
COPY . .

# Forzar el modo sin buffer para los logs de Python
ENV PYTHONUNBUFFERED=1
ENV CONTAINER_NAME="holamundo-container"
ENV APP_VERSION="1.0"

# Variables de entorno para las APIs (se sobrescribirán con docker-compose)
ENV GOOGLE_API_KEY=""
ENV OPENAI_API_KEY=""

CMD ["python", "-u", "holamundo.py"] 