"""Boss card (427x240) and past win picture (115x71), composed from the hand-drawn pixel art only. The Gemini paintings
in reference/gemini/ are references, never shipped (the user asked for hand-drawn everything in 0.11)."""
import os

from PIL import Image, ImageDraw

import vetpixel as V
import vet_card as VC
import vet_poses as P

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
    """Hand-drawn only (0.11): Pluto on the exam table, the Vet lying on the tiles."""
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
