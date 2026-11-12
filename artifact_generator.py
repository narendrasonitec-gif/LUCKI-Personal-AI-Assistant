"""Lucki artifact generation helpers.

Outputs are written locally to the generated/ directory. Image output supports
HD/FHD/4K and common aspect ratios. PDF uses vector text and standard print
sizes; PPTX uses a 16:9 widescreen canvas for modern displays.
"""
from pathlib import Path
from datetime import datetime
import os
import sys
import textwrap
import re

if getattr(sys, "frozen", False):
    OUT = Path(os.getenv("USERPROFILE", str(Path.home()))) / "Documents" / "Lucki AI" / "generated"
else:
    OUT = Path(__file__).resolve().parent / "generated"
OUT.mkdir(parents=True, exist_ok=True)

IMAGE_SIZES = {
    "sd": (1280, 720),
    "hd": (1280, 720),
    "fhd": (1920, 1080),
    "full hd": (1920, 1080),
    "1080p": (1920, 1080),
    "2k": (2560, 1440),
    "4k": (3840, 2160),
    "uhd": (3840, 2160),
}


def _safe_name(text):
    value = "".join(c if c.isalnum() or c in "-_ " else "_" for c in text).strip()
    return (value[:60] or "lucki_output").replace(" ", "_")


def _requested_image_size(text):
    low = str(text or "").lower()
    for key, size in sorted(IMAGE_SIZES.items(), key=lambda x: -len(x[0])):
        if re.search(rf"\b{re.escape(key)}\b", low):
            return size
    return (1920, 1080)


def _requested_ratio(text):
    low = str(text or "").lower()
    if "9:16" in low or "portrait" in low or "vertical" in low:
        return "9:16"
    if "1:1" in low or "square" in low:
        return "1:1"
    return "16:9"


def generate_pdf(title, content, page_size="A4"):
    from reportlab.lib.pagesizes import A4, A3, LETTER, landscape
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    sizes = {"A4": A4, "A3": A3, "LETTER": LETTER}
    pagesize = sizes.get(str(page_size).upper(), A4)
    path = OUT / f"{_safe_name(title)}_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(path), pagesize=pagesize, title=str(title))
    story = [Paragraph(str(title), styles["Title"]), Spacer(1, 16)]
    for block in str(content).split("\n"):
        if block.strip():
            story.append(Paragraph(block.replace("&", "&amp;"), styles["BodyText"]))
            story.append(Spacer(1, 8))
    doc.build(story)
    return str(path)


def generate_ppt(title, content, aspect="16:9"):
    from pptx import Presentation
    from pptx.util import Inches, Pt

    prs = Presentation()
    if aspect == "4:3":
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(7.5)
    else:
        prs.slide_width = Inches(13.333333)
        prs.slide_height = Inches(7.5)

    slides = [x.strip() for x in str(content).split("\n\n") if x.strip()] or [str(content)]
    for index, block in enumerate(slides[:30]):
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = title if index == 0 else f"{title} — {index + 1}"
        body = slide.placeholders[1].text_frame
        body.clear()
        for line in block.splitlines():
            p = body.paragraphs[0] if not body.paragraphs[0].text else body.add_paragraph()
            p.text = line.lstrip("-• ")
            p.font.size = Pt(22)

    path = OUT / f"{_safe_name(title)}_{datetime.now():%Y%m%d_%H%M%S}.pptx"
    prs.save(path)
    return str(path)


def generate_image(title, prompt, size=None, ratio=None):
    """Create a local high-resolution poster layout. This is not generative image synthesis."""
    from PIL import Image, ImageDraw, ImageFont

    requested = size or _requested_image_size(prompt)
    if isinstance(requested, str):
        requested = IMAGE_SIZES.get(requested.lower(), (1920, 1080))
    width, height = requested

    ratio = ratio or _requested_ratio(prompt)
    if ratio == "9:16":
        width, height = height, width
    elif ratio == "1:1":
        side = min(width, height)
        width = height = side

    path = OUT / f"{_safe_name(title)}_{datetime.now():%Y%m%d_%H%M%S}.png"
    img = Image.new("RGB", (width, height), (24, 27, 34))
    draw = ImageDraw.Draw(img)
    try:
        scale = max(1, width // 1920)
        font_big = ImageFont.truetype("arial.ttf", 64 * scale)
        font_small = ImageFont.truetype("arial.ttf", 30 * scale)
    except Exception:
        font_big = font_small = ImageFont.load_default()
    margin = max(60, width // 20)
    draw.text((margin, margin), str(title)[:70], font=font_big, fill=(240, 240, 245))
    wrapped = "\n".join(textwrap.wrap(str(prompt), max(45, width // 28))[:16])
    draw.text((margin, margin + 150), wrapped, font=font_small, fill=(190, 200, 215), spacing=12)
    draw.text((margin, height - margin - 40), "LUCKI AI • Local Poster", font=font_small, fill=(140, 220, 255))
    img.save(path, format="PNG", optimize=True)
    return str(path)
