import os
import datetime
import sys

def log_info(mensaje):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    print(f"[INFO] {timestamp} - {mensaje}")

def main():
    try:
        log_info("Sistema operativo: " + sys.platform)
        log_info("Directorio de trabajo actual: " + os.getcwd())
        log_info("Usuario ejecutando el script: " + os.getenv('USER', 'desconocido'))
        
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
            
        log_info("Abriendo archivo para escritura...")
        with open(ruta_archivo, 'w') as f:
            mensaje = '¡Hola Mundo!'
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
            
    except IOError as e:
        log_info(f"❌ Error de E/S: {str(e)}")
        log_info(f"Detalles del error: {e.__class__.__name__}")
        raise
    except Exception as e:
        log_info(f"❌ Error inesperado: {str(e)}")
        log_info(f"Tipo de error: {e.__class__.__name__}")
        log_info(f"Detalles adicionales: {sys.exc_info()}")
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