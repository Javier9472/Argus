import cv2
import numpy as np
import logging
import time
from config.constants import MJPEG_QUALITY

logger = logging.getLogger("VideoCompressor")
logger.setLevel(logging.INFO)

def compress_frame_batch(frames: list[np.ndarray], quality: int = MJPEG_QUALITY) -> list[bytes]:
    compressed_frames = []
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]

    start_time = time.time()

    for idx, frame in enumerate(frames):
        success, encoded = cv2.imencode('.jpg', frame, encode_param)
        if not success:
            logger.warning(f"Falló la compresión del frame {idx}")
            continue
        compressed_bytes = encoded.tobytes()
        compressed_frames.append(compressed_bytes)
        size_kb = len(compressed_bytes) / 1024
        logger.debug(f"Frame {idx}: comprimido a {size_kb:.2f} KB")

    elapsed = time.time() - start_time
    logger.info(f"Comprimidos {len(compressed_frames)} frames en {elapsed:.2f} s")

    return compressed_frames
