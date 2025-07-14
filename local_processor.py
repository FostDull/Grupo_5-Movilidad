import os
import sys
import time
import json
import re
import traceback
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configurar entorno antes de cualquier import
os.environ['ULTRALYTICS_AUTOUPDATE'] = 'disabled'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Configuración actualizada de Backblaze
B2_KEY_ID = "005edb6e50f32700000000003"
B2_APP_KEY = "K005P0f0Ubgb5zP7aFezbKC/6ri7l0Y"
B2_BUCKET_ID = "3e5dfb167e65e0af93720710"  # ID directo del bucket

# Rutas locales
CARPETA_VIDEOS = "./data/videos"
CARPETA_PROCESADOS = "./data/procesados"

# Importar después de configurar el entorno
from utils.video_processing import procesar_video
from utils.backblaze_utils import subir_video_b2


class VideoHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Añadir .webm a las extensiones soportadas
        if not event.is_directory and event.src_path.lower().endswith(('.mp4', '.avi', '.mov', '.webm')):
            print(f"\nNuevo video detectado: {event.src_path}")
            try:
                # Esperar a que el archivo esté completamente escrito
                time.sleep(2)
                procesar_video_local(event.src_path)
            except Exception as e:
                print(f"Error procesando video: {str(e)}")
                print(traceback.format_exc())


def procesar_video_local(video_path):
    # Procesar video
    resultados, video_procesado = procesar_video(video_path)

    # Guardar resultados JSON
    nombre_base = os.path.basename(video_path).rsplit('.', 1)[0]
    json_salida = os.path.join(CARPETA_PROCESADOS, f"{nombre_base}.json")
    with open(json_salida, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    print(f"Resultados guardados en: {json_salida}")

    # Subir a Backblaze si hay alertas
    if resultados.get("alertas"):
        # Limpiar nombre para Backblaze
        nombre_limpio = re.sub(r'[^a-zA-Z0-9_\-]', '_', nombre_base)
        nombre_evidencia = f"evidencia_kuntur_{nombre_limpio}.mp4"

        try:
            print(f"Intentando subir: {video_procesado} como {nombre_evidencia}")
            subido = subir_video_b2(
                video_procesado,
                nombre_evidencia,
                B2_KEY_ID,
                B2_APP_KEY,
                B2_BUCKET_ID  # Usar ID directamente
            )
            if subido:
                print(f"¡Video subido a Backblaze como {nombre_evidencia}!")
        except Exception as e:
            print(f"Error subiendo a Backblaze: {str(e)}")

    # Mover archivos a carpeta procesados
    try:
        # Mover video procesado
        destino_procesado = os.path.join(CARPETA_PROCESADOS, os.path.basename(video_procesado))
        os.rename(video_procesado, destino_procesado)

        # Mover video original
        destino_original = os.path.join(CARPETA_PROCESADOS, os.path.basename(video_path))
        os.rename(video_path, destino_original)

        print(f"Archivos movidos a: {CARPETA_PROCESADOS}")
    except Exception as e:
        print(f"Error moviendo archivos: {str(e)}")


if __name__ == "__main__":
    # Crear carpetas si no existen
    os.makedirs(CARPETA_VIDEOS, exist_ok=True)
    os.makedirs(CARPETA_PROCESADOS, exist_ok=True)

    # Iniciar monitorización
    event_handler = VideoHandler()
    observer = Observer()
    observer.schedule(event_handler, CARPETA_VIDEOS, recursive=False)
    observer.start()

    print(f"Monitoreando carpeta {CARPETA_VIDEOS}...")
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()