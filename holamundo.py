import os
import datetime
import sys
import warnings
from pathlib import Path
from dotenv import load_dotenv
import dspy
import google.generativeai as genai

# Filtrar warnings específicos
warnings.filterwarnings('ignore', category=UserWarning, module='pydantic')
warnings.filterwarnings('ignore', message='.*All log messages before.*')

def log_info(mensaje):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    print(f"[INFO] {timestamp} - {mensaje}")

def verificar_estructura_proyecto():
    """Verifica la existencia de directorios y archivos necesarios."""
    try:
        # Obtener el directorio base (fuera de /app)
        base_dir = Path('/workspace')
        
        # Verificar directorios requeridos con rutas absolutas
        directorios_requeridos = [
            base_dir / 'input',
            base_dir / 'models',
            base_dir / 'models/staging'
        ]
        
        for directorio in directorios_requeridos:
            if not directorio.exists():
                log_info(f"Creando directorio: {directorio}")
                directorio.mkdir(parents=True, exist_ok=True)
            log_info(f"✓ Directorio verificado: {directorio}")
            
        # Verificar archivo de input
        input_file = base_dir / 'input/input2.txt'
        if not input_file.exists():
            raise FileNotFoundError(f"No se encontró el archivo de entrada: {input_file}")
        log_info(f"✓ Archivo de entrada verificado: {input_file}")
        
        return True
        
    except Exception as e:
        log_info(f"❌ Error en verificación de estructura: {str(e)}")
        raise

def verificar_output(output_file: Path) -> bool:
    """Verifica que el archivo de output se haya generado correctamente."""
    try:
        log_info(f"Verificando archivo de salida: {output_file}")
        
        # Verificar que el directorio existe
        if not output_file.parent.exists():
            log_info(f"❌ El directorio {output_file.parent} no existe")
            return False
            
        # Verificar permisos del directorio
        try:
            test_file = output_file.parent / '.test_write'
            test_file.touch()
            test_file.unlink()
            log_info("✓ Permisos de escritura verificados en el directorio")
        except Exception as e:
            log_info(f"❌ Error de permisos en el directorio: {str(e)}")
            return False
        
        if not output_file.exists():
            log_info(f"❌ No se encontró el archivo de salida: {output_file}")
            return False
        
        # Verificar que el archivo no esté vacío
        size = output_file.stat().st_size
        log_info(f"Tamaño del archivo: {size} bytes")
        if size == 0:
            log_info("❌ El archivo está vacío")
            return False
            
        # Leer el contenido para verificar que sea SQL válido
        contenido = output_file.read_text()
        num_lineas = len(contenido.splitlines())
        log_info(f"Número de líneas en el archivo: {num_lineas}")
        
        if not contenido.strip():
            log_info("❌ El archivo no contiene SQL válido")
            return False
            
        # Verificar contenido básico de SQL
        if not any(keyword in contenido.lower() for keyword in ['select', 'from', 'config']):
            log_info("❌ El contenido no parece ser un modelo DBT válido")
            return False
            
        log_info("✓ Contenido SQL verificado correctamente")
        log_info(f"✓ Archivo guardado en: {output_file.absolute()}")
        return True
        
    except Exception as e:
        log_info(f"❌ Error en verificación de output: {str(e)}")
        return False

def verificar_archivo_input(input_file: Path):
    """Verifica que el archivo de input exista."""
    if not input_file.exists():
        mensaje = f"❌ No se encontró el archivo de input: {input_file}"
        log_info(mensaje)
        raise FileNotFoundError(mensaje)
    if not input_file.is_file():
        mensaje = f"❌ La ruta no es un archivo válido: {input_file}"
        log_info(mensaje)
        raise ValueError(mensaje)
    log_info(f"✓ Archivo de input verificado: {input_file}")

class GeminiLLM:
    """Implementación personalizada de un modelo de lenguaje para DSpy usando Gemini."""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.cache = {}
        self.kwargs = {
            'temperature': 0.1,
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 2048,
        }
    
    def basic_request(self, prompt, **kwargs):
        try:
            cache_key = str(prompt)
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            request_kwargs = {**self.kwargs, **kwargs}
            generation_config = genai.types.GenerationConfig(
                temperature=request_kwargs.get('temperature', 0.1),
                top_p=request_kwargs.get('top_p', 0.95),
                top_k=request_kwargs.get('top_k', 40),
                max_output_tokens=request_kwargs.get('max_output_tokens', 2048),
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            result = response.text
            self.cache[cache_key] = result
            return result
        except Exception as e:
            log_info(f"Error en GeminiLLM: {str(e)}")
            return ""
    
    def __call__(self, prompt, **kwargs):
        if isinstance(prompt, dict):
            # Si es un diccionario (como lo envía DSpy), extraer el prompt
            actual_prompt = prompt.get('prompt', '')
            if not actual_prompt:
                # Buscar el prompt en los valores del diccionario
                for value in prompt.values():
                    if isinstance(value, str):
                        actual_prompt = value
                        break
            return self.basic_request(actual_prompt, **kwargs)
        return self.basic_request(prompt, **kwargs)

class DBTModelGenerator(dspy.Signature):
    """Genera modelos DBT basados en schemas de BigQuery."""
    input_schema = dspy.InputField(desc="Schema de BigQuery en formato texto")
    table_name = dspy.InputField(desc="Nombre de la tabla")
    source_name = dspy.InputField(desc="Nombre del source en dbt")
    sql_model = dspy.OutputField(desc="Código SQL del modelo DBT generado")
    
    def forward(self, input_schema, table_name, source_name):
        prompt = f"""
        Genera un modelo DBT de staging (stg) basado en el siguiente schema de BigQuery.
        
        SCHEMA:
        {input_schema}
        
        REQUISITOS:
        1. El modelo debe ser ephemeral
        2. Usar safe_cast para cada columna según su tipo de dato
        3. Generar una primary key usando dbt_utils.generate_surrogate_key
        4. Seguir este formato:
        {{{{ config(materialized="ephemeral") }}}}

        with stg_{table_name} as (
            select
                {{{{ dbt_utils.generate_surrogate_key(['columnas_pk']) }}}} as pk_{table_name},
                [safe cast statements para cada columna]
            from {{{{ source('{source_name}','{table_name}') }}}}
        )

        select * from stg_{table_name}
        
        IMPORTANTE:
        - Mantener los nombres de columnas originales
        - Usar SAFE_CAST para cada columna
        - Incluir todas las columnas del schema
        - La primary key debe usar las columnas más relevantes
        """
        
        resultado = self.lm({"prompt": prompt})
        return dspy.Prediction(sql_model=resultado)

def procesar_schema_bigquery(input_file: Path):
    """Lee y procesa el archivo de schema de BigQuery."""
    try:
        schema_lines = [
            line.strip() 
            for line in input_file.read_text().splitlines() 
            if line.strip() and 'Field name' not in line
        ]
        return '\n'.join(schema_lines)
    except Exception as e:
        log_info(f"❌ Error leyendo schema: {str(e)}")
        raise

def generar_modelo_staging(schema_text: str, table_name: str, source_name: str):
    """Genera el modelo de staging usando IA."""
    try:
        log_info(f"Iniciando generación del modelo staging para tabla: {table_name}")
        log_info(f"Source name configurado: {source_name}")
        log_info(f"Longitud del schema: {len(schema_text.splitlines())} líneas")
        
        # Construir el prompt con un formato más estructurado
        prompt = f"""Genera un modelo DBT de staging (stg) basado en el siguiente schema de BigQuery.
        El modelo debe seguir EXACTAMENTE este formato, reemplazando los placeholders con el contenido apropiado:

        {{{{ config(materialized='ephemeral') }}}}

        with source as (
            select *
            from {{{{ source('{source_name}', '{table_name}') }}}}
        ),

        staged as (
            select
                {{{{ dbt_utils.generate_surrogate_key(['id', 'created_at']) }}}} as pk_{table_name},
                -- Aquí van los SAFE_CAST para cada columna
                [SAFE_CAST statements]
            from source
        )

        select * from staged

        El schema de entrada es:
        {schema_text}

        REGLAS IMPORTANTES:
        1. DEBES incluir SAFE_CAST para CADA columna
        2. Mantén los nombres originales de las columnas
        3. Usa el formato exacto proporcionado
        4. La primary key debe usar las columnas más relevantes para identificación única
        5. NO incluyas comentarios explicativos, solo el código SQL
        """
        
        log_info("Enviando prompt a Gemini...")
        response = genai.GenerativeModel('gemini-pro').generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
            )
        )
        
        sql_generado = response.text.strip()
        
        # Verificar que el SQL generado sea válido
        if not sql_generado or len(sql_generado) < 50:  # Un modelo válido debe tener al menos 50 caracteres
            raise ValueError("El SQL generado es demasiado corto o está vacío")
            
        if not all(keyword in sql_generado.lower() for keyword in ['config', 'select', 'from', 'source']):
            raise ValueError("El SQL generado no contiene las palabras clave necesarias")
        
        log_info(f"SQL generado exitosamente - Longitud: {len(sql_generado)} caracteres")
        log_info("Preview de las primeras 5 líneas del SQL generado:")
        for i, linea in enumerate(sql_generado.splitlines()[:5]):
            log_info(f"  {i+1}: {linea}")
        
        # Asegurar que el SQL termine con una nueva línea
        if not sql_generado.endswith('\n'):
            sql_generado += '\n'
        
        return sql_generado
        
    except Exception as e:
        log_info(f"❌ Error generando modelo: {str(e)}")
        raise

def guardar_modelo_sql(sql_content: str, output_file: Path):
    """Guarda el modelo SQL en el archivo especificado."""
    try:
        # Asegurar que el directorio existe
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Guardar el contenido
        with output_file.open('w', encoding='utf-8') as f:
            f.write(sql_content)
            
        log_info(f"Archivo SQL guardado en: {output_file.absolute()}")
        return True
    except Exception as e:
        log_info(f"❌ Error guardando archivo SQL: {str(e)}")
        return False

def generar_modelo_intermedio(table_name: str, stg_model_path: Path):
    """Genera el modelo intermedio (int) basado en el modelo de staging."""
    try:
        log_info(f"Iniciando generación del modelo intermedio para tabla: {table_name}")
        
        # Leer el modelo de staging para verificar su existencia
        if not stg_model_path.exists():
            raise FileNotFoundError(f"No se encontró el modelo de staging: {stg_model_path}")
        
        log_info("Generando modelo intermedio...")
        
        # Construir el modelo intermedio
        sql_intermedio = f"""{{{{ config(materialized='ephemeral') }}}}

with staging as (
    select * from {{{{ ref('stg_{table_name}') }}}}
),

deduplicacion as (
    select
        *,
        row_number() over (
            partition by pk_{table_name}
            order by recordstamp desc
        ) as rownum
    from staging
    {{% if is_incremental() %}}
        where recordstamp > (select max(recordstamp) from {{{{ this }}}})
    {{% endif %}}
),

final as (
    select
        *
    from deduplicacion
    where rownum = 1
)

select * from final"""

        log_info("Modelo intermedio generado exitosamente")
        log_info("Preview del modelo intermedio:")
        for i, linea in enumerate(sql_intermedio.splitlines()[:5]):
            log_info(f"  {i+1}: {linea}")
        
        return sql_intermedio
        
    except Exception as e:
        log_info(f"❌ Error generando modelo intermedio: {str(e)}")
        raise

def generar_modelo_final(table_name: str, int_model_path: Path):
    """Genera el modelo final basado en el modelo intermedio."""
    try:
        log_info(f"Iniciando generación del modelo final para tabla: {table_name}")
        
        # Verificar que existe el modelo intermedio
        if not int_model_path.exists():
            raise FileNotFoundError(f"No se encontró el modelo intermedio: {int_model_path}")
        
        log_info("Generando modelo final...")
        
        # Construir el modelo final
        sql_final = f"""{{{{ config(materialized='table') }}}}

select * from {{{{ ref('int_{table_name}') }}}}"""

        log_info("Modelo final generado exitosamente")
        log_info("Preview del modelo final:")
        for i, linea in enumerate(sql_final.splitlines()):
            log_info(f"  {i+1}: {linea}")
        
        return sql_final
        
    except Exception as e:
        log_info(f"❌ Error generando modelo final: {str(e)}")
        raise

def main():
    try:
        warnings.simplefilter('ignore', ResourceWarning)
        
        log_info("=== Iniciando generación de modelos DBT ===")
        log_info("Sistema operativo: " + sys.platform)
        
        # Configurar directorio base
        base_dir = Path('/workspace')
        log_info("Directorio base del proyecto: " + str(base_dir))
        
        # Verificar estructura del proyecto
        verificar_estructura_proyecto()
        
        # Configurar APIs
        load_dotenv()
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if not google_api_key:
            raise ValueError("No se encontró la clave de API de Google")
        
        genai.configure(api_key=google_api_key)
        log_info("✓ API de Google Gemini configurada correctamente")
        
        # Configurar nombres
        table_name = 'mi_tabla'
        source_name = 'mi_source'
        
        # PASO 1: Generar modelo de staging
        log_info("=== PASO 1: Generando modelo de staging ===")
        input_file = base_dir / 'input/input2.txt'
        
        log_info(f"Procesando archivo de schema: {input_file}")
        schema_text = procesar_schema_bigquery(input_file)
        log_info(f"Schema procesado - {len(schema_text.splitlines())} líneas")
        
        sql_staging = generar_modelo_staging(schema_text, table_name, source_name)
        
        # Guardar modelo de staging
        stg_output_file = base_dir / 'models/staging' / f'stg_{table_name}.sql'
        if not guardar_modelo_sql(sql_staging, stg_output_file):
            raise RuntimeError("No se pudo guardar el modelo de staging")
        
        if not verificar_output(stg_output_file):
            raise RuntimeError("No se pudo verificar el modelo de staging")
        
        log_info(f"✓ Modelo de staging generado: {stg_output_file}")
        
        # PASO 2: Generar modelo intermedio
        log_info("\n=== PASO 2: Generando modelo intermedio ===")
        sql_intermedio = generar_modelo_intermedio(table_name, stg_output_file)
        
        # Guardar modelo intermedio
        int_output_file = base_dir / 'models/intermediate' / f'int_{table_name}.sql'
        int_output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not guardar_modelo_sql(sql_intermedio, int_output_file):
            raise RuntimeError("No se pudo guardar el modelo intermedio")
        
        if not verificar_output(int_output_file):
            raise RuntimeError("No se pudo verificar el modelo intermedio")
        
        log_info(f"✓ Modelo intermedio generado: {int_output_file}")
        
        # PASO 3: Generar modelo final
        log_info("\n=== PASO 3: Generando modelo final ===")
        sql_final = generar_modelo_final(table_name, int_output_file)
        
        # Guardar modelo final
        final_output_file = base_dir / 'models/marts' / f'{table_name}.sql'
        final_output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not guardar_modelo_sql(sql_final, final_output_file):
            raise RuntimeError("No se pudo guardar el modelo final")
        
        if not verificar_output(final_output_file):
            raise RuntimeError("No se pudo verificar el modelo final")
        
        log_info(f"✓ Modelo final generado: {final_output_file}")
        log_info(f"  Ruta absoluta: {final_output_file.absolute()}")
        
    except Exception as e:
        log_info(f"❌ Error: {str(e)}")
        raise
    finally:
        log_info("=== Proceso finalizado ===")

if __name__ == '__main__':
    main() 