import socket, struct, json
from multiprocessing import Process
from typing import Tuple, List
from modules.queue_manager import make_queue
from utils.logger import get_logger
from config import settings, constants

log = get_logger("SocketServer")

raw_batch_q = make_queue()

def _client_worker(conn: socket.socket, addr: Tuple[str,int]):
    log.info(f"[{addr}] Conectado")
    conn.settimeout(settings.SOCKET_TIMEOUT)

    try:
        while True:
            size_bytes = _recv_exact(conn, constants.HEADER_SIZE_BYTES)
            if not size_bytes: break
            header_len = struct.unpack(">I", size_bytes)[0]

            header_raw = _recv_exact(conn, header_len)
            if not header_raw: break
            meta = json.loads(header_raw.decode())

            frames = _recv_mjpeg_batch(conn, meta["batch_size"])
            if frames is None:
                log.warning(f"[{addr}] Desconexión inesperada")
                break

            raw_batch_q.put((meta, frames))
    except socket.timeout:
        log.warning(f"[{addr}] Timeout")
    except Exception as e:
        log.exception(f"[{addr}] Error: {e}")
    finally:
        conn.close()
        log.info(f"[{addr}] Desconectado")

def _recv_exact(sock: socket.socket, n: int) -> bytes | None:
    data = b""
    while len(data) < n:
        part = sock.recv(n - len(data))
        if not part:
            return None
        data += part
    return data

def _recv_mjpeg_batch(sock: socket.socket, frames_expected: int) -> List[bytes] | None:
    buffer = bytearray()
    frames: List[bytes] = []
    while len(frames) < frames_expected:
        chunk = sock.recv(4096)
        if not chunk:
            return None
        buffer.extend(chunk)

        while True:
            soi = buffer.find(b"\xff\xd8")
            if soi == -1: break
            eoi = buffer.find(b"\xff\xd9", soi+2)
            if eoi == -1: break
            frame = buffer[soi:eoi+2]
            frames.append(bytes(frame))
            del buffer[:eoi+2]
            if len(frames) == frames_expected:
                break
    return frames

def _listen_on_port(port: int):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((settings.SERVER_IP_IN, port))
    srv.listen()
    log.info(f"Escuchando Raspberrys en :{port}")

    try:
        while True:
            conn, addr = srv.accept()
            proc = Process(target=_client_worker, args=(conn, addr), daemon=True)
            proc.start()
    except KeyboardInterrupt:
        log.warning(f"Listener {port} detenido por Ctrl+C")
    finally:
        srv.close()

def launch_socket_listeners():
    listeners = []
    for p in settings.PORTS_IN:
        pr = Process(target=_listen_on_port, args=(p,), name=f"SocketPort{p}")
        pr.start()
        listeners.append(pr)
    return listeners

