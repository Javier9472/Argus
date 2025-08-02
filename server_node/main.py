# server_node/main.py
from multiTasks.server_tasks import launch_all_tasks
from utils.logger import get_logger

log = get_logger("Main")

if __name__ == "__main__":
    log.info("🟢 Arrancando Argus SERVER_NODE …")
    launch_all_tasks()
