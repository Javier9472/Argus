# server_node/utils/flags.py
from multiprocessing import Manager
from config.constants import FLAG_PERSON_DETECTED

_manager = Manager()
FLAGS = _manager.dict()   # acceso concurrente entre procesos


def init_camera_flags(node_ids: list[str]) -> None:
    """
    Crea FLAGS[PERSON_DETECTED_<node>] = False por cada Raspberry.
    Se llama una sola vez al arrancar server_node.
    """
    for nid in node_ids:
        FLAGS[f"{FLAG_PERSON_DETECTED}_{nid}"] = False
