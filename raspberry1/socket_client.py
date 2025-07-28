import socket
from config import settings
import logging

logging.basicConfig(filename='logs/raspberry.log', level=logging.INFO)

def send_data(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((settings.SERVER_IP, settings.SERVER_PORT))
            s.sendall(data)
            logging.info(f"Frame enviado al servidor {settings.SERVER_IP}:{settings.SERVER_PORT}")
    except Exception as e:
        logging.error(f"Error al enviar frame: {e}")
