from b2sdk.v2 import InMemoryAccountInfo, B2Api
import os

# ✅ Configuración real (NO compartas esto públicamente en producción)
B2_KEY_ID = "005edb6e50f32700000000003"
B2_APP_KEY = "K005P0f0Ubgb5zP7aFezbKC/6ri7l0Y"
B2_BUCKET_NAME = "evidenciaskunturmovilidad"

info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", B2_KEY_ID, B2_APP_KEY)
bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)

def subir_a_backblaze(path_archivo_local):
    nombre_remoto = os.path.basename(path_archivo_local)
    with open(path_archivo_local, "rb") as f:
        bucket.upload_bytes(f.read(), nombre_remoto)
    print(f"✅ Archivo subido a Backblaze: {nombre_remoto}")

def subir_bytes(nombre_archivo: str, data: bytes):
    bucket.upload_bytes(data, nombre_archivo)
