import time
import numpy as np
import face_recognition
import cv2
from pathlib import Path
from config import settings
from config import constants
from utils.logger import get_logger
from utils.flags import FLAGS

log = get_logger("FaceDetector")
ENC_PATH   = Path(settings.EMBEDDINGS_DIR) / "encodings.npy"
NAMES_PATH = Path(settings.EMBEDDINGS_DIR) / "names.npy"
while not ENC_PATH.exists() or not NAMES_PATH.exists():
    log.info("Esperando encodings.npy y names.npy…")
    time.sleep(1)

known_faces = np.load(str(ENC_PATH), allow_pickle=True)
known_names = np.load(str(NAMES_PATH), allow_pickle=True)

def detect_faces(meta: dict, frames: list[np.ndarray], output_q):
    for frame in frames:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locs = face_recognition.face_locations(rgb, model="hog")
        encs = face_recognition.face_encodings(rgb, locs)

        for loc, enc in zip(locs, encs):
            dists = face_recognition.face_distance(known_faces, enc)
            if dists.size == 0:
                continue
            idx = int(np.argmin(dists))
            if dists[idx] <= constants.CONF_THRESHOLD_FACE:
                name = known_names[idx]
                FLAGS[f"{constants.FLAG_FACE_FOUND}_{meta['node_id']}"] = True
                output_q.put((meta, frame, name))
                return
