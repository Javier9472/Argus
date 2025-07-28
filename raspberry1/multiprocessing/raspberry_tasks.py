from multiprocessing import Queue
from camera_stream import get_camera
from video_compressor import compress_frame
from socket_client import send_data
from config import settings
import time
import logging

logging.basicConfig(filename='logs/raspberry.log', level=logging.INFO)

def capture_process(queue: Queue):
    cam = get_camera()
    while True:
        ret, frame = cam.read()
        if ret:
            queue.put(frame)
            logging.debug("Frame capturado y colocado en cola")
        time.sleep(settings.SEND_INTERVAL)

def compress_process(input_q: Queue, output_q: Queue):
    while True:
        if not input_q.empty():
            frame = input_q.get()
            compressed = compress_frame(frame)
            if compressed:
                output_q.put(compressed)
                logging.debug("Frame comprimido y colocado en cola")

def send_process(output_q: Queue):
    while True:
        if not output_q.empty():
            data = output_q.get()
            send_data(data)
