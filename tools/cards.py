"""Boss card (427x240) and past win picture (115x71). Uses reference/gemini/*_raw.png when present, else composes
from the pixel art so the build never depends on the API."""
import os

from PIL import Image, ImageDraw

import vetpixel as V
import vet_poses as P

CARD = (427, 240)
WIN = (115, 71)


def gemini(project, name):
    p = os.path.join(project, 'reference', 'gemini', name)
    return Image.open(p).convert('RGBA') if os.path.exists(p) else None


def fit_cover(im, w, h):
    """Resize to cover w x h, then centre-crop."""
    s = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * s)), max(h, round(im.height * s))), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def boss_card(project):
    src = gemini(project, 'vet_bosscard_raw.png')
    if src is not None:
        return fit_cover(src, *CARD)
    im = Image.new('RGBA', CARD, (0, 0, 0, 0))
    vet = V.image(P.BASE).crop(V.image(P.BASE).getbbox())
    vet = vet.resize((vet.width * 5, vet.height * 5), Image.NEAREST)
    im.paste(vet, (CARD[0] - vet.width - 24, CARD[1] - vet.height - 12), vet)
    return im


def win_pic(project):
    src = gemini(project, 'past_win_pic_raw.png')
    if src is not None:
        big = fit_cover(src, WIN[0] * 4, WIN[1] * 4)
        return big.resize(WIN, Image.LANCZOS).quantize(64).convert('RGBA')
    im = Image.new('RGBA', WIN, V.PALETTE['_'])
    d = ImageDraw.Draw(im)
    for y in range(0, WIN[1], 8):                      # tile grid
        d.line((0, y, WIN[0], y), fill=V.PALETTE['0'])
    for x in range(0, WIN[0], 8):
        d.line((x, 0, x, WIN[1]), fill=V.PALETTE['0'])
    lying = V.image(P.CLIPS['die'][-1])
    im.paste(lying, (8, WIN[1] - lying.height), lying)
    d.rectangle((60, 12, 106, 40), fill=V.PALETTE['&'], outline=V.PALETTE['o'])  # exam table
    try:
        import character_anims as A                     # the main mod's Pluto, read-only
        cat = V.image(A.IDLE_SIDE[0])
        im.paste(cat, (72, 12 - cat.height + 2), cat)
    except (ImportError, AttributeError, KeyError, IndexError):
        d.ellipse((74, 0, 96, 14), fill=(0x8E, 0x71, 0x50, 255), outline=V.PALETTE['o'])
    d.rectangle((2, 2, 12, 12), fill=V.PALETTE['!'])
    return im


def write(project):
    card = os.path.join(project, 'Resources', 'Boss', 'vet_bosscard.png')
    win = os.path.join(project, 'Resources', 'past_win_pic.png')
    os.makedirs(os.path.dirname(card), exist_ok=True)
    boss_card(project).save(card)
    win_pic(project).save(win)
    return card, win
