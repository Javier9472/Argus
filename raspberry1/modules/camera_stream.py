import cv2
import time
from config import constants
from utils.logger_config import get_logger

logger = get_logger("CameraStream")

assert constants.CAMERA_INDEX >= 0, "CAMERA_INDEX debe estar definido y ser >= 0"
assert constants.CAMERA_WIDTH > 0 and constants.CAMERA_HEIGHT > 0, "Resolución de cámara inválida"

def get_camera():
    cap = cv2.VideoCapture(constants.CAMERA_INDEX)

    if not cap.isOpened():
        logger.error(f"[CAMERA] No se pudo abrir la cámara USB (índice: {constants.CAMERA_INDEX})")
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, constants.CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, constants.CAMERA_HEIGHT)

    logger.info(f"[CAMERA] Cámara USB conectada correctamente (res: {constants.CAMERA_WIDTH}x{constants.CAMERA_HEIGHT})")
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
