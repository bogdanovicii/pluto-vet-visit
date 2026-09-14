"""The four clinic NPCs: the owner, the receptionist, Rex the nervous dog and Grandma the ancient cat.

NPCs are not AIActors, so unlike the Vet they ship WITH their 1-px 'o' outline. Every frame of one
character shares one canvas, feet on the bottom row, only vetpixel PALETTE keys. Row-strings below use
'c' as a placeholder for '\\' (wood/brown) so the art stays readable; rows() swaps it in.
"""
import os
from collections import OrderedDict

import vet_poses as VP
from vetpixel import R, pad, shift, overlay, erase, save, sheet, lowest_opaque_row

_C = str.maketrans({'c': '\\'})


def rows(art, width):
    """Right-pad readable row-strings to width and swap the 'c' placeholder for the '\\' key."""
    return R([r.ljust(width, '.').translate(_C) for r in art])


def recolor(art, mapping):
    return [r.translate(str.maketrans(mapping)) for r in art]


def head_bob(frame, chin):
    """Rows 1..chin one pixel up; the chin row is duplicated so the neck stays attached."""
    return frame[1:chin + 1] + [frame[chin]] + frame[chin + 1:]


# ================================================================== owner 48x40, facing right
# The Vet's pose pipeline recoloured: grey hoodie (% base, # shade, hood down behind the neck), blue jeans,
# white sneakers, brown hair, tired face, no syringe. 36-wide pose at DX=8 like the Vet.
OWNER_CANVAS = (48, 40)
OWNER_POSE = rows([
    "",
    "............oooooo",
    "...........occcccco",
    "..........occcccccco",
    "..........occ+ccccco",
    "..........occc=====o",
    "..........oc========o",
    "..........o==+==+==o",
    "..........o=Kg=Kg==o",
    "..........o=-==-===o",
    "..........o===-=-==o",
    "...........o==oo==o",
    ".........ooo.oooooo",
    "........o###o%%%%%%oo",
    "........o###%%%%W%%%%o",
    "........o##%%%%W%W%%%%o",
    "........o#%%%%%%%%%#%%o",
    "........o#%%%%%W%W%#%%o",
    "........o#%%%%%%%%%#%%o",
    "........o#%%%%%%%%%#%%o",
    "........o#%%%%%%%%%#%%o",
    "........o#%%%%%%%%%#%%o",
    "........o#%%%%%%%%%#%%o",
    "........o#%%%%%%%%%#%%o",
    "........o#%oooooo%%#%%o",
    "........o#%o%%%%o%%#%%o",
    "........o#%o%%%%o%%#%%o",
    "........o#%oooooo%%o==o",
    "........o#%%%%%%%%%o==o",
    "........o##%%%%%%%%%##o",
    "........o#############o",
    ".........oooooooooooooo",
    "..........o|||o.o|||o",
    "..........o|||o.o|||o",
    "..........o|||o.o|||o",
    "..........o|||o.o|||o",
    "..........o|||o.o|||o",
    "..........o///o.o///o",
    ".........oWwwWo.oWwwWo",
    ".........oooooo.oooooo",
], 36)
_JEANS = {'~': '|', '$': '|', '@': 'W'}


def _jeans(legs):
    out = recolor(legs, _JEANS)
    out[5] = out[5].replace('|', '/')              # dark cuff row above the sneakers
    return out


OWNER_LEGS_A, OWNER_LEGS_B = _jeans(VP.LEGS_A), _jeans(VP.LEGS_B)
OWNER_BASE = pad(OWNER_POSE, OWNER_CANVAS[0], OWNER_CANVAS[1], VP.DX, 0)

# blue plastic cat carrier 14x10, barred door on the right, handle held at knee height
CARRIER = rows([
    ".....oooo",
    "....oo..oo",
    ".oooooooooooo",
    "o////////////o",
    "o||||||||o_o_o",
    "o||oo||||o_o_o",
    "o||||||||o_o_o",
    "o||oo||||o_o_o",
    "o////////ooooo",
    ".oooooooooooo",
], 14)
CARRIER_AT = (VP.DX + 15, 29)


def _owner_bob(f):
    return head_bob(f, 11)


def _owner_walk(carrier):
    a = VP.with_legs(OWNER_BASE, OWNER_LEGS_A)
    b = VP.with_legs(OWNER_BASE, OWNER_LEGS_B)
    frames = [a, _owner_bob(a), OWNER_BASE, b, _owner_bob(b), OWNER_BASE]
    if carrier:
        frames = [overlay(f, CARRIER, *CARRIER_AT) for f in frames]
    return frames


CLIPS_OWNER = OrderedDict([
    ('idle', [OWNER_BASE, _owner_bob(OWNER_BASE)]),
    ('walk', _owner_walk(True)),
    ('walk_free', _owner_walk(False)),
])

# ================================================================== receptionist 32x40, side pose facing right
# Headset (# band over dark hair, ear cup, mic to the mouth), beige cardigan (light wood tone) over a teal shirt
# with a white collar. Whole figure drawn; only the upper body shows behind the desk.
REC_CANVAS = (32, 40)
REC_POSE = rows([
    "",
    "...........oooooooo",
    "..........o@@@@@@@@o",
    ".........o@@@@@@@@@@o",
    ".........o##########o",
    ".........o@@@@@=====o",
    ".........o@@@@======o",
    ".........o@@@##=@==@o",
    ".........o@@@##Kg=Kgo",
    ".........o@@@@#=====o",
    ".........o@@@@=#=-==o",
    "..........o@@@=#=oo=o",
    "...........oo@@oooo",
    "...........ooccccccoo",
    "..........occcW$$Wccco",
    ".........occccW$$Wcccco",
    ".........occcc+$$+cc#cco",
    ".........occcc+$$+cc#cco",
    ".........occcc+$$+cc#cco",
    ".........occcc+$$+cc#cco",
    ".........occcc+$$+cc#cco",
    ".........occcc+$$+cc#cco",
    ".........occcc+$$+cc#cco",
    ".........occcc+$$+cc#cco",
    ".........occcc+$$+cc#cco",
    ".........occcc+$$+cc#cco",
    ".........occcc+$$+cc#cco",
    ".........occcc+$$+cco==o",
    ".........occcc+$$+cco==o",
    ".........occcc+$$+ccccco",
    ".........oo+++++++++++oo",
    ".........o#############o",
    "..........ooooooooooooo",
    "...........o###o.o###o",
    "...........o###o.o###o",
    "...........o###o.o###o",
    "...........o###o.o###o",
    "...........o###o.o###o",
    "..........o@@@@o.o@@@@o",
    "..........oooooo.oooooo",
], 32)
REC_BASE = R(REC_POSE)
# raised near arm: forearm up beside the chest, open hand at shoulder height (waving / explaining)
_REC_ARM_DOWN = ['.' * 32] * 40
_REC_ARM_DOWN = overlay(_REC_ARM_DOWN, rows(['#cc'] * 12 + ['o=='] * 2, 3), 20, 15)
REC_ARM_UP = rows([
    "....oooo",
    "...o====o",
    "...o====o",
    "....occo",
    "....occo",
    "....occo",
    "....occo",
    "...occco",
    "#cccccco",
    "#cccccco",
    "#cccooo",
    "#cco",
], 9)


def _rec_arm_up(f):
    """Near arm bent up: forearm in front of the shoulder, open hand raised beside the face."""
    cleared = erase(f, _REC_ARM_DOWN)
    cleared = overlay(cleared, rows(['ccco'] * 14, 4), 20, 15)   # cardigan side where the arm hung
    return overlay(cleared, REC_ARM_UP, 20, 8)


def _rec_mouth_open(f):
    g = [list(r) for r in f]
    g[11][17], g[11][18] = 'o', 'o'
    g[10][17], g[10][18] = 'o', 'o'
    g[11][16] = '-'
    return [''.join(r) for r in g]


CLIPS_REC = OrderedDict([
    ('idle', [REC_BASE, head_bob(REC_BASE, 9)]),
    ('talk', [_rec_mouth_open(_rec_arm_up(REC_BASE)), _rec_arm_up(head_bob(REC_BASE, 9))]),
])

# ================================================================== rex 24x24: nervous brown dog, sitting
REX_CANVAS = (24, 24)
REX_POSE = rows([
    "",
    "........oooooooo",
    ".......occcccccco",
    "...o+++cccccccccc+++o",
    "...o+++cc+cccc+cc+++o",
    "...o+++c+cccccc+c+++o",
    "...o+++cKKccccKKc+++o",
    "...o+++cgKccccKgc+++o",
    "...oooocccWWWWcccoooo",
    "......occWWooWWcco",
    "......occWoWWoWcco",
    ".......occW==Wcco",
    "........occccccco",
    ".......occccccccco",
    "......o+cccWWccc+o",
    ".....o+ccccWWcccc+o",
    ".....o+ccccWWcccc+o",
    ".....o+cccccccccc+o",
    ".....o+cc+cccc+cc+o",
    ".....o+cc+cccc+cc+o",
    ".....occcoccccocccco",
    "....occccoooooocccco",
    "....oooooo....oooooo",
], 24)
REX_BASE = pad(REX_POSE, REX_CANVAS[0], REX_CANVAS[1], 0, 1)
_TICKS_L = ['o', '.', 'o']
_TICKS_R = ['o', '.', 'o']
REX_TREMBLE = [
    overlay(overlay(shift(REX_BASE, -1, 0), _TICKS_L, 1, 13), _TICKS_R, 21, 13),
    overlay(overlay(shift(REX_BASE, 1, 0), _TICKS_L, 2, 12), _TICKS_R, 22, 12),
]
CLIPS_REX = OrderedDict([('idle', REX_TREMBLE)])

# ================================================================== grandma 24x24: ancient grey cat in a loaf
# Pluto's loaf (main mod poses_extra.loaf) remapped to vetpixel keys: grey base, dark stripes, white chin and
# chest, half-closed unimpressed eyes. The main palette has keys vetpixel lacks, hence the translation dict.
GRANDMA_CANVAS = (24, 24)
_PLUTO_TO_GREY = {'B': 'Z', 'b': '#', 'd': '#', 'P': '%', 'p': '#', 'G': 'g', '9': 'o', 'L': 'Z', 'x': 'w', 'q': '%'}


def _grandma(head_dy):
    import poses_extra as PX  # main mod, read-only (on sys.path via vetpixel)
    import poses as PP
    art = PX.loaf(head_dy)
    unknown = {ch for r in art for ch in r} - set(_PLUTO_TO_GREY) - {'.', 'o', 'W', 'w', 'g'}
    assert not unknown, unknown
    art = recolor(art, _PLUTO_TO_GREY)
    g = [list(r) for r in art]
    for (x, y) in PP.EYES_SIDE:                    # half-closed: dark lid over a 2-px slit
        g[y + head_dy][x], g[y + head_dy][x + 1] = '#', '#'
        g[y + head_dy + 1][x], g[y + head_dy + 1][x + 1] = 'g', 'g'
    for y in (5, 6):                               # no white head spot on a grey cat
        for x in (9, 10, 11):
            g[y + head_dy][x] = 'Z'
    g[8 + head_dy][10] = g[8 + head_dy][11] = 'Z'  # no blaze
    g[11 + head_dy][11] = 'W'                      # wispy white chin instead of the mouth dot
    g[11 + head_dy][12] = 'w'
    art = [''.join(r) for r in g]
    return pad(art, GRANDMA_CANVAS[0], GRANDMA_CANVAS[1], 3, 2)


CLIPS_GRANDMA = OrderedDict([('loaf', [_grandma(6), _grandma(7)])])

NPCS = OrderedDict([
    ('owner', {'canvas': OWNER_CANVAS, 'clips': CLIPS_OWNER}),
    ('receptionist', {'canvas': REC_CANVAS, 'clips': CLIPS_REC}),
    ('rex', {'canvas': REX_CANVAS, 'clips': CLIPS_REX}),
    ('grandma', {'canvas': GRANDMA_CANVAS, 'clips': CLIPS_GRANDMA}),
])


def write(project):
    paths = []
    for who, spec in NPCS.items():
        for clip, frames in spec['clips'].items():
            for i, f in enumerate(frames, 1):
                p = os.path.join(project, 'Resources', 'Npcs', who, clip, '%s_%s_%03d.png' % (who, clip, i))
                save(f, p)                        # NPCs keep their outline (not AIActors)
                paths.append(p)
    return paths


def preview(project):
    p = os.path.join(project, 'docs', 'preview', 'npc-sheet.png')
    lines = []
    for who, spec in NPCS.items():
        for clip, frames in spec['clips'].items():
            lines.append(frames)
    sheet(lines, p, scale=4)
    return p
