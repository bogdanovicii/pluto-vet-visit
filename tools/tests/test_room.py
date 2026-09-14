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
        for name, (x, y) in C.PLACEABLES:
            self.assertTrue(C.is_floor(x, y), '%s at %s,%s is not on floor' % (name, x, y))

    def test_named_cells_on_floor(self):
        for name, (x, y) in C.NAMED.items():
            self.assertTrue(C.is_floor(x, y), name)

    def test_zone_walls_and_door_gaps(self):
        # two-cell-thick dividers with a two-cell gap on the centre line, everything else floor
        for y in range(C.HEIGHT):
            wall_row = y in (13, 14, 32, 33)
            for x in range(C.WIDTH):
                expect_wall = wall_row and x not in (14, 15)
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
            for x, y in cells:
                self.assertTrue(C.is_floor(x, y), (name, x, y))
                self.assertTrue(C.ZONES['WARD_MIN_Y'] <= y < 32, (name, x, y))

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

    def test_preview_image_size(self):
        im = C.preview_image()
        self.assertEqual(im.size, (C.WIDTH * C.SCALE, C.HEIGHT * C.SCALE))


if __name__ == '__main__':
    unittest.main()
