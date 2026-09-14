"""Props of the vet clinic: ASCII sprites, collider specs and where they stand in the room.

OBJECTS: every prop prefab (name -> art + collider). PROPS: placements (name, (x, y)) in room cells,
x to the right and y up from the room's bottom-left corner; the sprite's lower-left corner sits on the cell.
Colliders are (layer, off_x, off_y, w, h) in pixels from the sprite's lower-left; 'high' blocks everything,
'low' blocks walking but bullets fly over it. Decor has no collider and lies flat under actors, except the wall faces and
the decor hung on them, which stand (Obj.stand) so they sort in front of the tileset's wall face.
"""
import os

from vetpixel import R, pad, overlay, save, sheet


class Obj:
    def __init__(self, name, png, rows, collider=None, height_off_ground=0.0, stand=None):
        self.name = name                        # StaticReferences.customObjects key, e.g. pluto_exam_table
        self.png = png                          # file stem under Resources/Objects/
        self.rows = rows                        # ASCII map
        self.collider = collider                # None or (layer, off_x, off_y, w, h) in pixels; layer 'low'|'high'
        self.height_off_ground = height_off_ground
        # standing (perpendicular) sprite; defaults to "has a collider". Wall faces and wall decor stand without one.
        self.stand = (collider is not None) if stand is None else bool(stand)

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

# ------------------------------------------------------------------ wall clock 16x16 (v0.10.1): readable round clock, '#' ring,
# white face with a 'K' glint top-left, ticks at 12/3/6/9, minute hand up, hour hand to three, red centre pin
CLOCK = R([
    ".....oooooo.....",
    "...oo######oo...",
    "..o##KK##__##o..",
    ".o#KKK_______#o.",
    "o#KK___#______#o",
    "o#K____#______#o",
    "o#K____#______#o",
    "o##____!###__##o",
    "o#____________#o",
    "o#____________#o",
    "o#____________#o",
    "o#____________#o",
    ".o#__________#o.",
    "..o##__##__##o..",
    "...oo######oo...",
    ".....oooooo.....",
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

# ------------------------------------------------------------------ paw print 6x6: four toes over a round pad (not a heart)
def paw(key):
    return [r.replace('p', key) for r in [
        ".p..p.",
        "p....p",
        "..pp..",
        ".pppp.",
        ".pppp.",
        "..pp..",
    ]]


# ------------------------------------------------------------------ floor mat 48x24 (v0.10.1): brown doormat, '+' border and
# bottom shade, a trail of four small '+' paw prints (props_waiting_room / level_overview concept)
_mat = box(48, 24, '\\')
_mat[1] = 'o' + '+' * 46 + 'o'
_mat[21] = 'o' + '+' * 46 + 'o'
_mat[22] = 'o' + '+' * 46 + 'o'
for y in range(1, 23):
    _mat[y] = 'o+' + _mat[y][2:46] + '+o'
for y in range(3, 20):
    _mat[y] = _mat[y][:3] + '+' + _mat[y][4:44] + '+' + _mat[y][45:]    # inner stitch line
_mat[3] = _mat[3][:3] + '+' * 42 + _mat[3][45:]
_mat[19] = _mat[19][:3] + '+' * 42 + _mat[19][45:]
for x, y in ((7, 11), (16, 6), (26, 11), (35, 6)):
    _mat = overlay(_mat, paw('+'), x, y)
FLOOR_MAT = R(_mat)

# ------------------------------------------------------------------ paw prints 24x16 (v0.10.1): a faint warm-grey trail (decor)
_pp = ['.' * 24] * 16
for x, y in ((0, 9), (9, 3), (18, 9)):
    _pp = overlay(_pp, paw('6'), x, y)
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


# v0.10.1: the kennel bank (zone2_ward concept). Each unit is 40x48, three cells, two stacked cages of 20 px behind 'o' bars
# every 4 px over a dark '#'/'%' interior, in a steel '&'/'%' frame; units stack touching along the ward's long walls.
# Occupants are drawn first and the bars over them. 'b' in the rows below is the wood key '\' (brown dog), swapped on load.
TABBY_CURLED = R([
    "..o...o...............",
    ".o?o.o?o..oooooooo....",
    ".o??o??ooo7??7??7?oo..",
    "o??????o??7??7??7???o.",
    "o?7??7?o?7??7??7??7??o",
    "o??????o?????????????o",
    "oWW??WWo??????????7??o",
    ".oWWWWo?WWWWWWWWW??7o.",
    "..oooo77??7777777??o..",
    "......oo?????????oo...",
    "........ooooooooo.....",
])
DOG_SITTING = R([r.replace('b', '\\') for r in [
    "...oooooooo...",
    "..obbbbbbbbo..",
    ".o+bbbbbbbb+o.",
    "o++bgbbbbgb++o",
    "o++bbbbbbbb++o",
    "o++bbWWWWbb++o",
    ".o+bbWggWbb+o.",
    "..obbWWWWbbo..",
    "...obbbbbbo...",
    "..obbbbbbbbo..",
    ".obbbWWWWbbbo.",
    ".obbbWWWWbbbo.",
    ".o++o+oo+o++o.",
    "..oo.o..o.oo..",
]])
BLANKET = ['|' * 34, '|' * 34, '/' * 34]

_KW, _KH = 40, 48
_CAGE_TOPS = (3, 23)                                                           # rail rows; interior rows top+1..top+16


def _kennel_unit(upper=None, lower=None, open_lower=False):
    """upper/lower: (rows, x) of an occupant in that cage's 34x16 interior (bottom-aligned), 'blanket', or None."""
    rows = ['.' * _KW] * _KH
    rows[0] = 'o' * _KW
    rows[1] = 'o' + '&' * 38 + 'o'
    rows[2] = 'o' + '%' * 38 + 'o'
    for y in range(3, 43):
        rows[y] = 'o&%' + '#' * 34 + '%#o'
    for ci, top in enumerate(_CAGE_TOPS):
        rows[top] = 'o&%' + 'o' * 34 + '%#o'                                    # top rail
        interior = ['#' * 34] * 2 + ['%' * 34] * 14                             # shadowed back wall, lit floor
        content = upper if ci == 0 else lower
        if content == 'blanket':
            interior = overlay(interior, BLANKET, 0, 13)
        elif content is not None:
            art, ox = content
            interior = overlay(interior, art, ox, 16 - len(art))
        barred = not (ci == 1 and open_lower)
        if barred:
            interior = [''.join('o' if x % 4 == 2 else ch for x, ch in enumerate(r)) for r in interior]
        rows = overlay(rows, interior, 3, top + 1)
        if barred:
            rows = overlay(rows, ['oo', 'o&', 'o&', 'oo'], 34, top + 7)          # latch
        rows[top + 17] = 'o&%' + 'o' * 34 + '%#o'                               # bottom rail
        rows[top + 18] = 'o' + '&' * 38 + 'o'                                   # ledge
        rows[top + 19] = 'o' + '#' * 38 + 'o'
    rows[43] = 'o' + '%' * 38 + 'o'
    rows[44] = 'o' + '#' * 38 + 'o'
    rows[45] = 'o#' + '%#' * 18 + '#o'                                          # base vent
    rows[46] = 'o' + '#' * 38 + 'o'
    rows[47] = 'o' * _KW
    return rows


def _swung_door():
    """12x24 barred door panel swung out to the right: hinge column first, the free edge drops 3 px (seen at an angle)."""
    rows = ['.' * 12] * 24
    rows = [list(r) for r in rows]
    for i in range(12):
        top = (i * 3) // 11
        bottom = top + 20
        for y in range(top, bottom + 1):
            if i in (0, 11) or y in (top, bottom):
                ch = 'o'
            elif i in (1, 10) or y in (top + 1, bottom - 1, top + 10):
                ch = '~' if y == bottom - 1 else '$'
            else:
                ch = 'o' if i % 2 == 0 else '.'
            rows[y][i] = ch
    for y in range(9 + 2, 9 + 4):
        rows[y][9] = '&'                                                        # handle
    return [''.join(r) for r in rows]


def _kennel_open_r(upper):
    rows = [r + '.' * 12 for r in _kennel_unit(upper=upper, lower='blanket', open_lower=True)]
    return overlay(rows, _swung_door(), 40, 24)


KENNEL_CAT = R(_kennel_unit(upper=(TABBY_CURLED, 6), lower='blanket'))
KENNEL_DOG = R(_kennel_unit(upper='blanket', lower=(DOG_SITTING, 10)))
KENNEL_CONE = R(_kennel_unit(upper=(PATIENT_CONE, 11), lower='blanket'))
KENNEL_OPEN_R = R(_kennel_open_r(upper=(DOG_SITTING, 16)))
KENNEL_OPEN_L = R([r[::-1] for r in _kennel_open_r(upper=(TABBY_CURLED, 6))])

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

# ------------------------------------------------------------------ wall face 480x48 (v0.10.1): the south face of a zone wall, three
# cells tall and STANDING (tiles_and_walls concept), so it sorts in front of the tileset's own wall face (see WALL_HOG below).
# Top to bottom: 'o', dark steel top with a '%' highlight, teal stripe, '~', a '0' shadow row, the white '_' panel with '0'
# seams every 32 px, teal skirting, '~', '#', 'o'. The gapped variant is open at px 224..255 in its bottom 32 rows (the door is
# two cells tall); the top 16 rows run on as a lintel and a steel frame lines the opening.
WALL_FACE_H = 48
WALL_PANEL = (9, 38)        # sprite rows (from the top) of the '0' shadow row .. the last white panel row
WALL_BASES = (13.0, 32.0, 52.0)
WALL_HOG = -0.2


def wall_face(door_gap):
    rows = []
    for y in range(WALL_FACE_H):
        row = []
        for x in range(480):
            if y == 0:
                ch = 'o'
            elif y == 2:
                ch = '%'
            elif y < 5:
                ch = '#'
            elif y < 8:
                ch = '$'
            elif y == 8:
                ch = '~'
            elif y == 9:
                ch = '0'
            elif y <= 38:
                ch = '0' if x % 32 == 31 else '_'
            elif y < 45:
                ch = '$'
            elif y == 45:
                ch = '~'
            elif y == 46:
                ch = '#'
            else:
                ch = 'o'
            row.append(ch)
        rows.append(''.join(row))
    if door_gap:
        frame = ['o' * 40, 'o' + '&' * 38 + 'o', 'o' + '%' * 38 + 'o', 'o' + '&' * 38 + 'o'] + ['o&%o' + '.' * 32 + 'o%&o'] * 32
        rows = overlay(rows, frame, 220, 12)
        for y in range(16, WALL_FACE_H):
            rows[y] = rows[y][:224] + '.' * 32 + rows[y][256:]
        rows[WALL_FACE_H - 1] = rows[WALL_FACE_H - 1][:220] + 'oooo' + '.' * 32 + 'oooo' + rows[WALL_FACE_H - 1][260:]
    return R(rows)


WALL_FACE = wall_face(True)
WALL_FACE_SOLID = wall_face(False)


def wall_decor_hog(offset):
    """Height off ground of a standing prop hung `offset` cells above its wall face's base: 0.05 in front of the face at
    every pixel (face z = 2*base - WALL_HOG - H, decor z = 2*(base + offset) - hog - H)."""
    return WALL_HOG + 2.0 * offset + 0.05


# Wall decor: how far above the face's base each piece hangs (cells). One offset per prop, so the same HOG fits every wall
# it hangs on; every sprite lies inside the white panel band (base + 0.6 .. base + 2.35).
WALL_DECOR_OFFSET = {
    'pluto_wall_tv': 0.75, 'pluto_window': 0.75, 'pluto_clock': 1.0, 'pluto_poster': 0.75, 'pluto_intercom': 1.125,
    'pluto_xray_box': 0.75, 'pluto_prep_sign': 1.25, 'pluto_wall_shelf': 0.75,
}


def on_wall(name, x, base):
    return (name, (x, base + WALL_DECOR_OFFSET[name]))


# ------------------------------------------------------------------ wall shelf 32x24 (v0.10.1, replaces the floor medicine shelf):
# two steel boards on the wall with bottles, jars and a box standing on them (zone2_ward concept)
def _board():
    return ['o' * 32, 'o' + '&' * 30 + 'o', 'o' + '%' * 30 + 'o', 'oo' + '.' * 28 + 'oo']


_ws = ['.' * 32] * 24
for bx, item in ((2, _jar(5, 8, '+')), (8, _jar(4, 6, '!')), (13, _syringe_box(9, 5)), (23, _jar(5, 7, '$'))):
    _ws = overlay(_ws, item, bx, 10 - len(item) + 1)
for bx, item in ((3, _jar(4, 6, '*')), (8, _jar(6, 7, ':')), (16, _syringe_box(8, 5)), (25, _jar(4, 5, '!'))):
    _ws = overlay(_ws, item, bx, 20 - len(item) + 1)
_ws = overlay(_ws, _board(), 0, 10)
_ws = overlay(_ws, _board(), 0, 20)
WALL_SHELF = R(_ws)

# ------------------------------------------------------------------ zone floors (v0.10.1): plain 16x16 white tiles with a pale
# '0' grout line right and bottom; a few variant tiles per zone at fixed tiles chosen away from the props: small round drain
# grates, teal paw prints (the concept's paw) and single '0' hairline cracks. The top two rows are a '0' shadow band under the
# wall to the north.
_TILE = ['_' * 15 + '0'] * 15 + ['0' * 16]
_TILE_DRAIN = overlay(_TILE, [
    "...0000...",
    ".00%%%%00.",
    ".0%0000%0.",
    "0%0#0#00%0",
    "0%000000%0",
    "0%0#0#00%0",
    "0%000000%0",
    ".0%0000%0.",
    ".00%%%%00.",
    "...0000...",
], 3, 3)
_TILE_PAW = overlay(_TILE, [
    "..$...$..",
    "$.$...$.$",
    "$.......$",
    "...$$$...",
    "..$$$$$..",
    "..$$$$$..",
    "...$$$...",
], 3, 4)
_TILE_CRACK = overlay(_TILE, [
    "0......",
    ".0.....",
    ".0.....",
    "..0....",
    "...00..",
    ".....0.",
    "......0",
], 4, 4)
FLOOR_TILES = {'drain': _TILE_DRAIN, 'paw': _TILE_PAW, 'crack': _TILE_CRACK}
FLOOR_LIMITS = {'drain': 3, 'paw': 2, 'crack': 2}

# zone floor -> (lower-left cell y, cells high, how many of each variant)
FLOOR_ZONES = {
    'pluto_floor_waiting': (0, 13, {'drain': 2, 'paw': 1, 'crack': 1}),
    'pluto_floor_ward': (15, 17, {'drain': 3, 'paw': 2, 'crack': 2}),
    'pluto_floor_theatre': (34, 18, {'drain': 2, 'paw': 2, 'crack': 1}),
}


def floor(cells_wide, cells_high, variants):
    """variants: {(cell_x, cell_y_from_the_floor's_bottom): kind}."""
    rows = ['.' * (cells_wide * 16)] * (cells_high * 16)
    for ty in range(cells_high):
        for tx in range(cells_wide):
            kind = variants.get((tx, cells_high - 1 - ty))
            rows = overlay(rows, FLOOR_TILES[kind] if kind else _TILE, tx * 16, ty * 16)
    rows[0] = '0' * (cells_wide * 16)
    rows[1] = '0' * (cells_wide * 16)
    return R(rows)


# Placements (game cells) by zone. The sprite's lower-left corner sits on the cell.
# Waiting room y 1..12: carrier and spawn bottom-left, orange chairs along the west wall and the south wall, reception on the east.
# Ward y 15..31: a kennel bank along each long wall, nurse station in the middle, the medical kit under the north wall.
# Theatre y 34..51: cabinets, fridge and sink along the north wall, the strapped table under the lamp, toys in the south-west corner.
# The zone wall faces stand on the '#' rows of the map (base y 13, 32, 52); wall decor hangs inside their white panel.
PROPS = [
    ('pluto_floor_waiting', (0.0, 0.0)), ('pluto_floor_ward', (0.0, 15.0)), ('pluto_floor_theatre', (0.0, 34.0)),
    ('pluto_wall_face', (0.0, 13.0)), ('pluto_wall_face', (0.0, 32.0)), ('pluto_wall_face_solid', (0.0, 52.0)),
    # --- waiting room
    ('pluto_carrier', (1.5, 2.5)),
    ('pluto_chair', (0.75, 4.0)), ('pluto_chair', (0.75, 6.0)), ('pluto_chair', (0.75, 8.0)), ('pluto_chair', (0.75, 10.0)),
    ('pluto_chair', (8.0, 0.75)), ('pluto_chair', (9.5, 0.75)), ('pluto_chair', (11.0, 0.75)), ('pluto_chair', (12.5, 0.75)), ('pluto_chair', (14.0, 0.75)),
    on_wall('pluto_wall_tv', 3.5, 13.0), on_wall('pluto_window', 7.0, 13.0), on_wall('pluto_clock', 10.5, 13.0),
    on_wall('pluto_poster', 12.0, 13.0), on_wall('pluto_intercom', 16.375, 13.0),     # intercom right of the door frame
    ('pluto_wet_floor_sign', (14.5, 5.0)),
    ('pluto_paw_prints', (9.0, 3.5)),
    ('pluto_toy_mouse', (11.0, 7.0)),
    ('pluto_reception_desk', (19.0, 10.0)),
    ('pluto_floor_mat', (19.5, 7.5)),
    ('pluto_plant', (26.5, 10.5)),
    ('pluto_fish_tank', (26.0, 5.5)),
    ('pluto_scratch_post', (26.5, 3.0)),
    ('pluto_plant', (26.5, 1.0)),
    # --- ward: two kennel banks of five stacked units, bottom to top. They start at y 16, not 15: the waiting room's standing
    # wall face (base 13, three cells tall) covers the ward's first row and would hide the bottom unit's lower cage.
    ('pluto_kennel_cat', (0.5, 16.0)), ('pluto_kennel_open_r', (0.5, 19.0)), ('pluto_kennel_cone', (0.5, 22.0)),
    ('pluto_kennel_dog', (0.5, 25.0)), ('pluto_kennel_cat', (0.5, 28.0)),
    ('pluto_kennel_dog', (27.0, 16.0)), ('pluto_kennel_cat', (27.0, 19.0)), ('pluto_kennel_open_l', (26.25, 22.0)),
    ('pluto_kennel_cat', (27.0, 25.0)), ('pluto_kennel_cone', (27.0, 28.0)),
    ('pluto_nurse_station', (12.0, 23.0)),
    on_wall('pluto_xray_box', 4.0, 32.0), on_wall('pluto_prep_sign', 11.5, 32.0), on_wall('pluto_wall_shelf', 18.0, 32.0),
    ('pluto_iv_stand', (10.0, 29.8)), ('pluto_sharps_bin', (17.0, 30.0)), ('pluto_litter_box', (19.5, 30.0)),
    # --- operating theatre
    ('pluto_cabinet_wide', (1.0, 49.0)), ('pluto_vaccine_fridge', (5.5, 49.0)),
    on_wall('pluto_clock', 10.5, 52.0), on_wall('pluto_poster', 12.0, 52.0),
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
    ('pluto_toy_mouse', (2.5, 37.5)), ('pluto_toy_ball', (4.0, 36.5)), ('pluto_feather_wand', (3.0, 39.0)),
    ('pluto_cone', (2.0, 41.5)), ('pluto_scratch_post', (5.5, 36.0)),
]

PROP_OBJECTS = [
    Obj('pluto_exam_table', 'exam_table', EXAM_TABLE, ('low', 4, 0, 72, 16)),
    Obj('pluto_cabinet', 'cabinet', CABINET, ('high', 0, 0, 32, 20)),
    Obj('pluto_cart', 'cart', CART, ('low', 0, 0, 24, 14)),
    Obj('pluto_sink', 'sink', SINK, ('high', 0, 0, 32, 20)),
    Obj('pluto_scale', 'scale', SCALE, None, -1.5),
    Obj('pluto_carrier', 'carrier', CARRIER, ('high', 0, 0, 32, 16)),
    Obj('pluto_poster', 'poster', POSTER, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_poster']), stand=True),
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
    Obj('pluto_window', 'window', WINDOW, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_window']), stand=True),
    Obj('pluto_xray_box', 'xray_box', XRAY_BOX, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_xray_box']), stand=True),
    Obj('pluto_clock', 'clock', CLOCK, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_clock']), stand=True),
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
    Obj('pluto_nurse_station', 'nurse_station', NURSE_STATION, ('high', 0, 0, 96, 12)),
    # v0.6: theatre kit, wall decor, the side door
    Obj('pluto_prep_sign', 'prep_sign', PREP_SIGN, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_prep_sign']), stand=True),
    Obj('pluto_monitor_cart', 'monitor_cart', MONITOR_CART, ('low', 0, 0, 24, 10)),
    Obj('pluto_vaccine_fridge', 'vaccine_fridge', VACCINE_FRIDGE, ('high', 0, 0, 24, 16)),
    Obj('pluto_intercom', 'intercom', INTERCOM, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_intercom']), stand=True),
    Obj('pluto_wall_tv', 'wall_tv', WALL_TV, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_wall_tv']), stand=True),
    Obj('pluto_side_door', 'side_door', SIDE_DOOR, None, 0.5),
    # v0.10: the lamp in three layers (the head hangs over the actors), the wide cabinet
    Obj('pluto_lamp_head', 'lamp_head', LAMP_HEAD, None, 2.0),
    Obj('pluto_lamp_arm', 'lamp_arm', LAMP_ARM, None, 0.5),
    Obj('pluto_lamp_pool', 'lamp_pool', LAMP_POOL, None, -1.4),
    Obj('pluto_cabinet_wide', 'cabinet_wide', CABINET_WIDE, ('high', 0, 0, 64, 20)),
    # v0.10.1: standing wall faces, the wall shelf, the kennel bank
    Obj('pluto_wall_face', 'wall_face', WALL_FACE, None, WALL_HOG, stand=True),
    Obj('pluto_wall_face_solid', 'wall_face_solid', WALL_FACE_SOLID, None, WALL_HOG, stand=True),
    Obj('pluto_wall_shelf', 'wall_shelf', WALL_SHELF, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_wall_shelf']), stand=True),
    Obj('pluto_kennel_cat', 'kennel_cat', KENNEL_CAT, ('high', 0, 0, 40, 48)),
    Obj('pluto_kennel_dog', 'kennel_dog', KENNEL_DOG, ('high', 0, 0, 40, 48)),
    Obj('pluto_kennel_cone', 'kennel_cone', KENNEL_CONE, ('high', 0, 0, 40, 48)),
    Obj('pluto_kennel_open_r', 'kennel_open_r', KENNEL_OPEN_R, ('high', 0, 0, 40, 48)),
    Obj('pluto_kennel_open_l', 'kennel_open_l', KENNEL_OPEN_L, ('high', 12, 0, 40, 48)),
]


def prop_rects():
    """Sprite rectangles (x0, y0, x1, y1) in cells of every placed prop except the floors and wall faces."""
    sizes = {o.name: o.size for o in PROP_OBJECTS}
    rects = []
    for name, (x, y) in PROPS:
        if name in FLOOR_ZONES or name.startswith('pluto_wall_face'):
            continue
        w, h = sizes[name]
        rects.append((x, y, x + w / 16.0, y + h / 16.0))
    return rects


def floor_variants(name):
    """Deterministic variant tiles for one zone floor: {(cell_x, cell_y_from_floor_bottom): kind}. Tiles one cell clear of every
    prop sprite, never on the zone's first or last row, at least four cells apart."""
    import random
    y0, cells_high, counts = FLOOR_ZONES[name]
    rects = prop_rects()

    def clear(cx, cy):
        return all(not (cx - 1 < x1 and x0 < cx + 2 and cy - 1 < y1 and y0_ < cy + 2) for x0, y0_, x1, y1 in rects)

    candidates = [(tx, ty) for ty in range(1, cells_high - 1) for tx in range(1, 29) if clear(tx, y0 + ty)]
    rnd = random.Random(name)
    rnd.shuffle(candidates)
    chosen = {}
    for kind in ('drain', 'paw', 'crack'):
        for _ in range(counts[kind]):
            for c in candidates:
                if c not in chosen and all(max(abs(c[0] - o[0]), abs(c[1] - o[1])) >= 4 for o in chosen):
                    chosen[c] = kind
                    break
    return chosen


FLOOR_VARIANTS = {name: floor_variants(name) for name in FLOOR_ZONES}
FLOOR_WAITING = floor(30, 13, FLOOR_VARIANTS['pluto_floor_waiting'])    # y 0..12
FLOOR_WARD = floor(30, 17, FLOOR_VARIANTS['pluto_floor_ward'])          # y 15..31
FLOOR_THEATRE = floor(30, 18, FLOOR_VARIANTS['pluto_floor_theatre'])    # y 34..51

OBJECTS = PROP_OBJECTS + [
    Obj('pluto_floor_waiting', 'floor_waiting', FLOOR_WAITING, None, -4.0),
    Obj('pluto_floor_ward', 'floor_ward', FLOOR_WARD, None, -4.0),
    Obj('pluto_floor_theatre', 'floor_theatre', FLOOR_THEATRE, None, -4.0),
]

# Extra sprites that are not placeable props: alternate frames a component swaps in (file stem -> rows).
EXTRA_PNGS = {'clinic_door_open': CLINIC_DOOR_OPEN}


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
