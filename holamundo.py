import os
import datetime
import sys
from dotenv import load_dotenv
import dspy
import google.generativeai as genai

def log_info(mensaje):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    print(f"[INFO] {timestamp} - {mensaje}")

class GeminiLLM(dspy.LM):
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.kwargs = {
            'temperature': 0.7,
            'top_p': 1.0,
            'top_k': 40,
            'max_output_tokens': 1024,
        }
    
    def basic_request(self, prompt, **kwargs):
        try:
            request_kwargs = {**self.kwargs, **kwargs}
            generation_config = genai.types.GenerationConfig(
                temperature=request_kwargs.get('temperature', 0.7),
                top_p=request_kwargs.get('top_p', 1.0),
                top_k=request_kwargs.get('top_k', 40),
                max_output_tokens=request_kwargs.get('max_output_tokens', 1024),
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            log_info(f"Error en GeminiLLM: {str(e)}")
            return ""

class GeneradorSaludo(dspy.Signature):
    """Genera un saludo personalizado en español."""
    context = dspy.InputField(desc="Contexto para generar el saludo")
    saludo = dspy.OutputField(desc="Un saludo amigable en español")
    
    def forward(self, context):
        # Generar el prompt para el modelo
        prompt = f"""
        Basándote en este contexto: {context}
        Genera un saludo amigable, emotivo y personal en español.
        El saludo debe ser creativo y único.
        """
        # Usar el modelo de lenguaje configurado en DSpy
        resultado = self.lm(prompt)
        return dspy.Prediction(saludo=resultado)

def configurar_apis():
    try:
        load_dotenv()
        
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if google_api_key:
            genai.configure(api_key=google_api_key)
            log_info("✓ API de Google Gemini configurada correctamente")
            
            dspy.settings.configure(lm=GeminiLLM())
            log_info("✓ DSpy configurado con adaptador Gemini personalizado")
        else:
            raise ValueError("No se encontró la clave de API de Google")
        
    except Exception as e:
        log_info(f"❌ Error configurando APIs: {str(e)}")
        raise

def generar_mensaje():
    try:
        # Paso 1: Generar saludo inicial con Gemini
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Genera un saludo creativo y amigable en español")
        mensaje_base = response.text
        log_info(f"Mensaje base generado por Gemini: {mensaje_base}")
        
        # Paso 2: Mejorar el saludo con DSpy
        try:
            predictor = dspy.Predict(GeneradorSaludo)
            resultado = predictor(context=mensaje_base)
            mensaje_final = resultado.saludo
            log_info(f"Mensaje final mejorado por DSpy+Gemini: {mensaje_final}")
            return mensaje_final
        except Exception as e:
            log_info(f"Error en DSpy: {str(e)}")
            return mensaje_base
        
    except Exception as e:
        log_info(f"❌ Error generando mensaje: {str(e)}")
        return "¡Hola Mundo! (mensaje por defecto)"

def main():
    try:
        log_info("Sistema operativo: " + sys.platform)
        log_info("Directorio de trabajo actual: " + os.getcwd())
        log_info("Usuario ejecutando el script: " + os.getenv('USER', 'desconocido'))
        
        # Configurar APIs
        configurar_apis()
        
        # Crear directorio data si no existe
        data_dir = 'data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            log_info(f"Directorio {data_dir} creado")
        
        ruta_archivo = os.path.join(data_dir, 'output.txt')
        log_info(f"Intentando acceder a la ruta del archivo: {os.path.abspath(ruta_archivo)}")
        
        log_info("Verificando permisos de escritura en el directorio...")
        if os.access(data_dir, os.W_OK):
            log_info("✓ Permisos de escritura confirmados")
        else:
            log_info("⚠ No hay permisos de escritura en el directorio")
            
        log_info("Generando mensaje usando IA...")
        mensaje = generar_mensaje()
            
        log_info("Abriendo archivo para escritura...")
        with open(ruta_archivo, 'w') as f:
            log_info(f"Preparando mensaje para escribir: '{mensaje}'")
            log_info(f"Codificación del archivo: {f.encoding}")
            
            log_info("Iniciando proceso de escritura...")
            f.write(mensaje)
            log_info(f"Bytes escritos: {len(mensaje.encode(f.encoding))}")
            
        if os.path.exists(ruta_archivo):
            tamaño = os.path.getsize(ruta_archivo)
            log_info(f"✓ Archivo creado exitosamente (tamaño: {tamaño} bytes)")
            
            with open(ruta_archivo, 'r') as f:
                contenido = f.read()
                log_info(f"Verificación de contenido: '{contenido}'")
        else:
            log_info("⚠ El archivo no existe después de la escritura")
            
    except Exception as e:
        log_info(f"❌ Error inesperado: {str(e)}")
        log_info(f"Tipo de error: {e.__class__.__name__}")
        raise
    finally:
        log_info("Finalizando operación de escritura")

if __name__ == '__main__':
    log_info("=== Iniciando programa holamundo.py ===")
    try:
        main()
        log_info("=== Programa finalizado exitosamente ===")
    except:
        log_info("=== Programa finalizado con errores ===")
        raise 