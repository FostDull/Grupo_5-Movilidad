import requests
import time


def clasificar_acoso(texto_descripcion: str) -> bool:
    prompt = f"""Dado este escenario: "{texto_descripcion}", responde únicamente con 'sí' o 'no'. 
    ¿Hay indicios de acoso o comportamiento inapropiado basado en un patrón persistente de acercamiento?"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma:2b",
                "prompt": prompt,
                "stream": False
            },
            timeout=15
        )
        respuesta = response.json()["response"].strip().lower()
        return "sí" in respuesta or "si" in respuesta
    except Exception as e:
        print("Error con Ollama:", e)
        return False


def generar_justificacion(descripcion: str) -> str:
    prompt = f"""Explica por qué esta situación podría indicar acoso o peligro: 
    "{descripcion}". 
    Responde en máximo 2 oraciones con un enfoque profesional."""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma:2b",
                "prompt": prompt,
                "stream": False
            },
            timeout=20
        )
        return response.json()["response"].strip()
    except Exception as e:
        print("Error generando justificación:", e)
        return "El sistema detectó un patrón de comportamiento sospechoso que podría indicar acoso."