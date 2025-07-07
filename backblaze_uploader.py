from b2sdk.v2 import InMemoryAccountInfo, B2Api
import os

# Reemplaza estos valores con los datos reales de tu cuenta
B2_KEY_ID = "005b278d89dfc3e0000000001"
B2_APP_KEY = "K0053GPlUDge3hAND2GOZlx5bDhct7c"
B2_BUCKET_NAME = "Prueba1aud"

# Inicializa la API de Backblaze
info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", B2_KEY_ID, B2_APP_KEY)
bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)

def subir_a_backblaze(path_archivo_local):
    """
    Sube un archivo local a Backblaze B2.
    """
    nombre_remoto = os.path.basename(path_archivo_local)
    with open(path_archivo_local, "rb") as f:
        bucket.upload_bytes(f.read(), nombre_remoto)
    print(f"Archivo subido a Backblaze: {nombre_remoto}")
