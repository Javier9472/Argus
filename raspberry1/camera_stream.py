import cv2
from config import constants
import logging

logging.basicConfig(filename='logs/raspberry.log', level=logging.INFO)

def get_camera():
    gst_pipeline = (
        f"tcpclientsrc host=localhost port={constants.GSTREAMER_PORT} ! "
        f"decodebin ! videoconvert ! "
        f"videoscale ! video/x-raw,width={constants.CAMERA_WIDTH},height={constants.CAMERA_HEIGHT} ! appsink"
    )
    cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

    if not cap.isOpened():
        logging.error("No se pudo abrir la cámara Global Shutter (pipeline GStreamer)")
    else:
        logging.info("Cámara Global Shutter inicializada correctamente")
    
    return cap
