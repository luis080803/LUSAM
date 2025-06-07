import cv2
import numpy as np
from fastapi import APIRouter,Request, Cookie
from fastapi.responses import StreamingResponse, JSONResponse
from datetime import datetime, date
import os
from app.models.imagenes import ImagenBase
from app.repository.imagen_rep import ImagenRepository
from pydantic import BaseModel

router = APIRouter()

ESP32_IP = "192.168.4.1"
STREAM_URL = f"http://{ESP32_IP}:81/stream"

# === CARGA DEL MODELO ===
classNames = []
with open('app/models/coco.names', 'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

configPath = 'app/models/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath = 'app/models/frozen_inference_graph.pb'

net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

# === FLAGS Y VARIABLES GLOBALES ===
detectar = False
ultimo_frame = None  # Aquí se guarda el último frame procesado

class CapturaRequest(BaseModel):
    stream_id: str

# === FUNCION PARA GENERAR FRAMES DEL STREAM ===
def generar_frames():
    global ultimo_frame
    cap = cv2.VideoCapture(STREAM_URL)
    if not cap.isOpened():
        print("❌ No se pudo abrir el stream de video")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # 🔄 ROTAR EL FRAME 180° para alinear imagen con las detecciones
        frame = cv2.rotate(frame, cv2.ROTATE_180)

        # Guardar el último frame
        ultimo_frame = frame.copy()

        # Aplicar detección si está activado
        if detectar:
            classIds, confs, bbox = net.detect(frame, confThreshold=0.5)
            if len(classIds) != 0:
                for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                    label = f'{classNames[classId - 1]}: {int(round(confidence * 100))}%'
                    cv2.rectangle(frame, box, color=(0, 255, 0), thickness=2)
                    cv2.putText(frame, label, (box[0], box[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                ultimo_frame = frame

        # Codificar y enviar el frame como MJPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

# === ENDPOINT PARA ACTIVAR/DESACTIVAR DETECCIÓN ===
@router.post("/deteccion/toggle")
def toggle_deteccion():
    global detectar
    detectar = not detectar
    return {"status": "started" if detectar else "stopped"}

# === ENDPOINT PARA EL STREAMING CON DETECCIÓN ===
@router.get("/deteccion_feed/{stream_id}")
def video_feed(stream_id: str):
    return StreamingResponse(generar_frames(),
                             media_type='multipart/x-mixed-replace; boundary=frame')

@router.get("/stream/{stream_id}")
async def stream_video(stream_id: str):
    def generar_desde_frame_global():
        global ultimo_frame

        while True:
            if ultimo_frame is not None:
                # Codifica el frame como JPEG
                ret, buffer = cv2.imencode('.jpg', ultimo_frame)
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    return StreamingResponse(generar_desde_frame_global(),
                             media_type='multipart/x-mixed-replace; boundary=frame')


# === ENDPOINT PARA TOMAR FOTO DESDE EL ULTIMO FRAME ===
@router.post("/deteccion/capturar_foto")
async def capturar_foto(request: CapturaRequest,   usuario: str = Cookie(None, alias="current_user")):
    global stream_id  # Asumiendo que tienes esta variable global

    if ultimo_frame is None:
        return JSONResponse(content={"error": "No hay frame disponible aún"}, status_code=500)

    # Crear nombre único para la imagen
    fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"foto_{fecha_hora}.jpg"
    ruta_guardado_relativa = f"app/views/static/uploads/{nombre_archivo}"
    ruta_guardado_absoluta = os.path.join(os.getcwd(), ruta_guardado_relativa)

    # Guardar el frame como imagen
    cv2.imwrite(ruta_guardado_absoluta, ultimo_frame)

    # Crear objeto ImagenBase para guardar en BD
    imagen_data = ImagenBase(
        Usuario=usuario,
        codigo_acceso=request.stream_id,  # Asumiendo que stream_id es tu variable global
        Fecha=date.today(),
        Ruta=f"/static/uploads/{nombre_archivo}"
    )

    # Guardar en base de datos
    nueva_imagen = await ImagenRepository.create_image(imagen_data)

    return {
        "mensaje": "Foto capturada",
        "ruta": f"/static/uploads/{nombre_archivo}",
        "imagen_db": nueva_imagen
    }
