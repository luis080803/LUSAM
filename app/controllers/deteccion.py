# importación de librerías necesarias para el procesamiento de imágenes (opencv, numpy, fastapi) 
import cv2
import numpy as np
from fastapi import APIRouter,Request, Cookie, HTTPException, Form
from fastapi.responses import StreamingResponse, JSONResponse
from datetime import datetime, date
import os
from app.models.imagenes import ImagenBase
from app.repository.imagen_rep import ImagenRepository
from pydantic import BaseModel
from app.repository.stream import StreamRepository
from motor.motor_asyncio import AsyncIOMotorClientSession
from app.config.database import db

# el router se encarga de manejar las rutas de la página 
router = APIRouter()

# configuración de la dirección ip y url del stream de la cámara esp32 que estará en el carrito manejable
ESP32_IP = "192.168.100.190" #"192.168.4.1"
STREAM_URL = f"http://{ESP32_IP}:81/stream"

# cargamos el modelo de detección de objetos
classNames = []
# coco.names: es un archivo que contiene los nombres de los objetos que se pueden detectar, 
# como por ejemplo personas, bicicletas, carros, motocicletas, aviones, buses, trenes, camiones, animales, etc.
with open('app/models/coco.names', 'rt') as f: 
    classNames = f.read().rstrip('\n').split('\n')

# cargamos el modelo de detección de objetos
configPath = 'app/models/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
# ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt: es un archivo que contiene la configuración del modelo de detección de objetos
weightsPath = 'app/models/frozen_inference_graph.pb'
# frozen_inference_graph.pb: es un archivo que contiene los pesos del modelo de detección de objetos
net = cv2.dnn_DetectionModel(weightsPath, configPath) 
net.setInputSize(320, 320) # tamaño de la imagen de entrada
net.setInputScale(1.0 / 127.5) # escala de la imagen de entrada
net.setInputMean((127.5, 127.5, 127.5)) # media de la imagen de entrada
net.setInputSwapRB(True) # intercambiar los canales de la imagen de entrada


detectar = False # bandera para activar/desactivar la detección de objetos
ultimo_frame = None  # Aquí se guarda el último frame procesado

class CapturaRequest(BaseModel):
    stream_id: str

# función para generar frames del stream
def generar_frames(): 
    global ultimo_frame # guardamos el último frame procesado para poder tomar una foto 
    cap = cv2.VideoCapture(STREAM_URL) # capturamos el stream de la cámara esp32
    if not cap.isOpened(): # si no se pudo abrir el stream de video, imprime un mensaje de error
        print("No se pudo abrir el stream de video")
        return 

    while True: # mientras se esté capturando el stream de video    
        ret, frame = cap.read() # capturamos el frame
        if not ret: # si no se pudo capturar el frame, continua con el siguiente
            continue

        # rotar el frame 180° para alinear imagen con las detecciones (porque la cámara está invertida)
        frame = cv2.rotate(frame, cv2.ROTATE_180)

        # guardar el último frame para poder tomar una foto de la última detección
        ultimo_frame = frame.copy()

        # Aplicar detección si está activado
        if detectar: 
            classIds, confs, bbox = net.detect(frame, confThreshold=0.5) # detectamos los objetos en el frame
            if len(classIds) != 0: # si se detectaron objetos
                for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox): # iteramos sobre los objetos detectados
                    label = f'{classNames[classId - 1]}: {int(round(confidence * 100))}%' # mostramos el nombre del objeto y su confianza
                    cv2.rectangle(frame, box, color=(0, 255, 0), thickness=2) # dibujamos un rectángulo alrededor del objeto
                    cv2.putText(frame, label, (box[0], box[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2) # mostramos el nombre del objeto y su confianza (el porcentaje de seguridad de que el objeto es el que se detectó)
                ultimo_frame = frame # guardamos el último frame para poder tomar una foto de la última detección

        # codificar y enviar el frame como MJPEG
        ret, buffer = cv2.imencode('.jpg', frame) 
        if not ret: # si no se pudo codificar el frame, continua con el siguiente
            continue
        frame_bytes = buffer.tobytes() # convertimos el frame a bytes
        yield (b'--frame\r\n' # indicamos que el frame es un frame de video
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n') # indicamos el tipo de contenido y el frame

    cap.release() # liberamos la cámara

# endpoint para activar/desactivar la detección de objetos
@router.post("/deteccion/toggle")
def toggle_deteccion():
    global detectar # globalizar la variable detectar
    detectar = not detectar # invertimos el valor de la variable detectar
    return {"status": "started" if detectar else "stopped"} # devolvemos el estado de la detección

# endpoint para el streaming con detección mediante peticiones get CON DETECCIÓN DE OBJETOS
@router.get("/deteccion_feed/{stream_id}") 
def video_feed(stream_id: str):
    return StreamingResponse(generar_frames(), # generamos los frames 
                             media_type='multipart/x-mixed-replace; boundary=frame') # indicamos el tipo de contenido y el frame

# endpoint para el streaming con detección mediante peticiones get SIN DETECCIÓN DE OBJETOS
@router.get("/stream/{stream_id}") 
async def stream_video(stream_id: str):
    def generar_desde_frame_global(): # función para generar frames del stream
        global ultimo_frame # globalizar la variable ultimo_frame

        while True: # mientras se esté capturando el stream de video
            if ultimo_frame is not None: # si el último frame no es None
                # Codifica el frame como JPEG
                ret, buffer = cv2.imencode('.jpg', ultimo_frame)
                if ret: # si se pudo codificar el frame
                    frame_bytes = buffer.tobytes() # convertimos el frame a bytes
                    yield (b'--frame\r\n' # indicamos que el frame es un frame de video
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n') # indicamos el tipo de contenido y el frame

    return StreamingResponse(generar_desde_frame_global(), # generamos los frames
                             media_type='multipart/x-mixed-replace; boundary=frame') # indicamos el tipo de contenido y el frame


# endpoint para tomar foto desde el último frame
@router.post("/deteccion/capturar_foto")
async def capturar_foto(request: CapturaRequest, usuario: str = Cookie(None, alias="current_user")):
    global stream_id  # variable global stream_id

    if ultimo_frame is None: # si el último frame es nulo
        return JSONResponse(content={"error": "No hay frame disponible aún"}, status_code=500) # devolvemos un error 500 (error interno del servidor)

    # creamos nombre único para la imagen
    fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"foto_{fecha_hora}.jpg"
    ruta_guardado_relativa = f"app/views/static/uploads/{nombre_archivo}"
    ruta_guardado_absoluta = os.path.join(os.getcwd(), ruta_guardado_relativa)

    # guardar el frame como imagen
    cv2.imwrite(ruta_guardado_absoluta, ultimo_frame)

    # crear objeto ImagenBase para guardar en BD
    imagen_data = ImagenBase(
        Usuario=usuario,
        codigo_acceso=request.stream_id,  # stream_id es el id del stream de la cámara esp32
        Fecha=date.today(), # fecha de la imagen (hoy)
        Ruta=f"/static/uploads/{nombre_archivo}" # ruta de la imagen donde se almacenará
    )

    # guardar en base de datos
    nueva_imagen = await ImagenRepository.create_image(imagen_data) # guardamos la imagen en la base de datos

    return { # devolvemos el mensaje de éxito
        "mensaje": "Foto capturada", # mensaje de éxito
        "ruta": f"/static/uploads/{nombre_archivo}", # ruta de la imagen donde se almacenará
        "imagen_db": nueva_imagen # imagen guardada en la base de datos
    }