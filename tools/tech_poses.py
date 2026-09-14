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


IDLE = [BASE, head_bob(BASE), BASE, arm(BASE, 0, 1)]
MOVE = [with_legs(BASE, LEGS_A), head_bob(with_legs(BASE, LEGS_A)), with_legs(BASE, LEGS_B),
        with_legs(BASE, LEGS_C), head_bob(with_legs(BASE, LEGS_C)), with_legs(BASE, LEGS_B)]
TELL = [arm(BASE, 0, -1), arm(BASE, 0, -2), arm(BASE, 0, -3)]
FIRE = [arm(BASE, 1, 0), arm(BASE, 1, -1), arm(BASE, 0, -1)]
_lying = fall(BASE, -90)
DIE = [shift(BASE, -1, 0), fall(BASE, -20), fall(BASE, -45), fall(BASE, -70), _lying, _lying]

CLIPS = OrderedDict([('idle', IDLE), ('move', MOVE), ('tell', TELL), ('fire', FIRE), ('die', DIE)])


def write(project):
    root = os.path.join(project, 'Resources', 'Enemies', 'tech')
    paths = []
    for clip, frames in CLIPS.items():
        for i, f in enumerate(frames, 1):
            p = os.path.join(root, clip, 'tech_%s_%03d.png' % (clip, i))
            save(strip_outline(f), p)     # the game adds the outline to actors at runtime
            paths.append(p)
    return paths


def preview(project):
    p = os.path.join(project, 'docs', 'preview', 'tech-sheet.png')
    sheet([IDLE + TELL, MOVE, FIRE, DIE], p, scale=4)
    return p
