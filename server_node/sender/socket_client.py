import socket, json, time
from pathlib import Path
from datetime import datetime, timezone
from queue import Empty
from config import settings
from utils.logger import get_logger

log = get_logger("SenderAI")

class AISocketClient:
    def __init__(self):
        self.sock = None
        self._connect()

    def _connect(self):
        retry = settings.RETRY_DELAY
        while True:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(settings.SOCKET_TIMEOUT)
                self.sock.connect((settings.AI_NODE_IP, settings.AI_NODE_PORT))
                log.info(f"Conectado a ai_node {settings.AI_NODE_IP}:{settings.AI_NODE_PORT}")
                break
            except Exception as e:
                log.error(f"Conexión ai_node falló: {e}. Reintento en {retry}s")
                time.sleep(retry)
                retry = min(retry * 2, settings.MAX_DELAY)

    def send_batch(self, meta: dict, batch: list[bytes]):
        if not self.sock:
            self._connect()

        meta = {**meta, "person_detected": True}
        header = json.dumps(meta).encode()
        header_size = len(header).to_bytes(4, "big")
        body = b"".join(batch)

        try:
            self.sock.sendall(header_size + header + body)
        except Exception as e:
            log.error(f"Error enviando a ai_node: {e}")
            self._connect()

def _save_batch(meta, batch):
    node = meta["node_id"]
    ts = datetime.fromtimestamp(meta["timestamp"], tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_dir = Path(settings.VIDEO_DIR) / node
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{ts}.mjpg"
    with open(path, "wb") as f:
        for b in batch:
            f.write(b)
    log.info(f"Lote guardado en {path}")

def run_sender(send_q):
    client = AISocketClient()
    while True:
        try:
            meta, batch = send_q.get(timeout=5)
        except Empty:
            continue
        _save_batch(meta, batch)
        client.send_batch(meta, batch)
