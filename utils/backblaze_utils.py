import os
import requests
import hashlib
import json


def obtener_token_acceso(key_id, app_key):
    """Obtiene token de acceso usando el endpoint correcto"""
    auth_url = "https://api.backblazeb2.com/b2api/v2/b2_authorize_account"
    try:
        print(f"Autenticando con Backblaze usando keyID: {key_id[:5]}...")
        response = requests.get(auth_url, auth=(key_id, app_key), timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error de autenticación: {str(e)}")
        if 'response' in locals():
            print(f"Respuesta del servidor: {response.status_code} - {response.text[:200]}")
        return None


def subir_video_b2(video_path, nombre_archivo, key_id, app_key, bucket_id):
    """
    Sube un video a Backblaze B2 usando el bucket ID directamente
    :param video_path: Ruta local del video
    :param nombre_archivo: Nombre del archivo en B2
    :param key_id: B2_KEY_ID
    :param app_key: B2_APP_KEY
    :param bucket_id: ID del bucket (no nombre)
    :return: True si la subida fue exitosa, False en caso contrario
    """
    # 1. Autenticación
    auth_data = obtener_token_acceso(key_id, app_key)
    if not auth_data:
        return False

    # 2. Obtener URL de subida
    try:
        upload_url_endpoint = f"{auth_data['apiUrl']}/b2api/v2/b2_get_upload_url"
        headers = {"Authorization": auth_data["authorizationToken"]}
        payload = {"bucketId": bucket_id}

        print(f"Obteniendo URL de subida desde: {upload_url_endpoint}")
        response = requests.post(upload_url_endpoint, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        upload_data = response.json()
        print(f"URL de subida obtenida: {upload_data['uploadUrl']}")
    except Exception as e:
        print(f"❌ Error obteniendo URL de subida: {str(e)}")
        if 'response' in locals():
            try:
                print(f"Respuesta del servidor: {response.status_code} - {response.text[:200]}")
            except:
                pass
        return False

    # 3. Preparar y subir archivo
    try:
        # Leer archivo
        file_size = os.path.getsize(video_path)
        print(f"Tamaño del archivo: {file_size / 1024 / 1024:.2f} MB")

        with open(video_path, 'rb') as f:
            file_data = f.read()

        # Calcular SHA1
        sha1 = hashlib.sha1(file_data).hexdigest()

        # Cabeceras
        upload_headers = {
            "Authorization": upload_data["authorizationToken"],
            "Content-Type": "application/octet-stream",
            "X-Bz-File-Name": nombre_archivo,
            "X-Bz-Content-Sha1": sha1,
            "Content-Length": str(file_size)
        }

        # 4. Subir
        print(f"Subiendo {os.path.basename(video_path)}...")
        response = requests.post(
            upload_data["uploadUrl"],
            headers=upload_headers,
            data=file_data,
            timeout=120  # Tiempo mayor para videos grandes
        )
        response.raise_for_status()

        print(f"✅ Video subido exitosamente: {nombre_archivo}")
        print(f"File ID: {response.json()['fileId']}")
        return True

    except Exception as e:
        print(f"❌ Error en subida: {str(e)}")
        if 'response' in locals():
            try:
                error_resp = response.text
                print(f"Respuesta del servidor ({response.status_code}): {error_resp[:200]}")
            except:
                pass
        return False