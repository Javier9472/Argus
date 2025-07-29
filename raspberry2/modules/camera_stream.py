import cv2
import time
import os
from config import constants
from utils.logger_config import get_logger

logger = get_logger ("CameraStream2")

assert constants.GSTREAMER_PORT, "GSTREAMER_PORT no está definido"
assert constants.CAMERA_WIDTH > 0 and constants.CAMERA_HEIGHT > 0, "Resolución de cámara inválida"

def build_gst_pipeline(host, port, width, height):

    return (
        f"tcpclientsrc host={host} port={port} ! "
        f"decodebin ! videoconvert ! videoscale ! "
        f"video/x-raw,width={width},height={height} ! appsink"
    )

def get_camera():

    gst_pipeline = build_gst_pipeline(
        host="localhost",
        port=constants.GSTREAMER_PORT,
        width=constants.CAMERA_WIDTH,
        height=constants.CAMERA_HEIGHT
    )

    cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

    if not cap.isOpened():
        logger.error(f"[CAMERA] No se pudo abrir el stream desde libcamera-vid (puerto: {constants.GSTREAMER_PORT})")
        return None

    logger.info(f"[CAMERA] Cámara conectada correctamente por GStreamer (res: {constants.CAMERA_WIDTH}x{constants.CAMERA_HEIGHT})")
    return cap

def check_camera_stream(cap, retries=3, delay=1):

    for attempt in range(1, retries + 1):
        try:
            ret, frame = cap.read()
            if ret and frame is not None:
                logger.info(f"[CAMERA] Stream verificado exitosamente en intento {attempt}")
                return True
        except Exception as e:
            logger.exception(f"[CAMERA] Excepción al leer frame en intento {attempt}: {e}")
        time.sleep(delay)

    logger.error("[CAMERA] La cámara está abierta pero no entrega frames válidos.")
    cap.release()
    return False