"""Thunderstore icon (256x256). Uses reference/gemini/icon_raw.png when it exists, else draws a fallback."""
import os
from PIL import Image, ImageDraw


def fallback():
    im = Image.new('RGBA', (256, 256), (0x2C, 0x73, 0x67, 255))
    d = ImageDraw.Draw(im)
    d.ellipse((28, 28, 228, 228), fill=(0xF4, 0xF6, 0xF8, 255))
    d.rectangle((112, 60, 144, 196), fill=(0xD8, 0x3A, 0x3A, 255))   # red cross
    d.rectangle((60, 112, 196, 144), fill=(0xD8, 0x3A, 0x3A, 255))
    d.rectangle((150, 150, 230, 174), fill=(0x8C, 0x94, 0xA2, 255))  # syringe barrel
    d.rectangle((230, 158, 252, 166), fill=(0x3A, 0x3F, 0x4A, 255))  # needle
    return im


def build(project):
    src = os.path.join(project, 'reference', 'gemini', 'icon_raw.png')
    if os.path.exists(src):
        return Image.open(src).convert('RGBA').resize((256, 256), Image.LANCZOS)
    return fallback()


def write(project):
    out = os.path.join(project, 'thunderstore', 'icon.png')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build(project).save(out)
    return out
