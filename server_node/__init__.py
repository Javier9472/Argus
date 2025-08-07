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
    sys.modules.setdefault(_name, importlib.import_module(full))

del importlib, sys, _name, full, _pkg, _subpackages
