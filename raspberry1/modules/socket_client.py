import socket
import json
import time
from config import settings 
from config import constants
from utils.logger_config import get_logger

logger = get_logger ("SocketClient")

class SocketClient:
    def __init__(self):
        self.server_ip = settings.SERVER_IP
        self.server_port = settings.SERVER_PORT
        self.node_id = constants.NODE_NAME
        self.socket = None
        self.connect()

    def connect(self):
        retry_delay = settings.RETRY_DELAY
        max_delay = settings.MAX_DELAY
        
        while True:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout (settings.SOCKET_TIMEOUT)
                self.socket.connect((self.server_ip, self.server_port))
                logger.info(f"[{self.node_id}] Conectado al servidor {self.server_ip}:{self.server_port}")
                break
            except Exception as e:
                logger.error(f"[{self.node_id}] Error al conectar: {e}. Reintentando en 3s...")
                time.sleep(retry_delay)
                retry_delay = min (retry_delay*2, max_delay)

    def send_batch(self, batch_frames: list[bytes]):
        if not self.socket: 
            logger.warning(f"[{self.node_id}] Socket no disponible. Reconectando...")
            self.connect()
            
        oversized = [i for i, f in enumerate(batch_frames) if len(f) > settings.BUFFER_SIZE]
        if oversized:
            logger.warning(f"[{self.node_id}] {len(oversized)} frames exceden BUFFER_SIZE ({settings.BUFFER_SIZE} bytes). Índices: {oversized}")
            
        try:
            self._send_metadata_and_data(batch_frames)
            logger.info(f"[{self.node_id}] Lote de {len(batch_frames)} frames enviado correctamente.")
        except (BrokenPipeError, ConnectionResetError, socket.timeout):
            logger.warning(f"[{self.node_id}] Conexión perdida. Reintentando...")
            self.connect()
        except Exception as e:
            logger.error(f"[{self.node_id}] Error inesperado al enviar lote: {e}")
            
    def _send_metadata_and_data(self, batch_frames: list[bytes]):
        metadata = {
            'node_id': self.node_id,
            'timestamp': time.time(),
            'batch_size': len(batch_frames)
        }
        header = json.dumps(metadata).encode('utf-8')
        header_size = len(header).to_bytes(4, 'big')
        batch_data = b''.join(batch_frames)
        self.socket.sendall(header_size + header + batch_data)

    def close(self):
        if self.socket:
            try:
                self.socket.close()
                logger.info(f"[{self.node_id}] Socket cerrado.")
            except Exception as e:
                logger.error(f"[{self.node_id}] Error al cerrar socket: {e}")