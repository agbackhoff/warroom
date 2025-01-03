# Hola Mundo Dockerizado con IA

Este proyecto es una implementación de un "Hola Mundo" en Python utilizando Docker, con un enfoque en la integración de modelos de IA (Gemini y DSpy) y logging detallado. Este proyecto servirá como base para desarrollar un agente de IA para automatización de modelos dbt.

## Objetivo del Agente IA

El objetivo principal es desarrollar un agente de IA capaz de generar automáticamente modelos dbt (data build tool) a partir de schemas de BigQuery, siguiendo una estructura y lineamientos específicos.

### Funcionalidad Objetivo
El agente deberá generar automáticamente los siguientes archivos:
- Modelos de staging (`stg.sql`)
- Modelos intermedios (`int.sql`)
- Modelos finales (`final.sql`)
- Archivos de documentación (`final.yml`)

### Pasos del Proceso
1. **Obtención de Input**
   - Lectura y procesamiento del schema de BigQuery como entrada inicial
   - Validación de la estructura del schema

2. **Análisis de Lineamientos**
   - Lectura de lineamientos específicos para la generación de modelos
   - Comprensión de ejemplos de outputs esperados
   - Validación de reglas y estándares

3. **Generación de Modelos**
   - Creación del modelo `stg.sql` (staging)
   - Desarrollo del modelo `int.sql` (intermedio)
   - Producción del modelo `final.sql`
   - Generación del archivo de documentación `final.yml`

## Evolución del Proyecto

### 1. Implementación Inicial
- Creación de `holamundo.py` con funcionalidad básica de escritura
- Configuración del `Dockerfile` con Python 3.9-slim
- Implementación del `docker-compose.yml` para gestión de contenedores
- Funcionalidad básica de escritura de mensaje en un archivo

### 2. Fase de Debugging
- Adición de manejo de errores try/except
- Implementación de logs básicos para seguimiento de operaciones
- Mejora en el manejo de excepciones específicas
- Configuración de PYTHONUNBUFFERED para logs en tiempo real

### 3. Mejora de Verbosidad
- Implementación de sistema de logging con timestamps
- Adición de información detallada del sistema
- Verificación de permisos y existencia de directorios
- Logging detallado de cada operación
- Uso de emojis para mejor visualización de estados (✓, ⚠, ❌)

### 4. Integración de IA
- Implementación de Gemini API para generación de texto
- Integración con DSpy para procesamiento de lenguaje
- Creación de adaptador personalizado GeminiLLM
- Sistema de generación de mensajes en dos pasos
- Manejo robusto de errores en cada capa de IA

### 5. Optimización del Código
- Eliminación de dependencias innecesarias
- Mejora en la estructura de clases y métodos
- Implementación correcta de interfaces DSpy
- Refinamiento del sistema de prompts
- Mejor manejo de configuraciones y parámetros

## Estructura del Proyecto
```
.
├── data/               # Directorio para archivos generados
│   └── output.txt     # Archivo de salida generado
├── Dockerfile         # Configuración de la imagen Docker
├── docker-compose.yml # Configuración de servicios Docker
├── requirements.txt   # Dependencias del proyecto
├── .env.example      # Ejemplo de variables de entorno
├── holamundo.py      # Script principal
└── README.md         # Este archivo
```

## Tecnologías Utilizadas
- Python 3.9
- Docker y Docker Compose
- Google Gemini API
- DSpy Framework
- Python-dotenv

## Características
- Integración con modelos de IA
- Logging detallado con timestamps
- Manejo robusto de errores
- Verificación de permisos y estados
- Containerización con Docker
- Persistencia de datos mediante volúmenes Docker

## Cómo Usar
1. Asegúrate de tener Docker y Docker Compose instalados
2. Clona este repositorio
3. Copia `.env.example` a `.env` y configura tu API key de Google:
```bash
cp .env.example .env
```
4. Edita el archivo `.env` con tu clave de API de Google
5. Ejecuta:
```bash
docker compose up --build
```

El programa creará un archivo `data/output.txt` con un mensaje generado por IA y mostrará logs detallados de todo el proceso.