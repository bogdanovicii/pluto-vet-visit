"""The vet clinic room as an ASCII cell map -> Alexandria .newroom JSON, ClinicLayout.cs and a preview.

One 30 x 54 room, three zones stacked south to north (waiting room, ward, operating theatre), separated by
two-cell-thick wall segments with a two-cell gap on the centre line; two more wall rows close the theatre's north
edge so its wall face (pluto_wall_face_solid) has something to stand on. A clinic door prop (pluto_clinic_door) sits
in each gap; VetVisitController seals it behind Pluto and opens the next one when the zone's waves are dead.

Coordinates everywhere else in this file are GAME coordinates: x to the right, y up, cell (0,0) at the
room's bottom-left. ROOM_MAP is written top row first for readability and flipped on export.
"""
import json
import os

from PIL import Image, ImageDraw

import clinic_objects as O

WIDTH, HEIGHT = 30, 54
SCALE = 8  # preview pixels per cell (the schematic); the sprite preview renders at 16

ROOM_MAP = [
    "##############################",  # y = 53 (north edge; the generator adds the outer walls beyond)
    "##############################",  # y = 52: the theatre's north wall rows carry pluto_wall_face_solid
    "..............................",  # y = 51 (theatre y 34..51)
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "##############..##############",  # theatre wall, door gap at x 14..15
    "##############..##############",
    "..............................",  # ward y 15..31
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "##############..##############",  # ward wall, door gap at x 14..15
    "##############..##############",
    "..............................",  # waiting room y 1..12
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",  # y = 0 (south edge)
]
CELL = {'.': '1', '#': '2'}

CONTROLLER = 'pluto_past_controller'
NAMED = {
    'Spawn': (5.0, 2.5),         # Pluto starts here, beside the carrier (waiting room)
    'Vet': (14.5, 44.5),         # The Vet stands behind the exam table (theatre)
    'Table': (14.5, 42.0),       # exam table centre
    'CameraFocus': (14.5, 41.5), # camera lock point during the dialogue
    'Controller': (14.0, 1.0),   # invisible controller object
    'WardDoor': (14.0, 13.0),    # lower-left cell of the door gap in the first wall (the door prop stands here)
    'TheatreDoor': (14.0, 32.0), # same for the second wall
    'IntroFocus': (12.0, 6.5),   # camera lock point during the waiting-room intro
    'OwnerStart': (3.5, 2.5),    # the Owner stands here beside the carrier (sprite lower-left)
    'OwnerExit': (13.0, -3.5),   # where he walks out (through the south exit, off the map)
    'Intercom': (14.5, 12.5),    # the speaker above the ward door: the "Pluto?" line comes from here
    'GreeterSpot': (14.5, 19.5),  # the Vet Tech who greets Pluto in the ward, just past the door
}
# Zone thresholds (cell y): Pluto is "in" a zone once his y passes it. The controller seals the door behind him then.
ZONES = {
    'WARD_MIN_Y': 15,
    'THEATRE_MIN_Y': 34,
}
# Where the waves stand up. Wave 1 comes out of the side doors (east and west wall, mid-ward); wave 2 out of
# the kennels. Each is a list of cells; the controller reads the enemy list from the config.
SPAWNS = {
    'Wave1Spawns': [(3.5, 23.5), (25.5, 23.5), (3.5, 19.0), (25.5, 27.5)],   # a cell and a half off the kennel columns
    'Wave2Spawns': [(3.5, 17.5), (3.5, 29.5), (25.5, 17.5), (25.5, 29.5), (14.5, 29.0), (9.0, 17.5)],
    'TheatreSpawns': [(26.0, 40.0), (26.5, 37.5), (26.5, 42.5)],   # the Nurse and two Techs, from the east side door
}
# Bystanders placed by the room (see cast_layout.NPC_OBJECTS for the art behind each name). Sprite lower-left on the cell.
NPCS = [
    ('pluto_npc_owner', (3.5, 2.5)),
    ('pluto_npc_receptionist', (21.5, 11.3)),  # behind the desk (desk top ends at y 12.5): head and shoulders show
    # Rex and Grandma sit on the third and fourth west-wall chairs (chairs at (0.75, 7.5) and (0.75, 9.0), 24 px tall like the
    # sprites): each stands a fifth of a cell SOUTH of its chair so it sorts in front of the seat and the back rest shows above it.
    ('pluto_npc_rex', (0.75, 7.3)),
    ('pluto_npc_grandma', (0.75, 8.8)),
]
EXITS = [((14, 0), 'SOUTH')]     # one unused south exit (the generator wants a door somewhere)


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
    for name, cells in SPAWNS.items():
        lines.append('        public static readonly Vector2[] %s = { %s };'
                     % (name, ', '.join('new Vector2(%sf, %sf)' % (x, y) for x, y in cells)))
    lines.append('        public static readonly ObjectSpec[] OBJECTS = {')
    for o in O.OBJECTS:
        if o.collider is None:
            layer, ox, oy, w, h = 'None', 0, 0, 0, 0
        else:
            layer_key, ox, oy, w, h = o.collider
            layer = {'low': 'Low', 'high': 'High'}[layer_key]
        lines.append('            new ObjectSpec("%s", "%s", ObjectSpec.Layer.%s, %d, %d, %d, %d, %sf),'
                     % (o.name, o.png, layer, ox, oy, w, h, o.height_off_ground))
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
        '        public ObjectSpec(string name, string png, Layer collider, int offX, int offY, int w, int h, float heightOffGround)',
        '        {',
        '            Name = name; Png = png; Collider = collider; OffX = offX; OffY = offY; W = w; H = h; HeightOffGround = heightOffGround;',
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


def sprite_preview_image(project):
    """The room as the game will draw it: the real prop PNGs (Resources/Objects) and the NPCs' first idle frames pasted at
    their placements in draw order - floors and flat decor by height off ground, then perpendicular props and NPCs from north
    to south, then flat decor with a height off ground of 1 or more (the lamp head hangs over everything)."""
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
        if spec.collider is not None:
            standing.append((y, png, x))
        elif spec.height_off_ground >= 1.0:
            flat_over.append((spec.height_off_ground, png, x, y))
        else:
            flat_under.append((spec.height_off_ground, png, x, y))
    for name, (x, y) in PLACEABLES_():
        if name == DOOR:
            standing.append((y, os.path.join(objects, 'clinic_door.png'), x))
    for name, (x, y) in NPCS:
        folder = cast_layout.NPC_OBJECTS[name]
        clip = next(iter(npc_poses.NPCS[folder]['clips']))
        standing.append((y, os.path.join(project, 'Resources', 'Npcs', folder, clip, '%s_%s_001.png' % (folder, clip)), x))
    for hog, png, x, y in sorted(flat_under, key=lambda t: t[0]):
        paste(png, x, y)
    for y, png, x in sorted(standing, key=lambda t: -t[0]):
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
    sprite_preview_image(project).save(sprites)
    return room, cs, prev, sprites
