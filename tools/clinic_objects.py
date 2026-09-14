"""Props of the vet clinic: ASCII sprites, collider specs and where they stand in the room.

OBJECTS: every prop prefab (name -> art + collider). PROPS: placements (name, (x, y)) in room cells,
x to the right and y up from the room's bottom-left corner; the sprite's lower-left corner sits on the cell.
Colliders are (layer, off_x, off_y, w, h) in pixels from the sprite's lower-left; 'high' blocks everything,
'low' blocks walking but bullets fly over it. Decor has no collider and lies flat under actors, except the wall faces and
the decor hung on them, which stand (Obj.stand) so they sort in front of the tileset's wall face.
"""
import os

from vetpixel import R, pad, overlay, save, sheet


# 0.12.1: HeightOffGround of a standing prop with a collider. Enter the Gungeon keeps the player's sprite at -0.5 and sorts a standing
# sprite by 2 * base - HeightOffGround, so a prop at 0 TIED with Pluto pressed against its collider from the south (his feet sit a
# quarter cell under its base) and the two z-fought: the reception counter's front panel was drawn over him (screenshot 19.44.02).
# At -0.5 a prop sorts exactly like the player standing on its base row: whoever is further south is in front.
STAND_HOG = -0.5


class Obj:
    def __init__(self, name, png, rows, collider=None, height_off_ground=None, stand=None, frames=None, fps=6.0, comment='',
                 extra=()):
        self.name = name                        # StaticReferences.customObjects key, e.g. pluto_exam_table
        self.png = png                          # file stem under Resources/Objects/
        self.rows = frames[0] if frames else rows   # ASCII map (an animated prop's first frame)
        self.collider = collider                # None or (layer, off_x, off_y, w, h) in pixels; layer 'low'|'high'
        # 0.12.1: more (off_x, off_y, w, h) rectangles on the same layer, for footprints one rectangle cannot cover
        self.extra = [tuple(r) for r in extra]
        # standing (perpendicular) sprite; defaults to "has a collider". Wall faces and wall decor stand without one.
        self.stand = (collider is not None) if stand is None else bool(stand)
        if height_off_ground is None:
            height_off_ground = STAND_HOG if (collider is not None and self.stand) else 0.0
        self.height_off_ground = height_off_ground
        # v0.11: None (static) or 2..8 equal-size frames; write() saves frame k >= 2 as <png>_f<k>.png
        self.frames = frames
        self.fps = float(fps)
        self.comment = comment                  # what Pluto thinks when he examines the prop ('' = not examinable)

    @property
    def colliders(self):
        """Every collider rectangle (layer, off_x, off_y, w, h): the main one, then the extra ones."""
        if self.collider is None:
            return []
        return [tuple(self.collider)] + [(self.collider[0],) + r for r in self.extra]

    @property
    def frame_count(self):
        return len(self.frames) if self.frames else 1

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

# ------------------------------------------------------------------ lamp light pool 64x24 (v0.10, -1.4): the pale light pool on the
# floor, dithered so it reads translucent. (0.12.0: the flat lamp head and arm are gone; see pluto_op_lamp.)
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

# ------------------------------------------------------------------ wall face 576x48 (v0.10.1, 480 wide until 0.12.0): the south face of a zone wall, three
# cells tall and STANDING (tiles_and_walls concept), so it sorts in front of the tileset's own wall face (see WALL_HOG below).
# Top to bottom: 'o', dark steel top with a '%' highlight, teal stripe, '~', a '0' shadow row, the white '_' panel with '0'
# seams every 32 px, teal skirting, '~', '#', 'o'. The gapped variant is open at px 224..255 in its bottom 32 rows (the door is
# two cells tall); the top 16 rows run on as a lintel and a steel frame lines the opening.
WALL_FACE_H = 48
WALL_PANEL = (9, 38)        # sprite rows (from the top) of the '0' shadow row .. the last white panel row
# v0.12.0: the room grew from 30 x 54 to 36 x 63 (clinic_room.WIDTH/HEIGHT read these); door gaps at cells 17..18
ROOM_W = 36
ROOM_H = 63
DOOR_GAP_X = 17
DOOR_GAP_PX = DOOR_GAP_X * 16
WALL_BASES = (16.0, 38.0, 61.0)
WALL_HOG = -0.2


def wall_face(door_gap):
    rows = []
    for y in range(WALL_FACE_H):
        row = []
        for x in range(ROOM_W * 16):
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
        g = DOOR_GAP_PX
        frame = ['o' * 40, 'o' + '&' * 38 + 'o', 'o' + '%' * 38 + 'o', 'o' + '&' * 38 + 'o'] + ['o&%o' + '.' * 32 + 'o%&o'] * 32
        rows = overlay(rows, frame, g - 4, 12)
        for y in range(16, WALL_FACE_H):
            rows[y] = rows[y][:g] + '.' * 32 + rows[y][g + 32:]
        rows[WALL_FACE_H - 1] = rows[WALL_FACE_H - 1][:g - 4] + 'oooo' + '.' * 32 + 'oooo' + rows[WALL_FACE_H - 1][g + 36:]
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
    # v0.11
    'pluto_notice_board': 0.75, 'pluto_sign_waiting': 1.5, 'pluto_sign_ward': 1.5, 'pluto_sign_surgery': 1.5,
    # v0.12.0 vet-clinic wall art
    'pluto_xray_cat': 0.75, 'pluto_anatomy_poster': 0.75, 'pluto_vaccine_chart': 0.75, 'pluto_healthy_pets': 0.75,
    'pluto_diploma': 0.75, 'pluto_weight_chart': 0.75, 'pluto_flea_poster': 0.75, 'pluto_whiteboard': 0.75, 'pluto_pet_photos': 0.75,
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
    'pluto_floor_waiting': (0, 16, {'drain': 2, 'paw': 1, 'crack': 1}),
    'pluto_floor_ward': (18, 20, {'drain': 3, 'paw': 2, 'crack': 2}),
    'pluto_floor_theatre': (40, 21, {'drain': 2, 'paw': 2, 'crack': 1}),
}


def floor(cells_wide, cells_high, variants, tone=('_', '0'), stripe_px=None):
    """variants: {(cell_x, cell_y_from_the_floor's_bottom): kind}. tone: the zone's (tile, grout) keys swapped in for '_'/'0'
    (v0.11: the waiting room warmer, the theatre cooler). stripe_px: x of a painted 8 px teal guide stripe ('~' edges, '$' fill)
    running the floor's full height (v0.11: the ward, door to door)."""
    rows = ['.' * (cells_wide * 16)] * (cells_high * 16)
    for ty in range(cells_high):
        for tx in range(cells_wide):
            kind = variants.get((tx, cells_high - 1 - ty))
            rows = overlay(rows, FLOOR_TILES[kind] if kind else _TILE, tx * 16, ty * 16)
    rows[0] = '0' * (cells_wide * 16)
    rows[1] = '0' * (cells_wide * 16)
    if stripe_px is not None:
        rows = [r[:stripe_px - 4] + '~' + '$' * 6 + '~' + r[stripe_px + 4:] if y >= 2 else r for y, r in enumerate(rows)]
    swap = str.maketrans({'_': tone[0], '0': tone[1]})
    return R([r.translate(swap) for r in rows])


FLOOR_TONES = {'pluto_floor_waiting': ('4', 'i'), 'pluto_floor_ward': ('_', '0'), 'pluto_floor_theatre': ('k', 'n')}
WARD_STRIPE_PX = (DOOR_GAP_X + 1) * 16   # the ward's guide stripe is centred on the door gaps' centre line (x 18 cells)


# ================================================================== v0.11: the structured, animated, examinable clinic
def _b(rows):
    """'b' stands for the wood key '\\' in the hand-drawn rows below (readability); swapped on load."""
    return [r.replace('b', '\\') for r in rows]


# ------------------------------------------------------------------ pixel letters 3x5 for the zone signs ('#' = ink)
FONT = {
    'A': [".#.", "#.#", "###", "#.#", "#.#"], 'D': ["##.", "#.#", "#.#", "#.#", "##."],
    'E': ["###", "#..", "##.", "#..", "###"], 'G': [".##", "#..", "#.#", "#.#", ".##"],
    'I': ["###", ".#.", ".#.", ".#.", "###"], 'M': ["#.#", "###", "#.#", "#.#", "#.#"],
    'N': ["##.", "#.#", "#.#", "#.#", "#.#"], 'O': [".#.", "#.#", "#.#", "#.#", ".#."],
    'R': ["##.", "#.#", "##.", "#.#", "#.#"], 'S': [".##", "#..", ".#.", "..#", "##."],
    'T': ["###", ".#.", ".#.", ".#.", ".#."], 'U': ["#.#", "#.#", "#.#", "#.#", "###"],
    'W': ["#.#", "#.#", "#.#", "###", "#.#"], 'Y': ["#.#", "#.#", ".#.", ".#.", ".#."],
    'P': ["##.", "#.#", "##.", "#..", "#.."], 'L': ["#..", "#..", "#..", "#..", "###"],   # v0.12.0: the whiteboard's PLUTO
    ' ': ["...", "...", "...", "...", "..."],
}


def sign(text, w):
    """Teal wall plaque 12 px tall: 'o' outline, '&' screws, white 'W' letters on '$', a '~' shadow row under the text."""
    ink = ['.'.join(FONT[c][y] for c in text) for y in range(5)]
    rows = ['o' * w, 'o&' + '$' * (w - 4) + '&o'] + ['o' + '$' * (w - 2) + 'o'] * 8 + ['o&' + '~' * (w - 4) + '&o', 'o' * w]
    x0 = (w - len(ink[0])) // 2
    for y in range(5):
        row = list(rows[3 + y])
        for i, ch in enumerate(ink[y]):
            if ch == '#':
                row[x0 + i] = 'W'
        rows[3 + y] = ''.join(row)
    return R(rows)


SIGN_WAITING = sign('WAITING ROOM', 56)
SIGN_WARD = sign('WARD', 24)
SIGN_SURGERY = sign('SURGERY', 36)

# ------------------------------------------------------------------ notice board 32x24 (wall): cork board in a dark wood frame,
# a pinned note, a yellow sticky, a LOST CAT poster (a black cat face with 'e' eyes over a red bar) and a blue pin cluster
_nb = ['o' * 32, 'o' + '+' * 30 + 'o'] + ['o+' + 'b' * 28 + '+o'] * 20 + ['o' + '+' * 30 + 'o', 'o' * 32]
_nb = overlay(_b(_nb), _b([                      # cork grain: a few dark flecks
    "b+bbbbbbbbbbbbbbbbbbbbbbbb",
    "bbbbbbbbbbbbbb+bbbbbbbbbbb",
    "bbbbbbbbbbbbbbbbbbbbbbbbbb",
    "bbbbbbb+bbbbbbbbbbbbbbbb+b",
]), 3, 17)
_nb = overlay(_nb, [
    "..!...",
    "______",
    "_000__",
    "______",
    "_00___",
    "______",
    "_000__",
    "______",
    "_0____",
    "______",
], 3, 3)                                                                       # pinned note
_nb = overlay(_nb, [
    ":::::",
    ":000:",
    ":::::",
    ":00::",
    ":::::",
], 10, 9)                                                                      # sticky
_nb = overlay(_nb, [
    "....!...",
    "WWWWWWWW",
    "WoWWWWoW",
    "WooWWooW",
    "WooooooW",
    "WoeooeoW",
    "WooooooW",
    "WWooooWW",
    "WWWWWWWW",
    "W!!!!!!W",
    "WWWWWWWW",
    "WW0000WW",
    "WWWWWWWW",
    "WW00W00W",
    "WWWWWWWW",
], 20, 3)                                                                      # LOST CAT poster
_nb = overlay(_nb, ['.*.', '***', '.*.'], 12, 3)                                # pin cluster
NOTICE_BOARD = R(_nb)

# ------------------------------------------------------------------ coffee table 48x24: wood top with a 'K' far edge and '+' near
# edge, two magazines (pink and blue) and a yellow mug on it, '+' apron, two legs
_ct = ['.' * 48] * 24
_ct = overlay(_ct, _b([
    "oooooooooooooooooooooooooooooooooooooooooooooooo",
    "obbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbo",
    "obbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbo",
    "obbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbo",
    "obbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbo",
    "obbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbo",
    "o++++++++++++++++++++++++++++++++++++++++++++++o",
    "oooooooooooooooooooooooooooooooooooooooooooooooo",
    "..o+++o++++++++++++++++++++++++++++++++++o+++o..",
    "..o+++oooooooooooooooooooooooooooooooooooo+++o..",
]), 0, 8)
for y in range(18, 23):
    _ct = overlay(_ct, ['o++o'], 3, y)
    _ct = overlay(_ct, ['o++o'], 41, y)
_ct = overlay(_ct, ['oooo'], 3, 23)
_ct = overlay(_ct, ['oooo'], 41, 23)
_ct = overlay(_ct, [
    ".oooooooooooo",
    "oHHHHHHHHHHHo",
    "oHWWWWWHHHHHo",
    "oHHHHHHHH:HHo",
    "oHWWWHHHHHHHo",
    "o___________o",
    ".oooooooooooo",
], 5, 5)                                                                       # pink magazine
_ct = overlay(_ct, [
    "ooooooooooo..",
    "o*********o..",
    "o*KK******oo.",
    "o****WWW**o_o",
    "o*********o_o",
    "o__________oo",
    "ooooooooooooo",
], 20, 6)                                                                    # blue magazine, pages fanned
_ct = overlay(_ct, [
    ".oooo..",
    "o::::oo",
    "o:::o.o",
    "o:::o.o",
    "o7777oo",
    ".oooo..",
], 36, 5)                                                                      # mug
COFFEE_TABLE = R(_ct)

# ------------------------------------------------------------------ waiting-room rug 136x104 (flat, under the chair rows): teal field,
# '~' border, a white '_' inner line and a lattice of small '~' diamonds
def _rug(w, h):
    rows = []
    for y in range(h):
        row = []
        for x in range(w):
            e = min(x, y, w - 1 - x, h - 1 - y)
            if e == 0:
                ch = 'o'
            elif e <= 3:
                ch = '~'
            elif e == 5:
                ch = '_'
            else:
                dx, dy = (x - 8) % 16, (y - 8) % 16
                ch = '~' if abs(dx - 8) + abs(dy - 8) in (3,) else '$'
            row.append(ch)
        rows.append(''.join(row))
    return R(rows)


RUG = _rug(136, 104)

# ------------------------------------------------------------------ water cooler 16x32: blue bottle with a 'K' glint, white body with
# a red (hot) and a blue (cold) tap over a steel drip tray, a stack of paper cups on the side, '0' shade down the right
WATER_COOLER = R([
    "....oooooooo....",
    "....o&&&&&&o....",
    "...oo******oo...",
    "..o*KK*******o..",
    "..o*K********o..",
    "..o*K****//**o..",
    "..o**********o..",
    "..o*******//*o..",
    "..o**********o..",
    "...o********o...",
    "....oo****oo....",
    ".oooooooooooooo.",
    "o______________o",
    "o_____________0o",
    "o__oooo__oooo_0o",
    "o__o!!o__o**o_0o",
    "o__oooo__oooo_0o",
    "o_____________0o",
    "o_oooooooooooo0o",
    "o_o%%%%%%%%%%o0o",
    "o_oooooooooooo0o",
    "o_____________0o",
    "o_000000000000_o",
    "o_____________0o",
    "o_____oo______0o",
    "o_____oo______0o",
    "o_____________0o",
    "o_____________0o",
    "o000000000000000",
    "o##############o",
    "o#oo########oo#o",
    "oooooooooooooooo",
])

# ------------------------------------------------------------------ open carrier 32x24: the carrier with its barred door swung
# open to the right and a dark, empty inside (somebody got out)
_cop = list(CARRIER)
_cop = overlay(_cop, ['o' * 10] + ['o' + '/' * 8 + 'o'] + ['o' + '#' * 8 + 'o'] * 11 + ['o' * 10], 20, 8)
_cop = overlay(_cop, [
    "oo..",
    "o_o.",
    "o_oo",
    "oo_o",
    "o_oo",
    "oo_o",
    "o_oo",
    "oo_o",
    "o_oo",
    "oo_o",
    "o_oo",
    "oo_o",
    "o_o.",
    "oo..",
], 28, 8)
_cop = overlay(_cop, ['.W.', 'WwW'], 23, 19)                                 # a tuft of white fur left behind
CARRIER_OPEN = R(_cop)

# ------------------------------------------------------------------ back cabinet 64x32 (behind the reception): wood cabinet, 'K' top
# edge, four doors with '&' knobs; binders ('!', '*', ':', '$') and a stack of files stand on top
_bc = ['.' * 64] * 32
_bc = overlay(_bc, [
    "oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
    "oKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKo",
    "o++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++o",
    "oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
], 0, 10)
_door_rows = ['o' + ('o' + 'b' * 13 + '+o') * 4 + 'bbbbbbb'[:0]]
for y in range(14, 29):
    row = 'o' + ''.join('o' + ('b' if y != 21 else 'b') * 13 + '+' for _ in range(4)) + 'o' * 3
    _bc[y] = row[:64]
_bc = _b(_bc)
for dx in (13, 27, 45, 59):
    _bc = overlay(_bc, ['o&', 'o&'], dx - 2, 20)
_bc[29] = 'o' + '+' * 62 + 'o'
_bc[30] = 'o' + '#' * 62 + 'o'
_bc[31] = 'o' * 64
_bc = overlay(_bc, [
    "ooooooooooooooooo......oooooooooooo........ooooooooooo.",
    "o!!o**o::o$$o!!o.......o__________o........o0000000o...",
    "o!!o**o::o$$o!!o.......o0000000000o.......o_______o....",
    "o!!o**o::o$$o!!o......oooooooooooooo.....ooooooooooo...",
    "o!_o*_o:_o$_o!_o......o____________o.....o_________o...",
    "o!!o**o::o$$o!!o......o000000000000o.....o000000000o...",
    "o!!o**o::o$$o!!o......oooooooooooooo.....ooooooooooo...",
    "o!!o**o::o$$o!!o.......................................",
    "o!!o**o::o$$o!!o.......................................",
    "ooooooooooooooooo......................................",
], 3, 0)
BACK_CABINET = R([r[:64] for r in _bc])

# ------------------------------------------------------------------ theatre side counters 48x32: white '_' top with a '0' edge, two
# steel doors with '&' handles. Left: a stack of folded teal/white towels and the cone of shame on it. Right: a printer with a sheet
# in its tray and a green hand-sanitizer pump bottle.
def _side_counter():
    rows = ['.' * 48] * 32
    rows = overlay(rows, ['o' * 48, 'o' + '_' * 46 + 'o', 'o' + '0' * 46 + 'o', 'o' * 48], 0, 12)
    for y in range(16, 29):
        rows[y] = 'o' + 'o' + '&' * 20 + '%' + 'o' + 'o' + '&' * 20 + '%' + 'o' + 'o'
    rows = overlay(rows, ['o&', 'o&', 'o&'], 20, 20)
    rows = overlay(rows, ['&o', '&o', '&o'], 26, 20)
    rows[29] = 'o' + '#' * 46 + 'o'
    rows[30] = 'o#' + '%' * 44 + '#o'
    rows[31] = 'o' * 48
    return rows


TOWELS = [
    ".oooooooooooo.",
    "o$$$$$$$$$$$~o",
    "o~~~~~~~~~~~~o",
    "oWWWWWWWWWWWwo",
    "owwwwwwwwwwwwo",
    "o$$$$$$$$$$$~o",
    "o~~~~~~~~~~~~o",
    "oWWWWWWWWWWWwo",
    "owwwwwwwwwwwwo",
    "oooooooooooooo",
]
PRINTER = [
    "....oooooooooooo....",
    "....o__________o....",
    "....o_0000000__o....",
    "oooooooooooooooooooo",
    "o&&&&&&&&&&&&&&&&&&o",
    "o%%%%%%%%%%%%tt5!%%o",
    "o%%oooooooooooo%%%%o",
    "o%%o__________o%%%%o",
    "o%%oooooooooooo%%%%o",
    "o##################o",
    "oooooooooooooooooooo",
]
SANITIZER = [
    "...ooo..",
    "..o&&&oo",
    "...o&o..",
    "..ooooo.",
    ".o^^^^^o",
    ".o^55^^o",
    ".o^55^^o",
    ".o_____o",
    ".o^^^^^o",
    ".ooooooo",
]
COUNTER_TOWELS = R(overlay(overlay(_side_counter(), TOWELS, 4, 3), CONE, 30, 3))
COUNTER_PRINTER = R(overlay(overlay(_side_counter(), PRINTER, 4, 2), SANITIZER, 34, 3))

# ------------------------------------------------------------------ theatre floor mat 144x96 (flat, under the operating table and its
# kit): a '~' teal border with a '$' inner line around a pale steel '&' field ruled into tiles by '%' lines
def _table_mat(w, h):
    rows = []
    for y in range(h):
        row = []
        for x in range(w):
            e = min(x, y, w - 1 - x, h - 1 - y)
            if e == 0:
                ch = 'o'
            elif e <= 2:
                ch = '~'
            elif e == 3:
                ch = '$'
            elif x % 16 == 7 or y % 16 == 7:
                ch = '%'
            else:
                ch = '&'
            row.append(ch)
        rows.append(''.join(row))
    return R(rows)


TABLE_MAT = _table_mat(144, 96)

# ------------------------------------------------------------------ animated: reception desk (2 frames) - the monitor shows two
# lines of text and a blinking 'K' cursor
_SCREEN = [
    "************",
    "*____*___***",
    "************",
    "*___*_____**",
    "************",
    "*__*_KK*****",
    "*****KK*****",
]
RECEPTION_DESK_FRAMES = [
    R(overlay(RECEPTION_DESK, _SCREEN, 15, 3)),
    R(overlay(RECEPTION_DESK, _SCREEN[:5] + ["*__*_*******", "************"], 15, 3)),
]

# ------------------------------------------------------------------ animated: fish tank (4 frames) - the orange fish swims right and
# turns back; two bubbles rise 2 px a frame, 8 px apart, so frame 4 loops seamlessly into frame 1
FISH_R = [
    "....ooo..",
    "oo.o???o.",
    "o?o???g?o",
    "oo.o7??o.",
    "....ooo..",
]
FISH_L = [r[::-1] for r in FISH_R]


def _tank_frame(k):
    t = box(32, 24, '*', top='&', bottom='&')
    t = overlay(t, ['o' + '&' * 30 + 'o', 'o' + '%' * 30 + 'o'], 0, 0)
    t = overlay(t, ['o' + '#' * 30 + 'o', 'o' + '%' * 30 + 'o', 'o' * 32], 0, 21)
    t = overlay(t, ['^' * 3] * 17, 2, 3)
    t = overlay(t, ['..$..', '.$$$.', '.$e$.', '$$$$$', '.$$$.', '..$..'], 23, 12)
    t = overlay(t, ['%' * 30, '::%%' * 7 + '::'], 1, 19)
    for i, y0 in enumerate((17, 9)):
        y = 3 + (y0 - 2 * k - 3) % 16
        t = overlay(t, ['K'], 8 + (y // 4) % 2, y)
    fx, fish = ((9, FISH_R), (12, FISH_R), (14, FISH_L), (11, FISH_L))[k]
    t = overlay(t, fish, fx, 8)
    return R(t + _stand)


FISH_TANK_FRAMES = [_tank_frame(k) for k in range(4)]

# ------------------------------------------------------------------ animated: wall clock (2 frames) - a thin '%' second hand ticks
# from six o'clock to seven
CLOCK_FRAMES = [
    R(overlay(CLOCK, ['%', '%', '%'], 7, 8)),
    R(overlay(CLOCK, ['.%', '.%', '%.'], 5, 8)),
]

# ------------------------------------------------------------------ animated: IV stand 16x40 (3 frames) - a drip bag with a 'K' glint on
# a hook, a glass drip chamber where one '*' drop falls, the tube, a steel pole and a five-wheel base
_IV = [
    "...oooooooooo...",
    "...o&&&&&&&&o...",
    "...oooooo%%o....",
    "...o.o..o%%o....",
    "..ooooo.o%%o....",
    ".o^^^^^oo%%o....",
    ".o^K***oo%%o....",
    ".o^****oo%%o....",
    ".o^****oo%%o....",
    ".o^****oo%%o....",
    ".o^****oo%%o....",
    ".o^^^^^oo%%o....",
    "..ooooo.o%%o....",
    "...o^o..o%%o....",
    "..o^^^o.o%%o....",
    "..o^^^o.o%%o....",
    "..o^^^o.o%%o....",
    "..o***o.o%%o....",
    "...ooo..o%%o....",
    "...o*o..o%%o....",
    "...o*o..o%%o....",
    "...o*o..o%%o....",
    "...o*oo.o%%o....",
    "....o**oo%%o....",
    ".....oo*o%%o....",
    "......o*o%%o....",
    "......o*o%%o....",
    "......o*o%%o....",
    "......ooo%%o....",
    "........o%%o....",
    "........o%%o....",
    "........o%%o....",
    "........o%%o....",
    "........o%%o....",
    ".......oo%%oo...",
    "....ooo%%%%%%ooo",
    "...o%%%%%%%%%%%o",
    "...o#oo##o##oo#o",
    "....oo..oo..oo..",
    "................",
]
IV_FRAMES = [R(overlay(_IV, ['*'], 4, 14 + k)) for k in range(3)]

# ------------------------------------------------------------------ theatre: heart monitor 24x40 (6 frames, replaces the monitor cart
# art) - a steel monitor on a pole; the green '5' ECG trace scrolls 3 px a frame (period 18 = 6 frames) under a fixed sweep gap and
# a 'K' write head; a red LED blinks with the beat; a blue blood-pressure cuff with a red bulb hangs on the pole; five-wheel base
_ECG = [5, 5, 5, 5, 5, 4, 1, 7, 5, 5, 5, 5, 4, 4, 5, 5, 5, 5]      # trace row per column of one period


def _monitor_frame(k):
    rows = ['.' * 24] * 40
    rows = overlay(rows, box(24, 16, '%', top='&'), 0, 0)
    rows = overlay(rows, box(22, 12, 't', edge='#'), 1, 1)
    screen = [['t'] * 20 for _ in range(10)]
    for x in range(20):
        screen[_ECG[(x + 3 * k) % 18]][x] = '5'
    for y in range(10):
        for x in (14, 15):
            screen[y][x] = 't'
    screen[_ECG[(13 + 3 * k) % 18]][13] = 'K'
    rows = overlay(rows, [''.join(r) for r in screen], 2, 2)
    rows = overlay(rows, ['!' if k in (0, 3) else '#'], 3, 13)                  # beat LED
    rows = overlay(rows, ['5'], 5, 13)                                           # power LED
    rows = overlay(rows, ['oo', 'o&'], 19, 12)                                   # knob
    for y in range(16, 35):
        rows = overlay(rows, ['o%%o'], 10, y)
    rows = overlay(rows, [                                                       # blood-pressure cuff and bulb
        "ooooo..",
        "o***o..",
        "o*o*o..",
        "o***oo.",
        "ooooo.o",
        "......o",
        ".....oo",
        "....o!o",
        "....o!o",
        ".....o.",
    ], 14, 18)
    rows = overlay(rows, [
        ".......oo%%oo...",
        "....ooo%%%%%%ooo",
        "...o%%%%%%%%%%%o",
        "...o#oo##o##oo#o",
        "....oo..oo..oo..",
    ], 2, 34)
    return R(rows)


HEART_MONITOR_FRAMES = [_monitor_frame(k) for k in range(6)]

# ------------------------------------------------------------------ theatre: anaesthesia machine 32x48 (3 frames) - a steel head with a
# 't' screen and '5' readout, a glass tube where the '&'/'%' bellows rise and fall, a gauge panel, teal and blue gas cylinders, a
# corrugated hose, a 'K' work shelf and wheels
def _bellows(h):
    col = ['^' * 8] * (16 - h) + ['########'] + [('&' * 8) if i % 2 == 0 else ('^' + '%' * 6 + '^') for i in range(h - 1)]
    return col


def _anaesthesia_frame(k):
    rows = ['.' * 32] * 48
    rows = overlay(rows, box(24, 12, '%', top='&'), 8, 0)
    rows = overlay(rows, box(12, 7, 't', edge='#'), 10, 2)
    rows = overlay(rows, ['5.5.55', '55.5.5'], 13, 4)
    rows = overlay(rows, ['o!o', 'o:o', 'o5o'], 26, 2)
    rows = overlay(rows, box(12, 20, '%', top='&'), 8, 11)
    rows = overlay(rows, _bellows((7, 11, 15)[k]), 10, 13)
    rows = overlay(rows, box(12, 20, '&', top='K'), 19, 11)
    for gy in (14, 22):
        rows = overlay(rows, ['.oooo.', 'oKKKKo', 'oK!KKo', 'oKK!Ko', '.oooo.'], 22, gy)
    rows = overlay(rows, ['.ooo.', 'o$$$o'] + ['o$K$o', 'o$$$o'] + ['o$$$o'] * 16 + ['o~~~o', 'ooooo'], 0, 14)
    rows = overlay(rows, ['.ooo.', 'o***o'] + ['o*K*o', 'o***o'] + ['o***o'] * 14 + ['o///o', 'ooooo'], 3, 18)
    for y in range(12, 30):
        rows = overlay(rows, ['#' if y % 2 else 'o'], 31, y)
    rows = overlay(rows, box(32, 4, '&', top='K'), 0, 31)
    rows = overlay(rows, box(28, 9, '%', top='&', bottom='#'), 2, 35)
    rows = overlay(rows, ['oooooooo', 'o######o', 'oooooooo'], 12, 38)
    rows = overlay(rows, ['.oo.' + '.' * 16 + '.oo.', 'o##o' + '.' * 16 + 'o##o', '.oo.' + '.' * 16 + '.oo.'], 4, 44)
    return R(rows)


ANAESTHESIA_FRAMES = [_anaesthesia_frame(k) for k in range(3)]

# ------------------------------------------------------------------ theatre: instrument trolley 24x24 - a 'K'-rimmed steel tray with a
# scalpel, scissors, forceps and a white gauze square; a folded towel on the lower shelf; wheels
INSTRUMENT_TROLLEY = R([
    "........................",
    "oooooooooooooooooooooooo",
    "oKKKKKKKKKKKKKKKKKKKKKKo",
    "oK%%%%%%%%%%%%%%%%%%%%Ko",
    "oK%K####%%oK%Ko%%____%Ko",
    "oK%%%%%%%%%oo%%%%____%Ko",
    "oK%&&&&&&%%%K%K%%____%Ko",
    "oK%%%%%%%%%K%%%K%%%%%%Ko",
    "o&&&&&&&&&&&&&&&&&&&&&&o",
    "oooooooooooooooooooooooo",
    ".o&o................o&o.",
    ".o&o................o&o.",
    ".o&o..oooooooooo....o&o.",
    ".o&o..o$$$$$$$~o....o&o.",
    ".o&o..oWWWWWWWwo....o&o.",
    ".oooooooooooooooooooooo.",
    ".o&&&&&&&&&&&&&&&&&&&&o.",
    ".oooooooooooooooooooooo.",
    ".o&o................o&o.",
    ".o&o................o&o.",
    ".o&o................o&o.",
    "o&&&o..............o&&&o",
    "oo#oo..............oo#oo",
    ".ooo................ooo.",
])

# ------------------------------------------------------------------ theatre: biohazard bin 14x18 - yellow pedal bin, red lid with a
# glint, the three-lobed hazard mark in 'o', a steel pedal
BIOHAZARD_BIN = R([
    "..oooooooooo..",
    ".o!!!!!!!!!!o.",
    "o!!KK!!!!!!!!o",
    "oooooooooooooo",
    "o::::::::::::o",
    "o:::::oo:::::o",
    "o::::o::o::::o",
    "o:::::oo:::::o",
    "o::oo:oo:oo::o",
    "o:o::oooo::o:o",
    "o:oo:o::o:oo:o",
    "o::::::::::::o",
    "o:::::::::::7o",
    "o777777777777o",
    ".oooooooooooo.",
    "...o%%%%%%o...",
    "...oooooooo...",
    "..............",
])

# ------------------------------------------------------------------ ward: supply shelf 48x40 - steel uprights and three '&'/'%'
# boards; cardboard boxes with '+' tape, bandage rolls, a blue glove box, bottles and a big box with a red cross
def _card(w, h, label=None):
    rows = ['o' * w] + _b(['o' + 'b' * (w // 2 - 1) + '+' + 'b' * (w - w // 2 - 2) + '+o'] * (h - 3)) + ['o' + '+' * (w - 2) + 'o', 'o' * w]
    if label:
        rows = overlay(rows, label, (w - len(label[0])) // 2, 2)
    return rows


_ROLL = ['.oooo.', 'o____o', 'o_00_o', 'o____o', '.oooo.']
_ss = ['.' * 48] * 40
for y in range(40):
    _ss[y] = 'o&o' + '.' * 42 + 'o%o'
for bx, item in ((4, _card(14, 9)), (19, _card(10, 7)), (30, _ROLL), (36, _ROLL)):
    _ss = overlay(_ss, item, bx, 12 - len(item))
_ss = overlay(_ss, _ROLL, 33, 2)
for bx, item in ((4, _jar(5, 8, '!')), (10, _jar(4, 6, ':')), (15, box(14, 7, '*', top='&')), (31, _jar(5, 7, '$')), (37, _jar(6, 8, '?'))):
    _ss = overlay(_ss, item, bx, 25 - len(item))
_ss = overlay(_ss, _card(20, 10, ['..!!..', '!!!!!!', '..!!..']), 4, 28)
_ss = overlay(_ss, _card(12, 8), 26, 30)
_ss = overlay(_ss, _ROLL, 39, 33)
for y in (12, 25, 38):
    _ss = overlay(_ss, ['o' * 48, 'o' + '&' * 46 + 'o'], 0, y)
_ss[39] = 'ooo' + '.' * 42 + 'ooo'
SUPPLY_SHELF = R(_ss)

# ------------------------------------------------------------------ ward: scrubs rack 48x40 - a steel rail on two posts with wheels;
# two teal scrub tops, a white coat and a pair of scrub trousers on hangers
SCRUB_TOP = [
    "....oo....",
    "...o..o...",
    "oooooooooo",
    "o$$~oo~$$o",
    "o$$$~~$$$o",
    "o$$$$$$$$o",
    "oo$$$$$$oo",
    ".o$$$$$$o.",
    ".o$$$$$$o.",
    ".o$$$$~$o.",
    ".o$$$$~$o.",
    ".o$$$$$$o.",
    ".o$$$$$$o.",
    ".o~~~~~~o.",
    ".oooooooo.",
]
LAB_COAT = [r.replace('$', 'W').replace('~', 'w') for r in SCRUB_TOP] + [".oW&&&Wo..", ".oooooooo."]
SCRUB_PANTS = [
    "....oo....",
    "...o..o...",
    ".oooooooo.",
    ".o$$$$$$o.",
    ".o$$$$$$o.",
    ".o$$oo$$o.",
    ".o$$oo$$o.",
    ".o$$oo$$o.",
    ".o$~oo~$o.",
    ".o$~oo~$o.",
    ".o$$oo$$o.",
    ".ooo..ooo.",
]
_sr = ['.' * 48] * 40
for y in range(2, 36):
    _sr = overlay(_sr, ['o%o'], 1, y)
    _sr = overlay(_sr, ['o%o'], 44, y)
_sr = overlay(_sr, ['o' * 48, 'o' + '&' * 46 + 'o', 'o' * 48], 0, 2)
for gx, g in ((5, SCRUB_TOP), (16, LAB_COAT), (27, SCRUB_TOP), (37, SCRUB_PANTS)):
    _sr = overlay(_sr, g, gx, 0)
_sr = overlay(_sr, ['o' * 48, 'o' + '%' * 46 + 'o', 'o' * 48], 0, 34)
for wx in (1, 41):
    _sr = overlay(_sr, ['.oo.oo', 'o##o##', '.oo.oo'], wx, 37)
SCRUBS_RACK = R(_sr)

# ------------------------------------------------------------------ ward: medicine trolley 24x32 - pill bottles and a dropper box on a
# steel top, four coloured drawers with '&' handles, wheels
_mt = ['.' * 24] * 32
for bx, item in ((2, _jar(4, 6, '!')), (7, _jar(4, 5, '?')), (12, _syringe_box(9, 6))):
    _mt = overlay(_mt, item, bx, 8 - len(item))
_mt = overlay(_mt, ['o' * 24, 'o' + 'K' * 22 + 'o', 'o' + '%' * 22 + 'o', 'o' * 24], 0, 8)
for i, colour in enumerate('!:*$'):
    y = 12 + 4 * i
    _mt = overlay(_mt, ['o&' + colour * 19 + '%#o'] * 3 + ['o' * 24], 0, y)
    _mt = overlay(_mt, ['o&&o'], 10, y + 1)
_mt = overlay(_mt, ['o' + '#' * 22 + 'o', '.oo.oo' + '.' * 12 + 'oo.oo.', 'o##o##' + '.' * 12 + '##o##o', '.oo.oo' + '.' * 12 + 'oo.oo.'], 0, 28)
MED_TROLLEY = R(_mt)

# ------------------------------------------------------------------ ward: stool 12x14 - teal seat with a glint, steel stem and foot
STOOL = R([
    "..oooooooo..",
    ".o$$$$$$$$o.",
    "o$$KK$$$$$$o",
    "o~~~~~~~~~~o",
    ".oooooooooo.",
    "....o%%o....",
    "....o%%o....",
    "....o%%o....",
    "....o%%o....",
    "...oo%%oo...",
    "..o%%%%%%o..",
    ".o%oo%%oo%o.",
    ".oo..oo..oo.",
    "............",
])

# ================================================================== v0.12.0: vet-clinic wall art and the standing op lamp
# Hand-drawn wall decor for the three north walls (each hangs 0.75 cells above its wall face's base, inside the white panel) and
# one standing surgical lamp that replaces the flat lamp head + arm (the flat head at height +2 drew over the Vet's spawn).
def _blank(w, h):
    return ['.' * w] * h


def _frame(w, h, fill, rim='&', shade='%'):
    """Outlined frame: 'o' edge, a light rim on top/left, a shade rim bottom/right, the fill inside."""
    rows = ['o' * w, 'o' + rim * (w - 2) + 'o']
    rows += ['o' + rim + fill * (w - 4) + shade + 'o' for _ in range(h - 4)]
    rows += ['o' + shade * (w - 2) + 'o', 'o' * w]
    return rows


# ------------------------------------------------------------------ cat X-ray light box 32x24: steel box, two lit films on clips.
# Left film: a cat skull from the front (ears, eye sockets, nose, teeth). Right film: a cat's front paw, four toes of bones.
_xc = _frame(32, 24, '#', rim='%', shade='#')
_SKULL = [
    "/////////////",
    "/&K///////K&/",
    "/KK&/////&KK/",
    "/KKKKKKKKKKK/",
    "/KK/&KKK&/KK/",
    "/KK//KKK//KK/",
    "/KKK&KKK&KKK/",
    "//KKKK/KKKK//",
    "//KKK/K/KKK//",
    "///KKKKKKK///",
    "///K&K&K&K///",
    "////KKKKK////",
    "/////&K&/////",
    "/////////////",
    "/////////////",
    "//&////////&/",
    "/////////////",
    "/////////////",
]
_PAW = [
    "/////////////",
    "/K//K//K//K//",
    "/K//K//K//K//",
    "/&//&//&//&//",
    "/K//K//K//K//",
    "/K//K//K//K//",
    "/&//&//&//&//",
    "//K/K//K/K///",
    "//K/K//K/K///",
    "//&&KKKK&&///",
    "///KKKKKK////",
    "///K&KK&K////",
    "////KKKK/////",
    "////K//K/////",
    "////K//K/////",
    "////&//&/////",
    "////K//K/////",
    "/////////////",
]
_xc = overlay(_xc, ['^' * 28] * 20, 2, 2)                                 # the lit panel behind the films
_xc = overlay(_xc, _SKULL, 2, 4)
_xc = overlay(_xc, _PAW, 17, 4)
_xc = overlay(_xc, ['o&&o'], 6, 3)                                         # film clips
_xc = overlay(_xc, ['o&&o'], 22, 3)
XRAY_CAT = R(_xc)

# ------------------------------------------------------------------ cat anatomy poster 24x24: white sheet, teal title bar, a grey
# cat in profile with its organs (pink lungs, red heart, orange stomach, yellow gut) and label lines on '#' leaders
_ap = box(24, 24, '_', top='0')
_ap = overlay(_ap, ['$' * 22, '$W$WW$WWW$W$WW$WWW$W$$', '~' * 22], 1, 1)
_CAT = [
    "o...o.............o.",
    "oZ.oZo...........oZo",
    "oZZZZo...........oZo",
    "oZeZeZo..........oZo",
    "oZZZZZoooooooooooZo.",
    ".oZZZZHHHZZZZZZZZZo.",
    "..oZZHH!HZ??Z::ZZZo.",
    "..oZZZHHHZ??Z::ZZZo.",
    "...oZZZZZZZZZZZZZo..",
    "...oZo.oZo..oZo.oZo.",
    "...oo..oo...oo..oo..",
]
_ap = overlay(_ap, _CAT, 2, 5)
for lx, ly in ((3, 17), (9, 17), (15, 17)):
    _ap = overlay(_ap, ['#', '#', '%%%%'], lx + 3, ly)
_ap = overlay(_ap, ['0' * 18], 3, 21)
ANATOMY_POSTER = R(_ap)

# ------------------------------------------------------------------ vaccination schedule 32x24: warm paper, teal header with a
# syringe, a 4 x 5 grid ('0' rules) with a cat head and a dog head in the first column, green ticks and one red cross
_vc = box(32, 24, '4', top='i')
_vc = overlay(_vc, ['$' * 30, '$' * 30, '~' * 30], 1, 1)
_vc = overlay(_vc, ['.o.......', 'o*****&##', '.o.......'], 3, 1)         # syringe in the header
_vc = overlay(_vc, ['WW.WWW.W.WW.WWW'], 14, 2)                             # header text
for gy in (5, 9, 13, 17, 21):
    _vc = overlay(_vc, ['i' * 30], 1, gy)
for gx in (8, 13, 18, 23, 28):
    for y in range(5, 22):
        _vc = overlay(_vc, ['i'], gx, y)
_CATHEAD = ['o.o', 'BBB', 'BeB']
_DOGHEAD = ['o.o', '\\\\\\', '\\g\\']
for i, head in enumerate((_CATHEAD, _DOGHEAD, _CATHEAD, _DOGHEAD)):
    _vc = overlay(_vc, head, 3, 6 + 4 * i)
_TICK = ['...5', '5.5.', '.5..']
_CROSS = ['!.!', '.!.', '!.!']
marks = [(0, 0, _TICK), (1, 0, _TICK), (2, 0, _TICK), (3, 0, _TICK),
         (0, 1, _TICK), (1, 1, _TICK), (2, 1, _CROSS),
         (0, 2, _TICK), (1, 2, _TICK), (2, 2, _TICK), (3, 2, _TICK),
         (0, 3, _TICK), (1, 3, _CROSS)]
for cx, cy, mark in marks:
    _vc = overlay(_vc, mark, 9 + 5 * cx, 6 + 4 * cy)
VACCINE_CHART = R(_vc)

# ------------------------------------------------------------------ "healthy pets" poster 16x24: teal border, a red heart with a
# white paw in it, two dark text bars under it
_hp = ['o' * 16, 'o' + '$' * 14 + 'o'] + ['o$' + 'K' * 12 + '~o'] * 20 + ['o' + '~' * 14 + 'o', 'o' * 16]
_hp = overlay(_hp, [
    ".ooo..ooo.",
    "o!H!oo!!!o",
    "o!HW!W!W!o",
    "o!!!!!!!!o",
    ".o!!WWW!o.",
    "..o!WWW!o.",
    "...o!!!o..",
    "....o!o...",
    ".....o....",
], 3, 3)
_hp = overlay(_hp, ['#' * 10, '.' * 10, '%' * 8], 3, 14)
_hp = overlay(_hp, ['$' * 6], 5, 19)
HEALTHY_PETS = R(_hp)

# ------------------------------------------------------------------ framed vet diploma 16x20: dark wood frame with a light top edge,
# warm paper, a dark title line and grey text lines, a red wax seal with orange ribbon tails
_dp = ['o' * 16, 'o' + '\\' * 14 + 'o'] + ['o\\' + '4' * 12 + '+o'] * 16 + ['o' + '+' * 14 + 'o', 'o' * 16]
_dp = overlay(_dp, ['#' * 8], 4, 4)
for ly, lw in ((7, 10), (9, 8), (11, 10)):
    _dp = overlay(_dp, ['i' * lw], 3, ly)
_dp = overlay(_dp, ['.oo.', 'o!!o', 'o!Ho', '.oo.', '?..?'], 9, 12)
_dp = overlay(_dp, ['%%%%'], 3, 15)
DIPLOMA = R(_dp)

# ------------------------------------------------------------------ pet weight chart 16x24: white sheet, a dark axis, four bars
# rising green -> yellow -> orange -> red, a round cat face on top of the red bar
_wc = box(16, 24, '_', top='0')
_wc = overlay(_wc, ['$' * 14, '~' * 14], 1, 1)
_wc = overlay(_wc, ['.oo.', 'oBBo', 'oeeo', '.oo.'], 11, 4)
for bx, top, key in ((3, 16, '5'), (6, 13, ':'), (9, 10, '?'), (12, 8, '!')):
    for y in range(top, 20):
        _wc = overlay(_wc, ['o' + key], bx - 1, y)
for y in range(5, 21):
    _wc = overlay(_wc, ['#'], 1, y)
_wc = overlay(_wc, ['#' * 14], 1, 20)
WEIGHT_CHART = R(_wc)

# ------------------------------------------------------------------ flea & heartworm poster 24x24: yellow warning border with an
# orange shade, a white field, a brown flea under a red "no" ring and slash, two text bars
_fp = ['o' * 24, 'o' + ':' * 22 + 'o'] + ['o:' + 'K' * 20 + '?o'] * 20 + ['o' + '?' * 22 + 'o', 'o' * 24]
_ring = _ellipse(16, 14, 8.0, 7.0, 7.9, 6.9, [(0.72, '!'), (0.0, '.')])
_fp = overlay(_fp, _ring, 4, 3)
_fp = overlay(_fp, [
    "..o...o...",
    "...o.o....",
    "..o+++o...",
    ".o+\\\\\\+o..",
    "o+\\\\++\\+o.",
    ".o+\\\\\\++o.",
    "o.o+++++o.",
    ".o.o.o.o.o",
], 7, 5)
for i in range(10):
    _fp = overlay(_fp, ['!!'], 7 + i, 5 + (i * 8) // 10)              # the slash
_fp = overlay(_fp, ['#' * 14, '.' * 14, '%' * 10], 5, 18)
FLEA_POSTER = R(_fp)

# ------------------------------------------------------------------ appointments whiteboard 32x24: steel frame, white board with blue
# marker scribbles, PLUTO in red letters inside a red ring, a marker tray with a red and a blue marker
_wb = _frame(32, 22, 'K', rim='&', shade='%')
for ly, x0, lw in ((3, 3, 12), (3, 17, 8), (5, 3, 9), (5, 14, 12), (7, 3, 14)):
    _wb = overlay(_wb, ['*' * lw], x0, ly)
_wb = overlay(_wb, ['00'], 26, 3)
_ink = ['.'.join(FONT[c][y] for c in 'PLUTO') for y in range(5)]
for y in range(5):
    _wb = overlay(_wb, [_ink[y].replace('#', '!')], 6, 12 + y)
_wb = overlay(_wb, ['!!!'], 26, 6)                                           # a red tick by the last line
_wb = overlay(_wb, ['..' + '!' * 21 + '..', '.!' + '.' * 21 + '!.'] + ['!' + '.' * 23 + '!'] * 5
               + ['.!' + '.' * 21 + '!.', '..' + '!' * 21 + '..'], 3, 10)
_wb = _wb + ['.' * 32, '.' * 32]
_wb = overlay(_wb, ['.' + 'o' * 30 + '.', 'o' + '%' * 30 + 'o', '.' + 'o' * 30 + '.'], 0, 21)
_wb = overlay(_wb, ['o!!!!o'], 6, 21)
_wb = overlay(_wb, ['o****o'], 20, 21)
WHITEBOARD = R(_wb)

# ------------------------------------------------------------------ pet photo board 32x24: cork board, dark wood frame, four pinned
# polaroids (a ginger cat, a brown dog, a white rabbit, a goldfish) with coloured pins
_pb = ['o' * 32, 'o' + '+' * 30 + 'o'] + ['o+' + 'b' * 28 + '+o'] * 20 + ['o' + '+' * 30 + 'o', 'o' * 32]
_pb = _b(_pb)
_pb = overlay(_pb, _b(["b+bbbbbbbbbbbbbbbbbbbbbbbb", "bbbbbbbbbbbbbbbbbbbb+bbbbb"]), 3, 18)


def polaroid(photo):
    rows = ['o' * 9] + ['oWWWWWWWo'] + ['oW' + p + 'Wo' for p in photo] + ['oWWWWWWWo', 'oWWWWWWWo', 'o' * 9]
    return rows


_P_CAT = ["o...o", "?o.o?", "?????", "?e?e?", ".?!?."]
_P_DOG = ["\\\\.\\\\", "\\\\\\\\\\", "\\g\\g\\", "\\\\o\\\\", ".\\\\\\."]
_P_BUN = ["w.w..", "w.w..", "WWW..", "WgWW.", ".WWW."]
_P_FISH = ["*****", "*??.*", "?:??*", "*??.*", "*****"]
for (px, py), photo, pin in (((2, 2), _P_CAT, '!'), ((11, 3), _P_DOG, '*'), ((21, 2), _P_BUN, ':'), ((12, 13), _P_FISH, '!')):
    ph = [''.join('k' if c == '.' else c for c in r) for r in photo]
    _pb = overlay(_pb, polaroid(ph), px, py)
    _pb = overlay(_pb, [pin], px + 4, py)
_pb = overlay(_pb, ['_____', '_00__', '_____', '_0___'], 3, 15)            # a thank-you note
_pb = overlay(_pb, ['.H.H.', 'HHHHH', '.HHH.', '..H..'], 24, 14)            # a paper heart
PET_PHOTOS = R(_pb)

# ------------------------------------------------------------------ op lamp 80x56 (replaces the flat lamp head + arm): one STANDING
# sprite that stands at the exam table's base row and sorts just in front of the table. A wheeled base and a pole at the table's
# front-left corner, a boom across to a small round lamp dish hanging over the far half of the table.
_ol = _blank(80, 56)
_dish = _ellipse(32, 20, 16.0, 11.0, 15.5, 8.8, [(0.80, 'o'), (0.58, '%'), (0.44, '&'), (0.0, '^')])
for bx, by in ((16, 11), (10, 9), (22, 9), (10, 13), (22, 13)):
    _dish = overlay(_dish, ['KK', 'KK'], bx - 1, by - 1)
_ol = overlay(_ol, _dish, 48, 4)
# the boom: pole top to the stem, 4 px thick
for x in range(4, 64):
    _ol = overlay(_ol, ['o', '&', '%', 'o'], x, 1)
_ol = overlay(_ol, ['oooo', 'o&%o', 'o&%o', 'o&%o', 'o&%o'], 62, 1)          # the stem down to the dish
_ol = overlay(_ol, ['.oooooo.', 'o%&&&&%o', '.oooooo.'], 60, 5)              # the dish's hub
_ol = overlay(_ol, ['oooooo', 'o&&%%o', 'o&&%%o', 'o&&%%o', 'oooooo'], 1, 0)    # top joint
for y in range(5, 50):
    _ol = overlay(_ol, ['o&%o'], 2, y)                                       # the pole
_ol = overlay(_ol, ['o&&&%o', 'o%%%%o', 'oooooo'], 1, 47)                    # the pole's collar
_ol = overlay(_ol, ['.oooooooooo.', 'o&&&&&&&&%%o', 'o%%%%%%%%##o', '.oooooooooo.'], 0, 50)   # base
_ol[54] = '.oo......oo.' + _ol[54][12:]
_ol[55] = '.oo......oo.' + _ol[55][12:]
OP_LAMP = R(_ol)
OP_LAMP_HOG = STAND_HOG + 0.05   # stands on the exam table's base row: 0.05 in front of the table at every pixel


# Placements (game cells) by zone. The sprite's lower-left corner sits on the cell.
# v0.12.0 structured layout on the 36 x 63 room. Every zone is planned on the cell grid in functional groups, mirrored about the door
# centre line (x 18) wherever the concept is symmetric.
# Waiting room y 0..15: seating group x 1..14 (two rows of five chairs on a 1.5-cell pitch facing a coffee table, on a rug, a carrier
#   at each end), a clear centre aisle x 15..21 from the south exit to the ward door with plants framing the exit, reception group
#   x 23..36 (one straight counter with the back cabinet behind it and the mat in front; cooler and tank on the east wall).
# Ward y 18..37: kennel banks on both long walls; the nurse-station island on the centre line with a stool behind it and the
#   medicine trolley / food bowls at its ends; the north wall mirrored about x 18: supply shelf | sharps bin | IV stand | door |
#   IV stand | litter box | scrubs rack; a teal guide stripe on the floor from door to door.
# Theatre y 40..60: the north wall mirrored (cabinet, cabinet | sink, fridge, cabinet); the exam table centred on its mat with the
#   standing op lamp over it and an instrument trolley at each side; the Vet's stage is the open floor NORTH of the table (his
#   48x40 sprite at y 49.8..52.3 touches no prop), with the anaesthesia machine / heart monitor and the IV stand / cart flanking it
#   2+ cells to either side; side counters against the west and east walls; toys in the south corners.
# The zone wall faces stand on the '#' rows of the map (base y 16, 38, 61); wall decor (signs, clinic posters, charts, diplomas, the
# X-ray box, the whiteboard) hangs inside their white panel.
CHAIR_PITCH = 1.5
CHAIR_XS = [3.75 + CHAIR_PITCH * i for i in range(5)]
CHAIR_ROWS = (5.75, 9.75)                      # south row, north row (Rex and Grandma sit on the north row)
TABLE_AT = (15.5, 46.0)                        # the exam table (80 px = 5 cells wide, centred on x 18)

PROPS = [
    ('pluto_floor_waiting', (0.0, 0.0)), ('pluto_floor_ward', (0.0, 18.0)), ('pluto_floor_theatre', (0.0, 40.0)),
    ('pluto_wall_face', (0.0, 16.0)), ('pluto_wall_face', (0.0, 38.0)), ('pluto_wall_face_solid', (0.0, 61.0)),
    # --- waiting room: flat decor first
    ('pluto_rug', (3.25, 5.0)),
    ('pluto_paw_prints', (17.25, 3.0)),
    ('pluto_floor_mat', (28.0, 10.0)),
    ('pluto_toy_mouse', (1.25, 8.0)),
    # seating group
    ('pluto_carrier', (1.5, 2.5)),
] + [('pluto_chair', (x, y)) for y in CHAIR_ROWS for x in CHAIR_XS] + [
    ('pluto_coffee_table', (6.0, 7.75)),
    ('pluto_carrier_open', (11.75, 9.75)),
    # aisle
    ('pluto_plant', (15.0, 0.25)), ('pluto_plant', (20.0, 0.25)),
    ('pluto_wet_floor_sign', (20.75, 5.0)),
    # reception group
    ('pluto_reception_desk', (26.0, 13.0)),
    ('pluto_back_cabinet', (27.5, 14.75)),
    ('pluto_fish_tank', (33.5, 4.5)),
    ('pluto_water_cooler', (34.25, 1.0)),
    # the waiting room's north wall: window, room sign, clock, notice board, the healthy-pets poster and the weight chart over the
    # seating; the intercom and the WARD sign beside the door; the vaccination schedule, the TV over the counter and a poster
    on_wall('pluto_window', 1.0, 16.0), on_wall('pluto_sign_waiting', 3.5, 16.0), on_wall('pluto_clock', 7.75, 16.0),
    on_wall('pluto_notice_board', 9.75, 16.0), on_wall('pluto_healthy_pets', 12.25, 16.0), on_wall('pluto_weight_chart', 14.25, 16.0),
    on_wall('pluto_intercom', 19.375, 16.0), on_wall('pluto_sign_ward', 20.25, 16.0), on_wall('pluto_vaccine_chart', 23.0, 16.0),
    on_wall('pluto_wall_tv', 28.5, 16.0), on_wall('pluto_poster', 33.0, 16.0),
    # --- ward: two kennel banks of five stacked units, bottom to top. They start at y 19, not 18: the waiting room's standing
    # wall face (base 16, three cells tall) covers the ward's first row and would hide the bottom unit's lower cage.
    ('pluto_kennel_cat', (0.5, 19.0)), ('pluto_kennel_open_r', (0.5, 22.0)), ('pluto_kennel_cone', (0.5, 25.0)),
    ('pluto_kennel_dog', (0.5, 28.0)), ('pluto_kennel_cat', (0.5, 31.0)),
    ('pluto_kennel_dog', (33.0, 19.0)), ('pluto_kennel_cat', (33.0, 22.0)), ('pluto_kennel_open_l', (32.25, 25.0)),
    ('pluto_kennel_cat', (33.0, 28.0)), ('pluto_kennel_cone', (33.0, 31.0)),
    # the island
    ('pluto_food_bowls', (21.375, 27.0)),
    ('pluto_med_trolley', (13.25, 27.0)),
    ('pluto_nurse_station', (15.0, 27.0)),
    ('pluto_stool', (17.625, 28.25)),
    # the north wall group, mirrored about x 18
    ('pluto_supply_shelf', (6.5, 36.0)), ('pluto_sharps_bin', (11.5, 36.0)), ('pluto_iv_stand', (14.5, 36.0)),
    ('pluto_iv_stand', (20.5, 36.0)), ('pluto_litter_box', (23.5, 36.0)), ('pluto_scrubs_rack', (26.5, 36.0)),
    on_wall('pluto_anatomy_poster', 1.5, 38.0), on_wall('pluto_xray_box', 7.0, 38.0), on_wall('pluto_flea_poster', 10.25, 38.0),
    on_wall('pluto_sign_surgery', 14.25, 38.0), on_wall('pluto_prep_sign', 19.5, 38.0), on_wall('pluto_wall_shelf', 21.5, 38.0),
    on_wall('pluto_pet_photos', 26.5, 38.0), on_wall('pluto_poster', 32.5, 38.0),
    # --- operating theatre: the north wall, mirrored about x 18
    ('pluto_cabinet_wide', (1.0, 58.0)), ('pluto_cabinet_wide', (5.5, 58.0)),
    ('pluto_sink', (26.5, 58.0)), ('pluto_vaccine_fridge', (29.0, 58.0)), ('pluto_cabinet_wide', (31.0, 58.0)),
    # behind the Vet: a poster, the appointments whiteboard, three diplomas centred on x 18, the clock and the cat X-ray box
    on_wall('pluto_poster', 10.5, 61.0), on_wall('pluto_whiteboard', 12.25, 61.0),
    on_wall('pluto_diploma', 16.0, 61.0), on_wall('pluto_diploma', 17.5, 61.0), on_wall('pluto_diploma', 19.0, 61.0),
    on_wall('pluto_clock', 21.0, 61.0), on_wall('pluto_xray_cat', 23.0, 61.0),
    ('pluto_scale', (27.0, 56.0)),
    # the table group, mirrored about x 18
    ('pluto_table_mat', (13.5, 45.25)),
    ('pluto_lamp_pool', (16.0, 45.75)),
    ('pluto_exam_table', TABLE_AT),
    ('pluto_op_lamp', (14.0, TABLE_AT[1])),
    ('pluto_instrument_trolley', (12.0, 46.0)), ('pluto_instrument_trolley', (22.5, 46.0)),
    ('pluto_anaesthesia_machine', (12.0, 49.0)), ('pluto_monitor_cart', (22.25, 49.0)),
    ('pluto_iv_stand', (9.5, 49.0)), ('pluto_cart', (25.25, 49.0)),
    # side counters, the bin, the east side door
    ('pluto_counter_towels', (1.0, 50.0)), ('pluto_counter_printer', (32.0, 50.0)), ('pluto_biohazard_bin', (30.5, 50.0)),
    ('pluto_side_door', (35.0, 45.5)),
    # toys in the south corners
    ('pluto_toy_mouse', (2.5, 42.5)), ('pluto_toy_ball', (4.0, 41.5)), ('pluto_feather_wand', (3.0, 44.0)),
    ('pluto_scratch_post', (30.0, 42.0)),
]

PROP_OBJECTS = [
    # v0.12.0: the collider covers the slab's footprint (28 px deep), so nobody stands where the slab hides them
    Obj('pluto_exam_table', 'exam_table', EXAM_TABLE, ('low', 4, 0, 72, 28), comment='Straps. That is a hard no from me.'),
    Obj('pluto_cabinet', 'cabinet', CABINET, ('high', 0, 0, 32, 20)),
    Obj('pluto_cart', 'cart', CART, ('low', 0, 0, 24, 14)),
    Obj('pluto_sink', 'sink', SINK, ('high', 0, 0, 32, 32)),
    Obj('pluto_scale', 'scale', SCALE, None, -1.5),
    Obj('pluto_carrier', 'carrier', CARRIER, ('high', 0, 0, 32, 16), comment='The prison van. I know that door.'),
    Obj('pluto_poster', 'poster', POSTER, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_poster']), stand=True),
    Obj('pluto_cone', 'cone', CONE, None, -1.5),
    Obj('pluto_toy_mouse', 'toy_mouse', TOY_MOUSE, None, -1.5),
    Obj('pluto_toy_ball', 'toy_ball', TOY_BALL, None, -1.5),
    Obj('pluto_feather_wand', 'feather_wand', FEATHER_WAND, None, -1.5),
    Obj('pluto_scratch_post', 'scratch_post', SCRATCH_POST, ('low', 2, 0, 12, 8)),
    Obj('pluto_syringe_tray', 'syringe_tray', SYRINGE_TRAY, None, -1.5),
    # v0.4
    # 0.12.1: the counter's collider covers its front and most of the top (20 px); the two end pieces reach up to the back
    # cabinet's ends, so the strip behind the counter where the receptionist stands (x 27.5..31.5, y 14.25..14.75, under the
    # cabinet) is closed on every side.
    Obj('pluto_reception_desk', 'reception_desk', None, ('high', 0, 0, 112, 20), frames=RECEPTION_DESK_FRAMES, fps=2.0,
        comment='The bell. I must press the bell.', extra=[(0, 20, 24, 20), (88, 20, 24, 20)]),
    Obj('pluto_chair', 'chair', CHAIR, ('low', 2, 0, 20, 8)),
    Obj('pluto_plant', 'plant', PLANT, ('high', 4, 0, 8, 8)),
    Obj('pluto_window', 'window', WINDOW, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_window']), stand=True),
    Obj('pluto_xray_box', 'xray_box', XRAY_BOX, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_xray_box']), stand=True),
    Obj('pluto_clock', 'clock', None, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_clock']), stand=True, frames=CLOCK_FRAMES,
        fps=1.0, comment='Tick. Tock. Dinner is late.'),
    Obj('pluto_fish_tank', 'fish_tank', None, ('high', 0, 0, 32, 12), frames=FISH_TANK_FRAMES, fps=4.0,
        comment='Sushi. Behind glass. Cruel.'),
    Obj('pluto_sharps_bin', 'sharps_bin', SHARPS_BIN, ('low', 0, 0, 12, 6)),
    Obj('pluto_iv_stand', 'iv_stand', None, ('low', 4, 0, 10, 6), frames=IV_FRAMES, fps=3.0, comment='Drip. Drip. I refuse.'),
    Obj('pluto_treat_jar', 'treat_jar', TREAT_JAR, None, -1.5),
    Obj('pluto_food_bowls', 'food_bowls', FOOD_BOWLS, None, -1.5),
    Obj('pluto_litter_box', 'litter_box', LITTER_BOX, ('low', 0, 0, 20, 8), comment='Not in front of everyone.'),
    Obj('pluto_floor_mat', 'floor_mat', FLOOR_MAT, None, -2.5),
    Obj('pluto_paw_prints', 'paw_prints', PAW_PRINTS, None, -2.0),
    Obj('pluto_wet_floor_sign', 'wet_floor_sign', WET_FLOOR_SIGN, ('low', 0, 0, 12, 6)),
    # v0.5: the zone door (ClinicDoor.cs swaps in EXTRA_PNGS['clinic_door_open'] and drops the collider), the ward
    # the door is part of the wall: it keeps HeightOffGround 0, a hair in front of the wall face it stands in
    Obj('pluto_clinic_door', 'clinic_door', CLINIC_DOOR, ('high', 0, 0, 32, 32), 0.0),
    Obj('pluto_nurse_station', 'nurse_station', NURSE_STATION, ('high', 0, 0, 96, 12), comment='Treat jar. Locked. Of course.'),
    # v0.6: theatre kit, wall decor, the side door (v0.11: the monitor cart is redrawn as the animated heart monitor)
    Obj('pluto_prep_sign', 'prep_sign', PREP_SIGN, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_prep_sign']), stand=True),
    Obj('pluto_monitor_cart', 'monitor_cart', None, ('low', 4, 0, 16, 10), frames=HEART_MONITOR_FRAMES, fps=6.0,
        comment='Beep. Still alive. Good.'),
    # 0.12.1: the theatre's north-wall kit (cabinets, sink, fridge) and the ward's shelf and rack get colliders as deep as their
    # drawings (to the wall), or Pluto vanished in the strip between them and the wall
    Obj('pluto_vaccine_fridge', 'vaccine_fridge', VACCINE_FRIDGE, ('high', 0, 0, 24, 40), comment='Cold needles. Hard pass.'),
    Obj('pluto_intercom', 'intercom', INTERCOM, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_intercom']), stand=True),
    Obj('pluto_wall_tv', 'wall_tv', WALL_TV, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_wall_tv']), stand=True),
    Obj('pluto_side_door', 'side_door', SIDE_DOOR, None, 0.5),
    # v0.10: the lamp's light pool on the floor, the wide cabinet (0.12.0: the flat head + arm became the standing pluto_op_lamp)
    Obj('pluto_lamp_pool', 'lamp_pool', LAMP_POOL, None, -1.4),
    Obj('pluto_cabinet_wide', 'cabinet_wide', CABINET_WIDE, ('high', 0, 0, 64, 48)),
    # v0.10.1: standing wall faces, the wall shelf, the kennel bank
    Obj('pluto_wall_face', 'wall_face', WALL_FACE, None, WALL_HOG, stand=True),
    Obj('pluto_wall_face_solid', 'wall_face_solid', WALL_FACE_SOLID, None, WALL_HOG, stand=True),
    Obj('pluto_wall_shelf', 'wall_shelf', WALL_SHELF, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_wall_shelf']), stand=True),
    Obj('pluto_kennel_cat', 'kennel_cat', KENNEL_CAT, ('high', 0, 0, 40, 48)),
    Obj('pluto_kennel_dog', 'kennel_dog', KENNEL_DOG, ('high', 0, 0, 40, 48)),
    Obj('pluto_kennel_cone', 'kennel_cone', KENNEL_CONE, ('high', 0, 0, 40, 48)),
    # 0.12.1: the swung-open door (12 x 24 px beside the unit) blocks too, or Pluto stood inside its drawing
    Obj('pluto_kennel_open_r', 'kennel_open_r', KENNEL_OPEN_R, ('high', 0, 0, 40, 48), extra=[(40, 0, 12, 24)]),
    Obj('pluto_kennel_open_l', 'kennel_open_l', KENNEL_OPEN_L, ('high', 12, 0, 40, 48), extra=[(0, 0, 12, 24)]),
    # v0.11: the structured clinic
    Obj('pluto_rug', 'rug', RUG, None, -3.0),
    Obj('pluto_coffee_table', 'coffee_table', COFFEE_TABLE, ('low', 2, 0, 44, 8), comment='Dog magazines. How rude.'),
    Obj('pluto_carrier_open', 'carrier_open', CARRIER_OPEN, ('high', 0, 0, 32, 16), comment='Someone escaped. Respect.'),
    # 0.12.1: 20 px deep, flush with the wall (base 14.75 + 1.25 = 16): nothing gets in behind the receptionist
    Obj('pluto_back_cabinet', 'back_cabinet', BACK_CABINET, ('high', 0, 0, 64, 20)),
    Obj('pluto_water_cooler', 'water_cooler', WATER_COOLER, ('high', 1, 0, 14, 8), comment='Big water bottle. It burps.'),
    Obj('pluto_notice_board', 'notice_board', NOTICE_BOARD, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_notice_board']),
        stand=True, comment='LOST CAT. I know him. He is fine.'),
    Obj('pluto_sign_waiting', 'sign_waiting', SIGN_WAITING, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_sign_waiting']), stand=True),
    Obj('pluto_sign_ward', 'sign_ward', SIGN_WARD, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_sign_ward']), stand=True),
    Obj('pluto_sign_surgery', 'sign_surgery', SIGN_SURGERY, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_sign_surgery']), stand=True),
    Obj('pluto_supply_shelf', 'supply_shelf', SUPPLY_SHELF, ('high', 0, 0, 48, 32), comment='Boxes. I must sit in every box.'),
    Obj('pluto_scrubs_rack', 'scrubs_rack', SCRUBS_RACK, ('high', 0, 0, 48, 32), comment='Tiny blue pyjamas for villains.'),
    Obj('pluto_med_trolley', 'med_trolley', MED_TROLLEY, ('low', 0, 0, 24, 8), comment='Pills in cheese. Nice try.'),
    Obj('pluto_stool', 'stool', STOOL, ('low', 2, 0, 8, 4)),
    Obj('pluto_anaesthesia_machine', 'anaesthesia_machine', None, ('low', 0, 0, 32, 16), frames=ANAESTHESIA_FRAMES, fps=2.0,
        comment='It breathes for you. Creepy.'),
    Obj('pluto_instrument_trolley', 'instrument_trolley', INSTRUMENT_TROLLEY, ('low', 0, 0, 24, 8)),
    Obj('pluto_counter_towels', 'counter_towels', COUNTER_TOWELS, ('high', 0, 0, 48, 12), comment='The cone of shame. Never again.'),
    Obj('pluto_counter_printer', 'counter_printer', COUNTER_PRINTER, ('high', 0, 0, 48, 12)),
    Obj('pluto_biohazard_bin', 'biohazard_bin', BIOHAZARD_BIN, ('low', 1, 0, 12, 6), comment='Smells like the vet. Exactly.'),
    Obj('pluto_table_mat', 'table_mat', TABLE_MAT, None, -3.0),
    # v0.12.0: the standing op lamp (placed on the table's base row, OP_LAMP_HOG in front of it) and the vet-clinic wall art
    Obj('pluto_op_lamp', 'op_lamp', OP_LAMP, ('low', 0, 0, 12, 5), OP_LAMP_HOG),
    Obj('pluto_xray_cat', 'xray_cat', XRAY_CAT, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_xray_cat']), stand=True,
        comment='My X-ray. Nothing inside. Nothing at all.'),
    Obj('pluto_anatomy_poster', 'anatomy_poster', ANATOMY_POSTER, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_anatomy_poster']),
        stand=True, comment='They know where everything is. Unsettling.'),
    Obj('pluto_vaccine_chart', 'vaccine_chart', VACCINE_CHART, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_vaccine_chart']),
        stand=True, comment='Booster due today. Not if I can help it.'),
    Obj('pluto_healthy_pets', 'healthy_pets', HEALTHY_PETS, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_healthy_pets']), stand=True),
    Obj('pluto_diploma', 'diploma', DIPLOMA, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_diploma']), stand=True,
        comment='Doctor of Veterinary Villainy. Framed.'),
    Obj('pluto_weight_chart', 'weight_chart', WEIGHT_CHART, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_weight_chart']),
        stand=True, comment='That chart is lying. I am fluffy.'),
    Obj('pluto_flea_poster', 'flea_poster', FLEA_POSTER, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_flea_poster']), stand=True,
        comment='Fleas? Never met them. Scratch. Scratch.'),
    Obj('pluto_whiteboard', 'whiteboard', WHITEBOARD, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_whiteboard']), stand=True,
        comment='PLUTO. Circled. In red.'),
    Obj('pluto_pet_photos', 'pet_photos', PET_PHOTOS, None, wall_decor_hog(WALL_DECOR_OFFSET['pluto_pet_photos']), stand=True,
        comment='A wall of happy patients. Suspicious.'),
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

    stripe = (DOOR_GAP_X, DOOR_GAP_X + 1) if name == 'pluto_floor_ward' else ()     # never under the ward's guide stripe
    candidates = [(tx, ty) for ty in range(1, cells_high - 1) for tx in range(1, ROOM_W - 1) if clear(tx, y0 + ty) and tx not in stripe]
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
FLOOR_WAITING = floor(ROOM_W, 16, FLOOR_VARIANTS['pluto_floor_waiting'], FLOOR_TONES['pluto_floor_waiting'])    # y 0..15
FLOOR_WARD = floor(ROOM_W, 20, FLOOR_VARIANTS['pluto_floor_ward'], FLOOR_TONES['pluto_floor_ward'], WARD_STRIPE_PX)   # y 18..37
FLOOR_THEATRE = floor(ROOM_W, 21, FLOOR_VARIANTS['pluto_floor_theatre'], FLOOR_TONES['pluto_floor_theatre'])    # y 40..60

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
        for k, frame in enumerate(o.frames or [], start=1):
            if k >= 2:
                p = os.path.join(out, '%s_f%d.png' % (o.png, k))
                save(frame, p)
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
    anim = os.path.join(project, 'docs', 'preview', 'animated-props.png')
    sheet([o.frames for o in OBJECTS if o.frames], anim, scale=4, gap=6)
    return p
