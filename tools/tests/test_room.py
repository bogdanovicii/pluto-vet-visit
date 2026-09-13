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
        info = C.tile_info()
        bottom = ''.join(C.CELL[c] for c in C.ROOM_MAP[-1])
        top = ''.join(C.CELL[c] for c in C.ROOM_MAP[0])
        self.assertEqual(info[:C.WIDTH], bottom)
        self.assertEqual(info[-C.WIDTH:], top)

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
