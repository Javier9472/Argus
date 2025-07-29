import time
import argparse
import multiprocessing as mp
import time
import sys
import json 
import psutil

from datetime import datetime, timezone
from config import constants, settings
from modules.camera_stream import get_camera, check_camera_stream
from modules.socket_client import SocketClient
from multiTasks import raspberry_tasks as rt
from utils.logger_config import get_logger

logger = get_logger("Main")

def test_camera():
    logger.info("[TEST] Iniciando prueba de cámara...")
    cap = get_camera()
    if cap and check_camera_stream(cap):
        logger.info("[TEST] Cámara funciona correctamente.")
    else:
        logger.error("[TEST] Fallo en prueba de cámara.")
    if cap:
        cap.release()

def test_socket():
    logger.info("[TEST] Enviando mensaje de prueba al servidor...")
    try:
        client = SocketClient()
        test_msg = b'TEST_CONNECTION'
        metadata = {
            'node_id': constants.NODE_NAME,
            'timestamp': time.time(),
            'test': True,
            'length': len(test_msg)
        }
        header = json.dumps(metadata).encode('utf-8')
        header_size = len(header).to_bytes(4, 'big')
        client.socket.sendall(header_size + header + test_msg)
        logger.info("[TEST] Mensaje de prueba enviado correctamente.")
        client.close()
    except Exception as e:
        logger.error(f"[TEST] Error enviando mensaje de prueba: {e}")

def parse_args():
    parser = argparse.ArgumentParser(description="Nodo Raspberry Argus")
    parser.add_argument("--debug", action="store_true", help="Activar nivel de log DEBUG")
    parser.add_argument("--test-camera", action="store_true", help="Solo probar la cámara")
    parser.add_argument("--test-socket", action="store_true", help="Enviar mensaje de prueba al servidor")
    parser.add_argument("--single-thread", action="store_true", help="Ejecutar sin multiprocessing")
    return parser.parse_args()

def main():
    args = parse_args()

    if args.debug:
        logger.setLevel("DEBUG")

    if args.test_camera:
        test_camera()
        sys.exit(0)

    if args.test_socket:
        test_socket()
        sys.exit(0)

    if args.single_thread:
        logger.info("[MAIN] Ejecutando en modo single-thread (sin multiprocessing)")
        rt.run_raspberry_node()
        return

    logger.info("[MAIN] Iniciando procesos en paralelo usando multiprocessing")
    ctx = mp.get_context("spawn")

    queues = {
        "capture_to_compress": ctx.Queue(maxsize=constants.FRAME_BATCH_SIZE * 2),
        "compress_to_send": ctx.Queue(maxsize=constants.FRAME_BATCH_SIZE * 2)
    }

    processes = [
        ctx.Process(target=rt.capture_frames, args=(queues["capture_to_compress"],)),
        ctx.Process(target=rt.compress_frames, args=(queues["capture_to_compress"], queues["compress_to_send"])),
        ctx.Process(target=rt.send_batches, args=(queues["compress_to_send"],)),
    ]

    for p in processes:
        p.start()

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        logger.warning("[MAIN] Interrupción manual detectada. Cerrando procesos...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()
        logger.info("[MAIN] Procesos finalizados.")

def verify_system_clock(logger):
    now = datetime.now(timezone.utc)
    logger.info(f"[RELOJ] Hora UTC actual: {now.isoformat()}")


if __name__ == "__main__":
    logger.info(f"[{constants.NODE_NAME}] Iniciando sistema en {constants.NODE_NAME}...")
    verify_system_clock(logger)
    main()
