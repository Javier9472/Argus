import numpy as np, time
from queue import Empty, Full
from pathlib import Path
import cv2

from utils.logger import get_logger
from utils.flags import FLAGS
from modules.gpu_utils import load_engine, allocate_buffers, do_inference
from config import settings, constants

log = get_logger("YOLODetector")

def _preprocess(frames):
    """Redimensiona y normaliza a (N, 3, H, W) FP32"""
    inp = []
    for f in frames:
        img = cv2.resize(f, (640, 640))
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR->RGB, HWC->CHW
        inp.append(img.astype(np.float32) / 255.0)
    return np.ascontiguousarray(np.stack(inp))


def run_person_detector(infer_q, send_q):
    """Proceso GPU: lee lote, corre YOLO TensorRT, levanta flag y pasa lote a send_q."""
    engine = load_engine(settings.YOLO_ENGINE)
    context = engine.create_execution_context()
    h_bufs, d_bufs, bindings, stream = allocate_buffers(engine)

    while True:
        try:
            meta, frames_dec, frames_comp = infer_q.get(timeout=5)
        except Empty:
            continue

        inp = _preprocess(frames_dec)
        out = do_inference(context, h_bufs, d_bufs, bindings, stream, inp)

        # Simple umbral: si existe detección con label "person" > CONF_THRESHOLD
        if (out[..., 4] * out[..., 5:].max(axis=-1) > constants.CONF_THRESHOLD).any():
            flag_key = f"{constants.FLAG_PERSON_DETECTED}_{meta['node_id']}"
            FLAGS[flag_key] = True
            try:
                # reenviar lote al siguiente proceso
                send_q.put((meta, frames_comp), timeout=1)
            except Full:
                log.warning("send_q llena: lote descartado")
