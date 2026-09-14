import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import clinic_room as C  # noqa: E402


class RoomTests(unittest.TestCase):
    def test_map_is_rectangular(self):
        self.assertEqual(len(C.ROOM_MAP), C.HEIGHT)
        for row in C.ROOM_MAP:
            self.assertEqual(len(row), C.WIDTH)
            self.assertTrue(set(row) <= {'.', '#'}, row)

    def test_tileinfo_length_and_legend(self):
        info = C.tile_info()
        self.assertEqual(len(info), C.WIDTH * C.HEIGHT)
        self.assertTrue(set(info) <= {'1', '2'})

    def test_tileinfo_bottom_row_first(self):
        saved = C.ROOM_MAP
        try:
            # asymmetric map so the bottom (last ASCII row) and top (first ASCII row) differ
            C.ROOM_MAP = ['#' + '.' * (C.WIDTH - 1)] + ['.' * C.WIDTH] * (C.HEIGHT - 1)
            info = C.tile_info()
            bottom = ''.join(C.CELL[c] for c in C.ROOM_MAP[-1])
            top = ''.join(C.CELL[c] for c in C.ROOM_MAP[0])
            self.assertEqual(info[:C.WIDTH], bottom)
            self.assertEqual(info[-C.WIDTH:], top)
        finally:
            C.ROOM_MAP = saved

    def test_flip_and_is_floor_with_an_asymmetric_map(self):
        saved = C.ROOM_MAP
        try:
            # one wall at the top-left ASCII cell = game cell (0, HEIGHT-1)
            C.ROOM_MAP = ['#' + '.' * (C.WIDTH - 1)] + ['.' * C.WIDTH] * (C.HEIGHT - 1)
            info = C.tile_info()
            self.assertEqual(len(info), C.WIDTH * C.HEIGHT)
            self.assertEqual(info[0], '1')                      # first char = game cell (0, 0) = bottom row
            self.assertEqual(info[-C.WIDTH], '2')               # last row of tileInfo = top ASCII row
            self.assertEqual(info.count('2'), 1)
            self.assertFalse(C.is_floor(0, C.HEIGHT - 1))       # the wall
            self.assertTrue(C.is_floor(0, 0))
            self.assertFalse(C.is_floor(-1, 0))
            self.assertFalse(C.is_floor(C.WIDTH, 0))
            self.assertFalse(C.is_floor(0, C.HEIGHT))
        finally:
            C.ROOM_MAP = saved

    def test_room_data_json_roundtrip(self):
        data = json.loads(C.to_json())
        self.assertEqual(data['roomSize'], {'x': C.WIDTH, 'y': C.HEIGHT})
        self.assertEqual(data['category'], 'ENTRANCE')
        self.assertEqual(data['floors'], [])
        self.assertEqual(len(data['placeablePositions']), len(data['placeableGUIDs']))
        self.assertEqual(len(data['placeablePositions']), len(data['placeableAttributes']))
        self.assertEqual(data['exitDirections'], ['SOUTH'])
        self.assertEqual(data['superSpecialRoomType'], 'none')

    def test_controller_is_placed(self):
        self.assertIn(C.CONTROLLER, [name for name, _ in C.PLACEABLES])

    def test_placeables_on_floor(self):
        # flat decor (no collider) may hang on a wall row: the wall faces and the pictures/signs on them
        flat = {o.name for o in C.O.OBJECTS if o.collider is None}
        for name, (x, y) in C.PLACEABLES:
            if name in flat:
                self.assertTrue(0 <= x < C.WIDTH and 0 <= y < C.HEIGHT, name)
                continue
            self.assertTrue(C.is_floor(x, y), '%s at %s,%s is not on floor' % (name, x, y))

    def test_wall_faces_sit_on_the_wall_rows(self):
        faces = [(n, c) for n, c in C.PLACEABLES if n.startswith('pluto_wall_face')]
        self.assertEqual(faces, [('pluto_wall_face', (0.0, 13.0)), ('pluto_wall_face', (0.0, 32.0)), ('pluto_wall_face_solid', (0.0, 52.0))])
        for _, (x, y) in faces:
            self.assertFalse(C.is_floor(x, y))
            self.assertFalse(C.is_floor(x, y + 1))
        self.assertEqual(C.HEIGHT, 54)

    def test_named_cells_on_floor(self):
        for name, (x, y) in C.NAMED.items():
            if name == 'OwnerExit':
                continue                                     # deliberately outside: the Owner leaves the room
            self.assertTrue(C.is_floor(x, y), name)

    def test_zone_walls_and_door_gaps(self):
        # two-cell-thick dividers with a two-cell gap on the centre line, everything else floor
        for y in range(C.HEIGHT):
            wall_row = y in (13, 14, 32, 33)
            for x in range(C.WIDTH):
                expect_wall = (wall_row and x not in (14, 15)) or y >= 52    # y 52..53: the theatre's solid north wall
                self.assertEqual(C.cell(x, y) == '#', expect_wall, (x, y))
        self.assertEqual(C.ZONES, {'WARD_MIN_Y': 15, 'THEATRE_MIN_Y': 34})
        self.assertLess(C.NAMED['Spawn'][1], 13)
        self.assertGreater(C.NAMED['Vet'][1], C.ZONES['THEATRE_MIN_Y'])

    def test_doors_stand_in_the_gaps(self):
        doors = [cell for name, cell in C.PLACEABLES if name == C.DOOR]
        self.assertEqual(doors, [(14.0, 13.0), (14.0, 32.0)])
        for x, y in doors:
            self.assertTrue(C.is_floor(x, y) and C.is_floor(x + 1, y) and C.is_floor(x, y + 1) and C.is_floor(x + 1, y + 1))
            self.assertFalse(C.is_floor(x - 1, y) or C.is_floor(x + 2, y))

    def test_wave_spawns_in_the_ward_on_floor(self):
        for name, cells in C.SPAWNS.items():
            self.assertGreaterEqual(len(cells), 3, name)
            lo, hi = (C.ZONES['THEATRE_MIN_Y'], C.HEIGHT) if name.startswith('Theatre') else (C.ZONES['WARD_MIN_Y'], 32)
            for x, y in cells:
                self.assertTrue(C.is_floor(x, y), (name, x, y))
                self.assertTrue(lo <= y < hi, (name, x, y))

    def test_npcs_wait_in_the_waiting_room(self):
        names = [n for n, _ in C.NPCS]
        self.assertEqual(names, ['pluto_npc_owner', 'pluto_npc_receptionist', 'pluto_npc_rex', 'pluto_npc_grandma'])
        for name, (x, y) in C.NPCS:
            self.assertTrue(C.is_floor(x, y), name)
            self.assertLess(y, 13, name)
        seats = {(x, y) for n, (x, y) in C.O.PROPS if n == 'pluto_chair'}
        for who in ('pluto_npc_rex', 'pluto_npc_grandma'):
            x, y = dict(C.NPCS)[who]
            self.assertIn((x, round(y + 0.2, 2)), seats, who)         # sits a fifth of a cell in front of a chair
        self.assertLess(C.NAMED['OwnerExit'][1], 0)          # he walks off the map through the south exit
        self.assertTrue(C.is_floor(*C.NAMED['OwnerStart']))
        self.assertTrue(C.is_floor(*C.NAMED['IntroFocus']))

    def test_layout_cs_has_zones_and_spawns(self):
        cs = C.layout_cs()
        for name in C.ZONES:
            self.assertIn('public const float %s = ' % name, cs)
        for name in C.SPAWNS:
            self.assertIn('public static readonly Vector2[] %s = { new Vector2(' % name, cs)

    def test_exit_on_south_border(self):
        (x, y), direction = C.EXITS[0]
        self.assertEqual(y, 0)
        self.assertEqual(direction, 'SOUTH')
        self.assertTrue(0 < x < C.WIDTH - 1)

    def test_layout_cs(self):
        cs = C.layout_cs()
        self.assertIn('public const int WIDTH = %d;' % C.WIDTH, cs)
        self.assertIn('public const string CONTROLLER_OBJECT = "%s";' % C.CONTROLLER, cs)
        for name in C.NAMED:
            self.assertIn('public static readonly Vector2 %s = ' % name, cs)
        self.assertIn('public static readonly ObjectSpec[] OBJECTS', cs)

    def test_layout_cs_object_spec_contract(self):
        """v0.11 contract: 12 constructor arguments - ..., bool perpendicular (Obj.stand), int frames, float fps, string comment."""
        cs = C.layout_cs()
        for field in ('public bool Perpendicular;', 'public int Frames;', 'public float Fps;', 'public string Comment;'):
            self.assertIn(field, cs)
        self.assertIn('public ObjectSpec(string name, string png, Layer collider, int offX, int offY, int w, int h, '
                      'float heightOffGround, bool perpendicular, int frames, float fps, string comment)', cs)
        self.assertIn('Perpendicular = perpendicular; Frames = frames; Fps = fps; Comment = comment;', cs)
        for o in C.O.OBJECTS:
            line = next(l.strip() for l in cs.splitlines() if l.strip().startswith('new ObjectSpec("%s",' % o.name))
            self.assertTrue(line.endswith('"),'), line)
            head, comment = line[:-3].rsplit(', "', 1)
            self.assertEqual(comment, C.cs_escape(o.comment), line)
            args = head[len('new ObjectSpec('):].split(', ')
            self.assertEqual(len(args) + 1, 12, line)
            self.assertEqual(args[8], 'true' if o.stand else 'false', line)
            self.assertEqual(args[9], str(o.frame_count), line)
            self.assertEqual(float(args[10].rstrip('f')), o.fps, line)
        faces = [l for l in cs.splitlines() if '"pluto_wall_face' in l]
        self.assertEqual(len(faces), 2)
        for l in faces:
            self.assertIn('-0.2f, true, 1, ', l)

    def test_cs_escape(self):
        self.assertEqual(C.cs_escape('Sushi. Behind glass.'), 'Sushi. Behind glass.')
        self.assertEqual(C.cs_escape('a "b" \\ c'), 'a \\"b\\" \\\\ c')
        self.assertEqual(C.cs_escape('café\n'), 'caf')

    def test_npc_and_spawn_positions_stay_clear(self):
        """Every wave spawn stays inside its zone; the NPCs stand on floor inside the waiting room, clear of high colliders."""
        specs = {o.name: o for o in C.O.OBJECTS}
        for name, (x, y) in C.NPCS:
            for prop, (px, py) in C.O.PROPS:
                col = specs[prop].collider
                if col is None or col[0] != 'high':
                    continue
                _, ox, oy, w, h = col
                inside = px + ox / 16.0 <= x < px + (ox + w) / 16.0 and py + oy / 16.0 <= y < py + (oy + h) / 16.0
                self.assertFalse(inside, (name, prop))

    def test_preview_image_size(self):
        im = C.preview_image()
        self.assertEqual(im.size, (C.WIDTH * C.SCALE, C.HEIGHT * C.SCALE))

    def test_sprite_preview_renders_the_generated_pngs(self):
        project = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if not os.path.exists(os.path.join(project, 'Resources', 'Objects', 'floor_ward.png')):
            raise unittest.SkipTest('run tools/make_art.py first')
        im = C.sprite_preview_image(project)
        self.assertEqual(im.size, (C.WIDTH * C.PX, C.HEIGHT * C.PX))
        self.assertEqual(im.getpixel((8, im.height - 8))[:3], (0xF8, 0xF3, 0xEA))        # the warm waiting-room floor at (0, 0)


if __name__ == '__main__':
    unittest.main()
