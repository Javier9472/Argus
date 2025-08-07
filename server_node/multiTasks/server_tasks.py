import signal
from multiprocessing import Process, Manager

from modules.queue_manager import make_queue
from utils.logger import get_logger
from utils.flags import init_camera_flags
from config import settings

from socket_server.socket_server import launch_socket_listeners, raw_batch_q
from video_decompressor.video_decompressor import run_decompressor
from streamer.stream_manager import run_stream_manager
from streamer.http_streamer import start_http_stream    
from detectors.yolo_person import run_person_detector
from sender.socket_client import run_sender

log = get_logger("ServerTasks")

def _install_signal_handlers(children: list[Process]) -> None:
    def _graceful(_sig, _frm):
        log.warning("⛔ Señal recibida → cerrando …")
        for p in children:
            if p.is_alive():
                p.terminate()
        for p in children:
            p.join()
        log.info("✅ Todos los procesos detenidos.")
        raise SystemExit

    signal.signal(signal.SIGINT, _graceful)
    signal.signal(signal.SIGTERM, _graceful)

def launch_all_tasks() -> None:
    log.info("🚀 Inicializando SERVER_NODE…")

    init_camera_flags(["raspberry1", "raspberry2"])

    frame_q = make_queue(settings.MAX_QUEUE_FRAMES * 2)
    infer_q = make_queue(settings.MAX_QUEUE_FRAMES)
    send_q  = make_queue(settings.MAX_QUEUE_FRAMES)

    manager = Manager()
    display_dict = manager.dict()      


    listener_procs = launch_socket_listeners()

    core_procs = [
        Process(name="Decompressor",
                target=run_decompressor,
                args=(raw_batch_q, frame_q)),
        Process(name="StreamManager",
                target=run_stream_manager,
                args=(frame_q, infer_q, display_dict)),
        Process(name="YOLODetector",
                target=run_person_detector,
                args=(infer_q, send_q)),
        Process(name="HTTPStreamer",
                target=start_http_stream,
                args=(display_dict,)),
        Process(name="SenderAI",
                target=run_sender,
                args=(send_q,))
    ]

    for p in listener_procs + core_procs:
        p.start()
        log.info(f"▶ {p.name} iniciado (PID {p.pid})")

    _install_signal_handlers(listener_procs + core_procs)

    for p in listener_procs + core_procs:
        p.join()


if __name__ == "__main__":
    launch_all_tasks()
