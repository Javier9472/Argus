import socket, struct, json
from multiprocessing import Process
from queue import Empty
from utils.logger import get_logger
from config.settings import AI_NODE_IP, AI_NODE_PORT, SOCKET_TIMEOUT
from config.constants import HEADER_SIZE_BYTES

log = get_logger("SocketServer")

raw_batch_q = __import__("queue").Queue()

def _recv_exact(sock, n):
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk: return None
        buf += chunk
    return buf

def _client_worker(conn, addr):
    conn.settimeout(SOCKET_TIMEOUT)
    while True:
        hdr = _recv_exact(conn, HEADER_SIZE_BYTES)
        if not hdr: break
        size = struct.unpack(">I", hdr)[0]
        meta_raw = _recv_exact(conn, size)
        meta = json.loads(meta_raw.decode())
        data = _recv_exact(conn, meta["batch_size"]) 
        raw_batch_q.put((meta, data))
    conn.close()

def launch_socket_server():
    srv = socket.socket()
    srv.bind((AI_NODE_IP, AI_NODE_PORT))
    srv.listen()
    log.info(f"Escuchando en {AI_NODE_IP}:{AI_NODE_PORT}")
    while True:
        conn, addr = srv.accept()
        p = Process(target=_client_worker, args=(conn, addr), daemon=True)
        p.start()
