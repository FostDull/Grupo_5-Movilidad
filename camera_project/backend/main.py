import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from b2_upload import subir_bytes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    if file.content_type not in ["video/webm", "video/mp4"]:
        raise HTTPException(400, "Tipo de archivo no soportado")

    content = await file.read()
    filename = f"{uuid.uuid4()}.webm"
    try:
        subir_bytes(filename, content)
    except Exception as e:
        raise HTTPException(500, f"Error al subir a B2: {e}")

    return {"message": "Subido exitosamente", "file_name": filename}
