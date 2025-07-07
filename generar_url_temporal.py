from b2sdk.v2 import *
import datetime

# Configura tus credenciales y bucket
B2_KEY_ID = "005b278d89dfc3e0000000001"
B2_APP_KEY = "K0053GPlUDge3hAND2GOZlx5bDhct7c"
B2_BUCKET_NAME = "Prueba1aud"
B2_BUCKET_NAME = "Prueba1aud"
TIEMPO_EN_SEGUNDOS = 3600  # 1 hora

# Inicializar B2
info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", B2_KEY_ID, B2_APP_KEY)
bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)
download_url = b2_api.account_info.get_download_url()

# Listar y generar URLs
print("🔎 Archivos encontrados:\n")
for file_version, folder_name in bucket.ls():
    file_name = file_version.file_name

    # ✅ Corrección aquí
    auth_token = bucket.get_download_authorization(file_name, TIEMPO_EN_SEGUNDOS)
    url = f"{download_url}/file/{B2_BUCKET_NAME}/{file_name}?Authorization={auth_token}"

    print(f"{file_name}:")
    print(f"🔗 {url}\n")
