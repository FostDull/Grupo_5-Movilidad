import sounddevice as sd
import numpy as np
from queue import Queue
from faster_whisper import WhisperModel
import tempfile
import os
import threading
from scipy.io.wavfile import write

# Configuración
fs = 16000  # Hz
chunk_duration = 2  # duración por bloque en segundos
modelo = "small"  # más rápido: tiny / small / base
idioma_fijo = "es"  # forzar idioma español
device = "cpu"
compute_type = "int8"

# Modelo
model = WhisperModel(modelo, device=device, compute_type=compute_type)

# Cola de audio
cola_audio = Queue()

def grabar_audio():
    print("🎙️ Grabando... (Ctrl+C para detener)")
    try:
        while True:
            audio = sd.rec(int(chunk_duration * fs), samplerate=fs, channels=1, dtype="int16")
            sd.wait()
            cola_audio.put(audio.copy())
    except KeyboardInterrupt:
        print("\n🛑 Grabación detenida por el usuario.")
        cola_audio.put(None)

def transcribir_audio():
    while True:
        audio = cola_audio.get()
        if audio is None:
            break

        # Guardar en archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            write(f.name, fs, audio)
            audio_path = f.name

        # Transcribir directamente en español
        segments, _ = model.transcribe(audio_path, language=idioma_fijo, beam_size=1)
        for segment in segments:
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

        os.remove(audio_path)

# Hilos
h1 = threading.Thread(target=grabar_audio)
h2 = threading.Thread(target=transcribir_audio)

h1.start()
h2.start()

h1.join()
h2.join()
