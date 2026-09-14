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


# ------------------------------------------------------------------ exam table 80x40 (v0.10): steel slab, three leather straps,
# a steel pedestal and a wheeled base. Seen from the south-front like the props_theatre concept; the slab's far edge is the
# 'K' highlight, the near edge steps down through '%' to '#'.
_slab = box(80, 18, '&', top='K')
_slab[2] = 'o' + 'K' * 78 + 'o'
_slab[15] = 'o' + '%' * 78 + 'o'
_slab[16] = 'o' + '#' * 78 + 'o'
_strap = ['oooooo'] + ['o\\\\\\\\+o'] * 16 + ['oooooo']
_strap = overlay(_strap, ['oooo', 'o66o', 'o66o', 'oooo'], 1, 7)                # buckle
for sx in (16, 37, 58):
    _slab = overlay(_slab, _strap, sx, 0)
_ped = box(24, 14, '%', top='&')                                                # pedestal rows 18..31
for y in range(1, 13):
    _ped[y] = 'o&' + _ped[y][2:22] + '#o'
_base = box(48, 6, '#', top='%')                                                # wheeled base rows 32..37
_base = overlay(_base, ['%' * 10], 19, 2)
_wheels = ['.oo.' + '.' * 40 + '.oo.', 'o##o' + '.' * 40 + 'o##o', '.oo.' + '.' * 40 + '.oo.']
_et = ['.' * 80] * 40
_et = overlay(_et, _slab, 0, 0)
_et = overlay(_et, _ped, 28, 18)
_et = overlay(_et, _base, 16, 31)
_et = overlay(_et, _wheels, 16, 37)
EXAM_TABLE = R(_et)

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


# ------------------------------------------------------------------ treat jar 8x10 (also drawn on the desk and the nurse station)
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

# ------------------------------------------------------------------ reception desk 112x40 (v0.10): wood top on a steel front with a
# teal back panel; a monitor, the bell, a paper tray, a red stamp and the treat jar stand on the top (props_waiting_room concept).
_desk = ['.' * 112] * 40
_desk = overlay(_desk, box(112, 10, '\\', top='\\', bottom='+'), 0, 12)       # wood top rows 12..21
_desk[13] = 'o' + 'K' * 110 + 'o'                                               # far-edge highlight
_desk = overlay(_desk, box(112, 18, '&', top='%', bottom='%'), 0, 22)           # steel front rows 22..39
_desk = overlay(_desk, ['$' * 110, '$' * 110, '~' * 110], 1, 25)                # teal panel strip
for x in (28, 76):
    _desk = overlay(_desk, ['oooooooo', 'o######o', 'o#%%%%#o', 'oooooooo'], x, 32)   # drawer plates
_mon = box(18, 13, '#', top='%')                                                # monitor
_mon = overlay(_mon, box(14, 9, '*', edge='*'), 2, 2)
_mon = overlay(_mon, ['KKK', 'K..'], 3, 3)
_mon = overlay(_mon, ['*%%%%%%*'], 4, 8)
_desk = overlay(_desk, _mon, 12, 0)
_desk = overlay(_desk, ['....oo....', '..oooooo..'], 16, 13)                    # monitor foot
_desk = overlay(_desk, ['..o..', '.o:o.', 'o:::o', 'ooooo'], 50, 9)              # bell
_desk = overlay(_desk, ['ooooooooooo', 'oKKKKKKKKKo', 'oK..K..K.Ko', 'oKKKKKKKKKo', 'ooooooooooo'], 64, 8)   # paper tray
_desk = overlay(_desk, ['oo', 'o!', 'oo'], 80, 10)                              # red stamp
_desk = overlay(_desk, TREAT_JAR, 92, 3)
RECEPTION_DESK = R(_desk)

# ------------------------------------------------------------------ waiting chair 24x24 (v0.10): orange moulded seat facing south,
# a hole in the back rest, steel legs. '7' is the darker orange for the crease and the seat's front lip.
CHAIR = R([
    "......oooooooooooo......",
    ".....o????????????o.....",
    "....o??????????????o....",
    "....o??????????????o....",
    "....o???oooooooo???o....",
    "....o???o......o???o....",
    "....o???oooooooo???o....",
    "....o??????????????o....",
    "....o??????????????o....",
    "...o7777777777777777o...",
    "..o??????????????????o..",
    ".o????????????????????o.",
    "o??????????????????????o",
    "o??????????????????????o",
    "o7777777777777777777777o",
    ".oooooooooooooooooooooo.",
    "..o%o..............o%o..",
    "..o%o..............o%o..",
    "..o%o..............o%o..",
    "..o%o..............o%o..",
    "..o%o..............o%o..",
    "..o%o..............o%o..",
    ".o%%o..............o%%o.",
    ".oooo..............oooo.",
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
# v0.10: the tank stands on a steel frame (rows 24..39), like the props_waiting_room concept
_stand = ['.' * 32] * 16
_stand = overlay(_stand, ['o' * 32, 'o' + '%' * 30 + 'o', 'o' * 32], 0, 0)                  # top rail
for y in range(3, 15):
    _stand = overlay(_stand, ['o##o' + '.' * 24 + 'o##o'], 0, y)                             # legs
_stand = overlay(_stand, ['o' * 28, '%' * 28, 'o' * 28], 2, 8)                              # cross bar
_stand[15] = 'oooo' + '.' * 24 + 'oooo'
FISH_TANK = R(_tank + _stand)

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

# ================================================================== v0.5 props: the gates and the ward
# ------------------------------------------------------------------ sliding clinic door 32x40: steel frame, two teal panels
# The door prop sits in the 2x2 gap of a zone wall. Closed: both panels meet in the middle. Open: the panels have
# slid into the wall, only the frame remains (transparent centre shows the floor behind). ClinicDoor.cs swaps them.
def _door_frame():
    rows = ['.' * 32] * 40
    rows = overlay(rows, box(32, 6, '%', top='&', bottom='#'), 0, 0)          # lintel
    for y in range(5, 40):
        rows[y] = 'o%&o' + rows[y][4:28] + 'o&%o'                             # side posts
    rows[39] = 'oooo' + rows[39][4:28] + 'oooo'
    return rows


def _door_panel(w, glass_x):
    pan = box(w, 34, '$', top='~', bottom='~')
    pan = overlay(pan, ['oooooo', 'o^^^^o', 'o^^^^o', 'o^^^^o', 'o^^^^o', 'o^^^^o', 'o^^^^o', 'oooooo'], glass_x, 5)  # window
    pan = overlay(pan, ['o', '&', '&', '&', '&', 'o'], w - 3, 18)            # handle
    return pan


_dc = _door_frame()
_dc = overlay(_dc, _door_panel(12, 3), 4, 5)
_dc = overlay(_dc, _door_panel(12, 3), 16, 5)
_dc[39] = 'o' * 32                                                            # sill
CLINIC_DOOR = R(_dc)

_do = _door_frame()
_do = overlay(_do, ['~~', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$',
                    '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '~~'], 4, 5)   # panel edge left
_do = overlay(_do, ['~~', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$',
                    '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '$$', '~~'], 26, 5)  # panel edge right
_do[39] = 'oooo' + '0' * 24 + 'oooo'                                          # sill
CLINIC_DOOR_OPEN = R(_do)

# ------------------------------------------------------------------ kennel cage 32x40 (v0.10): steel box, lit interior with a blue
# blanket, 'o' wire bars every 4 px, a '#' tray lip and base. Open: the box is 26 wide and the wire door is swung out to the
# right as a thin barred panel. Cone: a closed kennel with a small patient wearing the cone of shame (props_ward concept).
PATIENT_CONE = R([
    "..oWWWWWWo..",
    ".oWwWWWWwWo.",
    ".oWwBBBBwWo.",
    ".oWwBgBgwWo.",
    ".oWwBBBBwWo.",
    "..oWwBBwWo..",
    "...oWWWWo...",
    "...oBBBBo...",
    "..oBBBBBBo..",
    "..oBBBBBBo..",
    "..oBoBBoBo..",
    "..oo.oo.oo..",
])


def _kennel(open_door=False, patient=None):
    w = 26 if open_door else 32
    rows = ['.' * 32] * 40
    body = box(w, 40, '#', top='&')
    body[1] = 'o' + '&' * (w - 2) + 'o'
    body[2] = 'o' + '%' * (w - 2) + 'o'
    inner = box(w - 4, 28, '_', edge='0')                                      # lit interior rows 3..30
    for y in range(1, 27):
        inner[y] = '00' + inner[y][2:]
    inner = overlay(inner, ['|' * (w - 6)] * 5 + ['/' * (w - 6)], 1, 21)        # blanket
    inner = overlay(inner, ['6' * (w - 6)], 1, 23)                              # blanket fold
    body = overlay(body, inner, 2, 3)
    if patient is not None:
        body = overlay(body, patient, (w - 12) // 2, 12)
    body[31] = 'o' + '%' * (w - 2) + 'o'                                        # tray lip rows 31..33
    body[32] = 'o' + '#' * (w - 2) + 'o'
    body[33] = 'o' + '#' * (w - 2) + 'o'
    body[34] = 'o' * w
    body = overlay(body, ['%' * (w - 4)], 2, 36)                                # base vent
    if not open_door:
        bars = []
        for y in range(27):
            bars.append(''.join('o' if x % 4 == 0 else '.' for x in range(w - 6)))
        body = overlay(body, bars, 3, 4)
        body = overlay(body, ['o' * (w - 6)], 3, 4)
        body = overlay(body, ['o' * (w - 6)], 3, 30)
        body = overlay(body, ['oo', 'o&', 'oo'], w - 5, 16)                     # latch
    rows = overlay(rows, body, 0, 0)
    if open_door:
        door = ['o' * 6] + ['o.o.oo'] * 25 + ['o' * 6]                          # the wire door, edge-on, swung out right
        door = overlay(door, ['&'] * 25, 5, 1)
        rows = overlay(rows, door, 26, 4)
        rows = overlay(rows, ['o' * (w - 6)], 3, 4)
        rows = overlay(rows, ['o' * (w - 6)], 3, 30)
    return rows


KENNEL = R(_kennel())
KENNEL_OPEN = R(_kennel(open_door=True))
KENNEL_CONE = R(_kennel(patient=PATIENT_CONE))

# ------------------------------------------------------------------ nurse station 96x32 (v0.10): white counter with the treat jar,
# two food bowls and a clipboard ON it; steel front with a teal stripe and a call bell (props_ward concept)
_ns = ['.' * 96] * 32
_ns = overlay(_ns, box(96, 10, '_', top='0', bottom='0'), 0, 6)               # counter top rows 6..15
_ns = overlay(_ns, box(96, 16, '&', top='%', bottom='%'), 0, 16)             # steel front rows 16..31
_ns = overlay(_ns, ['$' * 94, '~' * 94], 1, 19)                              # teal stripe
_ns = overlay(_ns, TREAT_JAR, 12, 3)
_ns = overlay(_ns, FOOD_BOWLS, 40, 6)
_ns = overlay(_ns, ['oooooooooo', 'o&&&&&&&&o', 'o&oooooo&o', 'o&&&&&&&&o', 'o&oooooo&o', 'oooooooooo'], 72, 7)   # clipboard
_ns = overlay(_ns, ['..o..', '.o%o.', 'o%%%o', 'ooooo'], 26, 10)             # call bell
NURSE_STATION = R(_ns)

# ================================================================== v0.6 props: theatre kit, wall decor, side door
# ------------------------------------------------------------------ prep sign 16x10: teal plaque, white border, red cross
_ps = box(16, 10, '$', top='$')
_ps = overlay(_ps, ['W' * 14], 1, 1)
_ps = overlay(_ps, ['W' * 14], 1, 8)
for y in range(1, 9):
    _ps[y] = 'oW' + _ps[y][2:14] + 'Wo'
_ps = overlay(_ps, ['.!!.', '!!!!', '!!!!', '.!!.'], 6, 3)
PREP_SIGN = R(_ps)

# ------------------------------------------------------------------ surgical lamp (v0.10): three flat pieces.
# pluto_lamp_head 48x40 hangs OVER the actors (height off ground +2): a round steel dish seen from below-front, five 'K' bulbs
# behind '^' glass, a stem at the top where the arm joins. pluto_lamp_arm 48x40 (+0.5) runs from a wall mount at its top-left
# down-right to the head's stem. pluto_lamp_pool 64x24 (-1.4) is the pale light pool on the floor, dithered so it reads translucent.
def _ellipse(w, h, cx, cy, rx, ry, rings):
    """rings: [(max_d, key), ...] from the outside in; d = normalised squared distance from the centre."""
    rows = []
    for y in range(h):
        row = []
        for x in range(w):
            d = ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2
            key = '.'
            if d <= 1.0:
                for max_d, k in rings:
                    if d > max_d:
                        key = k
                        break
                else:
                    key = rings[-1][1]
            row.append(key)
        rows.append(''.join(row))
    return rows


_lh = ['.' * 48] * 40
_dish = _ellipse(48, 40, 24.0, 22.0, 22.5, 16.5, [(0.86, 'o'), (0.62, '%'), (0.50, '&'), (0.0, '^')])
for bx, by in ((24, 22), (15, 17), (33, 17), (15, 27), (33, 27)):
    _dish = overlay(_dish, _ellipse(9, 9, 4.5, 4.5, 4.4, 4.4, [(0.5, '&'), (0.0, 'K')]), bx - 4, by - 4)
_lh = overlay(_lh, _dish, 0, 0)
_lh = overlay(_lh, ['..oooo..', '.o%%%%o.', 'o%&&&&%o', 'o%&&&&%o', 'o%%%%%%o', '.oooooo.'], 20, 0)   # stem / handle
LAMP_HEAD = R(_lh)

_la = ['.' * 48] * 40
_la = overlay(_la, box(10, 10, '#', top='%'), 0, 0)                   # wall mount plate (top-left)
_la = overlay(_la, ['o%o', 'o%o'], 3, 2)                               # screw
_la = overlay(_la, ['oooo', 'o%&o', 'o%&o', 'o%&o', 'oooo'], 8, 3)    # first joint
# upper arm: 12 px across, 4 px thick, sloping down to the elbow
for i in range(13):
    _la = overlay(_la, ['o', '&', '%', 'o'], 11 + i, 5 + (i * 4) // 12)
_la = overlay(_la, ['oooooo', 'o%&&%o', 'o%&&%o', 'o%&&%o', 'oooooo'], 22, 7)   # elbow knob
# lower arm: from the elbow down-right to the head's stem at the bottom-right corner
for i in range(24):
    _la = overlay(_la, ['o&%o'], 26 + (i * 18) // 24, 11 + i)
_la = overlay(_la, ['oooo', 'o&%o', 'oooo'], 44, 35)                  # pin into the stem
LAMP_ARM = R(_la)

_lp = ['.' * 64] * 24
_pool = _ellipse(64, 24, 32.0, 12.0, 31.5, 11.5, [(0.0, '8')])
for y in range(24):
    row = list(_pool[y])
    for x in range(64):
        d = ((x + 0.5 - 32.0) / 31.5) ** 2 + ((y + 0.5 - 12.0) / 11.5) ** 2
        if row[x] == '8' and d > 0.62 and (x + y) % 2 == 0:
            row[x] = '.'                                                # dithered rim = soft edge
        elif row[x] == '8' and d < 0.2 and (x + y) % 2 == 0:
            row[x] = 'K'                                                # hot centre
    _pool[y] = ''.join(row)
_lp = overlay(_lp, _pool, 0, 0)
LAMP_POOL = R(_lp)

# ------------------------------------------------------------------ monitor cart 24x32: heartbeat monitor on a steel cart, keyboard shelf, wheels
_mc = ['.' * 24] * 32
_mc = overlay(_mc, box(20, 12, '#', top='%'), 2, 0)                  # monitor bezel
_mc = overlay(_mc, [
    "......e.........",
    ".....e.e........",
    "eeeee...e.eeeeee",
    "........e.e.....",
    ".........e......",
], 4, 3)
_mc = overlay(_mc, ['o%%o', 'o%%o', 'o%%o'], 10, 12)                 # post
_mc = overlay(_mc, box(24, 5, '&', top='K'), 0, 15)                  # keyboard shelf
_mc = overlay(_mc, ['o_o_o_o_o_o_o_o_o_'], 3, 17)                    # keys
_mc = overlay(_mc, box(24, 8, '%', top='&', bottom='#'), 0, 20)      # cart body
for x in (1, 7, 13, 19):
    _mc = overlay(_mc, ['.oo.', 'o##o', 'o##o', '.oo.'], x, 28)      # wheels
MONITOR_CART = R(_mc)

# ------------------------------------------------------------------ vaccine fridge 24x40: white fridge, glass door with rows of blue vials, steel handle
_vf = box(24, 40, '_', top='0', bottom='0')
for y in range(1, 39):
    _vf[y] = _vf[y][:21] + '0' + _vf[y][22:]                          # right-side shade
_vf = overlay(_vf, box(16, 26, '^'), 3, 4)                           # glass door
for sy in (8, 14, 20):
    _vf = overlay(_vf, ['o*o*o*o*o*o*', '.*.*.*.*.*.*', '.*.*.*.*.*.*', 'oooooooooooo'], 5, sy)  # vials on shelves
_vf = overlay(_vf, ['o&o'] * 10, 19, 12)                             # handle
_vf = overlay(_vf, ['o' + '0' * 22 + 'o', 'o' + '_' * 22 + 'o'], 0, 32)   # compressor lip
_vf = overlay(_vf, ['o' * 22, '0' * 22, 'o' * 22, '0' * 22], 1, 34)  # grille slats
VACCINE_FRIDGE = R(_vf)

# ------------------------------------------------------------------ intercom 10x12: steel box, speaker grille of dots, red light
_ic = box(10, 12, '%', top='&')
_ic = overlay(_ic, ['#.#.#.#', '.#.#.#.', '#.#.#.#', '.#.#.#.'], 2, 3)
_ic = overlay(_ic, ['!'], 4, 9)
_ic = overlay(_ic, ['o'], 7, 9)
INTERCOM = R(_ic)

# ------------------------------------------------------------------ wall tv 32x20: black bezel, blue screen with a glint, steel bracket
_tv = ['.' * 32] * 20
_tv = overlay(_tv, box(32, 16, '#'), 0, 0)
_tv = overlay(_tv, box(28, 12, '*', edge='*'), 2, 2)
_tv = overlay(_tv, ['KKK', 'K..', 'K..'], 4, 4)
_tv = overlay(_tv, ['o&&o', 'o&&o'], 14, 16)                          # bracket neck
_tv = overlay(_tv, ['o' + '&' * 10 + 'o', 'o' * 12], 10, 18)         # bracket plate
WALL_TV = R(_tv)

# ------------------------------------------------------------------ side door 16x32: plain steel door, small window, handle
_sd = box(16, 32, '&', top='%')
for y in range(1, 31):
    _sd[y] = 'o%' + _sd[y][2:14] + '%o'                              # steel frame
_sd = overlay(_sd, box(8, 8, '^'), 4, 4)                             # window
_sd = overlay(_sd, ['ooooo', 'o###o', 'ooooo'], 9, 16)               # handle
_sd = overlay(_sd, ['%' * 12], 2, 24)                                # kick plate seam
SIDE_DOOR = R(_sd)

# ================================================================== v0.10: the concept pass (reference/gemini/past_concepts)
# ------------------------------------------------------------------ double glass cabinet 64x56: two '^' doors, three shelves each
# of jars ('?', '!', '*', ':') and syringe boxes, '&' body with a 'K' top and a '%'/'#' plinth
def _jar(w, h, colour):
    return ['.' + 'o' * (w - 2) + '.'] + ['o' + colour * (w - 2) + 'o'] * (h - 2) + ['o' * w]


def _syringe_box(w, h):
    rows = box(w, h, '_', top='0')
    rows = overlay(rows, ['**' * ((w - 4) // 2)], 2, h // 2)
    return rows


def _shelf(items):
    """One 26x13 shelf: items (x, rows) stand on the 'o' shelf line at the bottom."""
    rows = ['^' * 26] * 12 + ['o' * 26]
    for x, item in items:
        rows = overlay(rows, item, x, 12 - len(item))
    return rows


_SHELVES = [
    [(1, _jar(5, 7, '?')), (7, _jar(5, 8, '!')), (13, _syringe_box(12, 6))],
    [(1, _jar(6, 8, '*')), (8, _jar(4, 6, ':')), (13, _jar(5, 7, '!')), (19, _jar(6, 8, '?'))],
    [(1, _syringe_box(10, 5)), (12, _jar(5, 8, ':')), (18, _jar(7, 7, '*'))],
]
_cw = box(64, 56, '&', top='K')
_cw[1] = 'o' + 'K' * 62 + 'o'
for dx in (3, 33):
    door = ['o' * 28] + ['o' + r + 'o' for shelf in _SHELVES for r in _shelf(shelf)] + ['o' * 28]
    _cw = overlay(_cw, door, dx, 3)
_cw = overlay(_cw, ['o&o', 'o&o', 'o&o', 'o&o'], 28, 24)                      # handles
_cw = overlay(_cw, ['o&o', 'o&o', 'o&o', 'o&o'], 33, 24)
_cw[51] = 'o' + '%' * 62 + 'o'
_cw[52] = 'o' + '%' * 62 + 'o'
_cw[53] = 'o' + '#' * 62 + 'o'
_cw[54] = 'o' + '#' * 62 + 'o'
CABINET_WIDE = R(_cw)

# ------------------------------------------------------------------ wall face 480x32: the south face of a zone wall (tiles_and_walls
# concept): dark top strip with a '%' highlight, white tile panel with '0' grout, teal skirting with a '~' shadow. The gapped
# variant is transparent at px 224..255 (cells 14..15) where the door stands.
def wall_face(door_gap):
    rows = []
    for y in range(32):
        row = []
        for x in range(480):
            if door_gap and 224 <= x < 256:
                row.append('.')
            elif y == 0:
                row.append('o')
            elif y == 1:
                row.append('%')
            elif y in (2, 3):
                row.append('#')
            elif y == 4:
                row.append('o')
            elif 5 <= y < 25:
                row.append('0' if (x % 16 == 15 or y == 15) else '_')
            elif y == 25:
                row.append('o')
            elif y < 30:
                row.append('$')
            elif y == 30:
                row.append('~')
            else:
                row.append('o')
        rows.append(''.join(row))
    return R(rows)


WALL_FACE = wall_face(True)
WALL_FACE_SOLID = wall_face(False)

# ------------------------------------------------------------------ zone floors: 16x16 white tiles with a '0' grout line right and
# bottom; about one tile in thirty is a variant (paw print, hairline crack, rarely a drain grate), scattered by a seeded
# generator so the PNG is reproducible (one in twelve, as first tried, made the floor look dirty). The top two rows are a '0' shadow band under the wall to the north.
_TILE = ['_' * 15 + '0'] * 15 + ['0' * 16]
_TILE_DRAIN = overlay(_TILE, ['oooooooo', 'o666666o', 'o6#6#6#o', 'o66#6#6o', 'o6#6#6#o', 'o66#6#6o', 'o666666o', 'oooooooo'], 4, 4)
_TILE_PAW = overlay(_TILE, ['.BB.BB.', 'BBBBBBB', '.BBBBB.', '..BBB..'], 4, 5)
_TILE_CRACK = overlay(_TILE, ['0....', '.0...', '.00..', '..000', '..0..', '.0...'], 5, 4)


def floor(cells_wide, cells_high, seed):
    import random
    rnd = random.Random(seed)
    rows = ['.' * (cells_wide * 16)] * (cells_high * 16)
    for ty in range(cells_high):
        for tx in range(cells_wide):
            roll = rnd.randrange(30)
            tile = _TILE
            if roll == 0:
                tile = rnd.choice((_TILE_DRAIN, _TILE_PAW, _TILE_CRACK, _TILE_PAW, _TILE_CRACK, _TILE_CRACK))
            rows = overlay(rows, tile, tx * 16, ty * 16)
    rows[0] = '0' * (cells_wide * 16)
    rows[1] = '0' * (cells_wide * 16)
    return R(rows)


FLOOR_WAITING = floor(30, 13, seed=1)    # y 0..12
FLOOR_WARD = floor(30, 17, seed=2)       # y 15..31
FLOOR_THEATRE = floor(30, 18, seed=3)    # y 34..51

OBJECTS = [
    Obj('pluto_exam_table', 'exam_table', EXAM_TABLE, ('low', 4, 0, 72, 16)),
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
    Obj('pluto_reception_desk', 'reception_desk', RECEPTION_DESK, ('high', 0, 0, 112, 16)),
    Obj('pluto_chair', 'chair', CHAIR, ('low', 2, 0, 20, 8)),
    Obj('pluto_plant', 'plant', PLANT, ('high', 4, 0, 8, 8)),
    Obj('pluto_window', 'window', WINDOW, None, 0.5),
    Obj('pluto_xray_box', 'xray_box', XRAY_BOX, None, 0.5),
    Obj('pluto_med_shelf', 'med_shelf', MED_SHELF, ('high', 0, 0, 32, 16)),
    Obj('pluto_clock', 'clock', CLOCK, None, 0.5),
    Obj('pluto_fish_tank', 'fish_tank', FISH_TANK, ('high', 0, 0, 32, 12)),
    Obj('pluto_sharps_bin', 'sharps_bin', SHARPS_BIN, ('low', 0, 0, 12, 6)),
    Obj('pluto_iv_stand', 'iv_stand', IV_STAND, ('low', 0, 0, 12, 6)),
    Obj('pluto_treat_jar', 'treat_jar', TREAT_JAR, None, -1.5),
    Obj('pluto_food_bowls', 'food_bowls', FOOD_BOWLS, None, -1.5),
    Obj('pluto_litter_box', 'litter_box', LITTER_BOX, ('low', 0, 0, 20, 8)),
    Obj('pluto_floor_mat', 'floor_mat', FLOOR_MAT, None, -2.5),
    Obj('pluto_paw_prints', 'paw_prints', PAW_PRINTS, None, -2.0),
    Obj('pluto_wet_floor_sign', 'wet_floor_sign', WET_FLOOR_SIGN, ('low', 0, 0, 12, 6)),
    # v0.5: the zone door (ClinicDoor.cs swaps in EXTRA_PNGS['clinic_door_open'] and drops the collider), the ward
    Obj('pluto_clinic_door', 'clinic_door', CLINIC_DOOR, ('high', 0, 0, 32, 32)),
    Obj('pluto_kennel', 'kennel', KENNEL, ('high', 0, 0, 32, 16)),
    Obj('pluto_kennel_open', 'kennel_open', KENNEL_OPEN, ('high', 0, 0, 32, 16)),
    Obj('pluto_kennel_cone', 'kennel_cone', KENNEL_CONE, ('high', 0, 0, 32, 16)),
    Obj('pluto_nurse_station', 'nurse_station', NURSE_STATION, ('high', 0, 0, 96, 12)),
    # v0.6: theatre kit, wall decor, the side door
    Obj('pluto_prep_sign', 'prep_sign', PREP_SIGN, None, 0.5),
    Obj('pluto_monitor_cart', 'monitor_cart', MONITOR_CART, ('low', 0, 0, 24, 10)),
    Obj('pluto_vaccine_fridge', 'vaccine_fridge', VACCINE_FRIDGE, ('high', 0, 0, 24, 16)),
    Obj('pluto_intercom', 'intercom', INTERCOM, None, 0.5),
    Obj('pluto_wall_tv', 'wall_tv', WALL_TV, None, 0.5),
    Obj('pluto_side_door', 'side_door', SIDE_DOOR, None, 0.5),
    # v0.10: the lamp in three layers (the head hangs over the actors), the wide cabinet, the wall faces, the zone floors
    Obj('pluto_lamp_head', 'lamp_head', LAMP_HEAD, None, 2.0),
    Obj('pluto_lamp_arm', 'lamp_arm', LAMP_ARM, None, 0.5),
    Obj('pluto_lamp_pool', 'lamp_pool', LAMP_POOL, None, -1.4),
    Obj('pluto_cabinet_wide', 'cabinet_wide', CABINET_WIDE, ('high', 0, 0, 64, 20)),
    Obj('pluto_wall_face', 'wall_face', WALL_FACE, None, 0.5),
    Obj('pluto_wall_face_solid', 'wall_face_solid', WALL_FACE_SOLID, None, 0.5),
    Obj('pluto_floor_waiting', 'floor_waiting', FLOOR_WAITING, None, -4.0),
    Obj('pluto_floor_ward', 'floor_ward', FLOOR_WARD, None, -4.0),
    Obj('pluto_floor_theatre', 'floor_theatre', FLOOR_THEATRE, None, -4.0),
]

# Extra sprites that are not placeable props: alternate frames a component swaps in (file stem -> rows).
EXTRA_PNGS = {'clinic_door_open': CLINIC_DOOR_OPEN}

# Placements (game cells) by zone. The sprite's lower-left corner sits on the cell.
# Waiting room y 1..12: carrier and spawn bottom-left, orange chairs along the west wall and the south wall, reception on the east.
# Ward y 15..31: kennels along both long walls, nurse station in the middle, medical kit along the north wall.
# Theatre y 34..51: cabinets, fridge and sink along the north wall, the strapped table under the lamp in the middle.
# The zone wall faces (flat, +0.5) sit on the '#' rows of the map; wall decor hangs on them.
PROPS = [
    ('pluto_floor_waiting', (0.0, 0.0)), ('pluto_floor_ward', (0.0, 15.0)), ('pluto_floor_theatre', (0.0, 34.0)),
    ('pluto_wall_face', (0.0, 13.0)), ('pluto_wall_face', (0.0, 32.0)), ('pluto_wall_face_solid', (0.0, 52.0)),
    # --- waiting room
    ('pluto_carrier', (1.5, 2.5)),
    ('pluto_chair', (0.75, 4.5)), ('pluto_chair', (0.75, 6.0)), ('pluto_chair', (0.75, 7.5)), ('pluto_chair', (0.75, 9.0)),
    ('pluto_chair', (8.0, 0.75)), ('pluto_chair', (9.5, 0.75)), ('pluto_chair', (11.0, 0.75)), ('pluto_chair', (12.5, 0.75)), ('pluto_chair', (14.0, 0.75)),
    ('pluto_wall_tv', (3.5, 13.2)),
    ('pluto_window', (7.0, 13.2)), ('pluto_clock', (10.5, 13.4)),
    ('pluto_intercom', (16.2, 13.4)),
    ('pluto_poster', (12.0, 13.2)),
    ('pluto_wet_floor_sign', (14.5, 5.0)),
    ('pluto_paw_prints', (9.0, 3.5)),
    ('pluto_toy_mouse', (11.0, 7.0)),
    ('pluto_reception_desk', (19.0, 10.0)),
    ('pluto_floor_mat', (19.5, 7.5)),
    ('pluto_plant', (26.5, 10.5)),
    ('pluto_fish_tank', (26.0, 5.5)),
    ('pluto_scratch_post', (26.5, 3.0)),
    ('pluto_plant', (26.5, 1.0)),
    # --- ward
    ('pluto_kennel', (1.0, 16.5)), ('pluto_kennel_open', (1.0, 20.0)), ('pluto_kennel_cone', (1.0, 25.0)), ('pluto_kennel_open', (1.0, 28.5)),
    ('pluto_kennel_open', (27.0, 16.5)), ('pluto_kennel_cone', (27.0, 20.0)), ('pluto_kennel_open', (27.0, 25.0)), ('pluto_kennel', (27.0, 28.5)),
    ('pluto_nurse_station', (12.0, 23.0)),
    ('pluto_prep_sign', (11.5, 32.4)),
    ('pluto_side_door', (0.0, 22.5)), ('pluto_side_door', (29.0, 22.5)),
    ('pluto_litter_box', (10.0, 20.5)),
    ('pluto_xray_box', (5.0, 32.3)), ('pluto_med_shelf', (8.0, 29.5)),
    ('pluto_iv_stand', (19.5, 29.5)), ('pluto_sharps_bin', (21.5, 30.0)), ('pluto_litter_box', (24.0, 30.0)),
    ('pluto_paw_prints', (14.0, 17.0)),
    # --- operating theatre
    ('pluto_cabinet_wide', (1.0, 49.0)), ('pluto_vaccine_fridge', (5.5, 49.0)),
    ('pluto_clock', (10.6, 52.4)), ('pluto_poster', (12.0, 52.2)),
    ('pluto_cabinet_wide', (16.0, 49.0)), ('pluto_cabinet_wide', (21.0, 49.0)),
    ('pluto_sink', (25.0, 49.0)), ('pluto_scale', (27.2, 49.0)),
    ('pluto_lamp_pool', (11.0, 40.75)),
    ('pluto_exam_table', (12.0, 41.0)),
    ('pluto_lamp_arm', (10.0, 45.5)),
    ('pluto_lamp_head', (11.5, 43.0)),
    ('pluto_cart', (18.0, 41.5)),
    ('pluto_monitor_cart', (8.0, 41.5)),
    ('pluto_iv_stand', (23.5, 46.5)),
    ('pluto_side_door', (29.0, 39.5)),
    ('pluto_cone', (22.0, 45.0)),
    ('pluto_toy_mouse', (7.0, 39.0)),
    ('pluto_toy_ball', (20.0, 37.0)),
    ('pluto_feather_wand', (16.0, 36.5)),
    ('pluto_scratch_post', (24.5, 37.5)),
    ('pluto_paw_prints', (8.0, 36.0)),
]


def write(project):
    out = os.path.join(project, 'Resources', 'Objects')
    paths = []
    for o in OBJECTS:
        p = os.path.join(out, o.png + '.png')
        save(o.rows, p)
        paths.append(p)
    for stem, rows in EXTRA_PNGS.items():
        p = os.path.join(out, stem + '.png')
        save(rows, p)
        paths.append(p)
    return paths


def preview(project):
    p = os.path.join(project, 'docs', 'preview', 'objects-sheet.png')
    rows = [o.rows for o in OBJECTS] + list(EXTRA_PNGS.values())
    sheet([rows[i:i + 6] for i in range(0, len(rows), 6)], p, scale=4)
    return p
