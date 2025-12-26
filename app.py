from flask import Flask, render_template, request, send_file
from io import BytesIO
from datetime import datetime
import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

app = Flask(__name__)

# --- Turkish font support (DejaVu) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_REGULAR = os.path.join(BASE_DIR, "fonts", "DejaVuSans.ttf")
FONT_BOLD = os.path.join(BASE_DIR, "fonts", "DejaVuSans-Bold.ttf")

# Register fonts once at startup
pdfmetrics.registerFont(TTFont("DejaVuSans", FONT_REGULAR))
pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", FONT_BOLD))


def build_pdf(customer_name: str, order_no: str, product_type: str, dt_str: str) -> BytesIO:
    """
    Create a simple Loading Plan PDF.
    dt_str expected like '2025-12-26T16:30' (HTML datetime-local)
    """
    dt_display = dt_str.strip()
    try:
        dt_obj = datetime.fromisoformat(dt_str)
        dt_display = dt_obj.strftime("%d.%m.%Y %H:%M")
    except Exception:
        pass

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    c.setTitle("Yükleme Planı")

    # Header
    c.setFont("DejaVuSans-Bold", 18)
    c.drawString(25 * mm, h - 25 * mm, "YÜKLEME PLANI")

    c.setFont("DejaVuSans", 10)
    c.setFillColor(colors.grey)
    c.drawString(25 * mm, h - 32 * mm, f"Oluşturulma: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    c.setFillColor(colors.black)

    # Box
    left = 25 * mm
    top = h - 45 * mm
    box_w = w - 50 * mm
    box_h = 65 * mm
    c.setLineWidth(1)
    c.roundRect(left, top - box_h, box_w, box_h, 8, stroke=1, fill=0)

    rows = [
        ("MÜŞTERİ ADI", customer_name),
        ("SIRA NO", order_no),
        ("ÜRÜN TİPİ", product_type),
        ("SAAT VE TARİH", dt_display),
    ]

    c.setFont("DejaVuSans-Bold", 11)
    y = top - 15 * mm
    label_w = 38 * mm
    for label, val in rows:
        c.drawString(left + 10 * mm, y, f"{label}:")
        c.setFont("DejaVuSans", 11)
        c.drawString(left + 10 * mm + label_w, y, (val or "").strip())
        c.setFont("DejaVuSans-Bold", 11)
        y -= 13 * mm

    # Footer note
    c.setFont("DejaVuSans", 9)
    c.setFillColor(colors.grey)
    c.drawString(25 * mm, 18 * mm, "Not: Bu belge otomatik oluşturulmuştur.")
    c.setFillColor(colors.black)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


@app.get("/")
def index():
    return render_template("form.html")


@app.post("/generate")
def generate():
    customer_name = request.form.get("customer_name", "").strip()
    order_no = request.form.get("order_no", "").strip()
    product_type = request.form.get("product_type", "").strip()
    dt_str = request.form.get("datetime", "").strip()

    pdf_io = build_pdf(customer_name, order_no, product_type, dt_str)

    safe_customer = "".join(ch for ch in customer_name if ch.isalnum() or ch in (" ", "_", "-")).strip().replace(" ", "_")
    fname = f"Yukleme_Plani_{safe_customer or 'Musteri'}_{order_no or 'SiraNo'}.pdf"

    return send_file(
        pdf_io,
        as_attachment=True,
        download_name=fname,
        mimetype="application/pdf",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
