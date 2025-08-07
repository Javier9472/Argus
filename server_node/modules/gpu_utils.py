from __future__ import annotations
from pathlib import Path
from typing import Tuple, List

import numpy as np
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit  

from utils.logger import get_logger

log = get_logger("GPUUtils")


def load_engine(engine_path: str | Path) -> trt.ICudaEngine:
    engine_path = Path(engine_path)
    assert engine_path.exists(), f"Engine no encontrado: {engine_path}"
    TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

    with open(engine_path, "rb") as f, trt.Runtime(TRT_LOGGER) as runtime:
        engine = runtime.deserialize_cuda_engine(f.read())
        log.info(f"Engine TensorRT cargado: {engine_path.name}")
        return engine

def allocate_buffers(engine: trt.ICudaEngine
                    ) -> Tuple[List[np.ndarray],
                                List[cuda.DeviceAllocation],
                                List[int],
                                cuda.Stream]:

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



def do_inference(context: trt.IExecutionContext,
                host_bufs: List[np.ndarray],
                device_bufs: List[cuda.DeviceAllocation],
                bindings: List[int],
                stream: cuda.Stream,
                batch: np.ndarray) -> np.ndarray:

    np.copyto(host_bufs[0], batch.ravel())
    cuda.memcpy_htod_async(device_bufs[0], host_bufs[0], stream)

    context.execute_async_v2(bindings=bindings, stream_handle=stream.handle)

    cuda.memcpy_dtoh_async(host_bufs[1], device_bufs[1], stream)
    stream.synchronize()

    return host_bufs[1].reshape(context.get_binding_shape(1))
