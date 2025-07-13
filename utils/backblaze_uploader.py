from b2sdk.v2 import InMemoryAccountInfo, B2Api
import os

# Inicialización
b2_info = InMemoryAccountInfo()
b2_api = B2Api(b2_info)
b2_api.authorize_account(
    "production",
    os.getenv("B2_KEY_ID"),
    os.getenv("B2_APP_KEY")
)
bucket_name = os.getenv("B2_BUCKET")
bucket = b2_api.get_bucket_by_name(bucket_name)

# Función para subir según tipo
def subir_a_backblaze(ruta_local):
    nombre_base = os.path.basename(ruta_local)
    extension = os.path.splitext(nombre_base)[1].lower()

    # Determinar carpeta según extensión
    if extension in ['.wav', '.mp3', '.aac', '.flac']:
        carpeta = "Audio"
    elif extension in ['.mp4', '.mov', '.avi', '.mkv']:
        carpeta = "Video"
    else:
        carpeta = "Otros"

    # Construir ruta remota
    nombre_remoto = f"{carpeta}/{nombre_base}"

    print(f"Subiendo a Backblaze: {nombre_remoto}")
    file_version = bucket.upload_local_file(
        local_file=ruta_local,
        file_name=nombre_remoto
    )

    # URL pública (si tu bucket es público)
    url_publica = f"https://f000.backblazeb2.com/file/{bucket_name}/{nombre_remoto}"
    return url_publica
