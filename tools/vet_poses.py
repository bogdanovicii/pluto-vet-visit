"""The Vet: one hand-drawn base pose (32x40, facing right) on a 48x40 canvas, plus overlays and derived clips.

Palette: o outline, W/w/K white coat, = skin, - skin shade, @ hair/shoes/stethoscope, $ ~ teal scrubs, & % # steel,
* liquid, ^ glass, g eyes, ! pen, : name tag. v0.4: glasses, stethoscope, coat pocket, a vaccine gun (syringe pistol).
The left-facing versions are mirrored by the game (DirectionalAnimation FlipType.Flip), so only right-facing art exists.
Exported WITHOUT the outline: the Vet is an AIActor and the game draws his outline at runtime (procedurallyOutlined).
"""
import os
from collections import OrderedDict

from vetpixel import R, pad, shift, overlay, erase, rotate_free, settle, save, sheet, strip_outline

CANVAS = (48, 40)
DX = 8                      # the 36-wide pose sits at columns 8..43 of the 48-wide canvas
HITBOX = (16, 0, 14, 36)    # x, y, w, h in canvas pixels: the body column (head to shoes), not the syringe

POSE = R([
    "....................................",
    "............oooooo..................",
    "...........o@@@@@@o.................",
    "..........o@@@@@@@@o................",
    "..........o@@@@@@@@o................",
    "..........o@@@=====o................",
    "..........o@========o...............",
    "..........o=oo=oo==o................",
    "..........o=^g=^g==o................",
    "..........o========o................",
    "..........o===-=-==o................",
    "...........o==oo==o.................",
    "............oooooo..................",
    "..........ooWWWWWWoo................",
    ".........oWWW@$$@WWWo...............",
    "........oWWWW@$$@WWWWo..............",
    "........oWWWW@$$@WWWWoo.............",
    "........oWWWW@%%@WWWWW=o............",
    "........oWWWWW@@WWWWWW=oo...........",
    "........oWWWWWWWWWWWWW==o&&&&&&&&o..",
    "........oWWW!WWWWWWWWWo=##&******&%%",
    "........oWWW:WWWWWWWWWoo#&%%%%%%%&o.",
    "........oWWWWWWWWWWWWWo.oo###ooooo..",
    "........oWwWWWWWWWWWwWo..o###o......",
    "........oWwWWWWWWWWWwWo..ooooo......",
    "........oWwWWWWWWWWWwWo.............",
    "........oWwWWWWWWWWWwWo.............",
    "........oWwWWWWWWWWWwWo.............",
    "........oWwWWWWWWWWWwWo.............",
    "........oWwWWWWWWWWWwWo.............",
    "........oWwwwwwwwwwwwWo.............",
    ".........oooooooooooooo.............",
    "..........o~~~o.o~~~o...............",
    "..........o~~~o.o~~~o...............",
    "..........o~~~o.o~~~o...............",
    "..........o~$~o.o~$~o...............",
    "..........o~~~o.o~~~o...............",
    "..........o~~~o.o~~~o...............",
    ".........o@@@@o.o@@@@o..............",
    ".........oooooo.oooooo..............",
])
LEG_ROWS = (32, 40)                 # trouser + shoe rows of the pose
ARM_BOX = (23 + DX, 17, 36 + DX, 25)  # canvas x0, y0, x1, y1 of the arm + vaccine gun region
TORSO_EDGE = ['o'] * (ARM_BOX[3] - ARM_BOX[1])  # outline column where the arm meets the coat, redrawn after every arm move
BASE = overlay(pad(POSE, CANVAS[0], CANVAS[1], DX, 0), TORSO_EDGE, ARM_BOX[0] - 1, ARM_BOX[1])

# Walk cycle legs (8 rows x 32): A = stride, B = crossing.
LEGS_A = R([
    ".........o~~~o....o~~~o.........",
    "........o~~~o......o~~~o........",
    "........o~~~o......o~~~o........",
    ".......o~~~o........o~~~o.......",
    ".......o~~~o........o~~~o.......",
    "......o~~~o..........o~~~o......",
    ".....o@@@@o..........o@@@@o.....",
    ".....oooooo..........oooooo.....",
])
LEGS_B = R([
    "...........o~~~oo~~~o...........",
    "...........o~~~oo~~~o...........",
    "...........o~~~oo~~~o...........",
    "............o~~oo~~o............",
    "............o~~oo~~o............",
    "............o~~oo~~o............",
    "...........o@@@oo@@@o...........",
    "...........ooooooooo............",
])


def region(rows, x0, y0, x1, y1):
    """Copy of rows with everything outside the box made transparent."""
    return [''.join(ch if (x0 <= x < x1 and y0 <= y < y1) else '.' for x, ch in enumerate(row)) for y, row in enumerate(rows)]


def with_legs(base, legs):
    body = [row if not (LEG_ROWS[0] <= y < LEG_ROWS[1]) else '.' * len(row) for y, row in enumerate(base)]
    return overlay(body, legs, DX, LEG_ROWS[0])


def head_bob(rows):
    """Head (rows 0-11) one pixel up; the chin row is duplicated so the neck stays attached."""
    return rows[1:12] + [rows[11]] + rows[12:]


def arm(rows, dx, dy):
    """Move the arm + syringe region by (dx, dy) and redraw the coat edge it was attached to."""
    x0, y0, x1, y1 = ARM_BOX
    piece = region(rows, x0, y0, x1, y1)
    cleared = erase(rows, piece)
    return overlay(overlay(cleared, shift(piece, dx, dy)), TORSO_EDGE, x0 - 1, y0)


def fall(rows, angle):
    """Rotate on a taller temporary canvas so nothing clips, drop to the floor, crop back to CANVAS."""
    extra = CANVAS[0] - CANVAS[1]
    tall = pad(rows, CANVAS[0], CANVAS[0], 0, extra)
    return settle(rotate_free(tall, angle))[extra:]


IDLE = [BASE, head_bob(BASE), BASE, arm(BASE, 0, 1)]
MOVE = [with_legs(BASE, LEGS_A), head_bob(with_legs(BASE, LEGS_A)), BASE,
        with_legs(BASE, LEGS_B), head_bob(with_legs(BASE, LEGS_B)), BASE]
TELL = [arm(BASE, 0, -2), arm(BASE, 0, -4), arm(BASE, 0, -6)]
FIRE = [arm(BASE, 2, 0), shift(arm(BASE, 3, 0), 1, 0), arm(BASE, 1, 0)]
INTRO = [arm(BASE, 0, -4), arm(BASE, 0, -6), arm(BASE, 0, -4), arm(BASE, 0, -2),
         arm(BASE, 0, -4), arm(BASE, 0, -6), arm(BASE, 0, -4), BASE]
_lying = fall(BASE, -90)
DIE = [shift(BASE, -1, 0), shift(BASE, -2, 0), fall(BASE, -25), fall(BASE, -50), fall(BASE, -75), _lying, _lying, _lying]

CLIPS = OrderedDict([('idle', IDLE), ('move', MOVE), ('tell', TELL), ('fire', FIRE), ('intro', INTRO), ('die', DIE)])


def write(project):
    root = os.path.join(project, 'Resources', 'Boss', 'vet')
    paths = []
    for clip, frames in CLIPS.items():
        for i, f in enumerate(frames, 1):
            p = os.path.join(root, clip, 'vet_%s_%03d.png' % (clip, i))
            save(strip_outline(f), p)     # the game adds the outline to actors at runtime
            paths.append(p)
    return paths


def preview(project):
    p = os.path.join(project, 'docs', 'preview', 'vet-sheet.png')
    sheet([IDLE + TELL, MOVE, FIRE + INTRO[:5], DIE], p, scale=4)
    return p
