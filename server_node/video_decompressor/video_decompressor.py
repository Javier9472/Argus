import cv2, numpy as np, time
from utils.logger import get_logger
from queue import Empty
from config import settings

log = get_logger("Decompressor")

def run_decompressor(batch_q, frame_q):
    while True:
        try:
            meta, frames_bytes = batch_q.get(timeout=5)
        except Empty:
            continue

        tic = time.time()
        decoded = []
        for b in frames_bytes:
            img = cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR)
            if img is not None:
                decoded.append(img)
        frame_q.put((meta, decoded))
        log.debug(f"Lote de {len(decoded)} frames decodificado en {time.time()-tic:.3f}s")
