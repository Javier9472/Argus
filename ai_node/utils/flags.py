from multiprocessing import Manager
from config.constants import FLAG_FACE_FOUND, FLAG_CLOTHES_FOUND

_mgr = Manager()
FLAGS = _mgr.dict()

def init_flags(node_ids):
    for nid in node_ids:
        FLAGS[f"{FLAG_FACE_FOUND}_{nid}"]   = False
        FLAGS[f"{FLAG_CLOTHES_FOUND}_{nid}"] = False
