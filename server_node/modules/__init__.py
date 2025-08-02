"""
Pequeñas utilidades genéricas.
"""

from .queue_manager import CameraBuffer, make_queue
from .video_compressor import compress_batch         # versión de alto nivel

__all__ = ["CameraBuffer", "make_queue", "compress_batch"]
