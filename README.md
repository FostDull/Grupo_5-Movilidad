# Sistema de Seguridad Kuntur Movilidad

![Kuntur Movilidad Logo](https://via.placeholder.com/150?text=Kuntur+Logo)  
Sistema avanzado de detección de comportamientos sospechosos mediante análisis de video en tiempo real con inteligencia artificial.

---

## 🚀 Características Principales

- 🎥 Captura de video desde cámaras IP  
- 🧠 Detección de personas y armas con YOLOv8  
- 📏 Análisis de distancias e interacciones  
- ⚠️ Sistema de alertas inteligentes  
- ☁️ Almacenamiento en Backblaze B2  
- 💬 Justificación de alertas con LLM (Llama 3)  
- 📼 Grabación automática de segmentos de 25 segundos en `.mp4`

---

## 📦 Instalación
a

```bash
# Clonar repositorio
git clone https://github.com/FostDull/Grupo_5-Movilidad.git
cd Grupo_5-Movilidad

# Cambiar a rama de desarrollo
git checkout Jessiel

# Instalar dependencias
pip install -r requirements.txt

Estructura del proyecto
.
├── main.py # API principal
├── base/
│ └── MongoKr.py # Conexión y lógica con MongoDB
├── data/
│ └── videos/ # Carpeta para almacenar videos
├── static/ # Archivos estáticos servidos por la API
├── .env # Variables de entorno (no se sube al repo)
└── requirements.txt # Dependencias del proyecto

Aquitectura
https://lucid.app/lucidchart/fefcf5ee-3113-40f3-96e8-d510bd5ad54b/edit?viewport_loc=-895%2C-821%2C3638%2C1796%2C0_0&invitationId=inv_10ada966-30ef-40b8-b5fe-8ba6cffc1164

📤 Subida de Videos
Endpoint: POST /upload-video/

Parámetro: file (tipo UploadFile)

Formatos permitidos: .webm, .mp4, .mov, .avi

Ejemplo con curl:

bash
Copiar
Editar
curl -X POST "http://localhost:8001/upload-video/" -F "file=@video.mp4"
📥 Consulta de Alertas
Endpoint: GET /alertas/

Devuelve una lista de documentos de MongoDB convertidos a JSON.

🔐 CORS
Este proyecto permite solicitudes desde cualquier origen (*). Puedes restringirlo modificando la configuración de CORS en main.py.

🛠 Recomendaciones
Usa un servicio como Backblaze B2 o Amazon S3 para almacenar los videos en producción.

Implementa autenticación para proteger los endpoints.

🚀 Cómo Funciona
Carga los modelos de detección de personas y armas.

Lee el video frame a frame.

Detecta personas y realiza seguimiento (tracking).

Detecta armas cercanas a las personas.

Evalúa interacciones entre personas para identificar acercamientos progresivos (posible acoso).

Genera alertas e interpreta eventos.

Exporta video procesado con anotaciones y resultados en JSON.

▶️ Uso

from procesador_video import procesar_video

resultados, salida_video = procesar_video("ruta/del/video.mp4")
print(resultados)

💡 Notas
Incluye workaround para ultralytics==8.2.0 relacionado con DFLoss.

Compatible con YOLOv8 y YOLOv5 como fallback.

Si el modelo de armas no está presente, se descargará automáticamente desde Google Drive.

{
  "video": "nombre.mp4",
  "fecha_procesamiento": "2025-07-16T14:00:00",
  "alertas": [...],
  "tipo_evento": "POSIBLE_ACOSO",
  "confianza": 0.8,
  "frame_detectado": 232,
  "estadisticas": {
    "personas": 3,
    "armas": 1,
    "interacciones": 2
  }
}

