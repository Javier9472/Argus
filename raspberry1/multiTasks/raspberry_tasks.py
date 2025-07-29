import time
from multiprocessing import Process, Queue
from config import constants
from config import settings
from modules.camera_stream import get_camera, check_camera_stream
from modules.video_compressor import compress_frame_batch
from modules.socket_client import SocketClient
from utils.logger_config import get_logger

logger = get_logger("RaspberryTasks")

def capture_frames(queue: Queue):
    cap = get_camera()
    if cap is None:
        logger.error("[CAPTURE] Cámara no disponible. Finalizando proceso.")
        return

    if not check_camera_stream(cap):
        logger.error("[CAPTURE] Verificación de stream fallida. Finalizando proceso.")
        return

    logger.info("[CAPTURE] Proceso de captura iniciado.")
    try:
        while True:
            batch = []
            for _ in range(constants.FRAME_BATCH_SIZE):
                ret, frame = cap.read()
                if not ret or frame is None:
                    logger.warning("[CAPTURE] Frame inválido. Saltando.")
                    continue
                batch.append(frame)
            queue.put(batch)
    except Exception as e:
        logger.exception(f"[CAPTURE] Error: {e}")
    finally:
        cap.release()
        logger.info("[CAPTURE] Cámara liberada.")

def compress_frames(input_q: Queue, output_q: Queue):
    logger.info("[COMPRESSOR] Proceso de compresión iniciado.")
    while True:
        batch = input_q.get()
        compressed = compress_frame_batch(batch, quality=constants.MJPEG_QUALITY)
        if compressed:
            output_q.put(compressed)
        else:
            logger.warning("[COMPRESSOR] Lote vacío o fallido. Ignorando.")

def send_batches(output_q: Queue):
    client = SocketClient()
    logger.info("[SENDER] Proceso de envío iniciado.")
    while True:
        batch = output_q.get()
        if batch:
            client.send_batch(batch)
        time.sleep(settings.SEND_INTERVAL)

def run_raspberry_node():
    logger.info(f"[{constants.NODE_NAME}] Nodo iniciado con multiprocesamiento.")

    capture_q = Queue(maxsize=5)
    compress_q = Queue(maxsize=5)

    p1 = Process(target=capture_frames, args=(capture_q,), name="CaptureProcess")
    p2 = Process(target=compress_frames, args=(capture_q, compress_q), name="CompressorProcess")
    p3 = Process(target=send_batches, args=(compress_q,), name="SenderProcess")

    p1.start()
    p2.start()
    p3.start()

    logger.info(f"[{constants.NODE_NAME}] Todos los procesos iniciados correctamente.")

    try:
        p1.join()
        p2.join()
        p3.join()
    except KeyboardInterrupt:
        logger.info(f"[{constants.NODE_NAME}] Finalización manual detectada.")
        for p in [p1, p2, p3]:
            p.terminate()
            p.join()
        logger.info(f"[{constants.NODE_NAME}] Procesos finalizados.")
