FROM python:3.9-slim

WORKDIR /app
COPY holamundo.py .

# Forzar el modo sin buffer para los logs de Python
ENV PYTHONUNBUFFERED=1
# Agregar información del contenedor
ENV CONTAINER_NAME="holamundo-container"
ENV APP_VERSION="1.0"

# Mostrar información del sistema al inicio
RUN echo "Python version:" && python --version && \
    echo "Pip version:" && pip --version

CMD ["python", "-u", "holamundo.py"] 