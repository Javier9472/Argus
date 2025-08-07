import cv2
import numpy as np
from ultralytics import YOLO
from config.settings import MODELS_DIR
from config.constants import CONF_THRESHOLD_CLOTHES, FLAG_CLOTHES_FOUND
from utils.flags import FLAGS
from utils.logger import get_logger

log = get_logger("ClothesDetector")
model_path = MODELS_DIR / "clothes.engine"  
model = YOLO(str(model_path))

def detect_clothes(meta: dict, frames: list[np.ndarray], output_q):
    node_flag = f"{FLAG_CLOTHES_FOUND}_{meta['node_id']}"
    for frame in frames:
        results = model(frame, imgsz=(640, 640), conf=CONF_THRESHOLD_CLOTHES)
        detections = []
        for r in results:
            for box in r.boxes:
                conf = float(box.conf[0])
                if conf < CONF_THRESHOLD_CLOTHES:
                    continue
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append((x1, y1, x2, y2, conf))
        if detections:
            FLAGS[node_flag] = True
            output_q.put((meta, frame, detections))
            log.info(f"[ClothesDetector] Ropa detectada en {meta['node_id']} (conf>= {CONF_THRESHOLD_CLOTHES})")
            return
