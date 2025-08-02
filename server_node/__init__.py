"""
Paquete raíz del SERVER_NODE (Jetson Orin Nano).

• Re-exporta sub-paquetes como alias de nivel superior para mantener
  la misma convención de imports usada en raspberry y ai_node.
  Ej.:  from config import settings     →  funciona
        from socket_server.socket_server import launch_socket_listeners
• Añade atributo __version__ opcional.
"""

import importlib
import sys

__version__ = "0.1.0"
_subpackages = (
    "config", "utils", "modules",
    "socket_server", "streamer",
    "video_decompressor", "detectors",
    "sender", "multiTasks",
)

_pkg = __name__   # "server_node"

for _name in _subpackages:
    full = f"{_pkg}.{_name}"
    # Importa el sub-paquete y lo expone como alias de primer nivel
    sys.modules.setdefault(_name, importlib.import_module(full))

del importlib, sys, _name, full, _pkg, _subpackages
