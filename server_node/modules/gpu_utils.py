"""
gpu_utils.py
────────────
Funciones de ayuda para TensorRT + PyCUDA.

Uso típico:
    engine  = load_engine(settings.YOLO_ENGINE)
    buffers = allocate_buffers(engine)
    context = engine.create_execution_context(active_optimization_profile=0)
    out = do_inference(context, *buffers, batch)
"""

from __future__ import annotations
from pathlib import Path
from typing import Tuple, List

import numpy as np
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit  # noqa: F401  (inicializa contexto CUDA)

from utils.logger import get_logger

log = get_logger("GPUUtils")


# ── Carga de engine ────────────────────────────────────────────
def load_engine(engine_path: str | Path) -> trt.ICudaEngine:
    engine_path = Path(engine_path)
    assert engine_path.exists(), f"Engine no encontrado: {engine_path}"
    TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

    with open(engine_path, "rb") as f, trt.Runtime(TRT_LOGGER) as runtime:
        engine = runtime.deserialize_cuda_engine(f.read())
        log.info(f"Engine TensorRT cargado: {engine_path.name}")
        return engine


# ── Reservas de buffers ────────────────────────────────────────
def allocate_buffers(engine: trt.ICudaEngine
                     ) -> Tuple[List[np.ndarray],
                                List[cuda.DeviceAllocation],
                                List[int],
                                cuda.Stream]:
    """
    Devuelve (host_bufs, device_bufs, bindings, stream)
    host_bufs → pagelocked
    binding 0 → input; binding 1 → output (puedes ampliar en tu propio código).
    """
    host_bufs, device_bufs, bindings = [], [], []

    for idx in range(engine.num_bindings):
        shape = engine.get_binding_shape(idx)
        size = int(np.prod(shape))
        dtype = trt.nptype(engine.get_binding_dtype(idx))

        h_buf = cuda.pagelocked_empty(size, dtype)
        d_buf = cuda.mem_alloc(h_buf.nbytes)

        host_bufs.append(h_buf)
        device_bufs.append(d_buf)
        bindings.append(int(d_buf))

        log.debug(f"Binding {idx}: shape={shape}, dtype={dtype}, nbytes={h_buf.nbytes}")

    return host_bufs, device_bufs, bindings, cuda.Stream()


# ── Inferencia ─────────────────────────────────────────────────
def do_inference(context: trt.IExecutionContext,
                 host_bufs: List[np.ndarray],
                 device_bufs: List[cuda.DeviceAllocation],
                 bindings: List[int],
                 stream: cuda.Stream,
                 batch: np.ndarray) -> np.ndarray:
    """
    Ejecuta una pasada de inferencia:
        batch ndarray (contiguo, dtype correcto)  → copia H→D
        context.execute_async_v2(...)            → GPU
        copia D→H de salida                      → return ndarray
    """
    # copia input
    np.copyto(host_bufs[0], batch.ravel())
    cuda.memcpy_htod_async(device_bufs[0], host_bufs[0], stream)

    # inferencia asincrónica
    context.execute_async_v2(bindings=bindings, stream_handle=stream.handle)

    # copiar salida
    cuda.memcpy_dtoh_async(host_bufs[1], device_bufs[1], stream)
    stream.synchronize()

    return host_bufs[1].reshape(context.get_binding_shape(1))
