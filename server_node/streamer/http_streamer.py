from flask import Flask, Response
import cv2, time
import numpy as np
from utils.logger import get_logger
from config import settings

log = get_logger("HTTPStreamer")

def _gen_mjpeg(display_dict):
    """Generador MJPEG con mosaico de cámaras."""
    fps_interval = 1 / settings.FRAME_RATE
    while True:
        t0 = time.time()
        # recoger frames ordenados por key para mantener orden estable
        frames = [display_dict[k] for k in sorted(display_dict.keys()) if display_dict[k]]
        if frames:
            imgs = [cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR) for b in frames]
            # crear mosaico sencillo horizontal o vertical
            mosaic = cv2.hconcat(imgs) if len(imgs) > 1 else imgs[0]
            ok, enc = cv2.imencode(".jpg", mosaic, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if ok:
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" +
                       enc.tobytes() + b"\r\n")
        # mantener fps
        dt = time.time() - t0
        if dt < fps_interval:
            time.sleep(fps_interval - dt)


def start_http_stream(display_dict):
    """Proceso aparte: levanta Flask y sirve /video_feed"""
    app = Flask("ArgusStreamer")

    @app.route(settings.HTTP_ROUTE)
    def video_feed():
        return Response(_gen_mjpeg(display_dict),
                        mimetype="multipart/x-mixed-replace; boundary=frame")

    log.info(f"HTTP MJPEG en http://{settings.HTTP_HOST}:{settings.HTTP_PORT}{settings.HTTP_ROUTE}")
    app.run(host=settings.HTTP_HOST, port=settings.HTTP_PORT, threaded=True)
