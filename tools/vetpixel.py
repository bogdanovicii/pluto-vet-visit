"""Palette and helpers for the Vet Visit art. Reuses the main mod's palette-independent pixel
helpers read-only, but keeps its own literal PALETTE so an unrelated palette edit in the main mod
cannot silently re-render our committed PNGs (see tools/tests/test_palette.py).

Every sprite is a list of equal-length strings; each character is a palette key, '.' is transparent.
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
MAIN_TOOLS = os.path.join(os.path.dirname(PROJECT), 'tools')
if MAIN_TOOLS not in sys.path:
    sys.path.insert(0, MAIN_TOOLS)
from pixel import img_from_rows, check_rect, pad, shift, overlay, erase, rows_from_img, strip_outline  # noqa: E402,F401

# Snapshotted verbatim from ../tools/pixel.py's PALETTE: only the base cat/body keys our art
# actually uses (scanned from vet_poses.py, clinic_objects.py, projectiles.py and cards.py).
# Deliberately literal (not imported) so an unrelated edit to the main mod's palette cannot
# silently re-render our committed PNGs. tools/tests/test_palette.py enforces this stays in
# sync on purpose rather than by accident.
PALETTE = {
    '.': None,
    'o': (0x1E, 0x16, 0x14, 255),  # outline
    'W': (0xFA, 0xF6, 0xEE, 255),  # white fur
    'w': (0xD6, 0xCE, 0xC6, 255),  # white fur shade (cooler)
    'B': (0x8B, 0x7A, 0x66, 255),  # tabby base: grey-brown taupe (h32 s27 v55)
    'g': (0x1B, 0x2A, 0x1B, 255),  # pupil
    'K': (0xF2, 0xF2, 0xF2, 255),  # highlight white
    'H': (0xFF, 0x5C, 0x8A, 255),  # heart pink
    'Z': (0x74, 0x76, 0x80, 255),  # grey cat on the bag
    'e': (0xC3, 0xD3, 0x7A, 255),  # eye light (cards only)
}
PALETTE.update({
    '#': (0x3A, 0x3F, 0x4A, 255),  # steel dark
    '%': (0x8C, 0x94, 0xA2, 255),  # steel mid
    '&': (0xC9, 0xCF, 0xD8, 255),  # steel light
    '=': (0xF1, 0xC9, 0xA5, 255),  # skin
    '-': (0xC9, 0x9A, 0x76, 255),  # skin shade
    '@': (0x2B, 0x22, 0x1D, 255),  # hair
    '$': (0x3F, 0x9E, 0x8F, 255),  # scrubs teal
    '~': (0x2C, 0x73, 0x67, 255),  # scrubs teal dark
    '*': (0x4F, 0xA8, 0xE8, 255),  # syringe liquid blue
    '^': (0xD9, 0xF1, 0xFF, 200),  # glass (translucent)
    '!': (0xD8, 0x3A, 0x3A, 255),  # medical red
    '?': (0xF0, 0x8A, 0x24, 255),  # plastic orange
    ':': (0xF5, 0xD5, 0x47, 255),  # plastic yellow
    '|': (0x6F, 0x8F, 0xBF, 255),  # carrier blue plastic
    '/': (0x4A, 0x63, 0x90, 255),  # carrier blue dark
    '\\': (0xA9, 0x7B, 0x4F, 255), # wood / cardboard
    '+': (0x7A, 0x5A, 0x3A, 255),  # wood dark
    '_': (0xF4, 0xF6, 0xF8, 255),  # tile white
    '0': (0xDC, 0xE0, 0xE6, 255),  # tile white shade
})


def R(rows):
    return check_rect(rows)


def image(rows):
    return img_from_rows(rows, PALETTE)


def save(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im = image(rows)
    im.save(path)
    return im


def rotate_free(rows, angle):
    """Rotate about the canvas centre (nearest neighbour), keeping the canvas size."""
    im = image(rows)
    im = im.rotate(angle, resample=Image.NEAREST, expand=False, center=(im.width / 2, im.height / 2))
    return rows_from_img(im, PALETTE)


def lowest_opaque_row(rows):
    for y in range(len(rows) - 1, -1, -1):
        if any(ch != '.' for ch in rows[y]):
            return y
    return -1


def settle(rows):
    """Shift the sprite down so its lowest opaque pixel sits on the bottom row."""
    low = lowest_opaque_row(rows)
    if low < 0:
        return rows
    return shift(rows, 0, len(rows) - 1 - low)


def sheet(frame_lists, path, scale=4, gap=2, bg=(70, 70, 90, 255)):
    """Contact sheet with this palette: each entry of frame_lists is a list of row-lists."""
    ims = [[image(f) for f in row] for row in frame_lists]
    W = max(sum(i.width * scale + gap for i in row) for row in ims)
    H = sum(max(i.height for i in row) * scale + gap for row in ims)
    out = Image.new('RGBA', (W, H), bg)
    y = 0
    for row in ims:
        x = 0
        rh = max(i.height for i in row) * scale
        for i in row:
            out.paste(i.resize((i.width * scale, i.height * scale), Image.NEAREST), (x, y))
            x += i.width * scale + gap
        y += rh + gap
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out.save(path)
    return out
