"""
video_compressor.py
───────────────────
• Compresión de lotes de frames a JPEG (MJPEG).
• Soporta CPU (OpenCV) y, si está disponible, GPU con `cv2.cuda` (NvJPEG).
"""

from __future__ import annotations

import cv2
import numpy as np
import time
from typing import List

from config import settings
from utils.logger import get_logger

log = get_logger("VideoCompressor")

# ── Validación de frames ───────────────────────────────────────
def _is_valid_frame(frame: np.ndarray, idx: int) -> bool:
    if not isinstance(frame, np.ndarray):
        log.warning(f"[VALIDATE] Frame {idx}: no es ndarray")
        return False
    if frame.size == 0:
        log.warning(f"[VALIDATE] Frame {idx}: arreglo vacío")
        return False
    if frame.ndim != 3:
        log.warning(f"[VALIDATE] Frame {idx}: no es imagen 3-D (shape={frame.shape})")
        return False
    if np.isnan(frame).any() or np.isinf(frame).any():
        log.warning(f"[VALIDATE] Frame {idx}: contiene NaN/Inf")
        return False
    return True


# ── CPU (OpenCV) ───────────────────────────────────────────────
def compress_opencv(frames: List[np.ndarray],
                    quality: int | None = None) -> List[bytes]:
    """
    Compresión MJPEG en CPU usando `cv2.imencode`.
    """
    quality = quality or settings.MJPEG_QUALITY
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]

    t0 = time.time()
    out: List[bytes] = []

    for idx, fr in enumerate(frames):
        if not _is_valid_frame(fr, idx):
            continue
        ok, enc = cv2.imencode(".jpg", fr, encode_param)
        if ok:
            out.append(enc.tobytes())
        else:
            log.warning(f"[CPU] Falló compresión en frame {idx}")

    log.debug(f"[CPU] {len(out)}/{len(frames)} frames → {time.time()-t0:.3f}s")
    return out


# ── GPU (NvJPEG vía cv2.cuda) ──────────────────────────────────
def _cuda_available() -> bool:
    return cv2.cuda.getCudaEnabledDeviceCount() > 0


def compress_cuda(frames: List[np.ndarray],
                  quality: int | None = None) -> List[bytes]:
    """
    Compresión GPU con NvJPEG (solo si OpenCV fue compilado con CUDA).
    Lanza `RuntimeError` si CUDA no está disponible.
    """
    if not _cuda_available():
        raise RuntimeError("OpenCV CUDA no disponible en este entorno")

    quality = quality or settings.MJPEG_QUALITY
    param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    out: List[bytes] = []
    t0 = time.time()

    for idx, f in enumerate(frames):
        if not _is_valid_frame(f, idx):
            continue
        gpu = cv2.cuda_GpuMat()
        gpu.upload(f)
        ok, enc = cv2.imencode(".jpg", gpu, param)
        if ok:
            out.append(enc.tobytes())
        else:
            log.warning(f"[CUDA] Falló compresión frame {idx}")

    log.debug(f"[CUDA] {len(out)}/{len(frames)} frames → {time.time()-t0:.3f}s")
    return out


# ── API de alto nivel ──────────────────────────────────────────
def compress_batch(frames: List[np.ndarray],
                   prefer_gpu: bool = True) -> List[bytes]:
    """
    Comprime usando GPU si está disponible y `prefer_gpu=True`,
    de lo contrario utiliza la vía CPU.
    """
    if prefer_gpu:
        try:
            return compress_cuda(frames)
        except Exception as e:
            log.warning(f"[GPU->CPU] {e}. Conmutando a CPU.")
    return compress_opencv(frames)
