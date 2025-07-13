import os
import uuid
import time
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from b2sdk.v2 import InMemoryAccountInfo, B2Api
from dotenv import load_dotenv

# === Cargar .env ===
load_dotenv()

# === Configuración CORS ===
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === MongoDB Atlas ===
mongo_uri = os.getenv("MONGO_URI")
mongo_db = os.getenv("MONGO_DB")
mongo_collection = os.getenv("MONGO_COLLECTION")

client = MongoClient(mongo_uri, server_api=ServerApi("1"))
db = client[mongo_db]
coleccion = db[mongo_collection]

# === Backblaze B2 ===
info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", os.getenv("B2_KEY_ID"), os.getenv("B2_APP_KEY"))
bucket = b2_api.get_bucket_by_name(os.getenv("B2_BUCKET"))

# === Modelo de datos ===
class Denuncia(BaseModel):
    descripcion: str
    ubicacion: str
    url: Optional[HttpUrl] = None

# === Endpoint raíz ===
@app.get("/")
async def root():
    return {"message": "Servidor funcionando"}

# === Subida de video con metadatos ===
@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...), descripcion: str = "", ubicacion: str = ""):
    valid_types = [
        "video/webm",
        "video/mp4",
        "video/quicktime",
        "video/x-msvideo",
        "application/octet-stream"
    ]

    # Verificación MIME
    if file.content_type not in valid_types:
        if not any(file.filename.lower().endswith(ext) for ext in ['.webm', '.mp4', '.mov', '.avi']):
            raise HTTPException(400, "Tipo de archivo no soportado. Formatos aceptados: .webm, .mp4, .mov, .avi")

    # Generar nombre único
    file_ext = os.path.splitext(file.filename)[1] or ".webm"
    unique_filename = f"{uuid.uuid4()}{file_ext}"

    try:
        start = time.time()
        contenido = await file.read()
        archivo_subido = bucket.upload_bytes(contenido, unique_filename)
        url_publica = f"https://f000.backblazeb2.com/file/{os.getenv('B2_BUCKET')}/{archivo_subido.file_name}"
        elapsed = time.time() - start

        # Guardar en Mongo
        coleccion.insert_one({
            "descripcion": descripcion,
            "ubicacion": ubicacion,
            "url": url_publica,
            "nombre_original": file.filename,
            "nombre_guardado": archivo_subido.file_name,
            "fecha": datetime.utcnow()
        })

        return {
            "mensaje": f"Video subido a B2 ({len(contenido) / 1024:.1f} KB en {elapsed:.2f}s)",
            "url_video": url_publica,
            "nombre_archivo": archivo_subido.file_name
        }

    except Exception as e:
        raise HTTPException(500, f"Error al guardar el video: {str(e)}")

# === Endpoint para denuncias con archivo o URL ===
@app.post("/denuncias/")
async def crear_denuncia(data: Denuncia, archivo: Optional[UploadFile] = File(None)):
    if data.url and archivo:
        raise HTTPException(400, detail="No se puede enviar URL y archivo al mismo tiempo.")

    evidencia_url = data.url

    if archivo:
        contenido = await archivo.read()
        nombre = archivo.filename
        archivo_subido = bucket.upload_bytes(contenido, nombre)
        evidencia_url = f"https://f000.backblazeb2.com/file/{os.getenv('B2_BUCKET')}/{archivo_subido.file_name}"

    documento = {
        "descripcion": data.descripcion,
        "ubicacion": data.ubicacion,
        "url": str(evidencia_url) if evidencia_url else None,
        "fecha": datetime.utcnow()
    }

    coleccion.insert_one(documento)
    return {"mensaje": "Denuncia registrada", "url_evidencia": evidencia_url}

# === Endpoint para denuncias sin archivo (por ejemplo, audio ya transcrito) ===
@app.post("/denuncias/audio/")
async def denuncia_audio(data: Denuncia):
    try:
        coleccion.insert_one({
            "descripcion": data.descripcion,
            "ubicacion": data.ubicacion,
            "url": str(data.url) if data.url else None,
            "fecha": datetime.utcnow()
        })
        return {"mensaje": "Denuncia de audio registrada correctamente"}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# === Arranque local ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
