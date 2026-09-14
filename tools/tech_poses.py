"""The Vet Tech: one hand-drawn base pose (facing right) on a 32x32 canvas, plus overlays and derived clips.

A regular enemy on the Bullet Kin body plan: big head (half the body), short body, stick legs, teal scrubs
($ base, ~ dark folds and cap band), a teal surgical cap, a white mask (W, w shade) over the mouth, skin =,
dot eyes g, and a syringe pistol in the right hand: steel barrel (& light, % mid, # dark plunger and grip)
with blue liquid *, needle % pointing right.
The left-facing versions are mirrored by the game (DirectionalAnimation FlipType.Flip), so only right-facing art exists.
Exported WITHOUT the outline: the Tech is an AIActor and the game draws its outline at runtime (procedurallyOutlined).
"""
import os
from collections import OrderedDict

from vetpixel import R, pad, shift, overlay, erase, rotate_free, settle, save, sheet, strip_outline

CANVAS = (32, 32)
HITBOX = (8, 0, 12, 26)     # x, y, w, h in canvas pixels from the lower-left: the body column (cap to shoes), not the syringe
SHOOT_POINT = (30, 10)      # canvas pixels from the lower-left: the needle tip of the base pose

# Column ruler:      0123456789012345678901234567890 1
POSE = R([
    "................................",  # 0
    "................................",  # 1
    "................................",  # 2
    "................................",  # 3
    "................................",  # 4
    "................................",  # 5
    ".........oooooooooo.............",  # 6  cap top
    "........o$$$$$$$$$$o............",  # 7
    ".......o$$$$$$$$$$$$o...........",  # 8
    ".......o$$$$$$$$$~~$o...........",  # 9
    ".......o~~~~~~~~~~~~o...........",  # 10 cap band
    ".......o============o...........",  # 11 brow
    ".......o============o...........",  # 12
    ".......o======g===g=o...........",  # 13 eyes
    ".......o============o...........",  # 14
    ".......oWWWWWWWWWWWWo...........",  # 15 mask
    ".......oWWWWWWWWWWWWo...........",  # 16
    ".......oWWWWWWWWWWWwo...........",  # 17
    "........owwwwwwwwwwo............",  # 18 chin (mask bottom)
    "........o$$$~$$~$$~o.oooooooo...",  # 19 shoulders, V-neck; barrel top
    "........o$$$$~~$$$~oo#&&&&&&o...",  # 20 plunger + barrel light
    "........o$$$$$$$$$~oo#******%%%.",  # 21 liquid + needle (tip at column 30)
    "........o$$$$$$$$$~oo#%%%%%%o...",  # 22 barrel shade
    "........o$$$$$$$$$~o=====oooo...",  # 23 arm under the barrel
    "........o$$$$$$$$$~oo===o##o....",  # 24 hand + grip
    "........o~$$$$$$$~~o.oooo##o....",  # 25
    "........oooooooooooo....oooo....",  # 26 body bottom / grip bottom
    "..........o~~o.o~~o.............",  # 27 legs
    "..........o~~o.o~~o.............",  # 28
    "..........o~~o.o~~o.............",  # 29
    "..........o@@@o.o@@@o...........",  # 30 shoes
    "..........ooooo.ooooo...........",  # 31
])
HEAD_ROWS = (6, 19)                  # cap top to chin
LEG_ROWS = (27, 32)                  # trouser + shoe rows of the pose
ARM_BOX = (20, 19, 32, 27)           # canvas x0, y0, x1, y1 of the arm + syringe pistol region
TORSO_EDGE = ['o'] * (ARM_BOX[3] - ARM_BOX[1])  # outline column where the arm meets the scrubs, redrawn after every arm move
BASE = overlay(pad(POSE, CANVAS[0], CANVAS[1]), TORSO_EDGE, ARM_BOX[0] - 1, ARM_BOX[1])

# Walk cycle legs (5 rows x 32): A = stride (left leg forward), B = crossing, C = stride (right leg forward).
LEGS_A = R([
    ".........o~~o.....o~~o..........",
    "........o~~o.......o~~o.........",
    ".......o~~o.........o~~o........",
    "......o@@@o.........o@@@o.......",
    "......ooooo.........ooooo.......",
])
LEGS_B = R([
    "...........o~~oo~~o.............",
    "...........o~~oo~~o.............",
    "............o~oo~o..............",
    "...........o@@oo@@o.............",
    "...........oooooooo.............",
])
LEGS_C = R([
    ".........o~~o.....o~~o..........",
    "..........o~~o...o~~o...........",
    "...........o~~o.o~~o............",
    "...........o@@@oo@@@o...........",
    "...........ooooooooo............",
])


def region(rows, x0, y0, x1, y1):
    """Copy of rows with everything outside the box made transparent."""
    return [''.join(ch if (x0 <= x < x1 and y0 <= y < y1) else '.' for x, ch in enumerate(row)) for y, row in enumerate(rows)]


def with_legs(base, legs):
    body = [row if not (LEG_ROWS[0] <= y < LEG_ROWS[1]) else '.' * len(row) for y, row in enumerate(base)]
    return overlay(body, legs, 0, LEG_ROWS[0])


def head_bob(rows):
    """Head one pixel up; the last mask row is duplicated so the chin stays attached to the body."""
    y = HEAD_ROWS[1] - 2
    return rows[1:y + 1] + [rows[y]] + rows[y + 1:]


def arm(rows, dx, dy):
    """Move the arm + syringe pistol region by (dx, dy) and redraw the scrubs edge it was attached to."""
    x0, y0, x1, y1 = ARM_BOX
    piece = region(rows, x0, y0, x1, y1)
    cleared = erase(rows, piece)
    return overlay(overlay(cleared, shift(piece, dx, dy)), TORSO_EDGE, x0 - 1, y0)


def fall(rows, angle):
    """Rotate on a temporary canvas at least as tall as it is wide so nothing clips, drop to the floor, crop back."""
    extra = max(0, CANVAS[0] - CANVAS[1])
    tall = pad(rows, CANVAS[0], CANVAS[1] + extra, 0, extra)
    return settle(rotate_free(tall, angle))[extra:]


def make_clips(base):
    """The five clips of a Tech body: every frame is derived from the one hand-drawn base pose."""
    lying = fall(base, -90)
    return OrderedDict([
        ('idle', [base, head_bob(base), base, arm(base, 0, 1)]),
        ('move', [with_legs(base, LEGS_A), head_bob(with_legs(base, LEGS_A)), with_legs(base, LEGS_B),
                  with_legs(base, LEGS_C), head_bob(with_legs(base, LEGS_C)), with_legs(base, LEGS_B)]),
        ('tell', [arm(base, 0, -1), arm(base, 0, -2), arm(base, 0, -3)]),
        ('fire', [arm(base, 1, 0), arm(base, 1, -1), arm(base, 0, -1)]),
        ('die', [shift(base, -1, 0), fall(base, -20), fall(base, -45), fall(base, -70), lying, lying]),
    ])


CLIPS = make_clips(BASE)
IDLE, MOVE, TELL, FIRE, DIE = CLIPS['idle'], CLIPS['move'], CLIPS['tell'], CLIPS['fire'], CLIPS['die']

# ------------------------------------------------------------------ the Syringe Tech (0.11)
# The same body in plum scrubs, carrying the syringe shotgun: a wide pump syringe with two needles, hand-drawn into the
# arm box (12 x 8 canvas pixels, rows 19-26) so the tell and fire clips raise it the same way.
STECH_KEYS = {'$': '(', '~': ')'}
SHOTGUN = R([
    ".ooooooooo..",   # 19 barrel top
    "o#&&&&&&&o..",   # 20 plunger + barrel light
    "o#*******%%.",   # 21 upper needle (tip at canvas column 30: the fire clip shoves the arm one pixel forward)
    "o#*******o..",   # 22 liquid
    "o#*******%%.",   # 23 lower needle
    "o=%%%%%%%o..",   # 24 hand + barrel shade
    "o==ooo##o...",   # 25 fingers + pump grip
    ".ooo..oo....",   # 26 grip bottom
])
STECH_SHOOT_POINT = (30, 10)


def recolour(rows, keys):
    return [''.join(keys.get(ch, ch) for ch in row) for row in rows]


def _stech_base():
    body = recolour(BASE, STECH_KEYS)
    x0, y0, x1, y1 = ARM_BOX
    cleared = erase(body, region(body, x0, y0, x1, y1))
    return overlay(overlay(cleared, SHOTGUN, x0, y0), TORSO_EDGE, x0 - 1, y0)


STECH_BASE = _stech_base()
# The walk-leg overlays are drawn in the Vet Tech's teal, so recolour every derived frame, not only the base.
STECH_CLIPS = OrderedDict((clip, [recolour(f, STECH_KEYS) for f in frames]) for clip, frames in make_clips(STECH_BASE).items())


def write(project):
    paths = []
    for folder, clips in (('tech', CLIPS), ('stech', STECH_CLIPS)):
        root = os.path.join(project, 'Resources', 'Enemies', folder)
        for clip, frames in clips.items():
            for i, f in enumerate(frames, 1):
                p = os.path.join(root, clip, '%s_%s_%03d.png' % (folder, clip, i))
                save(strip_outline(f), p)     # the game adds the outline to actors at runtime
                paths.append(p)
    return paths


def preview(project):
    p = os.path.join(project, 'docs', 'preview', 'tech-sheet.png')
    sheet([IDLE + TELL, MOVE, FIRE, DIE], p, scale=4)
    sheet([STECH_CLIPS['idle'] + STECH_CLIPS['tell'], STECH_CLIPS['move'], STECH_CLIPS['fire'], STECH_CLIPS['die']],
          os.path.join(project, 'docs', 'preview', 'stech-sheet.png'), scale=4)
    return p
