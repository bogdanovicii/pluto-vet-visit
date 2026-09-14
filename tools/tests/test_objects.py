import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import clinic_objects as O  # noqa: E402
import clinic_room as C  # noqa: E402
import vetpixel as V  # noqa: E402

EXPECTED_SIZES = {
    'pluto_exam_table': (80, 40), 'pluto_cabinet': (32, 40), 'pluto_cart': (24, 24), 'pluto_sink': (32, 32),
    'pluto_scale': (16, 16), 'pluto_carrier': (32, 24), 'pluto_poster': (16, 24), 'pluto_cone': (12, 10),
    'pluto_toy_mouse': (10, 6), 'pluto_toy_ball': (6, 6), 'pluto_feather_wand': (14, 10),
    'pluto_scratch_post': (16, 24), 'pluto_syringe_tray': (16, 10),
    # v0.4
    'pluto_reception_desk': (112, 40), 'pluto_chair': (24, 24), 'pluto_plant': (16, 28), 'pluto_window': (32, 24),
    'pluto_xray_box': (24, 20), 'pluto_med_shelf': (32, 36), 'pluto_clock': (10, 10), 'pluto_fish_tank': (32, 40),
    'pluto_sharps_bin': (12, 14), 'pluto_iv_stand': (12, 32), 'pluto_treat_jar': (8, 10), 'pluto_food_bowls': (20, 8),
    'pluto_litter_box': (20, 12), 'pluto_floor_mat': (48, 24), 'pluto_paw_prints': (24, 16), 'pluto_wet_floor_sign': (12, 16),
    # v0.5
    'pluto_clinic_door': (32, 40), 'pluto_kennel': (32, 40), 'pluto_kennel_open': (32, 40), 'pluto_kennel_cone': (32, 40),
    'pluto_nurse_station': (96, 32),
    # v0.6
    'pluto_prep_sign': (16, 10), 'pluto_monitor_cart': (24, 32),
    'pluto_vaccine_fridge': (24, 40), 'pluto_intercom': (10, 12), 'pluto_wall_tv': (32, 20),
    'pluto_side_door': (16, 32),
    # v0.10
    'pluto_lamp_head': (48, 40), 'pluto_lamp_arm': (48, 40), 'pluto_lamp_pool': (64, 24),
    'pluto_cabinet_wide': (64, 56), 'pluto_wall_face': (480, 32), 'pluto_wall_face_solid': (480, 32),
    'pluto_floor_waiting': (480, 208), 'pluto_floor_ward': (480, 272), 'pluto_floor_theatre': (480, 288),
}
FLAT_ON_WALLS = {'pluto_wall_face', 'pluto_wall_face_solid'}


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
                                    'pluto_clinic_door', 'pluto_kennel', 'pluto_kennel_open', 'pluto_kennel_cone', 'pluto_nurse_station',
                                    'pluto_monitor_cart', 'pluto_vaccine_fridge', 'pluto_cabinet_wide'})

    def test_v010_depth(self):
        """The lamp head hangs over the actors; the arm sits on the wall face; the pool, mats and floors go under everything."""
        hog = {o.name: o.height_off_ground for o in O.OBJECTS}
        self.assertEqual(hog['pluto_lamp_head'], 2.0)
        self.assertEqual(hog['pluto_lamp_arm'], 0.5)
        self.assertEqual(hog['pluto_wall_face'], 0.5)
        self.assertLess(hog['pluto_lamp_pool'], hog['pluto_floor_mat'] + 2)
        for name in ('pluto_floor_waiting', 'pluto_floor_ward', 'pluto_floor_theatre'):
            self.assertEqual(hog[name], -4.0, name)
        self.assertLess(hog['pluto_floor_mat'], hog['pluto_lamp_pool'])

    def test_wall_face_door_gap(self):
        face = next(o for o in O.OBJECTS if o.name == 'pluto_wall_face')
        solid = next(o for o in O.OBJECTS if o.name == 'pluto_wall_face_solid')
        for row in face.rows:
            self.assertEqual(row[224:256], '.' * 32)
            self.assertNotIn('.', row[:224] + row[256:])
        for row in solid.rows:
            self.assertNotIn('.', row)

    def test_floors_cover_their_zones_edge_to_edge(self):
        floors = {name: (x, y) for name, (x, y) in O.PROPS if name.startswith('pluto_floor_') and name != 'pluto_floor_mat'}
        self.assertEqual(floors, {'pluto_floor_waiting': (0.0, 0.0), 'pluto_floor_ward': (0.0, 15.0), 'pluto_floor_theatre': (0.0, 34.0)})
        sizes = {o.name: o.size for o in O.OBJECTS}
        for name, (x, y) in floors.items():
            w, h = sizes[name]
            self.assertEqual(w, C.WIDTH * 16)
            for cy in range(int(y), int(y) + h // 16):
                self.assertTrue(C.is_floor(0, cy), (name, cy))         # never paints over a wall row
            self.assertFalse(C.is_floor(0, int(y) + h // 16) if int(y) + h // 16 < C.HEIGHT else False, name)  # ends at the wall
        for o in O.OBJECTS:
            if o.name in floors:
                self.assertNotIn('.', ''.join(o.rows), o.name)

    def test_high_colliders_do_not_overlap(self):
        """Two 'high' props whose colliders overlap in cell space would fuse into one blocker (and one would be sorted away)."""
        spec = {o.name: o for o in O.OBJECTS}
        boxes = []
        for name, (x, y) in O.PROPS:
            o = spec[name]
            if o.collider is None or o.collider[0] != 'high':
                continue
            _, ox, oy, w, h = o.collider
            boxes.append((name, (x, y), x + ox / 16.0, y + oy / 16.0, x + (ox + w) / 16.0, y + (oy + h) / 16.0))
        for i, (na, pa, ax0, ay0, ax1, ay1) in enumerate(boxes):
            for nb, pb, bx0, by0, bx1, by1 in boxes[i + 1:]:
                overlap = ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1
                self.assertFalse(overlap, '%s at %s overlaps %s at %s' % (na, pa, nb, pb))

    def test_removed_props_are_gone(self):
        names = {o.name for o in O.OBJECTS}
        placed = {n for n, _ in O.PROPS}
        for gone in ('pluto_surgical_lamp', 'pluto_strap_table_pad', 'pluto_floor_strip', 'pluto_floor_strip_1'):
            self.assertNotIn(gone, names)
        self.assertFalse(hasattr(O, 'FLOOR'))
        for kept_but_unplaced in ('pluto_treat_jar', 'pluto_food_bowls', 'pluto_syringe_tray', 'pluto_cabinet'):
            self.assertIn(kept_but_unplaced, names)
            self.assertNotIn(kept_but_unplaced, placed)
        self.assertEqual(sum(1 for n, _ in O.PROPS if n == 'pluto_chair'), 9)
        self.assertEqual(sum(1 for n, _ in O.PROPS if n == 'pluto_kennel_cone'), 2)
        self.assertEqual(sum(1 for n, _ in O.PROPS if n.startswith('pluto_kennel')), 8)

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
