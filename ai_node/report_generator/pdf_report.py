from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from config.settings import REPORTS_DIR
from utils.logger import get_logger

log = get_logger("PDFReport")

def save_report(meta, frame, faces, clothes):
    ts = datetime.utcfromtimestamp(meta["timestamp"]).strftime("%Y%m%d_%H%M%S")
    path = REPORTS_DIR / f"report_{ts}.pdf"
    doc = SimpleDocTemplate(str(path))
    styles = getSampleStyleSheet()
    elems = [Paragraph(f"Reporte {ts}", styles["Title"])]
    if faces:
        elems.append(Paragraph("Rostro reconocido:", styles["Heading2"]))
        for loc, name in faces:
            elems.append(Paragraph(name, styles["Normal"]))
    if clothes:
        elems.append(Paragraph("Ropa detectada:", styles["Heading2"]))
    elems.append(Spacer(1, 12))
    doc.build(elems)
    log.info(f"PDF guardado en {path}")
