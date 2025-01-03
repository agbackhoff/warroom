# Hola Mundo Dockerizado con Logs Detallados

Este proyecto es una implementación de un "Hola Mundo" en Python utilizando Docker, con un enfoque en logging detallado y buenas prácticas de desarrollo. Este proyecto servirá como base para desarrollar un agente de IA para automatización de modelos dbt.

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
- Funcionalidad básica de escritura de "¡Hola Mundo!" en un archivo

### 2. Fase de Debugging
- Adición de manejo de errores try/except
- Implementación de logs básicos para seguimiento de operaciones
- Mejora en el manejo de excepciones específicas (IOError, Exception)
- Configuración de PYTHONUNBUFFERED para logs en tiempo real

### 3. Mejora de Verbosidad
- Implementación de sistema de logging con timestamps
- Adición de información detallada del sistema:
  - Sistema operativo
  - Directorio de trabajo
  - Usuario ejecutando el script
- Verificación de permisos y existencia de directorios
- Logging detallado de cada operación de archivo
- Uso de emojis para mejor visualización de estados (✓, ⚠, ❌)

### 4. Corrección de Errores
- Solución del problema IsADirectoryError
- Implementación de estructura de directorios data/
- Mejora en el manejo de rutas y permisos

## Estructura del Proyecto
```
.
├── data/               # Directorio para archivos generados
│   └── output.txt     # Archivo de salida generado
├── Dockerfile         # Configuración de la imagen Docker
├── docker-compose.yml # Configuración de servicios Docker
├── holamundo.py      # Script principal
└── README.md         # Este archivo
```

## Características
- Logging detallado con timestamps
- Manejo robusto de errores
- Verificación de permisos y estados
- Containerización con Docker
- Persistencia de datos mediante volúmenes Docker

## Cómo Usar
1. Asegúrate de tener Docker y Docker Compose instalados
2. Clona este repositorio
3. Ejecuta:
```bash
docker compose up --build
```

El programa creará un archivo `data/output.txt` con el mensaje "¡Hola Mundo!" y mostrará logs detallados de todo el proceso.