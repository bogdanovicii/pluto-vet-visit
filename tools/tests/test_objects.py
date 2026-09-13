import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import clinic_objects as O  # noqa: E402
import clinic_room as C  # noqa: E402
import vetpixel as V  # noqa: E402

EXPECTED_SIZES = {
    'pluto_exam_table': (48, 32), 'pluto_cabinet': (32, 40), 'pluto_cart': (24, 24), 'pluto_sink': (32, 32),
    'pluto_scale': (16, 16), 'pluto_carrier': (32, 24), 'pluto_poster': (16, 24), 'pluto_cone': (12, 10),
    'pluto_toy_mouse': (10, 6), 'pluto_toy_ball': (6, 6), 'pluto_feather_wand': (14, 10),
    'pluto_scratch_post': (16, 24), 'pluto_syringe_tray': (16, 10),
}


class ObjectTests(unittest.TestCase):
    def test_registry(self):
        names = [o.name for o in O.OBJECTS]
        self.assertEqual(sorted(names), sorted(EXPECTED_SIZES))
        self.assertEqual(len(names), len(set(names)))

    def test_sizes_and_palette(self):
        for o in O.OBJECTS:
            V.R(o.rows)
            self.assertEqual(o.size, EXPECTED_SIZES[o.name], o.name)
            V.image(o.rows)  # raises KeyError on an unknown palette key

    def test_colliders_inside_sprite(self):
        for o in O.OBJECTS:
            if o.collider is None:
                continue
            layer, ox, oy, w, h = o.collider
            self.assertIn(layer, ('low', 'high'))
            self.assertTrue(0 <= ox and 0 <= oy and w > 0 and h > 0, o.name)
            self.assertLessEqual(ox + w, o.size[0], o.name)
            self.assertLessEqual(oy + h, o.size[1], o.name)

    def test_furniture_blocks_and_decor_does_not(self):
        blocking = {o.name for o in O.OBJECTS if o.collider is not None}
        self.assertEqual(blocking, {'pluto_exam_table', 'pluto_cabinet', 'pluto_cart', 'pluto_sink', 'pluto_carrier', 'pluto_scratch_post'})

    def test_props_placed_inside_room(self):
        sizes = {o.name: o.size for o in O.OBJECTS}
        for name, (x, y) in O.PROPS:
            self.assertIn(name, sizes)
            w, h = sizes[name]
            self.assertTrue(0 <= x and x + w / 16.0 <= C.WIDTH, name)
            self.assertTrue(0 <= y and y + h / 16.0 <= C.HEIGHT + 2.5, name)  # wall-side props may overhang the north edge

    def test_named_cells_clear_of_blocking_props(self):
        sizes = {o.name: (o.size, o.collider) for o in O.OBJECTS}
        for cell_name in ('Spawn', 'Vet'):
            cx, cy = C.NAMED[cell_name]
            for name, (x, y) in O.PROPS:
                (w, h), collider = sizes[name]
                if collider is None:
                    continue
                inside = x <= cx < x + w / 16.0 and y <= cy < y + h / 16.0
                self.assertFalse(inside, '%s stands inside %s' % (cell_name, name))

    def test_placements_match_room(self):
        room_names = [n for n, _ in C.PLACEABLES_()]
        for name, _ in O.PROPS:
            self.assertIn(name, room_names)


if __name__ == '__main__':
    unittest.main()
