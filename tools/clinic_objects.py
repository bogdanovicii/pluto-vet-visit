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

# ------------------------------------------------------------------ kennel cage 32x32: steel box, barred door, tray
def _kennel(open_door):
    rows = box(32, 32, '#', top='&', bottom='%')
    rows[1] = 'o' + '&' * 30 + 'o'
    rows[2] = 'o' + '%' * 30 + 'o'
    # dark interior with a blue blanket
    rows = overlay(rows, box(28, 24, '#', top='#'), 2, 4)
    rows = overlay(rows, ['|' * 22, '/' * 22], 5, 24)
    if not open_door:
        bars = []
        for y in range(22):
            bars.append(''.join('%' if x % 4 == 1 else ('&' if x % 4 == 2 else '.') for x in range(26)))
        rows = overlay(rows, bars, 3, 5)
        rows = overlay(rows, ['o' * 26], 3, 5)
        rows = overlay(rows, ['o' * 26], 3, 26)
        rows = overlay(rows, ['oo', 'o&', 'oo'], 27, 14)                     # latch
    else:
        # door swung outward to the right: a short barred strip at the right edge, interior in full view
        strip = []
        for y in range(22):
            strip.append(''.join('%' if x % 3 == 0 else ('&' if x % 3 == 1 else '.') for x in range(5)))
        rows = overlay(rows, strip, 26, 5)
        rows = overlay(rows, ['o' * 5], 26, 5)
        rows = overlay(rows, ['o' * 5], 26, 26)
        rows = overlay(rows, ['o' * 26], 3, 5)
        rows = overlay(rows, ['o' * 26], 3, 26)
    rows[29] = 'o' + '%' * 30 + 'o'                                          # tray lip
    rows[30] = 'o' + '#' * 30 + 'o'
    return rows


KENNEL = R(_kennel(False))
KENNEL_OPEN = R(_kennel(True))

# ------------------------------------------------------------------ nurse station 48x24: white counter, steel front, teal stripe, clipboard
_ns = ['.' * 48] * 24
_ns = overlay(_ns, box(48, 10, '_', top='0', bottom='0'), 0, 4)               # counter top
_ns = overlay(_ns, box(48, 12, '&', top='%', bottom='%'), 0, 12)             # steel front
_ns = overlay(_ns, ['$' * 46], 1, 15)                                        # teal stripe
_ns[23] = 'o' * 48
_ns = overlay(_ns, ['oooooooo', 'o&&&&&&o', 'o&oooo&o', 'o&&&&&&o', 'o&oooo&o', 'oooooooo'], 32, 0)   # clipboard
_ns = overlay(_ns, ['..o..', '.o%o.', 'o%%%o', 'ooooo'], 8, 0)               # call bell
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

# ------------------------------------------------------------------ surgical lamp 32x32: round steel head, three bulbs, jointed arm up-right
_lamp_head = [
    "....oooooo....",
    "..oo%%%%%%oo..",
    ".o%%&&&&&&%%o.",
    ".o%&&&&&&&&%o.",
    "o%&oo&&&&oo&%o",
    "o%oKKo&&oKKo%o",
    "o%oKKo&&oKKo%o",
    "o%&oooooooo&%o",
    "o%&&&oKKo&&&%o",
    "o%&&&oKKo&&&%o",
    "o%&&&&oo&&&&%o",
    ".o%%&&&&&&%%o.",
    "..oo%%%%%%oo..",
    "....oooooo....",
]
_sl = ['.' * 32] * 32
_sl = overlay(_sl, box(6, 9, '#', top='%'), 26, 1)                  # wall mount plate
_sl = overlay(_sl, ['o' * 12, '&' * 12, '%' * 12, 'o' * 12], 14, 3)  # horizontal arm
_sl = overlay(_sl, ['oooooo', 'o%&&%o', 'o%&&%o', 'oooooo'], 9, 3)  # joint knob
_sl = overlay(_sl, ['o&%o'] * 12, 10, 7)                            # vertical arm down to the head
_sl = overlay(_sl, _lamp_head, 0, 18)
SURGICAL_LAMP = R(_sl)

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

# ------------------------------------------------------------------ strap pad 40x8: two leather straps with buckles across a thin steel strip
_sp = ['.' * 40] * 8
_sp = overlay(_sp, box(40, 4, '&', top='K'), 0, 2)
_strap = ['oooooo', 'o\\\\\\\\o', 'o\\\\\\\\o', 'o\\++\\o', 'o\\++\\o', 'o\\\\\\\\o', 'o\\\\\\\\o', 'oooooo']
_sp = overlay(_sp, _strap, 8, 0)
_sp = overlay(_sp, _strap, 26, 0)
STRAP_PAD = R(_sp)

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
    # v0.5: the zone door (ClinicDoor.cs swaps in EXTRA_PNGS['clinic_door_open'] and drops the collider), the ward
    Obj('pluto_clinic_door', 'clinic_door', CLINIC_DOOR, ('high', 0, 0, 32, 32)),
    Obj('pluto_kennel', 'kennel', KENNEL, ('high', 0, 0, 32, 16)),
    Obj('pluto_kennel_open', 'kennel_open', KENNEL_OPEN, ('high', 0, 0, 32, 16)),
    Obj('pluto_nurse_station', 'nurse_station', NURSE_STATION, ('high', 0, 0, 48, 12)),
    # v0.6: theatre kit, wall decor, the side door, the table straps
    Obj('pluto_prep_sign', 'prep_sign', PREP_SIGN, None, 0.5),
    Obj('pluto_surgical_lamp', 'surgical_lamp', SURGICAL_LAMP, None, 0.5),
    Obj('pluto_monitor_cart', 'monitor_cart', MONITOR_CART, ('low', 0, 0, 24, 10)),
    Obj('pluto_vaccine_fridge', 'vaccine_fridge', VACCINE_FRIDGE, ('high', 0, 0, 24, 16)),
    Obj('pluto_intercom', 'intercom', INTERCOM, None, 0.5),
    Obj('pluto_wall_tv', 'wall_tv', WALL_TV, None, 0.5),
    Obj('pluto_side_door', 'side_door', SIDE_DOOR, None, 0.5),
    Obj('pluto_strap_table_pad', 'strap_pad', STRAP_PAD, None, -1.5),
]

# Extra sprites that are not placeable props: alternate frames a component swaps in (file stem -> rows).
EXTRA_PNGS = {'clinic_door_open': CLINIC_DOOR_OPEN}

# Placements (game cells) by zone. The sprite's lower-left corner sits on the cell.
# Waiting room y 1..12: carrier and spawn bottom-left, chairs along the west wall, reception on the east.
# Ward y 15..31: kennels along both long walls, nurse station in the middle, medical kit along the north wall.
# Theatre y 34..50: the old clinic dressing moved up (cabinets along the north edge, the table in the middle).
PROPS = [
    # --- waiting room
    ('pluto_carrier', (2.0, 1.5)),
    ('pluto_floor_mat', (0.5, 4.0)),
    ('pluto_chair', (1.0, 5.5)), ('pluto_chair', (1.0, 7.0)), ('pluto_chair', (1.0, 8.5)), ('pluto_chair', (1.0, 10.0)),
    ('pluto_wall_tv', (3.5, 11.0)),
    ('pluto_window', (7.0, 10.5)), ('pluto_clock', (10.0, 11.4)),
    ('pluto_intercom', (14.7, 12.2)),
    ('pluto_poster', (12.0, 10.5)),
    ('pluto_wet_floor_sign', (14.5, 5.0)),
    ('pluto_paw_prints', (9.0, 3.5)),
    ('pluto_toy_mouse', (11.0, 7.0)),
    ('pluto_reception_desk', (19.0, 9.5)),
    ('pluto_treat_jar', (21.9, 11.3)),
    ('pluto_plant', (26.5, 10.5)),
    ('pluto_fish_tank', (26.0, 6.0)),
    ('pluto_scratch_post', (26.5, 3.0)),
    ('pluto_plant', (26.5, 1.0)),
    # --- ward
    ('pluto_kennel', (1.0, 16.5)), ('pluto_kennel_open', (1.0, 20.0)), ('pluto_kennel', (1.0, 25.0)), ('pluto_kennel_open', (1.0, 28.5)),
    ('pluto_kennel_open', (27.0, 16.5)), ('pluto_kennel', (27.0, 20.0)), ('pluto_kennel_open', (27.0, 25.0)), ('pluto_kennel', (27.0, 28.5)),
    ('pluto_nurse_station', (12.0, 22.5)),
    ('pluto_prep_sign', (11.5, 31.2)),
    ('pluto_side_door', (0.0, 22.5)), ('pluto_side_door', (29.0, 22.5)),
    ('pluto_food_bowls', (16.0, 21.0)),
    ('pluto_litter_box', (10.0, 20.5)),
    ('pluto_xray_box', (5.0, 30.0)), ('pluto_med_shelf', (8.0, 29.5)),
    ('pluto_iv_stand', (19.5, 29.5)), ('pluto_sharps_bin', (21.5, 30.0)), ('pluto_litter_box', (24.0, 30.0)),
    ('pluto_paw_prints', (14.0, 17.0)),
    # --- operating theatre
    ('pluto_cabinet', (1.0, 48.0)), ('pluto_cabinet', (3.5, 48.0)), ('pluto_cabinet', (6.0, 48.0)),
    ('pluto_vaccine_fridge', (9.0, 48.0)), ('pluto_clock', (11.6, 50.1)),
    ('pluto_poster', (12.0, 48.0)),
    ('pluto_cabinet', (16.0, 48.0)), ('pluto_cabinet', (19.0, 48.0)), ('pluto_cabinet', (22.0, 48.0)), ('pluto_cabinet', (25.0, 48.0)),
    ('pluto_exam_table', (13.0, 41.0)), ('pluto_strap_table_pad', (13.25, 42.4)),
    ('pluto_surgical_lamp', (14.0, 46.0)),
    ('pluto_cart', (18.0, 41.5)),
    ('pluto_monitor_cart', (8.0, 41.5)),
    ('pluto_iv_stand', (11.0, 44.0)),
    ('pluto_side_door', (29.0, 39.5)),
    ('pluto_syringe_tray', (10.0, 45.0)),
    ('pluto_cone', (22.0, 45.0)),
    ('pluto_sink', (25.0, 43.5)),
    ('pluto_scale', (4.0, 43.0)),
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
