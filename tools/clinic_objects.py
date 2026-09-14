"""Props of the vet clinic: ASCII sprites, collider specs and where they stand in the room.

OBJECTS: every prop prefab (name -> art + collider). PROPS: placements (name, (x, y)) in room cells,
x to the right and y up from the room's bottom-left corner; the sprite's lower-left corner sits on the cell.
Colliders are (layer, off_x, off_y, w, h) in pixels from the sprite's lower-left; 'high' blocks everything,
'low' blocks walking but bullets fly over it. Decor has no collider and renders under actors.
"""
import os

from vetpixel import R, pad, overlay, save, sheet


class Obj:
    def __init__(self, name, png, rows, collider=None, height_off_ground=0.0):
        self.name = name                        # StaticReferences.customObjects key, e.g. pluto_exam_table
        self.png = png                          # file stem under Resources/Objects/
        self.rows = rows                        # ASCII map
        self.collider = collider                # None or (layer, off_x, off_y, w, h) in pixels; layer 'low'|'high'
        self.height_off_ground = height_off_ground

    @property
    def size(self):
        return (max(len(r) for r in self.rows), len(self.rows))


def box(w, h, fill, edge='o', top=None, bottom=None):
    """Outlined rectangle; optional distinct top/bottom fill rows."""
    rows = [edge * w]
    for i in range(h - 2):
        f = fill
        if top is not None and i == 0:
            f = top
        if bottom is not None and i == h - 3:
            f = bottom
        rows.append(edge + f * (w - 2) + edge)
    rows.append(edge * w)
    return rows


# ------------------------------------------------------------------ exam table 48x32: steel slab on two legs
_slab = box(48, 16, '&', top='K', bottom='K')
_slab[13] = 'o' + '%' * 46 + 'o'
_slab[14] = 'o' + '#' * 46 + 'o'
_legs = []
for i in range(11):
    _legs.append('...o##o' + '.' * 34 + 'o##o...')
_legs[0] = '...o%%o' + '.' * 34 + 'o%%o...'
_legs[1] = '...o%%o' + '.' * 34 + 'o%%o...'
_feet = ['..o%%%%o' + '.' * 32 + 'o%%%%o..', '..oooooo' + '.' * 32 + 'oooooo..']
EXAM_TABLE = R(_slab + _legs + _feet + ['.' * 48] * 3)

# ------------------------------------------------------------------ cabinet 32x40: glass doors with jars and syringe boxes
_cab = box(32, 40, '&', top='K')
_pane = ['^' * 12] * 12
_jars = [
    "^^!!^^**^^::",
    "^^!!^^**^^::",
    "^^!!^^**^^::",
    "^^oo^^oo^^oo",
    "^^^^^^^^^^^^",
    "^_______^^^^",
    "^_!_!_!_^^^^",
    "^_______^^^^",
    "^^^^^^^^^^^^",
    "^^**^^!!^^^^",
    "^^**^^!!^^^^",
    "^^oo^^oo^^^^",
]
for i in range(12):
    _pane[i] = _jars[i]
_cab = overlay(_cab, ['o' * 14] + ['o' + r + 'o' for r in _pane] + ['o' * 14], 2, 3)
_cab = overlay(_cab, ['o' * 14] + ['o' + r + 'o' for r in _pane] + ['o' * 14], 16, 3)
_cab = overlay(_cab, ['o' * 14] + ['o' + r + 'o' for r in _pane] + ['o' * 14], 2, 19)
_cab = overlay(_cab, ['o' * 14] + ['o' + r + 'o' for r in _pane] + ['o' * 14], 16, 19)
_cab[36] = 'o' + '%' * 30 + 'o'
_cab[37] = 'o' + '#' * 30 + 'o'
CABINET = R(_cab)

# ------------------------------------------------------------------ cart 24x24: steel cart, syringe tray on top, wheels
_cart = ['.' * 24] * 24
_tray = box(24, 8, 'K', top='&')
_cart = overlay(_cart, _tray, 0, 0)
_syringes = [
    "..&&&&%%..&&&&%%..&&&&%%",
    "..&**&....&**&....&**&..",
]
_cart = overlay(_cart, _syringes, 0, 2)
for y in range(8, 20):
    _cart[y] = '..o##o' + '.' * 12 + 'o##o..'
_cart[12] = 'o' + '%' * 22 + 'o'
_cart[13] = 'o' + '#' * 22 + 'o'
_cart[20] = '.o%%o' + '.' * 14 + 'o%%o.'
_cart[21] = 'o####o' + '.' * 12 + 'o####o'
_cart[22] = 'oo##oo' + '.' * 12 + 'oo##oo'
_cart[23] = '.oooo.' + '.' * 12 + '.oooo.'
CART = R(_cart)

# ------------------------------------------------------------------ sink counter 32x32: white counter, steel basin, tap
_sink = box(32, 32, '_', top='0')
_sink = overlay(_sink, box(18, 10, '%', top='&'), 7, 6)
_sink = overlay(_sink, ['.o#o.', '.o#o.', 'o###o', '.....'], 13, 1)
_sink[24] = 'o' + '0' * 30 + 'o'
for y in range(25, 31):
    _sink[y] = 'o' + '_' * 6 + 'o' + '_' * 16 + 'o' + '_' * 6 + 'o'
CUP = ['.:.', ':::']
SINK = R(_sink)

# ------------------------------------------------------------------ scale 16x16: flat pet scale with a dial
_scale = box(16, 8, '&', top='K')
_scale = overlay(_scale, ['oooo', 'o::o', 'o:!o', 'oooo'], 6, 2)
SCALE = R(['.' * 16] * 8 + _scale)

# ------------------------------------------------------------------ carrier 32x24: blue plastic, white barred door on the right
_car = box(32, 20, '|', top='/')
_car = overlay(_car, ['..oooooo..', '.o//////o.', 'o//////////o'], 10, 0)
_door = ['o' * 10] + ['o_o_o_o__o'] * 12 + ['o' * 10]
_car = overlay(_car, _door, 20, 4)
_vents = ['o..o..o', 'o..o..o']
_car = overlay(_car, _vents, 4, 8)
_car = overlay(_car, ['o' + '/' * 30 + 'o'], 0, 18)
CARRIER = R(['.' * 32] * 4 + _car)

# ------------------------------------------------------------------ poster 16x24: anatomy poster with a red cross
_post = box(16, 24, '_', top='0')
_post = overlay(_post, ['.!!.', '!!!!', '!!!!', '.!!.'], 6, 2)
_post = overlay(_post, ['.oo..oo.', 'oBBBBBBo', 'oBBWWBBo', 'oBBBBBBo', '.oBBBBo.', '..oooo..'], 4, 9)
_post = overlay(_post, ['o' * 8], 4, 18)
_post = overlay(_post, ['o' * 6], 5, 20)
POSTER = R(_post)

# ------------------------------------------------------------------ cone of shame 12x10
CONE = R([
    "....oooo....",
    "...o____o...",
    "..o__0___o..",
    "..o__0___o..",
    ".o___0____o.",
    ".o___0____o.",
    "o____0_____o",
    "o__________o",
    "o0000000000o",
    ".oooooooooo.",
])

# ------------------------------------------------------------------ toys
TOY_MOUSE = R([
    "..oo......",
    ".oZZo.....",
    "oZZZZoo...",
    "oZZZZZZo.o",
    "oZZZZZZZoo",
    ".oooooo...",
])
TOY_BALL = R([
    ".oooo.",
    "o::::o",
    "o:??:o",
    "o:??:o",
    "o::::o",
    ".oooo.",
])
FEATHER_WAND = R([
    "..........oHH.",
    ".........oHHHo",
    "........oHeHo.",
    ".......oHHHo..",
    "......o\\o.....",
    ".....o\\o......",
    "....o\\o.......",
    "...o\\o........",
    "..o\\o.........",
    ".oo...........",
])
SCRATCH_POST = R(
    ['.....oooooo.....'] +
    ['.....o\\\\\\\\o.....', '.....o\\++\\o.....'] * 8 +
    ['.....o\\\\\\\\o.....'] +
    ['.oooooooooooooo.', 'o\\\\\\\\\\\\\\\\\\\\\\\\\\\\o', 'o++++++++++++++o', '.oooooooooooooo.', '.' * 16, '.' * 16]
)
SYRINGE_TRAY = R([
    "oooooooooooooooo",
    "oKKKKKKKKKKKKKKo",
    "oK&&&&%%.KKKKKKo",
    "oK&**&...KKKKKKo",
    "oK&&&&%%.KKKKKKo",
    "oKKKKKKKKKKKKKKo",
    "oK.&&&&%%.KKKKKo",
    "oK.&**&...KKKKKo",
    "oKKKKKKKKKKKKKKo",
    "oooooooooooooooo",
])

# ================================================================== v0.4 props: waiting room, wall decor, floor decor
def hbox(w, h, fill, top=None, bottom=None):
    return box(w, h, fill, top=top, bottom=bottom)


# ------------------------------------------------------------------ reception desk 48x28: white counter, wood front, monitor, papers
_desk = ['.' * 48] * 28
_desk = overlay(_desk, box(48, 12, '_', top='0', bottom='0'), 0, 6)          # counter top
_desk = overlay(_desk, box(48, 12, '\\', top='+', bottom='+'), 0, 16)        # wood front
_desk[27] = 'o' * 48
_desk = overlay(_desk, ['..oooo..', '.o++++o.', '.o++++o.', '..oooo..'], 20, 19)  # drawer handle plate
_desk = overlay(_desk, ['oooooooooo', 'o########o', 'o#**%***#o', 'o#*%%%**#o', 'o########o', 'oooooooooo', '....oo....', '...oooo...'], 6, 0)  # monitor
_desk = overlay(_desk, ['ooooooooo', 'oKKKKKKKo', 'oK..K..Ko', 'oKKKKKKKo', 'oK..K..Ko', 'ooooooooo'], 30, 2)   # papers
_desk = overlay(_desk, ['oo', 'o!', 'oo'], 42, 4)                              # red stamp
RECEPTION_DESK = R(_desk)

# ------------------------------------------------------------------ waiting chair 16x20: blue plastic seat on steel legs
CHAIR = R([
    "....oooooooo....",
    "...o||||||||o...",
    "...o|//////|o...",
    "...o||||||||o...",
    "...o||||||||o...",
    "...o||||||||o...",
    "...o||||||||o...",
    ".oooooooooooooo.",
    "o||||||||||||||o",
    "o|////////////|o",
    "o||||||||||||||o",
    ".oooooooooooooo.",
    "..o%o......o%o..",
    "..o%o......o%o..",
    "..o%o......o%o..",
    "..o%o......o%o..",
    "..o%o......o%o..",
    ".o%%o......o%%o.",
    ".oooo......oooo.",
    "................",
])

# ------------------------------------------------------------------ potted plant 16x28
PLANT = R([
    "......oo........",
    ".....o$$o..oo...",
    "....o$e$$oo$$o..",
    "...o$$$$$$$$e$o.",
    "..o$e$$~$$$$$$o.",
    "..o$$$$~$$e$$$o.",
    ".o$$e$$~~$$$$$$o",
    ".o$$$$$~~$$$e$$o",
    ".o$$$$$~~$$$$$$o",
    "..o$e$$~~$$$$$o.",
    "..o$$$$~~$$e$$o.",
    "...o$$$~~$$$$o..",
    "....oo$~~$oo....",
    "......o~~o......",
    "......o~~o......",
    "....oooooooo....",
    "...o????????o...",
    "...o?::::::?o...",
    "...oooooooooo...",
    "....o??????o....",
    "....o??????o....",
    "....o??????o....",
    "....o??????o....",
    "....o??????o....",
    "....o?????+o....",
    "....o?????+o....",
    ".....oooooo.....",
    "................",
])

# ------------------------------------------------------------------ window 32x24: frame, blue sky, blinds
_win = box(32, 24, '*', top='&', bottom='&')
_win = overlay(_win, ['o' * 32], 11, 0) if False else _win
for y in (11, 12):
    _win[y] = 'o' + '&' * 30 + 'o'
for y in range(2, 22):
    _win[y] = _win[y][:15] + ('o&' if y not in (11, 12) else '&&') + _win[y][17:]
for y in (4, 7, 15, 18):
    if y not in (11, 12):
        _win[y] = 'o' + 'K' * 14 + _win[y][15:17] + 'K' * 14 + 'o'
WINDOW = R(_win)

# ------------------------------------------------------------------ X-ray light box 24x20: dark box, lit panel, cat skeleton
_xr = box(24, 20, '#', top='%', bottom='%')
_xr = overlay(_xr, box(20, 16, '*', top='^', bottom='^'), 2, 2)
_xr = overlay(_xr, [
    "...KK....KK.....",
    "..KKKKKKKKKK....",
    "..K.KK.KK.K.....",
    "..KKKKKKKKKKKKKK",
    "...KKKKKK..K..K.",
    "....K..K.......K",
    "...K....K.......",
], 4, 5)
XRAY_BOX = R(_xr)

# ------------------------------------------------------------------ medicine shelf 32x36: wood shelves with bottles and boxes
_shelf = ['.' * 32] * 36
for sy in (0, 12, 24):
    _shelf = overlay(_shelf, ['o' * 32, 'o' + '\\' * 30 + 'o', 'o' + '+' * 30 + 'o'], 0, sy + 9)
    bottles = [
        "oo.oo.oooo.oo.oooo.oo.oo.oooo.o",
        "o!o!!o!**!o::o!!!!o**o!!o****o!",
        "o!o!!o!**!o::o!!!!o**o!!o****o!",
        "o!o!!o!**!o::o!!!!o**o!!o****o!",
        "oooooooooooooooooooooooooooooo",
    ]
    _shelf = overlay(_shelf, [b.ljust(32, '.')[:32] for b in bottles], 0, sy + 4)
_shelf[33] = 'o' + '\\' * 30 + 'o'
_shelf[34] = 'o' + '+' * 30 + 'o'
_shelf[35] = 'o' * 32
MED_SHELF = R(_shelf)

# ------------------------------------------------------------------ wall clock 10x10
CLOCK = R([
    "...oooo...",
    "..oKKKKo..",
    ".oKKoKKKo.",
    "oKKKoKKKKo",
    "oKKKooooKo",
    "oKKKKKKKKo",
    "oKKKKKKKKo",
    ".oKKKKKKo.",
    "..oKKKKo..",
    "...oooo...",
])

# ------------------------------------------------------------------ fish tank 32x24: glass, water, gravel, an orange fish, a plant
_tank = box(32, 24, '*', top='&', bottom='&')
_tank = overlay(_tank, ['o' + '&' * 30 + 'o', 'o' + '%' * 30 + 'o'], 0, 0)
_tank = overlay(_tank, ['o' + '#' * 30 + 'o', 'o' + '%' * 30 + 'o', 'o' * 32], 0, 21)
_tank = overlay(_tank, ['^' * 3] * 17, 2, 3)                                      # glass highlight column
_tank = overlay(_tank, ['..o?o..', '.o???o.', 'o??g??oo', '.o???o.', '..o?o..'], 12, 8)  # fish
_tank = overlay(_tank, ['..$..', '.$$$.', '.$e$.', '$$$$$', '.$$$.', '..$..'], 23, 12)   # plant
_tank = overlay(_tank, ['%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%', '::%%::%%::%%::%%::%%::%%::%%::'], 1, 19)  # gravel
FISH_TANK = R(_tank)

# ------------------------------------------------------------------ sharps bin 12x14: yellow with a red lid and label
SHARPS_BIN = R([
    "..oooooooo..",
    ".o!!!!!!!!o.",
    "o!!!!!!!!!!o",
    "oooooooooooo",
    "o::::::::::o",
    "o::::::::::o",
    "o::o::::o::o",
    "o::oo::oo::o",
    "o::::oo::::o",
    "o::::::::::o",
    "o::::::::::o",
    "o::::::::::o",
    ".oooooooooo.",
    "............",
])

# ------------------------------------------------------------------ IV stand 12x32: steel pole, drip bag, wheeled base
IV_STAND = R([
    "....oooo....",
    "....o&&o....",
    "...oo&&oo...",
    "...o&**&o...",
    "...o&**&o...",
    "...o&**&o...",
    "...o&**&o...",
    "...o&**&o...",
    "...o&&&&o...",
    "....oo&o....",
    ".....o&o....",
    ".....o%o....",
    ".....o%o....",
    ".....o%o....",
    ".....o%o....",
    ".....o%o....",
    ".....o%o....",
    ".....o%o....",
    ".....o%o....",
    ".....o%o....",
    ".....o%o....",
    ".....o%o....",
    ".....o%o....",
    ".....o%o....",
    ".....o%o....",
    ".....o%o....",
    "....oo%oo...",
    "..oo%%%%%oo.",
    ".o%%%%%%%%%o",
    "o#o#o###o#o#",
    ".ooo.ooo.ooo",
    "............",
])

# ------------------------------------------------------------------ treat jar 8x10
TREAT_JAR = R([
    "..oooo..",
    ".o++++o.",
    "oooooooo",
    "o^^^^^^o",
    "o^BB^BBo",
    "o^BBBB^o",
    "oBB^^BBo",
    "o^BB^B^o",
    "o^^^^^^o",
    ".oooooo.",
])

# ------------------------------------------------------------------ Royal Canin bowls 20x8: red kibble bowl, blue water bowl
FOOD_BOWLS = R([
    "..oooooo....oooooo..",
    ".oBBB\\BBo..o******o.",
    "o!!!!!!!!oo|^*****|o",
    "o!!K!!!!!oo|||||||/o",
    "o!!!!!!!!oo////////o",
    ".o!!!!!!o..o//////o.",
    "..oooooo....oooooo..",
    "....................",
])

# ------------------------------------------------------------------ litter box 20x12: blue tray with sand
LITTER_BOX = R([
    "oooooooooooooooooooo",
    "o||||||||||||||||||o",
    "o|oooooooooooooooo|o",
    "o|o:::::::::::::::|o",
    "o|o::::::::::::::o|o",
    "o|o:::::::::::::::|o",
    "o|oooooooooooooooo|o",
    "o||||||||||||||||||o",
    "o//////////////////o",
    "oooooooooooooooooooo",
    "....................",
    "....................",
])

# ------------------------------------------------------------------ floor mat 48x24: grey mat with a light border and paw logo
_mat = box(48, 24, 'Z', top='%', bottom='#')
for y in range(1, 23):
    _mat[y] = 'o%' + _mat[y][2:46] + '#o'
_mat = overlay(_mat, ['.KK.KK.', 'KKKKKKK', '.KKKKK.', '..KKK..'], 20, 9)
FLOOR_MAT = R(_mat)

# ------------------------------------------------------------------ paw prints 24x16: a trail of tabby paw prints (decor)
_paw = ['.BB.BB.', 'BBBBBBB', '.BBBBB.', '..BBB..']
_pp = ['.' * 24] * 16
for i, (x, y) in enumerate(((0, 10), (8, 4), (16, 10))):
    _pp = overlay(_pp, _paw, x, y)
_pp = overlay(_pp, _paw, 8, 0) if False else _pp
PAW_PRINTS = R(_pp)

# ------------------------------------------------------------------ wet floor sign 12x16: yellow A-frame
WET_FLOOR_SIGN = R([
    ".....oo.....",
    "....o::o....",
    "....o::o....",
    "...o::::o...",
    "...o:!!:o...",
    "..o::!!::o..",
    "..o:::::::o.",
    ".o::::::::o.",
    ".o:!!!!!!:o.",
    "o::::::::::o",
    "o::::::::::o",
    "o::::::::::o",
    "oo::::::::oo",
    "o.oooooooo.o",
    "o..........o",
    "oo........oo",
])

OBJECTS = [
    Obj('pluto_exam_table', 'exam_table', EXAM_TABLE, ('low', 2, 0, 44, 16)),
    Obj('pluto_cabinet', 'cabinet', CABINET, ('high', 0, 0, 32, 20)),
    Obj('pluto_cart', 'cart', CART, ('low', 0, 0, 24, 14)),
    Obj('pluto_sink', 'sink', SINK, ('high', 0, 0, 32, 20)),
    Obj('pluto_scale', 'scale', SCALE, None, -1.5),
    Obj('pluto_carrier', 'carrier', CARRIER, ('high', 0, 0, 32, 16)),
    Obj('pluto_poster', 'poster', POSTER, None, 0.5),
    Obj('pluto_cone', 'cone', CONE, None, -1.5),
    Obj('pluto_toy_mouse', 'toy_mouse', TOY_MOUSE, None, -1.5),
    Obj('pluto_toy_ball', 'toy_ball', TOY_BALL, None, -1.5),
    Obj('pluto_feather_wand', 'feather_wand', FEATHER_WAND, None, -1.5),
    Obj('pluto_scratch_post', 'scratch_post', SCRATCH_POST, ('low', 2, 0, 12, 8)),
    Obj('pluto_syringe_tray', 'syringe_tray', SYRINGE_TRAY, None, -1.5),
    # v0.4
    Obj('pluto_reception_desk', 'reception_desk', RECEPTION_DESK, ('high', 0, 0, 48, 14)),
    Obj('pluto_chair', 'chair', CHAIR, ('low', 1, 0, 14, 8)),
    Obj('pluto_plant', 'plant', PLANT, ('high', 4, 0, 8, 8)),
    Obj('pluto_window', 'window', WINDOW, None, 0.5),
    Obj('pluto_xray_box', 'xray_box', XRAY_BOX, None, 0.5),
    Obj('pluto_med_shelf', 'med_shelf', MED_SHELF, ('high', 0, 0, 32, 16)),
    Obj('pluto_clock', 'clock', CLOCK, None, 0.5),
    Obj('pluto_fish_tank', 'fish_tank', FISH_TANK, ('high', 0, 0, 32, 14)),
    Obj('pluto_sharps_bin', 'sharps_bin', SHARPS_BIN, ('low', 0, 0, 12, 6)),
    Obj('pluto_iv_stand', 'iv_stand', IV_STAND, ('low', 0, 0, 12, 6)),
    Obj('pluto_treat_jar', 'treat_jar', TREAT_JAR, None, -1.5),
    Obj('pluto_food_bowls', 'food_bowls', FOOD_BOWLS, None, -1.5),
    Obj('pluto_litter_box', 'litter_box', LITTER_BOX, ('low', 0, 0, 20, 8)),
    Obj('pluto_floor_mat', 'floor_mat', FLOOR_MAT, None, -2.5),
    Obj('pluto_paw_prints', 'paw_prints', PAW_PRINTS, None, -2.0),
    Obj('pluto_wet_floor_sign', 'wet_floor_sign', WET_FLOOR_SIGN, ('low', 0, 0, 12, 6)),
]

# Placements (game cells). Cabinets and the poster stand along the north edge; the table is the arena centre;
# the carrier is in the waiting corner next to Pluto's spawn (6, 2.5); the Vet stands at (12.5, 11.5).
PROPS = [
    # north wall, left to right: cabinets, window, poster, X-ray box, medicine shelf, cabinets; clock above the window
    ('pluto_cabinet', (0.5, 15.0)), ('pluto_cabinet', (3.0, 15.0)),
    ('pluto_window', (6.0, 15.5)), ('pluto_clock', (8.6, 17.1)),
    ('pluto_poster', (9.0, 15.0)), ('pluto_xray_box', (10.5, 15.5)),
    ('pluto_med_shelf', (14.0, 15.0)),
    ('pluto_cabinet', (17.0, 15.0)), ('pluto_cabinet', (20.0, 15.0)), ('pluto_cabinet', (23.0, 15.0)),
    # exam area: table in the middle, cart and IV stand beside it, syringe tray and cone on the floor
    ('pluto_exam_table', (11.0, 8.0)),
    ('pluto_cart', (16.0, 8.5)),
    ('pluto_iv_stand', (9.5, 9.5)),
    ('pluto_syringe_tray', (8.0, 12.0)),
    ('pluto_cone', (20.0, 12.0)),
    ('pluto_wet_floor_sign', (16.0, 5.5)),
    ('pluto_paw_prints', (8.0, 5.0)),
    # right wall: sink, fish tank, sharps bin
    ('pluto_sink', (23.0, 10.5)),
    ('pluto_fish_tank', (23.0, 6.5)),
    ('pluto_sharps_bin', (24.5, 4.0)),
    # waiting corner (bottom-left): mat, chairs, plant, carrier by Pluto's spawn, toys
    ('pluto_floor_mat', (0.5, 4.0)),
    ('pluto_chair', (1.0, 5.0)), ('pluto_chair', (2.5, 5.0)),
    ('pluto_plant', (0.5, 8.0)),
    ('pluto_scale', (4.0, 10.0)),
    ('pluto_carrier', (2.0, 1.5)),
    ('pluto_toy_mouse', (7.0, 6.0)),
    ('pluto_toy_ball', (18.0, 4.0)),
    ('pluto_feather_wand', (14.0, 3.5)),
    # cat corner (left, under the scale): litter box and Royal Canin bowls
    ('pluto_litter_box', (1.0, 11.5)),
    ('pluto_food_bowls', (5.5, 12.5)),
    # reception (bottom-right): desk with the treat jar, scratching post
    ('pluto_reception_desk', (18.5, 1.5)),
    ('pluto_treat_jar', (21.4, 3.3)),
    ('pluto_scratch_post', (22.5, 4.5)),
]


def write(project):
    out = os.path.join(project, 'Resources', 'Objects')
    paths = []
    for o in OBJECTS:
        p = os.path.join(out, o.png + '.png')
        save(o.rows, p)
        paths.append(p)
    return paths


def preview(project):
    p = os.path.join(project, 'docs', 'preview', 'objects-sheet.png')
    sheet([[o.rows for o in OBJECTS[:5]], [o.rows for o in OBJECTS[5:9]], [o.rows for o in OBJECTS[9:13]],
           [o.rows for o in OBJECTS[13:19]], [o.rows for o in OBJECTS[19:25]], [o.rows for o in OBJECTS[25:]]], p, scale=4)
    return p
