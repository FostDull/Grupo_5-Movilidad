import sounddevice as sd
import numpy as np
from queue import Queue
from faster_whisper import WhisperModel
import tempfile
import os
import threading
from scipy.io.wavfile import write
from util.backblaze_uploader import subir_a_backblaze
import requests
import json

# === Configuración ===
fs = 16000  # frecuencia de muestreo
chunk_duration = 10  # segundos por bloque
modelo = "small"
idioma_fijo = "es"
device = "cpu"
compute_type = "int8"

# === Modelo ===
model = WhisperModel(modelo, device=device, compute_type=compute_type)

# === Cola de audio ===
cola_audio = Queue()

def grabar_audio():
    print("Grabando...")
    while True:
        audio = sd.rec(int(chunk_duration * fs), samplerate=fs, channels=1, dtype="int16")
        sd.wait()
        cola_audio.put(audio.copy())

def procesar_bloque(audio):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            write(f.name, fs, audio)
            audio_path = f.name

        # Subir a Backblaze (bloqueante para asegurarnos URL)
        url_evidencia = subir_a_backblaze(audio_path)

        # Transcribir (bloqueante)
        segments, _ = model.transcribe(audio_path, language=idioma_fijo, beam_size=1)

        texto_completo = ""
        for segment in segments:
            texto_completo += segment.text + " "
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

        texto_completo = texto_completo.strip()

        # Preparar datos para enviar a FastAPI, asegurándonos que sean strings UTF-8
        data = {
            "descripcion": texto_completo if isinstance(texto_completo, str) else texto_completo.decode("utf-8", errors="ignore"),
            "ubicacion": "No especificada",
            "url": url_evidencia if isinstance(url_evidencia, str) else url_evidencia.decode("utf-8", errors="ignore")
        }

        # Enviar a FastAPI
        response = requests.post("http://127.0.0.1:8086/denuncias/audio/", json=data)
        print(f"Enviado a FastAPI: {response.status_code} {response.text}")

    except Exception as e:
        print(f"Error en procesamiento: {e}")

    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)

def transcribir_audio():
    while True:
        audio = cola_audio.get()
        threading.Thread(target=procesar_bloque, args=(audio,), daemon=True).start()

# === Lanzar hilos ===
hilo_grabacion = threading.Thread(target=grabar_audio, daemon=True)
hilo_transcripcion = threading.Thread(target=transcribir_audio, daemon=True)

hilo_grabacion.start()
hilo_transcripcion.start()

hilo_grabacion.join()
hilo_transcripcion.join()
