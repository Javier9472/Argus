import cv2
from config import constants
import logging

logging.basicConfig(filename='logs/raspberry.log', level=logging.INFO)

def compress_frame(frame):
    ret, encoded = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), constants.MJPEG_QUALITY])
    if not ret:
        logging.warning("Fallo en compresión de frame")
        return None
    return encoded.tobytes()
