from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parent.parent
DATA_DIR   = BASE_DIR / "data"
LOG_DIR    = DATA_DIR / "log"
TMP_DIR    = DATA_DIR / "tmp"
VIDEO_DIR  = DATA_DIR / "videos"

for _p in (DATA_DIR, LOG_DIR, TMP_DIR, VIDEO_DIR):
    _p.mkdir(parents=True, exist_ok=True)

PORTS_IN        = [5001, 5002]          
SERVER_IP_IN    = '0.0.0.0'

AI_NODE_IP      = "192.168.1.200"       # <— cámbialo
AI_NODE_PORT    = 6100

HTTP_HOST       = "0.0.0.0"
HTTP_PORT       = 8080
HTTP_ROUTE      = "/video_feed"

FRAME_RATE          = 15
MJPEG_QUALITY       = 85
MAX_QUEUE_FRAMES    = 250         
MAX_BATCH_MB        = 50          

YOLO_ENGINE        = "/opt/argus/models/yolov8_person.engine"
NUM_GPU_WORKERS    = 2
NUM_CPU_WORKERS    = 3

SOCKET_TIMEOUT  = 10
RETRY_DELAY     = 3
MAX_DELAY       = 30

LOG_LEVEL       = "INFO"
