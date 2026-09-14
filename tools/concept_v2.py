"""Concept art for The Vet Visit v2: the cast lineup and the three-zone room mock.

The human characters reuse the Vet's base pose (recoloured / re-dressed), Grandma Cat reuses Pluto's loaf pose,
the Vet Tech and Nurse are the enemy variants. Vanilla enemies (rat, parrot, mutant kin, critters) are drawn as
rough stand-ins and labelled. Output: docs/preview/v2-cast.png and docs/preview/v2-room.png.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(PROJECT), 'tools'))
from PIL import Image, ImageDraw

from vetpixel import R, PALETTE, pad, overlay, image, erase
import vet_poses as VP
import clinic_objects as O
from pixel import strip_outline, outline_img, img_from_rows, recolor
import poses_extra as PX          # main mod (Pluto's loaf)
import character_anims as A       # main mod (Pluto idle)
import preview as V

PAL = dict(PALETTE)
PAL.update({'B': (0x8B, 0x7A, 0x66, 255), 'b': (0x3B, 0x2C, 0x24, 255), 'd': (0x66, 0x52, 0x4A, 255), 'L': (0xB4, 0xA1, 0x80, 255),
            'G': (0x9C, 0xB6, 0x4E, 255), 'P': (0xE8, 0xA0, 0xB0, 255), 'p': (0xD4, 0x6A, 0x7A, 255), '9': (0x2A, 0x1F, 0x1A, 255),
            'x': (0xB9, 0xB0, 0xA8, 255), 'q': (0xF5, 0xC6, 0xD0, 255), 'z': (0x4C, 0x4E, 0x58, 255)})


def img(rows):
    return img_from_rows(rows, PAL)


def actor(rows):
    """An AIActor as the game shows it: outline stripped and re-added."""
    return outline_img(img_from_rows(strip_outline(rows), PAL))


# ------------------------------------------------------------------ humans from the Vet's base pose
VET = VP.POSE
ARM = (23, 17, 36, 25)          # pose coords of the arm + gun region


def no_gun(rows):
    """Remove the arm/gun region and close the coat edge."""
    x0, y0, x1, y1 = ARM
    out = []
    for y, r in enumerate(rows):
        if y0 <= y < y1:
            r = r[:x0 - 1] + 'o' + '.' * (len(r) - x0)
        out.append(r)
    return out


def dress(rows, mapping):
    return recolor(rows, mapping)


# The Owner: hoodie (grey), jeans (blue), no glasses, hands in pockets.
OWNER = dress(no_gun(VET), {'W': 'Z', 'w': 'z', '$': '#', '~': '|', '%': 'Z', '&': 'Z', '@': '+'})
OWNER[7] = "..........o========o................"          # no glasses: plain brow
OWNER[8] = "..........o=g===g==o................"          # two dot eyes
OWNER = overlay(OWNER, ['oooooooo'], 11, 2)                    # short fringe line

# The Receptionist: hair bun, white blouse, no coat, at the desk (only the top half shows behind the counter).
RECEPTIONIST = dress(no_gun(VET), {'~': '@', '$': '!'})
RECEPTIONIST = overlay(RECEPTIONIST, ['...oooo...', '..o@@@@o..', '..o@@@@o..', '...oooo...'], 9, 0)   # bun

# Vet Tech: teal scrubs, cap, no coat, small syringe pistol.
TECH = dress(VET, {'W': '$', 'w': '~', 'K': '$'})
TECH = overlay(TECH, ['.oooooooo.', 'o$$$$$$$$o', 'o$$$$$$$$o', '.oooooooo.'], 10, 1)          # scrub cap

# The Nurse: the Tech with a white cap with a red cross and a bigger gun (same sprite, drawn 1.25x in the mock).
NURSE = dress(VET, {'W': '$', 'w': '~', 'K': '$'})
NURSE = overlay(NURSE, ['.oooooooo.', 'oWWW!!WWWo', 'oWWW!!WWWo', 'oW!!!!!!Wo', 'oWWW!!WWWo', '.oooooooo.'], 10, 0)

# ------------------------------------------------------------------ animals
GRANDMA_CAT = recolor(PX.LOAF, {'B': 'Z', 'b': '#', 'd': 'z', 'L': '&', 'W': 'K', 'w': 'x', 'G': ':', 'P': 'q', 'p': 'P'})   # grey loaf, yellow eyes

REX = R([                       # nervous brown dog, sitting, 24 x 20
    "........................",
    "....oo............oo....",
    "...o++o..........o++o...",
    "...o+\\\\oooooooooo\\\\+o...",
    "....o\\\\\\\\\\\\\\\\\\\\\\\\\\\\o....",
    "....o\\\\o\\\\\\\\\\\\o\\\\\\\\o....",
    "....o\\\\g\\\\\\\\\\\\g\\\\\\\\o....",
    "....o\\\\\\\\\\\\\\\\\\\\\\\\\\\\o....",
    ".....o\\\\\\\\WWWW\\\\\\\\o.....",
    ".....o\\\\\\WW@@WW\\\\\\o.....",
    "......o\\\\WWWWWW\\\\o......",
    "......oo\\\\\\\\\\\\\\\\oo......",
    ".....o\\\\\\\\\\\\\\\\\\\\\\\\o.....",
    "....o\\\\\\\\\\\\\\\\\\\\\\\\\\\\o....",
    "....o\\\\\\\\\\\\\\\\\\\\\\\\\\\\o....",
    "....o\\\\\\\\WW\\\\\\\\\\\\\\\\o....",
    "....o\\\\\\WWWW\\\\\\\\\\\\\\\\o...",
    "....oWWoWWWWoWWo++o.....",
    "....oWWoWWWWoWWo+o......",
    "....oooooooooooooo......",
])
HAMSTER_BALL = R([
    "...oooo...",
    ".oo^^^^oo.",
    ".o^^^^^^o.",
    "o^^===^^^o",
    "o^==g==^^o",
    "o^====^^^o",
    ".o^^^^^^o.",
    ".oo^^^^oo.",
    "...oooo...",
    "..........",
])
# vanilla stand-ins (rough): chick, rabbit, squirrel, rat, parrot, mutant kin
CHICK = R([".oo.", "o::o", "o:go", ".oo.", "oo.o"])
RABBIT = R(["o.o.", "oWoW", ".oo.", "oWWo", "oWWo", ".oo."])
SQUIRREL = R(["..o..", ".o\\o.", "o\\\\go", "o\\\\\\o", ".ooo."])
RAT = R(["......o.", "oooooZo.", "oZZZZZZo", "oZZgZZo.", ".oooooo.", ".o..o..."])
PARROT = R([".oo.", "o!!o", "o!go", "o!!o", ".oo.", "o:o."])
MUTANT_KIN = R(["..oooo..", ".oeeeeo.", "oeegegeo", "oeeeeeeo", "oeeeeeeo", ".oeeeeo.", ".oo..oo."])

# ------------------------------------------------------------------ new props for v2 (concept versions)
DOOR_CLOSED = R(['o' * 16] + ['o' + '_' * 14 + 'o'] * 2 + ['o__oooooooooo__o'] + ['o__o^^^^^^^^o__o'] * 6 + ['o__oooooooooo__o'] + ['o' + '_' * 14 + 'o'] * 14 + ['o__________%%__o', 'o__________%%__o'] + ['o' + '_' * 14 + 'o'] * 3 + ['o' * 16])
DOOR_OPEN = R(['o' * 16] + ['o' + '.' * 14 + 'o'] * 30 + ['o' * 16])
KENNEL = R(['o' * 32] + ['o' + '%' * 30 + 'o'] + ['o%' + 'o^^o' * 7 + '%o'] * 14 + ['o' + '%' * 30 + 'o', 'o' + '#' * 30 + 'o'] + ['o' * 32] + ['.' * 32] * 5)
KENNEL = overlay(KENNEL, ['..oo..oo..', '.o++oo++o.', 'o\\\\\\\\\\\\\\\\\\\\\\\\o', 'o\\\\g\\\\\\\\g\\\\o', 'o\\\\\\\\WW\\\\\\\\o', '.oooooooo.'], 11, 9)   # a dog behind the bars
NURSE_STATION = R(['.' * 48] * 4 + ['o' * 48] + ['o' + '_' * 46 + 'o'] * 6 + ['o' + '0' * 46 + 'o', 'o' * 48] + ['o' + '|' * 46 + 'o'] * 8 + ['o' + '/' * 46 + 'o', 'o' * 48] + ['.' * 48] * 2)
NURSE_STATION = overlay(NURSE_STATION, ['oooooooo', 'o######o', 'o#**%*#o', 'o######o', 'oooooooo', '...oo...', '..oooo..'], 6, 0)
SIGN_PREP = R(['oooooooooooooooo', 'o!!!!!!!!!!!!!!o', 'o!WW!W!WW!W!WW!o', 'o!W!!W!W!!W!W!!o', 'o!WW!WWWW!W!WW!o', 'o!!!!!!!!!!!!!!o', 'oooooooooooooooo'])
SURGICAL_LIGHT = R(['.' * 24] * 0 + [
    "..........oooo..........", ".........o####o.........", ".........o#KK#o.........", ".........o#KK#o.........", "..........oooo..........",
    "...........o%o..........", "...........o%o..........", "...........o%o..........", "........oooo%oooo.......", ".......o&&&&&&&&&o......",
    "......o&&&&&&&&&&&o.....", "......o&KKKKKKKKK&o.....", "......o&K:::::::K&o.....", "......o&KKKKKKKKK&o.....", "......o&&&&&&&&&&&o.....",
    ".......ooooooooooo......", "........o%%%%%%%o.......", ".........ooooooo........"] + ['.' * 24] * 6)
MONITOR_CART = R(['oooooooooooooooo', 'o##############o', 'o#*%%*%%%*%%%*#o', 'o#%%%%*%%%%%%%#o', 'o#%*%%%%%*%%%%#o', 'o##############o', 'oooooooooooooooo', '......o%%o......', '......o%%o......', 'oooooooooooooooo', 'o&&&&&&&&&&&&&&o', 'oooooooooooooooo', '.o%o........o%o.', '.o%o........o%o.', '.o%o........o%o.', '.o%o........o%o.', 'oo#oo......oo#oo', '.ooo........ooo.'] + ['.' * 16] * 6)
OR_TABLE = overlay(O.EXAM_TABLE, ['o' + '#' * 8 + 'o'] * 1, 12, 3)
OR_TABLE = overlay(OR_TABLE, ['o' + '#' * 8 + 'o'], 28, 3)     # straps
TV = R(['oooooooooooooooooooooooo', 'o######################o', 'o#*******************%#o', 'o#**%%%%***%%%%%*****%#o', 'o#**%%%%***%%%%%*****%#o', 'o#*******************%#o', 'o######################o', 'oooooooooooooooooooooooo', '..........oooo..........', '.........oooooo.........'])
CARRIER_OPEN = overlay(O.CARRIER, ['o' + '.' * 8 + 'o'] * 12, 20, 4) if False else O.CARRIER


def cast_sheet(path):
    entries = [
        ('Pluto (existing)', V.game_frame(A.IDLE_SIDE[0])),
        ('The Owner', img(OWNER)),
        ('The Receptionist', img(RECEPTIONIST)),
        ('Rex (NPC)', img(REX)),
        ('Grandma Cat (NPC)', img(GRANDMA_CAT)),
        ('Hamster', img(HAMSTER_BALL)),
        ('Vet Tech (enemy)', actor(TECH)),
        ('The Nurse (add)', actor(NURSE).resize((int(actor(NURSE).width * 1.25), int(actor(NURSE).height * 1.25)), Image.NEAREST)),
        ('The Vet (boss)', actor(VET)),
        ('vanilla: chick / rabbit / squirrel', None),
        ('vanilla: rat / parrot / mutant kin', None),
    ]
    sc = 4
    W = 0; H = 0
    cells = []
    for label, im in entries:
        if im is None:
            if 'chick' in label:
                ims = [actor(CHICK), actor(RABBIT), actor(SQUIRREL)]
            else:
                ims = [actor(RAT), actor(PARROT), actor(MUTANT_KIN)]
            w = sum(i.width for i in ims) * sc + 8 * sc; h = max(i.height for i in ims) * sc
            cells.append((label, ims, w, h))
        else:
            cells.append((label, [im], im.width * sc, im.height * sc))
    W = sum(c[2] + 24 for c in cells) + 24
    H = 48 * sc + 40
    out = Image.new('RGBA', (W, H), (74, 72, 88, 255)); d = ImageDraw.Draw(out)
    x = 12
    for label, ims, w, h in cells:
        xx = x
        for im in ims:
            big = im.resize((im.width * sc, im.height * sc), Image.NEAREST)
            out.alpha_composite(big, (xx, 12 + 48 * sc - big.height)); xx += big.width + 4 * sc
        d.text((x, 12 + 48 * sc + 8), label, fill=(240, 236, 240, 255))
        x += w + 24
    out.save(path)
    return out


# ------------------------------------------------------------------ the three-zone room (30 x 52 cells)
ROOM_W, ROOM_H = 30, 52
WALLS = [(0, 16), (0, 36)]          # y of the zone walls
GAP = (13, 17)                      # door gap columns in each wall


def room_mock(path):
    W, H = ROOM_W * 16, ROOM_H * 16
    im = Image.new('RGBA', (W, H), (244, 246, 248, 255)); d = ImageDraw.Draw(im)
    for cy in range(ROOM_H):
        for cx in range(ROOM_W):
            c = (236, 239, 243, 255) if (cx + cy) % 2 else (244, 246, 248, 255)
            d.rectangle([cx * 16, cy * 16, cx * 16 + 15, cy * 16 + 15], fill=c)
            d.line([(cx * 16, cy * 16), (cx * 16 + 15, cy * 16)], fill=(220, 224, 230, 255))
            d.line([(cx * 16, cy * 16), (cx * 16, cy * 16 + 15)], fill=(220, 224, 230, 255))

    def wall_band(y_cell, thick=1):
        y = (ROOM_H - y_cell) * 16
        d.rectangle([0, y - 20, W, y], fill=(200, 205, 212, 255))       # wall face
        d.rectangle([0, y - 24, W, y - 20], fill=(150, 156, 166, 255))  # wall top
    wall_band(ROOM_H)                              # north wall
    for _, wy in WALLS:                            # zone walls with a gap
        y = (ROOM_H - wy) * 16
        for x0, x1 in ((0, GAP[0]), (GAP[1], ROOM_W)):
            d.rectangle([x0 * 16, y - 20, x1 * 16, y], fill=(200, 205, 212, 255))
            d.rectangle([x0 * 16, y - 24, x1 * 16, y - 20], fill=(150, 156, 166, 255))

    items = []

    def put(sprite, x, y, key=None):
        items.append((y if key is None else key, x, y, sprite))

    objs = {o.name: o for o in O.OBJECTS}

    def prop(name, x, y):
        put(image(objs[name].rows), x, y)

    # --- zone 1: waiting room (y 0..15)
    prop('pluto_floor_mat', 1.0, 9.0); prop('pluto_chair', 1.5, 10.0); prop('pluto_chair', 3.0, 10.0); prop('pluto_chair', 4.5, 10.0)
    prop('pluto_plant', 0.5, 12.5); prop('pluto_fish_tank', 25.0, 12.0); prop('pluto_plant', 28.5, 12.5)
    put(img(TV), 12.0, 14.6)
    prop('pluto_reception_desk', 20.0, 8.5); put(img(RECEPTIONIST), 21.0, 9.6, key=9.7); prop('pluto_treat_jar', 22.8, 10.3)
    prop('pluto_carrier', 8.0, 4.0); put(V.game_frame(A.IDLE_SIDE[0]), 10.6, 3.9)
    put(img(OWNER), 12.5, 3.5)
    put(img(REX), 3.2, 10.6, key=10.5); put(img(GRANDMA_CAT), 15.0, 10.0)
    put(actor(CHICK), 6.5, 6.0); put(actor(RABBIT), 17.0, 5.5); put(actor(SQUIRREL), 22.0, 4.0); put(img(HAMSTER_BALL), 14.0, 7.0)
    prop('pluto_toy_ball', 5.0, 3.5); prop('pluto_toy_mouse', 18.0, 2.5); prop('pluto_paw_prints', 11.5, 7.5)
    put(img(DOOR_CLOSED), 14.0, 15.0)
    # --- zone 2: the ward (y 16..35)
    for x in (1.0, 5.0, 25.0):
        put(img(KENNEL), x, 33.0)
    for x in (1.0, 5.0, 25.0):
        put(img(KENNEL), x, 19.0)
    put(img(NURSE_STATION), 12.0, 31.5); put(img(SIGN_PREP), 21.5, 34.6)
    prop('pluto_food_bowls', 13.0, 30.2); prop('pluto_food_bowls', 16.0, 30.2)
    prop('pluto_cart', 9.0, 26.0); prop('pluto_iv_stand', 22.0, 25.0); prop('pluto_sharps_bin', 27.5, 22.0)
    prop('pluto_litter_box', 9.0, 20.0); prop('pluto_scale', 20.0, 21.0); prop('pluto_wet_floor_sign', 15.0, 24.0)
    put(actor(TECH), 8.0, 28.0); put(actor(TECH), 20.0, 27.5); put(actor(TECH), 14.0, 22.0)
    put(actor(RAT), 4.0, 24.0); put(actor(PARROT), 23.5, 29.5); put(actor(MUTANT_KIN), 17.5, 25.0)
    put(img(DOOR_CLOSED), 14.0, 35.0)
    # --- zone 3: the operating theatre (y 36..51)
    prop('pluto_cabinet', 0.5, 49.0); prop('pluto_cabinet', 3.0, 49.0); prop('pluto_xray_box', 6.5, 49.5); prop('pluto_med_shelf', 9.5, 49.0)
    prop('pluto_window', 13.0, 49.5); prop('pluto_clock', 16.0, 51.1); prop('pluto_poster', 17.0, 49.0); prop('pluto_cabinet', 19.0, 49.0)
    prop('pluto_cabinet', 22.0, 49.0); prop('pluto_sink', 26.0, 47.0)
    put(img(SURGICAL_LIGHT), 11.0, 45.0); put(img(OR_TABLE), 12.0, 41.0); put(img(MONITOR_CART), 17.0, 42.0)
    prop('pluto_cart', 8.5, 41.5); prop('pluto_iv_stand', 10.0, 43.5); prop('pluto_syringe_tray', 20.0, 44.0); prop('pluto_cone', 24.0, 42.0)
    put(actor(VET), 13.2, 44.2, key=44.3)
    nurse = actor(NURSE); put(nurse.resize((int(nurse.width * 1.25), int(nurse.height * 1.25)), Image.NEAREST), 21.5, 46.5)
    put(actor(TECH), 5.0, 39.0); put(actor(TECH), 24.0, 39.0)

    for key, x, y, sp in sorted(items, key=lambda t: -t[0]):
        im.alpha_composite(sp, (int(round(x * 16)), int(round(H - y * 16 - sp.height))))
    # labels
    for label, yc in (('ACT 1  waiting room', 1.0), ('ACT 2  the ward', 17.0), ('ACT 3  operating theatre', 37.0)):
        d.text((6, H - yc * 16 - 12), label, fill=(200, 40, 40, 255))
    d.text((16 * 16 + 4, H - 15.0 * 16 - 18), 'door (opens when the act ends)', fill=(200, 40, 40, 255))
    d.text((16 * 16 + 4, H - 35.0 * 16 - 18), 'door', fill=(200, 40, 40, 255))
    big = im.resize((W * 2, H * 2), Image.NEAREST); big.save(path)
    return big


if __name__ == '__main__':
    out = os.path.join(PROJECT, 'docs', 'preview')
    os.makedirs(out, exist_ok=True)
    cast_sheet(os.path.join(out, 'v2-cast.png'))
    room_mock(os.path.join(out, 'v2-room.png'))
    print('ok')
