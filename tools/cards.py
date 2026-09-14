"""Boss card (427x240) and past win picture (115x71), composed from the hand-drawn pixel art only. The Gemini paintings
in reference/gemini/ are references, never shipped (the user asked for hand-drawn everything in 0.11)."""
import os

from PIL import Image, ImageDraw

import vetpixel as V
import vet_card as VC
import vet_poses as P
import win_pic as WP

CARD = (427, 240)
WIN = (115, 71)


def boss_card(project):
    """Hand-drawn only (0.11): a transparent 427x240 card holding the Vet's portrait (tools/vet_card.py, drawn at card
    resolution with its own outline) in the right half, like the vanilla boss cards. The game draws the name, the speed
    streaks and the player's card (on top, over the left side) itself, so everything outside the portrait stays empty."""
    im = Image.new('RGBA', CARD, (0, 0, 0, 0))
    portrait = V.image(VC.PORTRAIT)
    im.paste(portrait, VC.ORIGIN, portrait)
    return im


def win_pic(project):
    """Hand-drawn only (0.13): the happy ending drawn in tools/win_pic.py (Pluto on the exam table, the Vet knocked out,
    Bogdan and Bianca coming in through the lit doorway)."""
    return WP.image()


def _font(size):
    from PIL import ImageFont
    for path in ('/System/Library/Fonts/Supplemental/Arial Black.ttf', '/Library/Fonts/Arial Black.ttf'):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def bosscard_preview(project, scale=3):
    """Mock of the in-game intro (docs only, never shipped): black letterbox, a diagonal teal/blue speed-streak band,
    the title top-left, a grey stand-in for the player's card bottom-left, and the portrait on top, all at 3x nearest."""
    w, h = CARD[0] * scale, CARD[1] * scale
    im = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    band = Image.new('L', (w, h), 0)
    ImageDraw.Draw(band).polygon([(0, 70 * scale), (w, 0), (w, 170 * scale), (0, 240 * scale)], fill=255)
    streaks = Image.new('RGBA', (w, h), (0x2B, 0x6F, 0x8A, 255))
    d = ImageDraw.Draw(streaks)
    seed = 7
    for y in range(0, h, 2 * scale):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        x = seed % w
        length = 40 * scale + (seed >> 8) % (140 * scale)
        colour = ((0x4F, 0xA8, 0xC8, 255), (0x9E, 0xE6, 0xFF, 255), (0x1F, 0x52, 0x6A, 255))[(seed >> 4) % 3]
        d.rectangle((x, y, x + length, y + scale), fill=colour)
    im.paste(streaks, (0, 0), band)
    t = ImageDraw.Draw(im)
    t.text((22 * scale, 10 * scale), "DOCTOR'S ORDERS", font=_font(13 * scale), fill='white', stroke_width=scale,
           stroke_fill='black')
    t.text((30 * scale, 26 * scale), 'THE VET', font=_font(34 * scale), fill='white', stroke_width=2 * scale,
           stroke_fill='black')
    t.rectangle((14 * scale, 120 * scale, 130 * scale, 239 * scale), fill=(0x78, 0x78, 0x82, 255))
    portrait = boss_card(project).resize((w, h), Image.NEAREST)
    im.paste(portrait, (0, 0), portrait)
    return im


def write(project):
    card = os.path.join(project, 'Resources', 'Boss', 'vet_bosscard.png')
    win = os.path.join(project, 'Resources', 'past_win_pic.png')
    preview = os.path.join(project, 'docs', 'preview', 'bosscard-preview.png')
    os.makedirs(os.path.dirname(card), exist_ok=True)
    os.makedirs(os.path.dirname(preview), exist_ok=True)
    boss_card(project).save(card)
    win_pic(project).save(win)
    bosscard_preview(project).save(preview)
    win_preview = os.path.join(project, 'docs', 'preview', 'win-pic-preview.png')
    WP.preview().save(win_preview)
    return card, win, preview, win_preview
