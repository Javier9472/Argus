"""
Detectores ligeros (actualmente: personas con YOLO TRT).
"""

from .yolo_person import run_person_detector

__all__ = ["run_person_detector"]
