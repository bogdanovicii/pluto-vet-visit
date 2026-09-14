"""The clinic NPCs: Pluto's owners Bogdan and Bianca, the receptionist, Rex the nervous dog and Grandma the ancient cat.

NPCs are not AIActors, so unlike the Vet they ship WITH their 1-px 'o' outline. Every frame of one
character shares one canvas, feet on the bottom row, only vetpixel PALETTE keys. Row-strings below use
'c' as a placeholder for '\\' (wood/brown) so the art stays readable; rows() swaps it in.
"""
import os
from collections import OrderedDict

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


# ================================================================== the owners 48x40, facing right: Bogdan and Bianca
# Pluto's people. Both share the old Owner's canvas and scale (figure in columns 14..31, feet on the bottom row, head bob on the
# idle), so they stand as tall as the Vet and the Receptionist. Placeholders in the rows below: N / D / L are the navy hoodie's
# mid / shade / light tone (vetpixel 'O', '"', "'" - quote characters are unreadable inside row strings); owner_rows() swaps them.
OWNER_CANVAS = (48, 40)
_NAVY = str.maketrans({'N': 'O', 'D': '"', 'L': "'"})


def owner_rows(art):
    return R([r.ljust(OWNER_CANVAS[0], '.').translate(_NAVY) for r in art])


def mirror(frame):
    """Faces the figure the other way inside the same canvas (the figure is centred, so it keeps its columns)."""
    return [r[::-1] for r in frame]


def swap_legs(frame, top, split, left, right):
    """The other stride of a walk: the left leg takes the near leg's tones and the right leg the far leg's (rows >= top)."""
    out = list(frame)
    for y in range(top, len(out)):
        r = out[y]
        out[y] = r[:split].translate(str.maketrans(left)) + r[split:].translate(str.maketrans(right))
    return out


# ------------------------------------------------------------------ Bogdan: short dark brown hair, light stubble, navy hoodie, jeans
BOGDAN_TOP = owner_rows([
    "",
    "....................ooooooo",
    "...................oXmmmXXXo",
    "..................oXmmXXXXXXo",
    ".................oXXXXXXXXXXXo",
    ".................oX@XXXXX@X@Xo",
    ".................o@X@========o",
    ".................o@X-=@@=@@==o",
    ".................o@X-=Kg=Kg==o",
    ".................o@=-======-=o",
    ".................o@-=====;;==o",
    "..................o-=-=-=-=-o",
    "...............ooDDDo-=-oNNoo",
    "..............oDDDDDoooooLLNNo",
    "..............oDLLNNLLLLLLNNNo",
    "..............oDLNNNWNNNWNDNNLo",
    "..............oDNNNNWNNNWNDNNNo",
    "..............oDNNNNNNNNNNDNNNo",
    "..............oDNNNNNNNNNNDNNNo",
    "..............oDNNNNNNNNNNDNNNo",
    "..............oDNNNNNNNNNNDNNNo",
    "..............oDNNNNNNNNNNDNNNo",
    "..............oDNNNNNNNNNNDNNNo",
    "..............oDNNNNNNNNNNoDDDo",
    "..............oDDDDDDDDDDDo==-o",
    "...............oooooooooooo==o",
    "...............o//|||||||2oooo",
])
BOGDAN_LEGS = 27                                    # first leg row (the hip row 26 stays)
BOGDAN_STAND = owner_rows([
    "...............o//||oo|||2o",
    "...............o//||oo|||2o",
    "...............o//||oo|||2o",
    "...............o//||oo|||2o",
    "...............o//||oo|||2o",
    "...............o//||oo|||2o",
    "...............o//||oo|||2o",
    "...............o//||oo|||2o",
    "...............o//||oo|||2o",
    "...............o////oo////o",
    "..............oWWWWwooWWWWwo",
    "..............o%%%%%oo%%%%%o",
    "..............oooooooooooooo",
])
BOGDAN_STRIDE = owner_rows([                        # far leg back, near leg forward
    "...............o//|||o|||2o",
    "..............o///|oo|||2o",
    "..............o///o.o||||2o",
    ".............o///o..o||||2o",
    ".............o///o...o|||2o",
    "............o///o....o|||2o",
    "............o///o.....o|||2o",
    "...........o///o......o|||2o",
    "...........o///o.......o|||2o",
    "..........o////o.......o////o",
    ".........oWWWWwo.......oWWWWwo",
    ".........o%%%%%o.......o%%%%%o",
    ".........ooooooo.......ooooooo",
])
BOGDAN_PASS = owner_rows([                          # legs passing under the body
    "...............o//||||||||2o",
    "...............o///||o|||2o",
    "................o//|o|||2o",
    "................o//|o|||2o",
    "................o///o|||2o",
    "................o///o|||2o",
    "................o///o|||2o",
    "................o///o|||2o",
    "................o///o|||2o",
    "................o///o////o",
    "...............oWWWWoWWWWwo",
    "...............o%%%%o%%%%%o",
    "...............ooooooooooo",
])


def _bogdan(legs):
    return R(BOGDAN_TOP + legs)


BOGDAN_BASE = _bogdan(BOGDAN_STAND)
BOGDAN_CHIN = 11

# blue plastic cat carrier 14x10, barred door on the right; Bogdan holds its handle in his near hand
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
CARRIER_AT = (23, 26)


def _bogdan_walk(carrier):
    a = _bogdan(BOGDAN_STRIDE)
    b = swap_legs(a, BOGDAN_LEGS, 20, {'|': '/', '2': '/'}, {'/': '|'})
    p = _bogdan(BOGDAN_PASS)
    frames = [a, head_bob(a, BOGDAN_CHIN), p, b, head_bob(b, BOGDAN_CHIN), p]
    if carrier:
        frames = [overlay(f, CARRIER, *CARRIER_AT) for f in frames]
    return frames


# 0.14.0 ending "pat" (spec A1; pose from the Gemini sheet reference/gemini/bogdan_pat): the near arm leaves his side, reaches
# forward at chest height and pats a little lower. Approved art source (reference/art/bogdan_pat), not a drawn clip in NPCS.
_BOGDAN_ARM_COLS = range(27, 31)


def _bogdan_armless():
    g = [list(r) for r in BOGDAN_BASE]
    for y in range(13, 27):
        for x in _BOGDAN_ARM_COLS:
            if x < len(g[y]):
                g[y][x] = '.'
    for y in range(14, 25):
        g[y][26] = 'o'                      # the hoodie's right side closes where the arm hung
    return g


def _paste(g, x, y, art):
    for i, ch in enumerate(art):
        if ch != ' ' and 0 <= x + i < len(g[y]):
            g[y][x + i] = ch


def bogdan_pat_frames():
    arms = [
        [(26, 14, "ooo"), (26, 15, "NNNo"), (26, 16, "DNNNo"), (27, 17, "oNNNo"), (28, 18, "oNNLo"), (28, 19, "o=-o"),
         (29, 20, "oo")],                                                       # elbow out, hand coming up
        [(26, 15, "oooooooooo"), (26, 16, "NLLLLLLLNo=o"), (26, 17, "NNNNNNNNNo==o"), (26, 18, "DDDDDDDDDo-o"),
         (27, 19, "oooooooooo")],                                               # arm straight out, open hand
        [(26, 16, "oooooooooo"), (26, 17, "NLLLLLLLNoo"), (26, 18, "NNNNNNNNNo=o"), (26, 19, "DDDDDDDDDo==o"),
         (27, 20, "oooooooooo-o")],                                             # hand pats one row lower
    ]
    frames = []
    for arm in arms:
        g = _bogdan_armless()
        for x, y, art in arm:
            _paste(g, x, y, art)
        frames.append(R(owner_rows([''.join(r) for r in g])))   # N/D/L arm placeholders -> the hoodie navy keys
    return frames


def write_pat_art(project):
    paths = []
    for i, f in enumerate(bogdan_pat_frames(), 1):
        p = os.path.join(project, 'reference', 'art', 'bogdan_pat', 'final_%03d.png' % i)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        save(f, p)
        paths.append(p)
    return paths


CLIPS_BOGDAN = OrderedDict([
    ('idle', [BOGDAN_BASE, head_bob(BOGDAN_BASE, BOGDAN_CHIN)]),
    ('walk', _bogdan_walk(True)),                  # carrying Pluto in
    ('walk_free', _bogdan_walk(False)),            # leaving empty-handed
])

# ------------------------------------------------------------------ Bianca: long brown hair with a highlight, yellow sweater dress
# Hair: 'm' chestnut, 'M' highlight streak, 'X' shade. Dress: 'A' light, ':' mid, 'a' shade. Light shoes: 'W' / 'w' on a '6' sole.
BIANCA_TOP = owner_rows([
    "",
    "",
    "",
    "...................ooooooo",
    "..................ommMMmmmo",
    ".................ommMMmmmmmo",
    "................ommMmmmmmmmmo",
    "................omMmmmX=====o",
    "................omMmmX======o",
    "................omMmmX=Kg=Kgo",
    "................omMmmX=-===-o",
    "................omMmmX==pp=o",
    "................omMmmoo===o",
    "................omMmmXo=-o",
    "................omMmXo:::aoo",
    "...............omMmXoA::::::o",
    "...............omMmXoA::::a::o",
    "...............omMmXoA::::a::o",
    "...............omMmXa::::::a:o",
    "...............oXmXa:::::::a:o",
    "................oooa:::::::a:o",
    "..................oa:::::::oo=o",
    "..................oa::::::::o=o",
    "..................oa::::::::ooo",
    ".................oa::::::::::o",
    ".................oa::::::::::o",
    "................oa::::::::::::o",
    "................oaaaaaaaaaaaaao",
    ".................oooooooooooooo",
])
BIANCA_LEGS = 29
BIANCA_STAND = owner_rows([
    "..................o--=o.o-==o",
    "..................o--=o.o-==o",
    "..................o--=o.o-==o",
    "..................o--=o.o-==o",
    "..................o--=o.o-==o",
    "..................o--=o.o-==o",
    "..................o--=o.o-==o",
    "..................o--=o.o-==o",
    ".................owWWWo.oWWWWo",
    ".................o6666o.o6666o",
    ".................oooooo.oooooo",
])
BIANCA_STRIDE = owner_rows([
    "..................o--=o.o-==o",
    ".................o--=o...o-==o",
    ".................o--=o...o-==o",
    "................o--=o.....o-==o",
    "................o--=o.....o-==o",
    "...............o--=o.......o-==o",
    "...............o--=o.......o-==o",
    "..............o--=o.........o-==o",
    ".............owWWWo.........oWWWWo",
    ".............o6666o.........o6666o",
    ".............oooooo.........oooooo",
])
BIANCA_PASS = owner_rows([
    "..................o--=o.o-==o",
    "...................o--=oo-==o",
    "...................o--=oo-==o",
    "...................o--=oo-==o",
    "...................o--=oo-==o",
    "...................o--=oo-==o",
    "...................o--=oo-==o",
    "...................o--=oo-==o",
    "..................owWWWoWWWWo",
    "..................o6666o6666o",
    "..................oooooooooo",
])


def _bianca(legs):
    return R(BIANCA_TOP + legs)


BIANCA_BASE = _bianca(BIANCA_STAND)
BIANCA_CHIN = 13                                   # the neck row: her hair below it stays attached when the head bobs

# near arm raised to wave: yellow sleeve up beside the face, open hand above the head (two hand positions)
_BIANCA_ARM_DOWN = [(27, 21, 'oo=o'), (28, 22, 'o=o'), (28, 23, 'ooo')]


def _bianca_wave(hand_dx):
    g = [list(r) for r in BIANCA_BASE]
    for x, y, art in _BIANCA_ARM_DOWN:              # the hanging hand goes; the dress side closes
        for i in range(len(art)):
            g[y][x + i] = '.'
    for y, x, art in ((21, 27, 'o'), (22, 28, 'o'), (23, 28, 'o')):
        g[y][x] = art
    f = [''.join(r) for r in g]
    hand = ['.oooo.', 'o====o', 'o=-==o', '.o==o.']
    sleeve = ['.o:o', 'oA:o', 'oA:o', 'oA:o', 'oA:o', 'oA::o', 'oA::o']
    f = overlay(f, sleeve, 28, 8)
    f = overlay(f, hand, 27 + hand_dx, 4)
    return R(f)


# 0.14.0 ending (spec A1; poses from the Gemini sheet reference/gemini/bianca_ending): Bianca kneels, lifts Pluto and carries
# him out. Approved art sources (reference/art/bianca_*), copied by hand onto her own rows with a small Pluto in her arms.
_TABBY = 'B'                                        # vetpixel key nearest Pluto's tabby mid (#8B7A66)
_PLUTO_HELD = [                                     # 14x15: head up-right, white chest and paws over her arm, ringed tail down
    "..oo....oo....",
    ".oPto..otPo...",
    ".otttttttto...",
    "otbtbttbtbto..",
    "otGtttttGtto..",
    "ottWWPPWWtto..",
    ".otWWWWWWto...",
    ".otWWWWWWdo...",
    "otttWWWWtddo..",
    "otbtttttbtdo..",
    ".oWooooooWo...",
    "......obo.....",
    "......oLo.....",
    "......obo.....",
    "......oo......",
]
_CARRY_ARM = ["oA::::::::o", "oA::::::::==o", "ooooooooooooo"]    # sleeve round under Pluto, hand on his side


def _held_pluto():
    return [r.replace('t', _TABBY) for r in _PLUTO_HELD]


def _armless(frame):
    g = [list(r) for r in frame]
    for x, y, art in _BIANCA_ARM_DOWN:
        for i in range(len(art)):
            g[y][x + i] = '.'
    for y, x in ((21, 27), (22, 28), (23, 28)):
        g[y][x] = 'o'
    return [''.join(r) for r in g]


def _carrying(frame, dy=0):
    f = overlay(_armless(frame), _held_pluto(), 26, 13 + dy)
    f = overlay(f, _CARRY_ARM, 24, 21 + dy)
    return R(f)


def _crouch(k, reach=False):
    """Upper body k rows lower, the legs k rows shorter (knees bend), shoes on the bottom row."""
    legs = list(BIANCA_STAND)
    f = ['.' * OWNER_CANVAS[0]] * k + list(BIANCA_TOP) + legs[:8 - k] + legs[8:]
    f = f[:OWNER_CANVAS[1]]
    if reach:                                       # the near hand reaches down and forward to pick him up
        f = overlay(_armless(f), ["oA:o", "oA::o", ".oA::o", "..o==o", "...oo"], 27, 21 + k)
    return R(f)


def bianca_ending_frames():
    stride = _bianca(BIANCA_STRIDE)
    other = swap_legs(stride, BIANCA_LEGS, 23, {'-': '='}, {'=': '-'})
    walk = [stride, head_bob(stride, BIANCA_CHIN), _bianca(BIANCA_PASS), other, head_bob(other, BIANCA_CHIN), _bianca(BIANCA_PASS)]
    return OrderedDict([
        ('kneel', [_crouch(0), _crouch(3), _crouch(5, reach=True)]),
        ('carry', [_carrying(BIANCA_BASE), _carrying(head_bob(BIANCA_BASE, BIANCA_CHIN), -1)]),
        ('carry_walk', [_carrying(f, -1 if i in (1, 4) else 0) for i, f in enumerate(walk)]),
    ])


def write_ending_art(project):
    paths = []
    for clip, frames in bianca_ending_frames().items():
        for i, f in enumerate(frames, 1):
            p = os.path.join(project, 'reference', 'art', 'bianca_' + clip, 'final_%03d.png' % i)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            save(f, p)
            paths.append(p)
    return paths


CLIPS_BIANCA = OrderedDict([
    ('idle', [BIANCA_BASE, head_bob(BIANCA_BASE, BIANCA_CHIN)]),
    ('walk', [_bianca(BIANCA_STRIDE), head_bob(_bianca(BIANCA_STRIDE), BIANCA_CHIN), _bianca(BIANCA_PASS),
              swap_legs(_bianca(BIANCA_STRIDE), BIANCA_LEGS, 23, {'-': '='}, {'=': '-'}),
              head_bob(swap_legs(_bianca(BIANCA_STRIDE), BIANCA_LEGS, 23, {'-': '='}, {'=': '-'}), BIANCA_CHIN),
              _bianca(BIANCA_PASS)]),
    ('wave', [mirror(_bianca_wave(0)), mirror(_bianca_wave(2)), mirror(_bianca_wave(0)), mirror(_bianca_wave(-1))]),
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
    ('bogdan', {'canvas': OWNER_CANVAS, 'clips': CLIPS_BOGDAN}),
    ('bianca', {'canvas': OWNER_CANVAS, 'clips': CLIPS_BIANCA}),
    ('receptionist', {'canvas': REC_CANVAS, 'clips': CLIPS_REC}),
    ('rex', {'canvas': REX_CANVAS, 'clips': CLIPS_REX}),
    ('grandma', {'canvas': GRANDMA_CANVAS, 'clips': CLIPS_GRANDMA}),
])

# 0.14.0 ending clips (spec A1): approved art from reference/art, installed by art_sources; write() never draws them.
# Must equal art_sources.ENDING_CLIPS (a test checks); kept literal so npc_poses does not import the object tables.
SOURCED = OrderedDict([('bianca', OrderedDict([('kneel', 3), ('carry', 2), ('carry_walk', 6)])),
                       ('bogdan', OrderedDict([('pat', 3)]))])


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
