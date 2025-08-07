import cv2, numpy as np
from queue import Empty
from utils.logger import get_logger

log = get_logger("Decompressor")

def run_decompressor(input_q, output_q):
    while True:
        try:
            meta, data = input_q.get(timeout=5)
        except Empty:
            continue
        frames = []
        for part in data.split(b"\xff\xd9")[:-1]:
            img = cv2.imdecode(np.frombuffer(part + b"\xff\xd9", np.uint8), cv2.IMREAD_COLOR)
            frames.append(img)
        output_q.put((meta, frames))
