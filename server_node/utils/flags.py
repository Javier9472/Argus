from multiprocessing import Manager
from config.constants import FLAG_PERSON_DETECTED

_manager = Manager()
FLAGS = _manager.dict() 

def init_camera_flags(node_ids: list[str]) -> None:

    for nid in node_ids:
        FLAGS[f"{FLAG_PERSON_DETECTED}_{nid}"] = False
