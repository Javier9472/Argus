from multiprocessing import Process, Queue, Manager
from socket_server.socket_server import launch_socket_server, raw_batch_q
from video_decompressor.video_decompressor import run_decompressor
from detectors.face_detector import detect_faces
from detectors.clothes_detector import detect_clothes
from report_generator.pdf_report import save_report
from utils.flags import init_flags
from config.settings import MAX_QUEUE_LOTS
from config.constants import FLAG_FACE_FOUND, FLAG_CLOTHES_FOUND
from utils.logger import get_logger
import signal

log = get_logger("AITasks")

def _install_signals(procs):
    def _exit(_s, _f):
        for p in procs:
            p.terminate()
        raise SystemExit
    signal.signal(signal.SIGINT, _exit)
    signal.signal(signal.SIGTERM, _exit)

def launch_ai():
    init_flags(["raspberry1", "raspberry2"])
    frame_q  = Queue(MAX_QUEUE_LOTS)
    detect_q = Queue(MAX_QUEUE_LOTS)
    manager  = Manager()
    
    p0 = Process(target=launch_socket_server, daemon=True)
    
    p1 = Process(target=run_decompressor, args=(raw_batch_q, frame_q))
    
    p2 = Process(target=lambda: detect_faces_loop(frame_q, detect_q))

    p3 = Process(target=lambda: detect_clothes_loop(frame_q, detect_q))

    p4 = Process(target=lambda: report_loop(detect_q))

    procs = [p0, p1, p2, p3, p4]
    for p in procs:
        p.start()
    _install_signals(procs)
    for p in procs:
        p.join()

def detect_faces_loop(input_q, output_q):
    while True:
        meta, frames = input_q.get()
        detect_faces(meta, frames, output_q)

def detect_clothes_loop(input_q, output_q):
    while True:
        meta, frames = input_q.get()
        detect_clothes(meta, frames, output_q)

def report_loop(q):
    while True:
        meta, frame = q.get()
        faces   = FLAGS[f"{FLAG_FACE_FOUND}_{meta['node_id']}"]
        clothes = FLAGS[f"{FLAG_CLOTHES_FOUND}_{meta['node_id']}"]
        save_report(meta, frame, faces, clothes)

if __name__ == "__main__":
    launch_ai()
