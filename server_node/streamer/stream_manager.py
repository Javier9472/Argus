import cv2, time
from queue import Empty, Full
from multiprocessing import Manager
from modules.queue_manager import CameraBuffer
from utils.logger import get_logger
from config import settings

log = get_logger("StreamManager")

def run_stream_manager(frame_q, infer_q, display_dict):
    """
    • Recibe (meta, frames_dec, frames_comp) -> frame_q     (producción: Decompressor)
    • Mantiene CameraBuffer por cámara.
    • Actualiza display_dict[node_id] = último JPEG para HTTP streamer.
    • Empuja lote a infer_q  (YOLO)   (si la cola lo permite)
    """
    buffers: dict[str, CameraBuffer] = {}

    while True:
        try:
            meta, frames_dec, frames_comp = frame_q.get(timeout=5)
        except Empty:
            continue

        node_id = meta["node_id"]

        # ── Buffer circular por cámara ────────────────────────
        if node_id not in buffers:
            buffers[node_id] = CameraBuffer(settings.MAX_QUEUE_FRAMES)

        for fr in frames_dec:
            buffers[node_id].push(fr)

        # ── Actualiza imagen para UI ──────────────────────────
        latest = buffers[node_id].latest()
        if latest is not None:
            ok, enc = cv2.imencode(
                ".jpg", latest,
                [int(cv2.IMWRITE_JPEG_QUALITY), 70]
            )
            if ok:
                display_dict[node_id] = enc.tobytes()

        # ── Enviar a YOLO ─────────────────────────────────────
        try:
            infer_q.put((meta, frames_dec, frames_comp), timeout=1)
        except Full:
            log.warning("infer_q llena, lote descartado")
