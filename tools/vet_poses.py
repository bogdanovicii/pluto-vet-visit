"""The Vet (v0.12 redesign): hand-drawn parts on a 48x40 canvas, facing right, composed into the boss clips.

Enter the Gungeon boss language: a big head (15 of 39 rows) with a slicked quiff, round glasses with a white glint and
1-px dot eyes, a smug one-sided grin; a lab coat over teal scrubs with a stethoscope; chunky legs and shoes; an
oversized syringe pistol (plunger ring, finger flange, glass barrel of glowing vaccine, steel collar, needle).
Light from the top-left, 3-4 tones per material:
  hair % / # / @      skin 8 / = / - / ;      glass K / k, eyes g      coat W / 0 / ,
  scrubs < / $ / ~ / t      steel & / % / #      vaccine K / > / * / /      pen !, name tag :
Interior lines use the darkest tone of their material, never 'o'. No outline is drawn at all: the Vet is an AIActor and
the game draws his 1-px black outline at runtime (procedurallyOutlined); write() still runs strip_outline as a guard.
The left-facing versions are mirrored by the game (DirectionalAnimation FlipType.Flip), so only right-facing art exists.
Gemini references (reference/gemini/past_concepts/vet_sprite_*.png) were looked at for proportions and poses only.
"""
import importlib.util
import os
import subprocess
import tempfile
from collections import OrderedDict

from PIL import Image

from vetpixel import R, pad, shift, overlay, erase, rotate_free, settle, save, sheet, strip_outline, image, PALETTE  # noqa: F401
from pixel import outline_img  # preview only (vetpixel puts the main mod's tools/ on sys.path)

# Canvas size in pixels (w, h). Shared with nurse_poses.CANVAS (tests/test_nurse.py pins them equal), so it stays 48x40.
CANVAS = (48, 40)
# Hurtbox in canvas pixels from the LOWER-LEFT (x, y, w, h): the body column from the shoe soles (y 0) to the top of the
# quiff (canvas row 1, so h 39), from the back sleeve (x 7) to the coat's front edge (x 26, 94 % of the coat and arm
# pixels); the syringe pistol starts at the plunger ring, x 27, and is outside it.
HITBOX = (7, 0, 20, 39)
# Needle tip of the base pose in canvas pixels from the LOWER-LEFT (x, y): canvas column 45, row 19 from the top.
SHOOT_POINT = (45, 20)

W, H = CANVAS
EMPTY = ['.' * W] * H


def at(x, s):
    """One row: s starting at column x (hand-authored parts are written as at(column, pixels))."""
    return '.' * x + s


def part(lines, width=None):
    width = width or max(len(l) for l in lines)
    return R([l.ljust(width, '.') for l in lines])


def plate(lines, top):
    """Full-canvas rows: `lines` start at canvas row `top`, the rest transparent."""
    return R(['.' * W] * top + [l.ljust(W, '.') for l in lines] + ['.' * W] * (H - top - len(lines)))


# ------------------------------------------------------------------ head (18x15, placed at HEAD_AT)
HEAD_AT = (11, 1)
HEAD = part([
    "....@@@@@@@@......",     # 0
    "..@@%%%%%%@@@@....",     # 1
    ".@%%%%####@@@@@@..",     # 2
    ".@%###@@@@@@@@%%@.",     # 3 quiff tip catches the light
    "@%##@@@@@@@@@@@@@@",     # 4 quiff overhangs the brow
    "@##@@@@@@@@@@@@@@.",     # 5
    "@#@@@@@=888888=@@.",     # 6 hairline
    "@@@@@=88888888888.",     # 7 forehead
    "@@@-==##==##=====.",     # 8 lens tops
    "@@;-=#kK##kK#===8.",     # 9 glint
    "@@;-=#gk##gk#==88.",     # 10 dot eyes, nose tip
    ".@;-==##==##=;;=..",     # 11 lens bottoms, grin corner curls up
    ".@;--=;WWWWW;=....",     # 12 one-sided grin
    "..;--=;;;;;;=.....",     # 13 lip, chin
    ".....;;;----;.....",     # 14 neck
])


def head_variant(rows):
    """HEAD with some rows replaced: {row: pixels}."""
    out = list(HEAD)
    for y, s in rows.items():
        out[y] = s
    return part(out, 18)


HEAD_GLINT = head_variant({9: "@@;-=#KK##KK#===8.", 10: "@@;-=#KK##KK#==88."})           # glasses flash white
HEAD_SMUG = head_variant({9: "@@;-=#KK##KK#===8.", 10: "@@;-=#KK##KK#==88.",
                          11: ".@;-==##==##;;;=..", 12: ".@;--;WWWWWW;=....", 13: "..;--=;;;;;;;.....",})  # bigger grin
HEAD_OUCH = head_variant({9: "@@;-=#kk##kk#===8.", 10: "@@;-=#;;##;;#==88.",
                          11: ".@;-==##==##====..", 12: ".@;--===;@;==....", 13: "..;--==;;;;=......"})  # squint, gasp
HEAD_KO = head_variant({9: "@@;-=#kk##kk#===8.", 10: "@@;-=#--##--#==88.",
                        11: ".@;-==##==##====..", 12: ".@;--==;@@;==.....", 13: "..;--==;;;;=......"})  # eyes shut, mouth open

# ------------------------------------------------------------------ body: coat, scrubs, stethoscope (full canvas rows)
#            0         1         2         3         4
#            012345678901234567890123456789012345678901234567
BODY = plate([
    "..........WWWWW@;$$$$$@W00",                 # 16 collar, stethoscope tubes
    ".........WWWWWW0@<$$$$@0WW0",                # 17
    "........WWWWWWW0<@$$$@$0WWW0",               # 18
    "........WWW!WWW0<$@$@$$0WW00",               # 19 pen
    "........WWW!WWW0<$$@$$$0WW00",               # 20
    "........W,,,,,W0<$$@$$$0WW00",               # 21 pocket
    "........WWWWWWW0<$$&$$$0WW00",               # 22 chest piece
    "........WWWWWW00<$&%#$$0WW00",               # 23
    "........WWWWWW00<$$#$$$0WW00",               # 24
    "........WWWWW000<$$$$$~0W000",               # 25
    ".......WWWWWW00,<$$$$$~0W000,",              # 26
    ".......WWWWW000,<$$$$$~00000,",              # 27
    ".......WWWWW000,<$$$$$~00000,",              # 28
    ".......WWWW0000,<$$$$$~0000,,",              # 29
    ".......WWW00000,<$$$$$~0000,,",              # 30
    "........,,,,,,,,<$$$$$~,,,,,",               # 31 hem
], 16)

BACK_AT = (6, 18)
BACK_ARM = part([             # far sleeve down the left side (a coat-shade seam where it meets the coat), hand at the hip
    "..W,", ".WW,", ".WW,", ".WW,", ".WW,", ".W0,", ".W0,", ".W0,", ".00,",
    ".=8,", ".==-", "..;;",
])

# ------------------------------------------------------------------ syringe pistol held level (23x9 at GUN_AT)
GUN_AT = (23, 16)
NEEDLE_TIP = (22, 3)          # local; GUN_AT + NEEDLE_TIP = canvas (45, 19) = SHOOT_POINT from the lower-left
GUN = part([
    "WW0.....%..............",   # 0 sleeve, finger flange top
    "WWW0.%%.%&&&&&&&&&.....",   # 1 plunger ring, barrel rim
    "0WW0%#%&%kKK>>>>>&%....",   # 2 ring, rod, glass glint, vaccine glow, collar
    "0000%%%&%k>>>>>>*%&&&&K",   # 3 needle, tip K
    "..0WW0..%k*****//%.....",   # 4 vaccine settles darker at the bottom
    "...0WW0.%%%%%%%%#......",   # 5 barrel underside
    "....0W=88=@#@..........",   # 6 hand on the grip
    ".....;=8==@#@..........",   # 7
    "......;--;@@@..........",   # 8
], 23)

# raised straight up beside the head for the wind-up and the intro flourish (canvas rows, so it can reach row 1)
GUN_UP = plate([
    at(34, "K"),                  # 1 needle tip
    at(34, "&"),                  # 2
    at(34, "&"),                  # 3
    at(33, "%&%"),                # 4 collar
    at(32, "&&&&%"),              # 5 barrel rim
    at(32, "&kK>%"),              # 6
    at(32, "&k>>%"),              # 7
    at(32, "&k>>%"),              # 8
    at(30, "=8=k>*%"),            # 9 hand around the barrel
    at(29, "=88=k**%"),           # 10
    at(29, ";=8=k*/%"),           # 11
    at(30, ";-%%%%%#"),           # 12 finger flange
    at(28, "0WW...&"),            # 13 sleeve, plunger rod
    at(27, "0WW0..%#%"),          # 14 plunger ring
    at(26, "WWW0..%%%"),          # 15
    at(23, "WWW0"),               # 16 shoulder
    at(23, "WW0"),                # 17
], 1)

EMPTY_HAND = part([           # gun dropped: the near arm hangs empty
    "WW0..", "WWW0.", "0WW0.", "00W0.", ".0WW0", ".00W0", "..=8=", "..==-", "..;;.",
])

FLASH_BIG = part([           # star centred just ahead of the needle tip: white core, glow, blue rim so it reads on white tiles
    "...*...",
    "..*>*..",
    ".*>K>*.",
    "*>KKK>*",
    ".*>K>*.",
    "..*>*..",
    "...*...",
])
FLASH_SMALL = part(["..*..", ".*>*.", "*>K>*", ".*>*.", "..*.."])
DROP = part([">", "*"])                                               # vaccine drop squirted in the intro

SYRINGE_FLOOR = part([        # the dropped syringe pistol lying on the floor, 17x4
    ".%%.%&&&&&&&%....",
    "%#%&%k>>>>>*%&&&K",
    ".%%.%%%%%%%%#....",
    "........@#@......",
])

# ------------------------------------------------------------------ legs (full canvas rows; feet on row 39)
LEGS_STAND = plate([
    "............t$$~~.~$$~~t",                   # 32
    "............t$$~~.~$$~~t",                   # 33
    "............t$~~~.~$~~~t",                   # 34
    "............t$~~~.~$~~~t",                   # 35
    "............t~~~t.t~~~tt",                   # 36
    "...........@@@@@@.@@@@@@@",                  # 37 shoes
    "...........@@#%@@.@@#%@@@@",                 # 38
    "...........@@@@@@.@@@@@@@@",                 # 39
], 32)
LEGS_WIDE = plate([                               # braced stance for the tell and fire
    "............t$$~~.~$$~~t",
    "...........t$$~~...~$$~~t",
    "...........t$~~~...~$~~~t",
    "..........t$~~~.....~$~~t",
    "..........t~~~t.....t~~~tt",
    ".........@@@@@@.....@@@@@@@",
    ".........@@#%@@.....@@#%@@@@",
    ".........@@@@@@.....@@@@@@@@",
], 32)
LEGS_STRIDE_R = plate([                           # near (right) leg forward
    "............t~~~~.~$$~~t",
    "............t~~~~..~$$~~t",
    "...........t~~~t...~$$~~t",
    "...........t~~~t....~$~~~t",
    "..........t~~~t......~$~~t",
    ".........@@@@@@.......@@@@@@",
    ".........@@#%@@.......@@#%@@@",
    ".........@@@@@@.......@@@@@@@",
], 32)
LEGS_STRIDE_L = plate([                           # far (left) leg forward, near leg trailing
    "............t$$~~.~~~~t",
    "............t$$~~..t~~~t",
    "...........t$$~~....t~~~t",
    "...........t$~~t.....t~~~t",
    "..........t$~~t.......t~~t",
    ".........@@@@@@.......@@@@@@",
    ".........@@#%@@.......@@#%@@@",
    ".........@@@@@@.......@@@@@@@",
], 32)
LEGS_PASS_R = plate([                             # body up one row, near leg lifted
    ".............t~~~$$~~t",                     # 31
    ".............t~~~$$~~t",
    ".............t~~t$$~~t",
    ".............t~~t$$~~t",
    ".............t~~tt$$~t",
    ".............t~~t.@@@@@@",
    ".............t~~t.@@#%@@@",
    "............@@@@@@.......",
    "............@@#%@@@......",
], 31)
LEGS_PASS_L = plate([                             # body up one row, far leg lifted
    ".............t$$~~~~~t",
    ".............t$$~~~~~t",
    ".............t$$~t~~~t",
    ".............t$$~t~~~t",
    ".............t$$~~t~~t",
    "...........@@@@@@t~~t",
    "...........@@#%@@t~~t",
    "................@@@@@@@",
    "................@@#%@@@@",
], 31)
LEGS_KNEEL = plate([                              # body down five rows: far shin on the floor, near knee up
    "...........t$$~~~~$$$~~t",                   # 36
    "........@@@t~~~~~.t$$~~t",                   # 37
    "........@#%@t~~~t..t~~~t",                   # 38
    "........@@@@@@@@...@@@@@@@",                 # 39
], 36)


# ------------------------------------------------------------------ composition
# 0.14.0 masked last phase (design from the Gemini sheets in reference/gemini/vet_mask_*): white surgical gloves on every hand
# and a pale blue surgical mask over the grin. 0 = none, 1 = gloves, 2 = gloves + mask pulled half up, 3 = gloves + full mask.
_MASK_LEVEL = 0
_SKIN = '=8-;'


def gloved(rows):
    """Skin on a hand part becomes a white glove ('W' light, '0' shade)."""
    return [r.replace('=', 'W').replace('8', 'W').replace('-', '0').replace(';', '0') for r in rows]


def masked_head(head, level):
    """The face below the glasses becomes a surgical mask: '>' pale blue, '*' fold shade on the right edge, lenses kept."""
    rows = [list(r) for r in head]
    first = 11 if level >= 3 else 12
    for y in range(first, 14):
        xs = [x for x in range(3, 15) if rows[y][x] in _SKIN + 'W@']
        for x in xs:
            rows[y][x] = '>'
        if xs:
            rows[y][max(xs)] = '*'
    return [''.join(r) for r in rows]


def compose(head=HEAD, gun=GUN, legs=LEGS_STAND, body=(0, 0), head_off=(0, 0), gun_off=(0, 0), extras=()):
    """Legs, then coat + back arm moved by body, head moved by body + head_off, then the gun (GUN at GUN_AT + body +
    gun_off, GUN_UP / plates moved by body + gun_off, EMPTY_HAND at GUN_AT). extras: (part, x, y) on top.
    With _MASK_LEVEL > 0 the hands are gloved and (level >= 2) the head wears the surgical mask."""
    bx, by = body
    lvl = _MASK_LEVEL
    f = legs
    f = overlay(f, shift(BODY, bx, by))
    f = overlay(f, gloved(BACK_ARM) if lvl else BACK_ARM, BACK_AT[0] + bx, BACK_AT[1] + by)
    f = overlay(f, masked_head(head, lvl) if lvl >= 2 else head, HEAD_AT[0] + bx + head_off[0], HEAD_AT[1] + by + head_off[1])
    if gun is GUN or gun is EMPTY_HAND:
        f = overlay(f, gloved(gun) if lvl else gun, GUN_AT[0] + bx + gun_off[0], GUN_AT[1] + by + gun_off[1])
    elif gun is not None:
        f = overlay(f, shift(gloved(gun) if lvl else gun, bx + gun_off[0], by + gun_off[1]))
    for piece, x, y in extras:
        f = overlay(f, piece, x, y)
    return R(f)


def tip(gun_off=(0, 0), body=(0, 0)):
    return (GUN_AT[0] + NEEDLE_TIP[0] + gun_off[0] + body[0], GUN_AT[1] + NEEDLE_TIP[1] + gun_off[1] + body[1])


def flash(piece, gun_off, ahead=1, body=(0, 0)):
    x, y = tip(gun_off, body)
    n = len(piece)
    return (piece, x + ahead - n // 2, y - n // 2)


BASE = compose()
POSE = BASE                   # kept for tools/concept_v2.py and tests/test_palette.py


def rotate_lying(rows, angle):
    """Rotate on a square temporary canvas (nothing clips), drop to the floor, crop back to CANVAS."""
    extra = W - H
    tall = pad(rows, W, W, 0, extra)
    return settle(rotate_free(tall, angle))[extra:]


def centre_x(rows, left=2):
    xs = [x for row in rows for x, ch in enumerate(row) if ch != '.']
    return shift(rows, left - min(xs), 0)


def _clips():
    """Every clip, composed at the current _MASK_LEVEL."""
    # idle, 6 fps loop: breathe (head sinks into the collar, the gun hand follows a beat later), glasses glint to close
    IDLE = [
        compose(),
        compose(head_off=(0, 1)),
        compose(head_off=(0, 1), gun_off=(0, 1)),
        compose(gun_off=(0, 1)),
        compose(head=HEAD_GLINT),
    ]

    # move, 8 fps loop: contact, pass (up a row, gun hand lags down), contact, pass
    MOVE = [                      # on the pass the coat rises a row while the head stays put (sinks into the collar)
        compose(legs=LEGS_STRIDE_R),
        compose(legs=LEGS_PASS_R, body=(0, -1), head_off=(0, 1), gun_off=(0, 1)),
        compose(legs=LEGS_PASS_R, body=(0, -1), head_off=(0, 1)),
        compose(legs=LEGS_STRIDE_L),
        compose(legs=LEGS_PASS_L, body=(0, -1), head_off=(0, 1), gun_off=(0, 1)),
        compose(legs=LEGS_PASS_L, body=(0, -1), head_off=(0, 1)),
    ]

    # tell, 8 fps once: crouch and pull the gun back, whip it up beside the grinning head, lean back with a glint, snap level
    TELL = [
        compose(legs=LEGS_WIDE, body=(0, 2), gun_off=(-3, 1)),          # deep crouch, gun pulled back: the anticipation
        compose(head=HEAD_GLINT, legs=LEGS_WIDE, gun=GUN_UP, body=(-1, 0)),
        compose(head=HEAD_SMUG, legs=LEGS_WIDE, gun=GUN_UP, body=(-2, 0), head_off=(-1, 0)),
        compose(head=HEAD_SMUG, legs=LEGS_WIDE, body=(1, 0)),           # snap forward (needle tip x 46, one column spare)
    ]

    # fire, 12 fps once: recoil back with a big flash on the needle, a smaller flash, settle
    FIRE = [
        compose(head=HEAD_SMUG, legs=LEGS_WIDE, gun_off=(-3, 0), body=(-1, 0), head_off=(-1, 0),
                extras=[flash(FLASH_BIG, (-3, 0), 2, (-1, 0))]),
        compose(head=HEAD_SMUG, legs=LEGS_WIDE, gun_off=(-2, 0), body=(-1, 0), extras=[flash(FLASH_SMALL, (-2, 0), 1, (-1, 0))]),
        compose(legs=LEGS_WIDE, gun_off=(-1, 0)),
        compose(legs=LEGS_WIDE),
    ]

    # intro, 8 fps once: raise the syringe, flick a drop of vaccine off the needle, glint, grin, level it at the player
    INTRO = [
        compose(),
        compose(body=(0, 1), gun_off=(-2, 1)),
        compose(gun=GUN_UP),
        compose(gun=GUN_UP, head=HEAD_GLINT, extras=[(DROP, 36, 1)]),
        compose(gun=GUN_UP, head=HEAD_SMUG, extras=[(DROP, 38, 2)]),
        compose(gun=GUN_UP, head=HEAD_SMUG, extras=[(DROP, 40, 4)]),
        compose(head=HEAD_SMUG, gun_off=(1, 0)),
        compose(head=HEAD_GLINT),
    ]

    # die, 8 fps once: hit, drop the gun, kneel, topple backwards, flat on his back
    _floor_gun = (SYRINGE_FLOOR, 29, 36)
    _kneel = compose(head=HEAD_OUCH, gun=EMPTY_HAND, legs=LEGS_KNEEL, body=(0, 5))
    _lying = centre_x(rotate_lying(compose(head=HEAD_KO, gun=EMPTY_HAND, legs=LEGS_STAND), 90))
    DIE = [
        compose(head=HEAD_OUCH, body=(-1, 0), gun_off=(0, -1)),
        compose(head=HEAD_OUCH, gun=EMPTY_HAND, body=(-2, 0), extras=[_floor_gun]),
        overlay(_kneel, SYRINGE_FLOOR, *_floor_gun[1:]),
        overlay(overlay(EMPTY, SYRINGE_FLOOR, *_floor_gun[1:]), rotate_lying(_kneel, 35)),
        overlay(overlay(EMPTY, SYRINGE_FLOOR, 30, 36), centre_x(rotate_lying(_kneel, 65))),   # keep the head off column 0
        overlay(_lying, SYRINGE_FLOOR, 29, 36),       # the dropped syringe rocks 29 / 30 (x 30 puts its tip on column 46)
        overlay(_lying, SYRINGE_FLOOR, 30, 36),
        overlay(_lying, SYRINGE_FLOOR, 30, 36),
    ]
    DIE[-1] = overlay(DIE[-1], DROP, 47 - 1, 38)   # a last drop leaks out of the needle on the hold frame
    return OrderedDict([('idle', IDLE), ('move', MOVE), ('tell', TELL), ('fire', FIRE), ('intro', INTRO), ('die', DIE)])

CLIPS = _clips()
IDLE, MOVE, TELL, FIRE, INTRO, DIE = (CLIPS[k] for k in ('idle', 'move', 'tell', 'fire', 'intro', 'die'))


def _at_level(level, fn):
    global _MASK_LEVEL
    _MASK_LEVEL = level
    try:
        return fn()
    finally:
        _MASK_LEVEL = 0


def _mask_clips():
    masked = _at_level(3, _clips)
    mask_on = [compose(),                                                    # bare hands, bare face
               _at_level(1, lambda: compose(gun_off=(0, 1))),                 # gloves snapped on
               _at_level(2, lambda: compose(head_off=(0, 1))),                # mask pulled half up
               _at_level(3, lambda: compose(head_off=(0, 1))),                # mask up
               _at_level(3, lambda: compose(head=HEAD_GLINT))]                # ready, glasses glint
    return OrderedDict([('mask_on', mask_on), ('mask_idle', masked['idle']), ('mask_move', masked['move']),
                        ('mask_tell', masked['tell']), ('mask_fire', masked['fire']), ('mask_die', masked['die'])])


MASK_CLIPS = _mask_clips()


def write_mask_art(project):
    """The masked clips as approved art sources (reference/art/vet_<clip>/final_NNN.png), installed by art_sources."""
    import os
    paths = []
    for clip, frames in MASK_CLIPS.items():
        for i, f in enumerate(frames, 1):
            p = os.path.join(project, 'reference', 'art', 'vet_' + clip, 'final_%03d.png' % i)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            save(f, p)
            paths.append(p)
    return paths

# ------------------------------------------------------------------ legacy parts (the Owner NPC in npc_poses.py reuses them)
DX = 8
LEG_ROWS = (32, 40)
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


def with_legs(base, legs):
    body = [row if not (LEG_ROWS[0] <= y < LEG_ROWS[1]) else '.' * len(row) for y, row in enumerate(base)]
    return overlay(body, legs, DX, LEG_ROWS[0])


# ------------------------------------------------------------------ output
def write(project):
    root = os.path.join(project, 'Resources', 'Boss', 'vet')
    paths = []
    for clip, frames in CLIPS.items():
        d = os.path.join(root, clip)
        names = set()
        for i, f in enumerate(frames, 1):
            p = os.path.join(d, 'vet_%s_%03d.png' % (clip, i))
            save(strip_outline(f), p)     # the game adds the outline to actors at runtime
            paths.append(p)
            names.add(os.path.basename(p))
        for stale in sorted(os.listdir(d)):
            if stale.startswith('vet_%s_' % clip) and stale.endswith('.png') and stale not in names:
                os.remove(os.path.join(d, stale))
    return paths


FLOOR = (214, 220, 228, 255)  # operating-theatre tile tone, so the runtime outline reads like in game


def outlined_sheet(rows_of_frames, path, scale=4, gap=4, bg=FLOOR, labels=None):
    """Contact sheet with the runtime outline simulated (1-px black around every frame's silhouette)."""
    ims = [[outline_img(image(strip_outline(f))) for f in row] for row in rows_of_frames]
    cw = max(i.width for row in ims for i in row) * scale
    ch = max(i.height for row in ims for i in row) * scale
    cols = max(len(row) for row in ims)
    out = Image.new('RGBA', ((cw + gap) * cols + gap, (ch + gap) * len(ims) + gap), bg)
    for r, row in enumerate(ims):
        for c, im in enumerate(row):
            big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
            out.paste(big, (gap + c * (cw + gap), gap + r * (ch + gap)), big)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out.save(path)
    return out


def old_clips(project):
    """The committed (git HEAD) vet_poses.CLIPS, imported from a temporary copy; None when git is unavailable."""
    try:
        src = subprocess.run(['git', 'show', 'HEAD:tools/vet_poses.py'], cwd=project, capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'vet_poses_head.py')
        with open(p, 'w') as fh:
            fh.write(src)
        spec = importlib.util.spec_from_file_location('vet_poses_head', p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    return mod.CLIPS


def preview(project):
    p = os.path.join(project, 'docs', 'preview', 'vet-sheet.png')
    outlined_sheet(list(CLIPS.values()), p, scale=4)
    old = old_clips(project)
    if old is not None:
        rows = []
        for clip in CLIPS:
            rows.append(old.get(clip, []) or [EMPTY])
            rows.append(CLIPS[clip])
        outlined_sheet(rows, os.path.join(project, 'docs', 'preview', 'vet-old-vs-new.png'), scale=4)
    return p
