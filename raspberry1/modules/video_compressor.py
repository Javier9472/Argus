import cv2
import numpy as np
import time
from config import constants
from utils.logger_config import get_logger

logger = get_logger ("VideoCompressor")

def is_valid_frame (frame: np.ndarray, idx: int) -> bool:
        
    if not isinstance(frame, np.ndarray):
        logger.warning(f"Frame {idx} inválido: no es ndarray")
        return False

    if np.isnan(frame).any() or np.isinf(frame).any():
        logger.warning(f"Frame {idx} inválido: contiene NaN o infinitos")
        return False

    if frame.size == 0:
        logger.warning(f"Frame {idx} inválido: arreglo vacío")
        return False

    if frame.shape[0] < 100 or frame.shape[1] < 100:
        logger.warning(f"Frame {idx} inválido: dimensiones sospechosas {frame.shape}")
        return False
    
    return True 

def compress_frame_batch(frames: list[np.ndarray], quality: int = constants.MJPEG_QUALITY) -> list[bytes]:
    compressed_frames = []
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]

    if not frames:
        logger.warning("Lote de frames vacío recibido.")
        return []

    invalid_type, empty_array, bad_dims, encode_fail, nan_inf = 0, 0, 0, 0, 0

    start_time = time.time()

    for idx, frame in enumerate(frames):
        if not is_valid_frame (frame, idx):
            if not isinstance (frame, np.ndarray):
               is_valid_type += 1 
            elif np.isnan (frame).any() or np.isinf (frame).any ():
               nan_inf +=1
            elif frame.size == 0:
               empty_array += 1 
            elif frame.shape [0] < 100 or frame.shape [1] < 100:
                bad_dims += 1
            continue
        
        success, encoded = cv2.imencode('.jpg', frame, encode_param)
        if not success:
            logger.warning(f"Falló la compresión del frame {idx}")
            encode_fail += 1
            continue
            
        compressed_bytes = encoded.tobytes()
        compressed_frames.append(compressed_bytes)
        size_kb = len(compressed_bytes) / 1024
        logger.debug(f"Frame {idx}: comprimido a {size_kb:.2f} KB")

    elapsed = time.time() - start_time
    logger.info(f"Comprimidos {len(compressed_frames)} frames en {elapsed:.2f} s")
    logger.info(f"Errores: tipo={invalid_type}, vacío={empty_array}, dims={bad_dims}, NaN/Inf={nan_inf}, encoding={encode_fail}")

    return compressed_frames