"""The Nurse (mini-boss): one hand-drawn base pose on the Vet's 48x40 canvas, facing right, plus derived clips.

Same pipeline as vet_poses: literal row-string blocks, strict transforms, exported WITHOUT the outline
(AIActors are outlined by the game at runtime). The pose is three literal blocks composed back to front:
NET_BACK (butterfly net slung over the far shoulder), BODY (cap, bun, stern face, teal scrubs, shoes) and
SYRINGE (the shotgun-sized syringe with both forearms and hands, held low and two-handed, pointing right).

Palette: o outline, W cap, ! red cross, @ hair/shoes, g eyes, = skin, - skin shade, $ ~ teal scrubs,
: name badge, & % # steel, ^ glass, * liquid, \\ + wood, K w net mesh.
Constants HITBOX and SHOOT_POINT are in canvas pixels from the lower-left, like vet_poses.HITBOX.
"""
import os
from collections import OrderedDict

from vetpixel import R, pad, shift, overlay, rotate_free, settle, save, sheet, strip_outline
from vet_poses import CANVAS

HITBOX = (11, 0, 21, 38)    # x, y, w, h from the lower-left: the body column (cap to shoes), not the syringe
SYRINGE_AT = (11, 21)       # canvas position of the SYRINGE block in the base pose
NEEDLE_TIP = (33, 2)        # needle tip inside the SYRINGE block
SHOOT_POINT = (SYRINGE_AT[0] + NEEDLE_TIP[0], CANVAS[1] - 1 - (SYRINGE_AT[1] + NEEDLE_TIP[1]))  # (44, 16)
NET_AT = (0, 2)             # canvas position of NET_BACK in the base pose

# Body without the syringe and the net: heavier than the Vet (torso 21 wide), upper arms only; the
# forearms live in the SYRINGE block so the whole two-handed hold moves as one piece.
BODY = R([
    "................................................",
    "................oooooooooo......................",
    "...............oWWWWW!WWWWo.....................",
    "...............oWWWW!!!WWWo.....................",
    "...............oWWWWW!WWWWo.....................",
    "..........oooooo@@@@@@@@@@o.....................",
    ".........o@@@@@@@@=========o....................",
    ".........o@@@@@@@=@@===@@==o....................",
    ".........o@@@@@@@=g=====g==o....................",
    ".........o@@@@@@@=====-====o....................",
    "..........o@@@@@@==========o....................",
    "...........o@@@@======--===o....................",
    "............o@@=========---o....................",
    "............ooooooo=====ooooooo.................",
    "..........oo$$$$$$~=====~$$$$$$oo...............",
    "..........o$$$$$$$~~===~~$$$$$$$o...............",
    "..........o$$$$$$$$~~~~~$$$$$$$$o...............",
    "..........o$$$$$$$$$~~~$$$:$$$$$o...............",
    "..........o~~~$$$$$$$$$$$$$$$~~~o...............",
    "..........o===o$$$$$$$$$$$$$o===o...............",
    "..........o===o$$$$$$$$$$$$$o===o...............",
    "..........o===o$$$$$$$$$$$$$o===o...............",
    "..........o=-=o$$$$$$$$$$$$$o=-=o...............",
    "...........o$$$$$$$$$$$$$$$$$$$o................",
    "...........o$$$$$$$$$$$$$$$$$$$o................",
    "...........o$$$$$$$$$$$$$$$$$$$o................",
    "...........o$$$$$$$$$$$$$$$$$$$o................",
    "...........o~~~~~~~~~~~~~~~~~~~o................",
    "...........ooooooooooooooooooooo................",
    "............o~~~~~~~~~~~~~~~~o..................",
    "............o~$~~~~o..o~$~~~~o..................",
    "............o~$~~~~o..o~$~~~~o..................",
    "............o~$~~~~o..o~$~~~~o..................",
    "............o~$~~~~o..o~$~~~~o..................",
    "............o~$~~~~o..o~$~~~~o..................",
    "............o~$~~~~o..o~$~~~~o..................",
    "............o~$~~~~o..o~$~~~~o..................",
    "............o~$~~~~o..o~$~~~~o..................",
    "............o@@@@@@@o.o@@@@@@@o.................",
    "............ooooooooo.ooooooooo.................",
])
LEG_ROWS = (29, 40)         # trouser + shoe rows of BODY
LEGS_AT = 8                 # canvas x of the leg blocks
HEAD_ROWS = 13              # rows 0-12 are the head (row 13 is the chin/shoulder line)

# Both forearms + hands + the syringe (9 rows x 35): thumb flange and plunger rod, steel caps, glass barrel full of liquid,
# the near forearm crossing in front of the barrel to the pump grip, the far forearm under it.
SYRINGE = R([
    "........o...ooooooooooooooooooo....",
    ".......o#oooo&&^^^^^^^^^^^^&&&ooooo",
    "o===o..o#%%%o&%***o===o****%&%o%%%o",
    ".o====oo#oooo%#****o===o***#%#ooooo",
    "...o====ooooooooooooo===ooooooo....",
    "......o===========o##====#o........",
    "......oooo-----===o##=--=#o........",
    ".........oooooooooo#######o........",
    "..................ooooooooo........",
])

# Butterfly net (15 x 14): wooden rim, K/w mesh, handle running down-right (behind the body when slung).
NET_BACK = R([
    "...oooooo......",
    "..o++++++o.....",
    ".o+KwKwKwK+o...",
    "o+wKwKwKwKw+o..",
    "o+KwKwKwKwK+o..",
    "o+wKwKwKwKw+o..",
    "o+KwKwKwKwK+o..",
    ".o+wKwKwKw+o...",
    "..o++++++++o...",
    "...oooooo\\\\o...",
    ".........o\\\\o..",
    "..........o\\\\o.",
    "...........o\\\\.",
    "............o\\\\",
])
NET_FRONT = [row[::-1] for row in NET_BACK]     # hoop on the right, handle down-left toward the hands

# Walk cycle legs (11 rows x 26 at LEGS_AT): A = stride, B = crossing.
LEGS_A = R([
    "....o~~~~~~~~~~~~~~~~o....",
    "...o~$~~~~o..o~$~~~~o.....",
    "...o~$~~~~o..o~$~~~~o.....",
    "..o~$~~~~o....o~$~~~~o....",
    "..o~$~~~~o....o~$~~~~o....",
    ".o~$~~~~o......o~$~~~~o...",
    ".o~$~~~~o......o~$~~~~o...",
    "o~$~~~~o........o~$~~~~o..",
    "o~$~~~~o........o~$~~~~o..",
    "o@@@@@@@o.......o@@@@@@@o.",
    "ooooooooo.......ooooooooo.",
])
LEGS_B = R([
    "....o~~~~~~~~~~~~~~~~o....",
    "......o~$~~~~oo~$~~~~o....",
    "......o~$~~~~oo~$~~~~o....",
    ".......o~$~~~oo~~~$~o.....",
    ".......o~$~~~oo~~~$~o.....",
    ".......o~$~~~oo~~~$~o.....",
    ".......o~$~~~oo~~~$~o.....",
    ".......o~$~~~oo~~~$~o.....",
    ".......o~$~~~oo~~~$~o.....",
    "......o@@@@@@oo@@@@@@o....",
    "......oooooooooooooooo....",
])

UPPER_ARM = ['o===o']       # one row of upper arm, drawn under the sleeves when the syringe is lowered
ARM_COLS = (10, 28)         # canvas x of the far and near upper arm


def blank():
    return ['.' * CANVAS[0]] * CANVAS[1]


def compose(body=BODY, syringe_at=SYRINGE_AT, net=NET_BACK, net_at=NET_AT, net_in_front=False):
    """Back to front: net (when slung), body, extended upper arms if the syringe hangs low, syringe, net (when swung)."""
    rows = blank()
    if net is not None and not net_in_front:
        rows = overlay(rows, net, *net_at)
    rows = overlay(rows, body)
    for y in range(SYRINGE_AT[1] + 2, syringe_at[1] + 2):        # keep the arms attached to the shoulders
        for x in ARM_COLS:
            rows = overlay(rows, UPPER_ARM, x, y)
    rows = overlay(rows, SYRINGE, *syringe_at)
    if net is not None and net_in_front:
        rows = overlay(rows, net, *net_at)
    return rows


def with_legs(body, legs):
    out = [row if not (LEG_ROWS[0] <= y < LEG_ROWS[1]) else '.' * len(row) for y, row in enumerate(body)]
    return overlay(out, legs, LEGS_AT, LEG_ROWS[0])


def head_bob(body):
    """Head one pixel up; the chin row is duplicated so the neck stays attached."""
    return body[1:HEAD_ROWS] + [body[HEAD_ROWS - 1]] + body[HEAD_ROWS:]


def arm(dx, dy, body=BODY):
    """Base pose with the two-handed syringe moved by (dx, dy)."""
    return compose(body, (SYRINGE_AT[0] + dx, SYRINGE_AT[1] + dy))


def fall(rows, angle):
    """Rotate on a taller temporary canvas so nothing clips, drop to the floor, crop back to CANVAS."""
    extra = CANVAS[0] - CANVAS[1]
    tall = pad(rows, CANVAS[0], CANVAS[0], 0, extra)
    return settle(rotate_free(tall, angle))[extra:]


BASE = compose()
IDLE = [BASE, compose(head_bob(BODY)), BASE, arm(0, 1)]
MOVE = [compose(with_legs(BODY, LEGS_A)), compose(head_bob(with_legs(BODY, LEGS_A))), BASE,
        compose(with_legs(BODY, LEGS_B)), compose(head_bob(with_legs(BODY, LEGS_B))), BASE]
TELL = [arm(-1, 0), arm(-2, 0), arm(-3, 0)]                       # pump pulled back
FIRE = [arm(1, 0), shift(arm(1, 0), 1, 0), arm(-1, 0)]            # kicks forward, settles
LOW = (SYRINGE_AT[0] - 2, SYRINGE_AT[1] + 5)                      # syringe lowered to the hip for the net swing
NET = [compose(syringe_at=(SYRINGE_AT[0] - 1, SYRINGE_AT[1] + 2), net=NET_BACK, net_at=(1, 0)),
       compose(syringe_at=LOW, net=NET_FRONT, net_at=(26, 0), net_in_front=True),
       compose(syringe_at=LOW, net=NET_FRONT, net_at=(32, 6), net_in_front=True),
       compose(syringe_at=LOW, net=NET_FRONT, net_at=(33, 12), net_in_front=True)]
_slump = compose(syringe_at=(SYRINGE_AT[0] - 8, SYRINGE_AT[1] + 2), net_at=(3, 2))  # syringe and net pulled in: < 40 px wide so it fits when lying
_lying = fall(_slump, -90)
DIE = [arm(-2, 1), arm(-5, 2), fall(_slump, -25), fall(_slump, -50), fall(_slump, -75), _lying, _lying, _lying]

CLIPS = OrderedDict([('idle', IDLE), ('move', MOVE), ('tell', TELL), ('fire', FIRE), ('net', NET), ('die', DIE)])


def write(project):
    root = os.path.join(project, 'Resources', 'Enemies', 'nurse')
    paths = []
    for clip, frames in CLIPS.items():
        for i, f in enumerate(frames, 1):
            p = os.path.join(root, clip, 'nurse_%s_%03d.png' % (clip, i))
            save(strip_outline(f), p)     # the game adds the outline to actors at runtime
            paths.append(p)
    return paths


def preview(project):
    p = os.path.join(project, 'docs', 'preview', 'nurse-sheet.png')
    sheet([IDLE + TELL, MOVE, FIRE + NET, DIE], p, scale=4)
    return p
