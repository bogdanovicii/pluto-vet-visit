import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import clinic_objects as O  # noqa: E402
import clinic_room as C  # noqa: E402
import vetpixel as V  # noqa: E402

EXPECTED_SIZES = {
    'pluto_floor_strip': (480, 32), 'pluto_floor_strip_1': (480, 16),
    'pluto_exam_table': (48, 32), 'pluto_cabinet': (32, 40), 'pluto_cart': (24, 24), 'pluto_sink': (32, 32),
    'pluto_scale': (16, 16), 'pluto_carrier': (32, 24), 'pluto_poster': (16, 24), 'pluto_cone': (12, 10),
    'pluto_toy_mouse': (10, 6), 'pluto_toy_ball': (6, 6), 'pluto_feather_wand': (14, 10),
    'pluto_scratch_post': (16, 24), 'pluto_syringe_tray': (16, 10),
    # v0.4
    'pluto_reception_desk': (48, 28), 'pluto_chair': (16, 20), 'pluto_plant': (16, 28), 'pluto_window': (32, 24),
    'pluto_xray_box': (24, 20), 'pluto_med_shelf': (32, 36), 'pluto_clock': (10, 10), 'pluto_fish_tank': (32, 24),
    'pluto_sharps_bin': (12, 14), 'pluto_iv_stand': (12, 32), 'pluto_treat_jar': (8, 10), 'pluto_food_bowls': (20, 8),
    'pluto_litter_box': (20, 12), 'pluto_floor_mat': (48, 24), 'pluto_paw_prints': (24, 16), 'pluto_wet_floor_sign': (12, 16),
    # v0.5
    'pluto_clinic_door': (32, 40), 'pluto_kennel': (32, 32), 'pluto_kennel_open': (32, 32), 'pluto_nurse_station': (48, 24),
    # v0.6
    'pluto_prep_sign': (16, 10), 'pluto_surgical_lamp': (32, 32), 'pluto_monitor_cart': (24, 32),
    'pluto_vaccine_fridge': (24, 40), 'pluto_intercom': (10, 12), 'pluto_wall_tv': (32, 20),
    'pluto_side_door': (16, 32), 'pluto_strap_table_pad': (40, 8),
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
        self.assertEqual(blocking, {'pluto_exam_table', 'pluto_cabinet', 'pluto_cart', 'pluto_sink', 'pluto_carrier', 'pluto_scratch_post',
                                    'pluto_reception_desk', 'pluto_chair', 'pluto_plant', 'pluto_med_shelf', 'pluto_fish_tank',
                                    'pluto_sharps_bin', 'pluto_iv_stand', 'pluto_litter_box', 'pluto_wet_floor_sign',
                                    'pluto_clinic_door', 'pluto_kennel', 'pluto_kennel_open', 'pluto_nurse_station',
                                    'pluto_monitor_cart', 'pluto_vaccine_fridge'})

    def test_props_placed_inside_room(self):
        sizes = {o.name: o.size for o in O.OBJECTS}
        for name, (x, y) in O.PROPS:
            self.assertIn(name, sizes)
            w, h = sizes[name]
            self.assertTrue(0 <= x and x + w / 16.0 <= C.WIDTH, name)
            self.assertTrue(0 <= y and y + h / 16.0 <= C.HEIGHT + 2.5, name)  # wall-side props may overhang the north edge

    def test_extra_pngs_are_valid_and_match_their_prop(self):
        door = next(o for o in O.OBJECTS if o.name == 'pluto_clinic_door')
        self.assertEqual(O.Obj('x', 'x', O.EXTRA_PNGS['clinic_door_open']).size, door.size)
        for rows in O.EXTRA_PNGS.values():
            V.R(rows)
            V.image(rows)

    def test_named_cells_clear_of_blocking_props(self):
        sizes = {o.name: (o.size, o.collider) for o in O.OBJECTS}
        checks = [C.NAMED[n] for n in ('Spawn', 'Vet')] + [c for cells in C.SPAWNS.values() for c in cells]
        for cx, cy in checks:
            cell_name = '(%s, %s)' % (cx, cy)
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
