from pathlib import Path

BASE_DIR         = Path(__file__).resolve().parent.parent
DATA_DIR         = BASE_DIR / "data"
EMBEDDINGS_DIR   = DATA_DIR / "embeddings"
MODELS_DIR       = DATA_DIR / "models"
REPORTS_DIR      = DATA_DIR / "reports"
TMP_DIR          = DATA_DIR / "tmp"



for p in (EMBEDDINGS_DIR, MODELS_DIR, REPORTS_DIR, TMP_DIR):
    p.mkdir(parents=True, exist_ok=True)

AI_NODE_IP       = "0.0.0.0"
AI_NODE_PORT     = 6100

FRAME_BATCH_SIZE = 10
MAX_QUEUE_LOTS   = 25
SOCKET_TIMEOUT   = 10

