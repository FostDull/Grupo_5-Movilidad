import cv2
import time
from transformers import pipeline
from playsound import playsound
import requests
import threading

# Cargar modelo de clasificación de imágenes de Hugging Face
modelo = pipeline("image-classification", model="google/vit-base-patch16-224")

# Simula funciones de impacto del sistema
def activar_alarma():
    print(" Alarma activada")
    # Puedes reemplazar con un archivo de sonido real
    playsound("alarma.mp3")

def cerrar_puertas():
    print("Puertas cerradas automáticamente (simulado)")

def notificar_autoridades(evento="Robo detectado"):
    print("Notificando a la policía...")
    data = {
        "evento": evento,
        "ubicacion": "Lat: -0.2345, Lon: -78.5243",  # Simulado
        "vehiculo": "Bus 012",
        "hora": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        # Simula notificación (puedes conectar a API real)
        # requests.post("https://policia.api/alerta", json=data)
        print("Autoridades notificadas:", data)
    except Exception as e:
        print("Error al notificar:", e)

# Procesa el frame con IA
def procesar_frame(frame):
    # Convertir frame (BGR) a RGB y luego a formato de PIL
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = modelo(rgb)

    # Mostrar resultados top 1
    etiqueta = results[0]['label']
    score = results[0]['score']
    print(f"[IA] Detectado: {etiqueta} - Confianza: {score:.2f}")

    # Simulación: si detecta "person" con score alto, activa sistema
    if "person" in etiqueta.lower() and score > 0.9:
        print("Comportamiento sospechoso detectado")
        activar_sistema_alerta()

# Lógica de alerta
def activar_sistema_alerta():
    threading.Thread(target=activar_alarma).start()
    cerrar_puertas()
    notificar_autoridades()

# Captura desde cámara
def iniciar_monitoreo():
    cap = cv2.VideoCapture(0)
    print("Monitoreo iniciado. Presiona 'q' para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Monitoreo en tiempo real", frame)

        # Procesar cada 3 segundos un frame
        if int(time.time()) % 3 == 0:
            procesar_frame(frame)
            time.sleep(1)  # evitar sobrecarga

        # Salir con tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Monitoreo detenido")

if __name__ == "__main__":
    iniciar_monitoreo()
