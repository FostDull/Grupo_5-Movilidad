import streamlit as st
import cv2
import os
import gdown
from ultralytics import YOLO
from utils.distance_utils import calcular_distancia_real
from utils.ollama_utils import generar_justificacion
from utils.alert_system import SistemaAlertas
from collections import defaultdict
from datetime import datetime

# ==== Workaround para ultralytics 8.2.0: stub de DFLoss ====
import ultralytics.utils.loss as _loss_mod
class DFLoss:
    def __init__(self, *args, **kwargs):
        pass
_loss_mod.DFLoss = DFLoss

# Configurar página
st.set_page_config(page_title="Detección Riesgos", layout="wide")

# ==== INPUT PARA CÁMARA IP ====
st.sidebar.header("Configuración de cámara IP")
ip_url = st.sidebar.text_input(
    "URL de la cámara IP (e.g. rtsp://192.168.1.60:554/stream1)",
    value="rtsp://192.168.1.60:554/stream1"
)

# Intentar abrir el stream
cap = cv2.VideoCapture(ip_url)
if not cap.isOpened():
    st.error(f"No se pudo abrir la cámara IP en: {ip_url}")
    st.stop()

# Función IOU
def calcular_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0]); yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2]); yB = min(boxA[3], boxB[3])
    inter = max(0, xB-xA) * max(0, yB-yA)
    areaA = (boxA[2]-boxA[0])*(boxA[3]-boxA[1])
    areaB = (boxB[2]-boxB[0])*(boxB[3]-boxB[1])
    return inter / float(areaA + areaB - inter)

# Carga de modelos
@st.cache_resource
def cargar():
    os.makedirs("modelos", exist_ok=True)

    # Modelo personas (COCO)
    p_path = "modelos/yolov8n.pt"
    if not os.path.exists(p_path):
        YOLO(p_path, task='detect')

    # Modelo armas especializado
    a_path = "modelos/weapon_yolov8n.pt"
    if not os.path.exists(a_path):
        url = "https://github.com/Musawer1214/Weapon-Detection-YOLO/raw/main/best%20(3).pt"
        try:
            import torch
            torch.hub.download_url_to_file(url, a_path)
        except:
            gdown.download(
                "https://drive.google.com/uc?id=1ZgqjONv3q43H9eBd5cG6JNkYd6tOjf1D",
                a_path, quiet=False
            )

    model_p = YOLO(p_path, task='detect')
    model_a = YOLO(a_path, task='detect')
    return model_p, model_a

yolo_personas, yolo_armas = cargar()
sistema = st.session_state.get('alertas', SistemaAlertas())
st.session_state['alertas'] = sistema

# Layout
col1, col2 = st.columns([3, 1])
vid_box           = col1.empty()
stats_box         = col2.empty()
situacion_box     = col2.empty()
justificacion_box = col2.empty()

# Parámetros
MAX_AREA_RATIO   = 0.1
DISTANCIA_UMBRAL = 1.5
MIN_TIEMPO_ACOSO = 10
MIN_ACERCAMIENTO = 0.2

historial   = defaultdict(list)
timestamps  = defaultdict(list)
frame_count = 0
res_pers    = None
res_armas   = None
ultima_act  = datetime.now()

while True:
    ret, frame = cap.read()
    if not ret:
        st.error("Error al capturar video. Verifica la cámara.")
        break

    frame_count += 1

    # --- PERSONAS: detectar cada 3 frames, trackear entre medio ---
    if frame_count % 3 == 0 or res_pers is None:
        res_pers = yolo_personas.track(
            frame, persist=True, classes=[0], imgsz=320, conf=0.3
        )[0]
    else:
        res_pers = yolo_personas.track(
            frame, persist=True, classes=[0], imgsz=320, conf=0.3
        )[0]

    cajas = {}
    if res_pers and res_pers.boxes is not None:
        for box in res_pers.boxes:
            tid = int(box.id) if box.id is not None else None
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
            if tid is not None:
                cajas[tid] = (x1, y1, x2, y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"ID:{tid}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # --- ARMAS: detectar cada 6 frames, trackear entre medio ---
    if frame_count % 6 == 0 or res_armas is None:
        res_armas = yolo_armas.track(
            frame, persist=True, imgsz=320, conf=0.5
        )[0]
    else:
        res_armas = yolo_armas.track(
            frame, persist=True, imgsz=320, conf=0.5
        )[0]

    armas = []
    if res_armas and res_armas.boxes is not None:
        for box in res_armas.boxes:
            conf = box.conf.item()
            if conf < 0.5:
                continue
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
            area = (x2 - x1) * (y2 - y1)
            if area / (frame.shape[0] * frame.shape[1]) > MAX_AREA_RATIO:
                continue
            if any(calcular_iou((x1, y1, x2, y2), p) > 0.2 for p in cajas.values()):
                continue
            armas.append((x1, y1, x2, y2, conf))
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(frame, f"ARMA {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # --- ACOSO ---
    ids = list(cajas.keys())
    posibles = []
    for i in range(len(ids)):
        for j in range(i+1, len(ids)):
            id1, id2 = ids[i], ids[j]
            b1, b2 = cajas[id1], cajas[id2]
            d = calcular_distancia_real(b1, b2, frame.shape)
            if d < DISTANCIA_UMBRAL:
                par = tuple(sorted((id1, id2)))
                historial[par].append(d)
                timestamps[par].append(datetime.now())
                historial[par] = [
                    h for k, h in enumerate(historial[par])
                    if (datetime.now() - timestamps[par][k]).seconds <= 30
                ]
                timestamps[par] = [
                    t for t in timestamps[par]
                    if (datetime.now() - t).seconds <= 30
                ]
                if len(historial[par]) > 2 and \
                   (historial[par][0] - historial[par][-1]) > MIN_ACERCAMIENTO and \
                   (timestamps[par][-1] - timestamps[par][0]).seconds > MIN_TIEMPO_ACOSO:
                    posibles.append((id1, id2, d))
                cx1, cy1 = (b1[0] + b1[2]) // 2, (b1[1] + b1[3]) // 2
                cx2, cy2 = (b2[0] + b2[2]) // 2, (b2[1] + b2[3]) // 2
                cv2.line(frame, (cx1, cy1), (cx2, cy2), (0, 0, 255), 2)
                cv2.putText(frame, f"{d:.2f}m", ((cx1 + cx2)//2, (cy1 + cy2)//2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # --- ALERTAS ---
    if armas:
        sistema.activar("ARMA DETECTADA")
    elif posibles and sistema.registrar(len(posibles)):
        sistema.activar("POSIBLE ACOSO")

    # --- RENDER UI ---
    vid_box.image(frame, channels="BGR", use_column_width=True)
    with stats_box.container():
        c1, c2, c3 = st.columns(3)
        c1.metric("Personas", len(cajas))
        c2.metric("Armas", len(armas))
        c3.metric("Acosos", len(posibles))

    ahora = datetime.now()
    if (ahora - ultima_act).seconds >= 5:
        ultima_act = ahora
        with situacion_box.container():
            if armas:
                st.error("**SITUACIÓN: CRÍTICA**\nDetección de arma")
            elif posibles:
                st.warning("**SITUACIÓN: ACOSO**\nPatrón sospechoso")
            else:
                st.success("**SITUACIÓN: NORMAL**")
        with justificacion_box.container():
            if sistema.alerta:
                if sistema.tipo == "ARMA DETECTADA":
                    st.error("**Justificación:** Amenaza directa: arma detectada.")
                else:
                    desc = f"{len(posibles)} acercamientos sospechosos."
                    just = generar_justificacion(desc)
                    st.warning(f"**Justificación:** {just}")
            else:
                st.info("Sin amenazas detectadas")

cap.release()
