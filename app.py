from flask import Flask, render_template, request, send_file, abort
from io import BytesIO
from datetime import datetime
import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader

app = Flask(__name__)

# --- Font (Turkish chars supported, safe for names) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_REGULAR = os.path.join(BASE_DIR, "fonts", "DejaVuSans.ttf")
FONT_BOLD = os.path.join(BASE_DIR, "fonts", "DejaVuSans-Bold.ttf")
pdfmetrics.registerFont(TTFont("DejaVuSans", FONT_REGULAR))
pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", FONT_BOLD))

# --- Simple access control ---
# Set on Render as env var if you want: PDF_PASSWORD=akansu
PDF_PASSWORD = os.getenv("PDF_PASSWORD", "akansu").strip()

LOGO_PATH = os.path.join(BASE_DIR, "static", "logo.png")


def _wrap_lines(text: str, font_name: str, font_size: int, max_width: float):
    """Wrap a single paragraph to a list of lines based on string width."""
    words = (text or "").split()
    lines = []
    cur = []
    for w in words:
        test = (" ".join(cur + [w])).strip()
        if stringWidth(test, font_name, font_size) <= max_width or not cur:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def _draw_bullets(c: canvas.Canvas, x: float, y: float, width: float, bullets: list[str],
                  font_name="DejaVuSans", font_size=9, leading=12):
    """Draw bullet list, returns final y."""
    bullet_indent = 4 * mm
    text_indent = 7 * mm
    for b in bullets:
        lines = _wrap_lines(b, font_name, font_size, width - text_indent)
        # first line with bullet
        c.setFont(font_name, font_size)
        c.drawString(x + bullet_indent, y, u"\u2022")
        c.drawString(x + text_indent, y, lines[0] if lines else "")
        y -= leading
        # remaining wrapped lines
        for ln in lines[1:]:
            c.drawString(x + text_indent, y, ln)
            y -= leading
        y -= 2  # small gap between bullets
    return y


def build_pdf(customer_name: str, queue_no: str, product_type: str, load_date: str, time_slot: str) -> BytesIO:
    """
    load_date expected: YYYY-MM-DD (HTML date)
    time_slot expected: '08:00-12:00' or '13:00-16:00'
    """
    date_display = (load_date or "").strip()
    try:
        d = datetime.fromisoformat(load_date)
        date_display = d.strftime("%d.%m.%Y")
    except Exception:
        pass

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    c.setTitle("Loading Plan")

    # Header title (left)
    title_x = 25 * mm
    title_y = h - 25 * mm
    c.setFont("DejaVuSans-Bold", 18)
    c.drawString(title_x, title_y, "LOADING PLAN")

    # Logo (right, aligned with title)
    try:
        logo = ImageReader(LOGO_PATH)
        logo_w = 32 * mm
        logo_h = 12 * mm
        c.drawImage(logo, w - 25 * mm - logo_w, title_y - logo_h + 4, width=logo_w, height=logo_h, mask='auto')
    except Exception:
        pass

    # Created at
    c.setFont("DejaVuSans", 10)
    c.setFillColor(colors.grey)
    c.drawString(25 * mm, h - 32 * mm, f"Created: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    c.setFillColor(colors.black)

    # Info box
    left = 25 * mm
    top = h - 45 * mm
    box_w = w - 50 * mm
    box_h = 60 * mm
    c.setLineWidth(1)
    c.roundRect(left, top - box_h, box_w, box_h, 8, stroke=1, fill=0)

    rows = [
        ("CUSTOMER NAME", customer_name),
        ("QUEUE NO", queue_no),
        ("PRODUCT TYPE", product_type),
        ("LOADING DATE", date_display),
        ("LOADING TIME", time_slot),
    ]

    c.setFont("DejaVuSans-Bold", 11)
    y = top - 12 * mm
    label_w = 40 * mm
    for label, val in rows:
        c.drawString(left + 10 * mm, y, f"{label}:")
        c.setFont("DejaVuSans", 11)
        c.drawString(left + 10 * mm + label_w, y, (val or "").strip())
        c.setFont("DejaVuSans-Bold", 11)
        y -= 11 * mm

    # Notes / Process Information
    section_top = top - box_h - 10 * mm
    c.setFont("DejaVuSans-Bold", 11)
    c.drawString(25 * mm, section_top, "Loading Process Information")

    bullets = [
        "Loading operations will be carried out within the date and time period specified in this document.",
        "If a vehicle arrives outside the specified date and time range, a new queue number must be obtained.",
        "Upon arrival at the factory, it is mandatory to present this document at the reception desk. Access to the loading area will not be permitted without this document.",
        "Vehicles arriving outside the designated loading date and time will not be loaded under any circumstances.",
        "After the loading process is completed, export operation procedures take approximately 2–3 hours.",
        "Akansu reserves the right to make changes to the loading schedule. In such cases, Akansu shall not be held responsible for any financial or non-financial losses.",
        "Vehicles must complete a tare (empty) weighing before loading. After loading, a gross weight weighing must be completed, and the weighbridge ticket must be submitted to the shipping department.",
        "Weighbridge fees are the responsibility of the customer or the logistics company.",
        "Drivers arriving for loading are required to comply with Akansu’s visitor regulations and shipment and warehouse occupational health and safety rules. These instructions are available at the reception desk at the factory entrance, and further information can be obtained from the reception.",
    ]

    _draw_bullets(
        c,
        x=25 * mm,
        y=section_top - 8 * mm,
        width=w - 50 * mm,
        bullets=bullets,
        font_name="DejaVuSans",
        font_size=9,
        leading=12,
    )

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


@app.get("/")
def index():
    return render_template("form.html")


@app.post("/generate")
def generate():
    # server-side password check (prevents bypassing UI)
    password = (request.form.get("password") or "").strip()
    if password != PDF_PASSWORD:
        abort(403)

    customer_name = (request.form.get("customer_name") or "").strip()
    queue_no = (request.form.get("queue_no") or "").strip()
    product_type = (request.form.get("product_type") or "").strip()
    load_date = (request.form.get("load_date") or "").strip()
    time_slot = (request.form.get("time_slot") or "").strip()

    # Basic validation
    if not all([customer_name, queue_no, product_type, load_date, time_slot]):
        abort(400)

    pdf_io = build_pdf(customer_name, queue_no, product_type, load_date, time_slot)

    safe_customer = "".join(ch for ch in customer_name if ch.isalnum() or ch in (" ", "_", "-")).strip().replace(" ", "_")
    fname = f"Loading_Plan_{safe_customer or 'Customer'}_{queue_no or 'QueueNo'}.pdf"

    return send_file(pdf_io, as_attachment=True, download_name=fname, mimetype="application/pdf")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
