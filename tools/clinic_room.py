"""The vet clinic room as an ASCII cell map -> Alexandria .newroom JSON, ClinicLayout.cs and a preview.

One 36 x 63 room (30 x 54 until 0.12.0), three zones stacked south to north (waiting room y 0..15, ward y 18..37, operating
theatre y 40..60), separated by two-cell-thick wall segments with a two-cell gap on the centre line (x 17..18); two more wall
rows close the theatre's north edge so its wall face (pluto_wall_face_solid) has something to stand on. A clinic door prop
(pluto_clinic_door) sits in each gap; VetVisitController seals it behind Pluto and opens the next one when the zone's waves are dead.

Coordinates everywhere else in this file are GAME coordinates: x to the right, y up, cell (0,0) at the
room's bottom-left. ROOM_MAP is written top row first for readability and flipped on export.
"""
import json
import os

from PIL import Image, ImageDraw

import clinic_objects as O

WIDTH, HEIGHT = O.ROOM_W, O.ROOM_H
SCALE = 8  # preview pixels per cell (the schematic); the sprite preview renders at 16
GAP = O.DOOR_GAP_X
DIVIDERS = (16, 38)          # lower row of each two-row zone wall (the wall face stands on it)
NORTH_WALL = 61              # rows 61..62: the theatre's solid north wall


def _row(y):
    if y >= NORTH_WALL:
        return '#' * WIDTH
    if any(d <= y <= d + 1 for d in DIVIDERS):
        return '#' * GAP + '..' + '#' * (WIDTH - GAP - 2)
    return '.' * WIDTH


# top row first: y = 62 (north edge) .. y = 0 (south edge)
ROOM_MAP = [_row(y) for y in range(HEIGHT - 1, -1, -1)]
CELL = {'.': '1', '#': '2'}

CONTROLLER = 'pluto_past_controller'
# The Vet's spawn is his body centre (AIActor.Spawn puts the rigidbody's UnitCenter there): his 48x40 sprite's lower-left is
# (VET - (17, 19.5) px), so at (18, 51) he stands on open floor 1.3 cells north of the exam table's top (y 48.5) and the op
# lamp's boom (y 49.5), with the anaesthesia machine and the heart monitor 2+ cells to either side.
NAMED = {
    'Spawn': (5.0, 2.5),         # Pluto starts here, beside the carrier (waiting room)
    'Vet': (18.0, 51.0),         # The Vet stands on open floor north of the exam table (theatre)
    'Table': (18.0, 47.0),       # exam table centre
    'CameraFocus': (18.0, 47.0), # camera lock point during the dialogue: between the theatre door and the Vet
    'Controller': (17.0, 1.0),   # invisible controller object
    'WardDoor': (17.0, 16.0),    # lower-left cell of the door gap in the first wall (the door prop stands here)
    'TheatreDoor': (17.0, 38.0), # same for the second wall
    'IntroFocus': (15.0, 7.5),   # camera lock point during the waiting-room intro
    'OwnerStart': (3.5, 2.5),    # the Owner stands here beside the carrier (sprite lower-left)
    'OwnerExit': (17.0, -3.5),   # where he walks out (through the south exit, off the map)
    'Intercom': (17.5, 15.5),    # the speaker above the ward door: the "Pluto?" line comes from here
    'GreeterSpot': (17.5, 22.5),  # the Vet Tech who greets Pluto in the ward, just past the door
}
# Zone thresholds (cell y): Pluto is "in" a zone once his y passes it. The controller seals the door behind him then.
ZONES = {
    'WARD_MIN_Y': 18,
    'THEATRE_MIN_Y': 40,
}
# Where the waves stand up. Both ward waves come out of the kennel bank (east and west wall); wave 2 also from the north
# kit and the south-west. Each is a list of cells; the controller reads the enemy list from the config.
SPAWNS = {
    'Wave1Spawns': [(4.5, 26.5), (31.5, 26.5), (4.5, 22.0), (31.5, 30.5)],   # out of the kennel bank, 1.5 cells off its colliders
    'Wave2Spawns': [(4.5, 20.5), (4.5, 32.5), (31.5, 20.5), (31.5, 32.5), (18.0, 33.0), (10.0, 21.5)],   # out of the kennel bank
    'TheatreSpawns': [(32.0, 46.5), (32.5, 44.0), (32.5, 48.5)],   # the Nurse and two Techs, from the east side door
}
# Other cells the controller uses (0.12.0; they were literals in VetVisitController): the waiting room's loose critters and the
# two hearts on the nurse station once the ward is clear.
SPOTS = {
    'CritterSpots': [(9.0, 3.5), (14.0, 12.0), (22.0, 4.0)],
    'HeartSpots': [(17.5, 28.6), (19.5, 28.6)],
}
# Bystanders placed by the room (see cast_layout.NPC_OBJECTS for the art behind each name). Sprite lower-left on the cell.
NPCS = [
    ('pluto_npc_owner', (3.5, 2.5)),
    ('pluto_npc_receptionist', (28.5, 14.3)),  # behind the counter (at x 26, right of its monitor), in front of the back cabinet
    # Rex and Grandma sit on the first and fourth chairs of the north row (chairs at (3.75, 9.75) and (8.25, 9.75), 24 px tall like
    # the sprites): each stands a fifth of a cell SOUTH of its chair so it sorts in front of the seat and the back rest shows above it.
    ('pluto_npc_rex', (3.75, 9.55)),
    ('pluto_npc_grandma', (8.25, 9.55)),
]
EXITS = [((GAP, 0), 'SOUTH')]     # one unused south exit (the generator wants a door somewhere)


DOOR = 'pluto_clinic_door'


def PLACEABLES_():
    return ([(CONTROLLER, NAMED['Controller']), (DOOR, NAMED['WardDoor']), (DOOR, NAMED['TheatreDoor'])]
            + list(NPCS) + list(O.PROPS))


PLACEABLES = PLACEABLES_()


def cell(x, y):
    return ROOM_MAP[HEIGHT - 1 - int(y)][int(x)]


def is_floor(x, y):
    return 0 <= x < WIDTH and 0 <= y < HEIGHT and cell(x, y) == '.'


def tile_info():
    return ''.join(''.join(CELL[c] for c in row) for row in reversed(ROOM_MAP))


def vec(x, y):
    return {'x': float(x), 'y': float(y)}


def room_data():
    placeables = PLACEABLES_()
    return {
        'tileInfo': tile_info(),
        'roomSize': {'x': WIDTH, 'y': HEIGHT},
        'waveTriggers': [], 'nodeTypes': [], 'nodeWrapModes': [], 'nodePositions': [], 'nodePaths': [], 'nodeOrder': [],
        'category': 'ENTRANCE', 'normalSubCategory': '', 'specialSubCategory': '', 'bossSubCategory': '',
        'enemyPositions': [], 'enemyGUIDs': [], 'enemyAttributes': [],
        'placeablePositions': [vec(x, y) for _, (x, y) in placeables],
        'placeableGUIDs': [name for name, _ in placeables],
        'placeableAttributes': ['' for _ in placeables],
        'enemyReinforcementLayers': [],
        'exitPositions': [vec(x, y) for (x, y), _ in EXITS],
        'exitDirections': [d for _, d in EXITS],
        'floors': [],
        'weight': 1.0,
        'isSpecialRoom': False, 'randomizeEnemyPositions': False,
        'doFloorDecoration': False, 'doWallDecoration': False, 'doLighting': True, 'darkRoom': False,
        'visualSubtype': -1,
        'superSpecialRoomType': 'none',
        'AmbientLight_R': 0.0, 'AmbientLight_G': 0.0, 'AmbientLight_B': 0.0, 'usesAmbientLight': False,
        'nodePathVisible': [], 'specialRoomPool': '', 'additionalPauseDelay': [],
    }


def to_json():
    return json.dumps(room_data(), indent=1)


def cs_escape(text):
    """A C# string literal body: backslashes and quotes escaped, anything outside printable ASCII dropped."""
    text = ''.join(ch for ch in text if 32 <= ord(ch) < 127)
    return text.replace('\\', '\\\\').replace('"', '\\"')


def layout_cs():
    lines = [
        '// GENERATED by tools/clinic_room.py from the ASCII room map. Do not edit by hand.',
        'using UnityEngine;',
        '',
        'namespace PlutoVetVisit',
        '{',
        '    public static class ClinicLayout',
        '    {',
        '        public const int WIDTH = %d;' % WIDTH,
        '        public const int HEIGHT = %d;' % HEIGHT,
        '        public const string CONTROLLER_OBJECT = "%s";' % CONTROLLER,
        '        public const string DOOR_OBJECT = "%s";' % DOOR,
    ]
    for name, (x, y) in NAMED.items():
        lines.append('        public static readonly Vector2 %s = new Vector2(%sf, %sf);' % (name, x, y))
    for name, value in ZONES.items():
        lines.append('        public const float %s = %sf;' % (name, float(value)))
    for name, cells in list(SPAWNS.items()) + list(SPOTS.items()):
        lines.append('        public static readonly Vector2[] %s = { %s };'
                     % (name, ', '.join('new Vector2(%sf, %sf)' % (x, y) for x, y in cells)))
    lines.append('        public static readonly ObjectSpec[] OBJECTS = {')
    for o in O.OBJECTS:
        if o.collider is None:
            layer, ox, oy, w, h = 'None', 0, 0, 0, 0
        else:
            layer_key, ox, oy, w, h = o.collider
            layer = {'low': 'Low', 'high': 'High'}[layer_key]
        lines.append('            new ObjectSpec("%s", "%s", ObjectSpec.Layer.%s, %d, %d, %d, %d, %sf, %s, %d, %sf, "%s"),'
                     % (o.name, o.png, layer, ox, oy, w, h, round(o.height_off_ground, 4), 'true' if o.stand else 'false',
                        o.frame_count, round(o.fps, 3), cs_escape(o.comment)))
    lines += [
        '        };',
        '    }',
        '',
        '    public class ObjectSpec',
        '    {',
        '        public enum Layer { None, Low, High }',
        '        public string Name;',
        '        public string Png;',
        '        public Layer Collider;',
        '        public int OffX, OffY, W, H;',
        '        public float HeightOffGround;',
        '        public bool Perpendicular;',
        '        public int Frames;      // 1 = static; frame k >= 2 is <Png>_f<k>.png',
        '        public float Fps;',
        '        public string Comment;  // what Pluto thinks when he examines it ("" = not examinable)',
        '        public ObjectSpec(string name, string png, Layer collider, int offX, int offY, int w, int h, float heightOffGround, bool perpendicular, int frames, float fps, string comment)',
        '        {',
        '            Name = name; Png = png; Collider = collider; OffX = offX; OffY = offY; W = w; H = h; HeightOffGround = heightOffGround;',
        '            Perpendicular = perpendicular; Frames = frames; Fps = fps; Comment = comment;',
        '        }',
        '    }',
        '}',
        '',
    ]
    return '\n'.join(lines)


def preview_image():
    im = Image.new('RGBA', (WIDTH * SCALE, HEIGHT * SCALE), (0x2E, 0x2E, 0x3A, 255))
    d = ImageDraw.Draw(im)
    sizes = {o.name: o.size for o in O.OBJECTS}
    for y in range(HEIGHT):
        for x in range(WIDTH):
            colour = (0xF4, 0xF6, 0xF8, 255) if cell(x, y) == '.' else (0x8C, 0x94, 0xA2, 255)
            py = (HEIGHT - 1 - y) * SCALE
            d.rectangle((x * SCALE, py, x * SCALE + SCALE - 1, py + SCALE - 1), fill=colour, outline=(0xDC, 0xE0, 0xE6, 255))
    for name, (x, y) in PLACEABLES_():
        w, h = sizes.get(name, (16, 16))
        px, py = x * SCALE, (HEIGHT - y) * SCALE - h / 16.0 * SCALE
        d.rectangle((px, py, px + w / 16.0 * SCALE, py + h / 16.0 * SCALE), outline=(0xD8, 0x3A, 0x3A, 255), fill=(0xF0, 0x8A, 0x24, 120))
        d.text((px + 1, py + 1), name.replace('pluto_', '')[:6], fill=(0, 0, 0, 255))
    for name, (x, y) in NAMED.items():
        px, py = x * SCALE, (HEIGHT - y) * SCALE
        d.ellipse((px - 3, py - 3, px + 3, py + 3), fill=(0x3F, 0x9E, 0x8F, 255))
        d.text((px + 4, py - 6), name, fill=(0x2C, 0x73, 0x67, 255))
    for name, cells in SPAWNS.items():
        for x, y in cells:
            px, py = x * SCALE, (HEIGHT - y) * SCALE
            d.rectangle((px - 3, py - 3, px + 3, py + 3), fill=(0xD8, 0x3A, 0x3A, 255))
    for (x, y), _ in EXITS:
        d.rectangle((x * SCALE, (HEIGHT - y) * SCALE - SCALE, x * SCALE + 2 * SCALE, (HEIGHT - y) * SCALE), fill=(0x7D, 0xB4, 0x47, 255))
    return im


PX = 16  # sprite preview pixels per cell


def vet_sprite_rect():
    """The Vet's 48x40 sprite rectangle (x0, y0, x1, y1) in cells at his spawn: AIActor.Spawn puts his rigidbody's UnitCenter
    (the centre of the vet_poses.HITBOX body collider) on NAMED['Vet']."""
    import vet_poses
    hx, hy, hw, hh = vet_poses.HITBOX
    vx, vy = NAMED['Vet']
    x0, y0 = vx - (hx + hw / 2.0) / 16.0, vy - (hy + hh / 2.0) / 16.0
    w, h = vet_poses.CANVAS
    return (x0, y0, x0 + w / 16.0, y0 + h / 16.0)


def sprite_preview_image(project, with_vet=True):
    """The room as the game will draw it: the real prop PNGs (Resources/Objects), the NPCs' first idle frames and the Vet's first
    idle frame at his spawn, pasted in draw order - floors and flat decor by height off ground, then standing props and actors
    from back to front (by their base depth 2*y - height off ground, which is north to south for everything at height 0 and puts
    wall decor just in front of its wall face; an actor stands at its feet), then flat decor with a height off ground of 1 or more."""
    import cast_layout
    import npc_poses

    objects = os.path.join(project, 'Resources', 'Objects')
    specs = {o.name: o for o in O.OBJECTS}
    im = Image.new('RGBA', (WIDTH * PX, HEIGHT * PX), (0x2E, 0x2E, 0x3A, 255))
    d = ImageDraw.Draw(im)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if cell(x, y) == '#':
                py = (HEIGHT - 1 - y) * PX
                d.rectangle((x * PX, py, x * PX + PX - 1, py + PX - 1), fill=(0x5A, 0x5E, 0x6A, 255))

    def paste(png, x, y):
        sprite = Image.open(png).convert('RGBA')
        px, py = int(round(x * PX)), int(round((HEIGHT - y) * PX)) - sprite.height
        im.alpha_composite(sprite, (px, py))

    flat_under, standing, flat_over = [], [], []
    for name, (x, y) in O.PROPS:
        spec = specs[name]
        png = os.path.join(objects, spec.png + '.png')
        if spec.stand:
            standing.append((2.0 * y - spec.height_off_ground, png, x, y))
        elif spec.height_off_ground >= 1.0:
            flat_over.append((spec.height_off_ground, png, x, y))
        else:
            flat_under.append((spec.height_off_ground, png, x, y))
    for name, (x, y) in PLACEABLES_():
        if name == DOOR:
            standing.append((2.0 * y - specs[DOOR].height_off_ground, os.path.join(objects, 'clinic_door.png'), x, y))
    for name, (x, y) in NPCS:
        folder = cast_layout.NPC_OBJECTS[name]
        clip = next(iter(npc_poses.NPCS[folder]['clips']))
        standing.append((2.0 * y, os.path.join(project, 'Resources', 'Npcs', folder, clip, '%s_%s_001.png' % (folder, clip)), x, y))
    vet_png = os.path.join(project, 'Resources', 'Boss', 'vet', 'idle', 'vet_idle_001.png')
    if with_vet and os.path.exists(vet_png):
        x0, y0, _, _ = vet_sprite_rect()
        standing.append((2.0 * y0, vet_png, x0, y0))
    for hog, png, x, y in sorted(flat_under, key=lambda t: t[0]):
        paste(png, x, y)
    for depth, png, x, y in sorted(standing, key=lambda t: -t[0]):
        paste(png, x, y)
    for hog, png, x, y in sorted(flat_over, key=lambda t: t[0]):
        paste(png, x, y)
    return im


def write(project):
    room = os.path.join(project, 'Resources', 'Rooms', 'vet_clinic.newroom')
    os.makedirs(os.path.dirname(room), exist_ok=True)
    with open(room, 'w') as fh:
        fh.write(to_json())
    cs = os.path.join(project, 'src', 'ClinicLayout.cs')
    with open(cs, 'w') as fh:
        fh.write(layout_cs())
    prev = os.path.join(project, 'docs', 'preview', 'clinic-room.png')
    os.makedirs(os.path.dirname(prev), exist_ok=True)
    preview_image().save(prev)
    sprites = os.path.join(project, 'docs', 'preview', 'clinic-room-sprites.png')
    full = sprite_preview_image(project)
    full.save(sprites)
    closeup = os.path.join(project, 'docs', 'preview', 'clinic-theatre-vet.png')
    theatre_closeup(full).save(closeup)
    return room, cs, prev, sprites, closeup


def theatre_closeup(full, scale=3):
    """The operating theatre's middle at 3x (x 8..28, y 40..58): the Vet at his spawn among the table group, his sprite rectangle
    outlined in teal so a prop drawn over it shows."""
    x0, y0, x1, y1 = 8, 40, 28, 58
    crop = full.crop((x0 * PX, (HEIGHT - y1) * PX, x1 * PX, (HEIGHT - y0) * PX))
    crop = crop.resize((crop.width * scale, crop.height * scale), Image.NEAREST)
    d = ImageDraw.Draw(crop)
    vx0, vy0, vx1, vy1 = vet_sprite_rect()
    d.rectangle(((vx0 - x0) * PX * scale, (y1 - vy1) * PX * scale, (vx1 - x0) * PX * scale - 1, (y1 - vy0) * PX * scale - 1),
                outline=(0x3F, 0x9E, 0x8F, 255))
    return crop
