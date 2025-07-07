# Grupo_5-Movilidad

Proyecto de la Desarrollo de Sistemas de Información enfocado en la seguridad, específicamente en movilidad.
# Sistema de Monitoreo y Alerta para Transporte Público
**Proyecto académico de la materia: Desarrollo de Sistemas**  
**Carrera:** Ingeniería en Sistemas  
**Semestre:** 6to  
**Grupo:** 5  
**Integrantes:**  
- Donovan (`DomoPili`)  
- Jonathan (`FostDull`) 
- Jessiel (``) 

---

## Descripción del proyecto

Este proyecto implementa un sistema inteligente de monitoreo para buses y taxis, utilizando inteligencia artificial (IA) para detectar situaciones sospechosas como robos o acoso dentro del vehículo. Al detectar un evento, el sistema:

- Activa una alarma sonora 
- Cierra automáticamente las puertas del vehículo 
- Notifica a las autoridades competentes con ubicación y datos del incidente 

---

## Tecnologías utilizadas

| Tecnología | Función |
|------------|---------|
| Python     | Lenguaje principal del proyecto |
| PyCharm    | Entorno de desarrollo (IDE) |
| Git & GitHub | Control de versiones y colaboración |
| OpenCV     | Captura y procesamiento de video |
| Hugging Face (Transformers) | Modelo de IA para detección |
| playsound  | Sonido de alarma |
| requests   | Comunicación con API (notificación policial) |

---

## Inteligencia Artificial usada

Utilizamos modelos preentrenados de [Hugging Face](https://huggingface.co/) como:
- `google/vit-base-patch16-224` para clasificación de imágenes.
- Opcionalmente se puede entrenar un modelo personalizado para detección de violencia o acoso.

---

##  Estructura del proyecto
Grupo_5-Movilidad/
├── main.py # Código principal del sistema
├── alarma.mp3 # Sonido de alarma
├── requirements.txt # Lista de librerías necesarias
└── README.md # Documentación del proyecto
