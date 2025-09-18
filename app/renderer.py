from __future__ import annotations

import os
from typing import Dict, List, Tuple, Any, Optional

from PIL import Image, ImageDraw, ImageFont

# ========= Helpers =========
def _hex_to_rgb(hx: str) -> Tuple[int, int, int]:
    try:
        hx = (hx or "#000000").strip()
        if hx.startswith("#"):
            hx = hx[1:]
        if len(hx) == 3:  # e.g. #abc
            hx = "".join(ch * 2 for ch in hx)
        r = int(hx[0:2], 16)
        g = int(hx[2:4], 16)
        b = int(hx[4:6], 16)
        return r, g, b
    except Exception:
        return (0, 0, 0)

def _load_font(path: Optional[str], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    # Prioritas: font_path valid → DejaVuSans (bundled Pillow) → default
    if path and os.path.isfile(path):
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            pass
    try:
        # DejaVuSans hampir selalu tersedia bersama Pillow
        from PIL import ImageFont
        return ImageFont.truetype("DejaVuSans.ttf", size=size)
    except Exception:
        return ImageFont.load_default()

def _text_size(font: ImageFont.FreeTypeFont, text: str) -> Tuple[int, int]:
    # gunakan getbbox agar akurat
    if not text:
        return (0, font.size)
    try:
        bbox = font.getbbox(text)
        w = max(0, bbox[2] - bbox[0])
        h = max(0, bbox[3] - bbox[1])
        return (w, h)
    except Exception:
        # fallback
        return font.getsize(text)

def _place_x(x: float, w_box: int, w_text: int, align: str) -> float:
    a = (align or "left").strip().lower()
    if w_box and w_box > 0:
        if a == "center":
            return x + (w_box - w_text) / 2.0
        if a == "right":
            return x + (w_box - w_text)
        # left
        return x
    # tanpa box width (tight): treat as left
    return x

# ========= Public API =========
def render_to_image(
    template_path: str,
    fields: List[Dict[str, Any]],
    row: Dict[str, str],
) -> Image.Image:
    """
    Menghasilkan PIL.Image dari template + field + satu baris data.
    - template_path: path gambar (PNG/JPG/WEBP)
    - fields: list dict {name,x,y,size,color,align,font_path,box_width}
    - row: mapping {field_name: value}
    """
    base = Image.open(template_path).convert("RGBA")
    canvas = base.copy()
    draw = ImageDraw.Draw(canvas)

    for f in fields:
        name = f.get("name", "")
        text = str(row.get(name, "") or "")
        if not text:
            continue

        x = float(f.get("x", 0))
        y = float(f.get("y", 0))
        size = int(f.get("size", 32) or 32)
        color = _hex_to_rgb(str(f.get("color", "#000000") or "#000000"))
        align = str(f.get("align", "left") or "left")
        font_path = f.get("font_path") or ""
        box_width = int(f.get("box_width", 0) or 0)

        font = _load_font(font_path, size)
        tw, th = _text_size(font, text)
        tx = _place_x(x, box_width, tw, align)
        ty = y  # pos dihitung sebagai top-left (sesuai kanvas)

        # Gambar teks (Pillow text() default anchor = top-left)
        draw.text((tx, ty), text, font=font, fill=color)

    # pastikan kembali ke RGB (tanpa alpha) untuk kompatibilitas luas
    return canvas.convert("RGB")


def draw_certificate(
    template_path: str,
    fields: List[Dict[str, Any]],
    row: Dict[str, str],
    out_path: str,
    fmt: str = "png",
):
    """
    Render dan simpan ke file.
    - fmt: 'png' atau 'pdf'
    """
    fmt = (fmt or "png").lower().strip()
    if fmt == "pdf":
        _save_as_pdf(template_path, fields, row, out_path)
    else:
        img = render_to_image(template_path, fields, row)
        # pastikan ekstensi
        if not out_path.lower().endswith(".png"):
            out_path = os.path.splitext(out_path)[0] + ".png"
        img.save(out_path, "PNG")


# ========= PDF (ReportLab) =========
def _save_as_pdf(
    template_path: str,
    fields: List[Dict[str, Any]],
    row: Dict[str, str],
    out_path: str,
):
    from reportlab.pdfgen import canvas as pdfcanvas
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # Muat template untuk tahu ukuran
    base = Image.open(template_path).convert("RGB")
    w_px, h_px = base.size

    # Buat canvas ukuran pixel-1:1 (ReportLab pakai point; asumsikan 72dpi ~ pixel)
    c = pdfcanvas.Canvas(out_path, pagesize=(w_px, h_px))

    # Lukis background
    c.drawImage(ImageReader(base), 0, 0, width=w_px, height=h_px, preserveAspectRatio=False, mask='auto')

    # cache font terdaftar agar tidak double-register
    registered = set(pdfmetrics.getRegisteredFontNames())

    for f in fields:
        name = f.get("name", "")
        text = str(row.get(name, "") or "")
        if not text:
            continue

        x = float(f.get("x", 0))
        y = float(f.get("y", 0))
        size = int(f.get("size", 32) or 32)
        color = _hex_to_rgb(str(f.get("color", "#000000") or "#000000"))
        align = str(f.get("align", "left") or "left")
        font_path = f.get("font_path") or ""
        box_width = int(f.get("box_width", 0) or 0)

        # Pilih font
        face = "Helvetica"
        if font_path and os.path.isfile(font_path):
            try:
                font_key = os.path.basename(font_path)
                name_no_ext = os.path.splitext(font_key)[0]
                if name_no_ext not in registered:
                    pdfmetrics.registerFont(TTFont(name_no_ext, font_path))
                    registered.add(name_no_ext)
                face = name_no_ext
            except Exception:
                face = "Helvetica"

        c.setFont(face, size)
        c.setFillColorRGB(color[0]/255.0, color[1]/255.0, color[2]/255.0)

        # Ukuran teks
        tw = pdfmetrics.stringWidth(text, face, size)
        if box_width and box_width > 0:
            if align.lower() == "center":
                tx = x + (box_width - tw) / 2.0
            elif align.lower() == "right":
                tx = x + (box_width - tw)
            else:
                tx = x
        else:
            tx = x

        # ReportLab drawString menempatkan baseline di y → agar mirip top-left,
        # geser turun sedikit: kira-kira ukuran font * 0.8 untuk memposisikan top.
        # Namun tampilan top-left vs baseline beda antar font. Compromise:
        ty = h_px - (y + size * 0.8)  # koordinat PDF (0,0) di kiri-bawah

        c.drawString(tx, ty, text)

    c.showPage()
    c.save()

