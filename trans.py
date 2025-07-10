import sounddevice as sd
import numpy as np
from queue import Queue
from faster_whisper import WhisperModel
import tempfile
import os
import threading
from scipy.io.wavfile import write
import signal
import sys

# Importar función de subida a Backblaze
from backblaze_uploader import subir_a_backblaze

# Configuración
fs = 16000  # Frecuencia de muestreo en Hz
chunk_duration = 2  # Duración de cada bloque de audio en segundos
modelo = "small"  # Opciones: tiny / base / small / medium / large
idioma_fijo = "es"
device = "cpu"
compute_type = "int8"

# Crear modelo de transcripción
model = WhisperModel(modelo, device=device, compute_type=compute_type)

# Cola de audio compartida
cola_audio = Queue()

# Evento para detener los hilos de forma segura
stop_event = threading.Event()

def grabar_audio():
    print("🎙️ Grabando audio... Presiona Ctrl+C para detener.")
    while not stop_event.is_set():
        try:
            audio = sd.rec(int(chunk_duration * fs), samplerate=fs, channels=1, dtype="int16")
            sd.wait()

            # Validar que no sea un bloque completamente silencioso
            if np.abs(audio).mean() < 50:
                print("⚠️ Audio muy silencioso, descartado.")
                continue

            cola_audio.put(audio.copy())
        except Exception as e:
            print(f"❌ Error al grabar audio: {e}")

def transcribir_audio():
    while not stop_event.is_set():
        try:
            audio = cola_audio.get(timeout=1)  # espera máximo 1s por audio

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                write(f.name, fs, audio)
                audio_path = f.name

            # Subir a Backblaze (opcional)
            subir_a_backblaze(audio_path)

            # Transcripción
            try:
                segments, _ = model.transcribe(audio_path, language=idioma_fijo, beam_size=1)
                for segment in segments:
                    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
            finally:
                os.remove(audio_path)

        except Exception as e:
            if not stop_event.is_set():
                print(f"❌ Error al transcribir audio: {e}")

# Manejo de señal para detener el programa con Ctrl+C
def detener_programa(signal_num, frame):
    print("\n🛑 Deteniendo programa...")
    stop_event.set()

# Asociar Ctrl+C al manejador
signal.signal(signal.SIGINT, detener_programa)

# Crear e iniciar hilos
hilo_grabacion = threading.Thread(target=grabar_audio)
hilo_transcripcion = threading.Thread(target=transcribir_audio)

hilo_grabacion.start()
hilo_transcripcion.start()

# Esperar a que los hilos terminen
hilo_grabacion.join()
hilo_transcripcion.join()

print("✅ Programa finalizado correctamente.")
