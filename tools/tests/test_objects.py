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
    'pluto_xray_box': (24, 20), 'pluto_clock': (16, 16), 'pluto_fish_tank': (32, 40),
    'pluto_sharps_bin': (12, 14), 'pluto_iv_stand': (12, 32), 'pluto_treat_jar': (8, 10), 'pluto_food_bowls': (20, 8),
    'pluto_litter_box': (20, 12), 'pluto_floor_mat': (48, 24), 'pluto_paw_prints': (24, 16), 'pluto_wet_floor_sign': (12, 16),
    # v0.5
    'pluto_clinic_door': (32, 40), 'pluto_nurse_station': (96, 32),
    # v0.6
    'pluto_prep_sign': (16, 10), 'pluto_monitor_cart': (24, 32),
    'pluto_vaccine_fridge': (24, 40), 'pluto_intercom': (10, 12), 'pluto_wall_tv': (32, 20),
    'pluto_side_door': (16, 32),
    # v0.10
    'pluto_lamp_head': (48, 40), 'pluto_lamp_arm': (48, 40), 'pluto_lamp_pool': (64, 24),
    'pluto_cabinet_wide': (64, 56),
    'pluto_floor_waiting': (480, 208), 'pluto_floor_ward': (480, 272), 'pluto_floor_theatre': (480, 288),
    # v0.10.1
    'pluto_wall_face': (480, 48), 'pluto_wall_face_solid': (480, 48), 'pluto_wall_shelf': (32, 24),
    'pluto_kennel_cat': (40, 48), 'pluto_kennel_dog': (40, 48), 'pluto_kennel_cone': (40, 48),
    'pluto_kennel_open_r': (52, 48), 'pluto_kennel_open_l': (52, 48),
}
WALL_FACES = {'pluto_wall_face', 'pluto_wall_face_solid'}
WALL_DECOR = {'pluto_wall_tv', 'pluto_window', 'pluto_clock', 'pluto_poster', 'pluto_intercom',
              'pluto_xray_box', 'pluto_prep_sign', 'pluto_wall_shelf'}
KENNELS = {'pluto_kennel_cat': 4, 'pluto_kennel_dog': 2, 'pluto_kennel_cone': 2, 'pluto_kennel_open_r': 1, 'pluto_kennel_open_l': 1}


def spec(name):
    return next(o for o in O.OBJECTS if o.name == name)


def collider_box(name, x, y):
    _, ox, oy, w, h = spec(name).collider
    return (x + ox / 16.0, y + oy / 16.0, x + (ox + w) / 16.0, y + (oy + h) / 16.0)


def wall_base(y):
    return max(b for b in O.WALL_BASES if b <= y)


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
                                    'pluto_reception_desk', 'pluto_chair', 'pluto_plant', 'pluto_fish_tank',
                                    'pluto_sharps_bin', 'pluto_iv_stand', 'pluto_litter_box', 'pluto_wet_floor_sign',
                                    'pluto_clinic_door', 'pluto_nurse_station',
                                    'pluto_monitor_cart', 'pluto_vaccine_fridge', 'pluto_cabinet_wide'} | set(KENNELS))

    def test_stand_flag(self):
        """Standing = has a collider, except the wall faces and the wall decor, which stand without one."""
        self.assertTrue(O.Obj('a', 'a', ['o'], ('low', 0, 0, 1, 1)).stand)
        self.assertFalse(O.Obj('a', 'a', ['o']).stand)
        self.assertTrue(O.Obj('a', 'a', ['o'], stand=True).stand)
        self.assertFalse(O.Obj('a', 'a', ['o'], ('low', 0, 0, 1, 1), stand=False).stand)
        for o in O.OBJECTS:
            if o.name in WALL_FACES | WALL_DECOR:
                self.assertTrue(o.stand, o.name)
                self.assertIsNone(o.collider, o.name)
            else:
                self.assertEqual(o.stand, o.collider is not None, o.name)

    def test_v010_depth(self):
        """The lamp head hangs over the actors; the pool, mats and floors go under everything; the wall faces stand at -0.2."""
        hog = {o.name: o.height_off_ground for o in O.OBJECTS}
        self.assertEqual(hog['pluto_lamp_head'], 2.0)
        self.assertEqual(hog['pluto_lamp_arm'], 0.5)
        self.assertEqual(O.WALL_HOG, -0.2)
        for name in WALL_FACES:
            self.assertEqual(hog[name], -0.2, name)
        self.assertLess(hog['pluto_lamp_pool'], hog['pluto_floor_mat'] + 2)
        for name in ('pluto_floor_waiting', 'pluto_floor_ward', 'pluto_floor_theatre'):
            self.assertEqual(hog[name], -4.0, name)
            self.assertFalse(spec(name).stand)
        self.assertLess(hog['pluto_floor_mat'], hog['pluto_lamp_pool'])

    def test_wall_decor_hangs_inside_the_panel_in_front_of_the_face(self):
        placed = [(n, c) for n, c in O.PROPS if n in WALL_DECOR]
        self.assertEqual({n for n, _ in placed}, WALL_DECOR)
        for name, (x, y) in placed:
            o = spec(name)
            base = wall_base(y)
            offset = y - base
            self.assertAlmostEqual(o.height_off_ground, -0.2 + 2 * offset + 0.05, places=6, msg=name)
            self.assertAlmostEqual(o.height_off_ground, O.wall_decor_hog(offset), places=6, msg=name)
            self.assertGreaterEqual(offset, 0.6 - 1e-9, name)
            self.assertLessEqual(offset + o.size[1] / 16.0, 2.35 + 1e-9, name)
            # every sprite pixel is 0.05 in front of the face: decor z - face z at the same screen height
            self.assertAlmostEqual((2 * y - o.height_off_ground) - (2 * base - O.WALL_HOG), -0.05, places=6, msg=name)
        # and that band is the white panel of the face sprite
        top_row, bottom_row = O.WALL_PANEL
        face = spec('pluto_wall_face_solid')
        self.assertLessEqual((O.WALL_FACE_H - 1 - bottom_row) / 16.0, 0.6)
        self.assertGreaterEqual((O.WALL_FACE_H - top_row) / 16.0, 2.35)
        for r in range(top_row + 1, bottom_row + 1):
            self.assertEqual(set(face.rows[r]), {'_', '0'}, r)

    def test_wall_face_door_gap(self):
        face = spec('pluto_wall_face')
        solid = spec('pluto_wall_face_solid')
        for y, row in enumerate(face.rows):
            if y < 16:
                self.assertNotIn('.', row, y)                                # the lintel runs across
            else:
                self.assertEqual(row[224:256], '.' * 32, y)
                self.assertNotIn('.', row[:224] + row[256:], y)
        for y in range(12, 16):
            self.assertIn(face.rows[y][240], 'o&%', y)                       # the frame's top bar across the lintel
        for y in range(16, 48):
            self.assertNotIn(face.rows[y][220], '._$', y)                    # steel frame down both sides of the opening
            self.assertIn(face.rows[y][221], '&o', y)
            self.assertIn(face.rows[y][258], '&o', y)
        for row in solid.rows:
            self.assertNotIn('.', row)
        self.assertEqual(set(solid.rows[0]), {'o'})
        self.assertEqual(set(solid.rows[-1]), {'o'})

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

    def test_floor_variants(self):
        """Plain tiles dominate: per zone at most 3 drains, 2 teal paws, 2 hairline cracks, away from every prop; no brown paw."""
        rects = O.prop_rects()
        for name, variants in O.FLOOR_VARIANTS.items():
            y0, cells_high, _ = O.FLOOR_ZONES[name]
            kinds = list(variants.values())
            for kind, limit in O.FLOOR_LIMITS.items():
                self.assertLessEqual(kinds.count(kind), limit, (name, kind))
                self.assertGreaterEqual(kinds.count(kind), 1, (name, kind))
            self.assertEqual(set(kinds), {'drain', 'paw', 'crack'})
            for (tx, ty), kind in variants.items():
                cx, cy = tx, y0 + ty
                for x0, y0_, x1, y1 in rects:
                    self.assertFalse(cx < x1 and x0 < cx + 1 and cy < y1 and y0_ < cy + 1, (name, kind, tx, ty))
            rows = spec(name).rows
            text = ''.join(rows)
            self.assertNotIn('B', text)
            self.assertTrue(set(text) <= {'_', '0', '$', '%', '#'}, (name, set(text)))
            self.assertLessEqual(text.count('$'), 2 * ''.join(O._TILE_PAW).count('$'), name)   # two paws at most
            tile_cells = (len(rows) // 16) * (len(rows[0]) // 16)
            self.assertLess(len(variants) / float(tile_cells), 0.03, name)
        self.assertEqual(set(''.join(O._TILE_DRAIN)), {'_', '0', '%', '#'})
        self.assertEqual(set(''.join(O._TILE_CRACK)), {'_', '0'})
        self.assertEqual(set(''.join(O._TILE_PAW)), {'_', '0', '$'})

    def test_paw_prints_only_in_the_waiting_room_and_light(self):
        placed = [c for n, c in O.PROPS if n == 'pluto_paw_prints']
        self.assertEqual(len(placed), 1)
        self.assertLess(placed[0][1], 13)
        self.assertTrue(set(''.join(spec('pluto_paw_prints').rows)) <= {'.', '6', '0'})
        mat = set(''.join(spec('pluto_floor_mat').rows))
        self.assertEqual(mat, {'o', '\\', '+'})
        self.assertEqual(spec('pluto_floor_mat').height_off_ground, -2.5)

    def test_clock_is_readable(self):
        text = ''.join(spec('pluto_clock').rows)
        self.assertEqual(text.count('!'), 1)
        self.assertTrue(set(text) <= {'.', 'o', '#', '_', 'K', '!'})

    def test_high_colliders_do_not_overlap(self):
        """Two 'high' props whose colliders overlap in cell space would fuse into one blocker (and one would be sorted away)."""
        boxes = []
        for name, (x, y) in O.PROPS:
            o = spec(name)
            if o.collider is None or o.collider[0] != 'high':
                continue
            boxes.append((name, (x, y)) + collider_box(name, x, y))
        for i, (na, pa, ax0, ay0, ax1, ay1) in enumerate(boxes):
            for nb, pb, bx0, by0, bx1, by1 in boxes[i + 1:]:
                overlap = ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1
                self.assertFalse(overlap, '%s at %s overlaps %s at %s' % (na, pa, nb, pb))

    def test_kennel_bank(self):
        placed = [(n, c) for n, c in O.PROPS if n.startswith('pluto_kennel')]
        self.assertEqual(len(placed), 10)
        self.assertEqual({n: sum(1 for m, _ in placed if m == n) for n in KENNELS}, KENNELS)
        for side, x_box in (('west', 0.5), ('east', 27.0)):
            units = sorted((collider_box(n, x, y), n) for n, (x, y) in placed if (x < 15) == (side == 'west'))
            self.assertEqual(len(units), 5, side)
            for (x0, y0, x1, y1), n in units:
                self.assertEqual((x0, x1 - x0, y1 - y0), (x_box, 2.5, 3.0), (side, n))
            for (a, _), (b, _) in zip(units, units[1:]):
                self.assertEqual(b[1], a[3], side)                          # stacked touching, no gaps
            self.assertGreaterEqual(units[0][0][1], 16.0, side)             # clear of the waiting room's standing face
            self.assertLessEqual(units[-1][0][3], 32.0, side)               # under the north wall
        self.assertIn(('pluto_kennel_open_r', (0.5, 19.0)), placed)
        self.assertIn(('pluto_kennel_open_l', (26.25, 22.0)), placed)
        for name in ('pluto_kennel_open_r', 'pluto_kennel_open_l'):
            rows = spec(name).rows
            door = [r[40:] for r in rows] if name.endswith('_r') else [r[:12] for r in rows]
            self.assertIn('$', ''.join(door), name)                         # the teal barred door sticks out
        self.assertEqual(O.KENNEL_OPEN_L, [r[::-1] for r in O._kennel_open_r(upper=(O.TABBY_CURLED, 6))])
        self.assertIn('?', ''.join(O.KENNEL_CAT))
        self.assertIn('7', ''.join(O.KENNEL_CAT))
        self.assertIn('\\', ''.join(O.KENNEL_DOG))

    def test_no_ward_side_doors(self):
        doors = [c for n, c in O.PROPS if n == 'pluto_side_door']
        self.assertEqual(doors, [(29.0, 39.5)])

    def test_removed_props_are_gone(self):
        names = {o.name for o in O.OBJECTS}
        placed = {n for n, _ in O.PROPS}
        for gone in ('pluto_surgical_lamp', 'pluto_strap_table_pad', 'pluto_floor_strip', 'pluto_floor_strip_1',
                     'pluto_kennel', 'pluto_kennel_open', 'pluto_med_shelf'):
            self.assertNotIn(gone, names)
        self.assertFalse(hasattr(O, 'FLOOR'))
        for kept_but_unplaced in ('pluto_treat_jar', 'pluto_food_bowls', 'pluto_syringe_tray', 'pluto_cabinet'):
            self.assertIn(kept_but_unplaced, names)
            self.assertNotIn(kept_but_unplaced, placed)
        self.assertEqual(sum(1 for n, _ in O.PROPS if n == 'pluto_chair'), 9)
        litter = [c for n, c in O.PROPS if n == 'pluto_litter_box']
        self.assertEqual(litter, [(19.5, 30.0)])                            # under the north wall, not mid-floor

    def test_theatre_toys_in_the_south_west_corner(self):
        for name in ('pluto_toy_mouse', 'pluto_toy_ball', 'pluto_feather_wand', 'pluto_cone', 'pluto_scratch_post'):
            cells = [c for n, c in O.PROPS if n == name and c[1] >= 34]
            self.assertEqual(len(cells), 1, name)
            x, y = cells[0]
            self.assertTrue(x <= 6.0 and y <= 42.0, name)

    def test_props_placed_inside_room(self):
        sizes = {o.name: o.size for o in O.OBJECTS}
        for name, (x, y) in O.PROPS:
            self.assertIn(name, sizes)
            w, h = sizes[name]
            self.assertTrue(0 <= x and x + w / 16.0 <= C.WIDTH, name)
            self.assertTrue(0 <= y and y + h / 16.0 <= C.HEIGHT + 2.5, name)  # wall-side props may overhang the north edge

    def test_extra_pngs_are_valid_and_match_their_prop(self):
        door = spec('pluto_clinic_door')
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

    def test_spawns_clear_of_colliders(self):
        """No wave spawn inside a collider footprint or within half a cell of one."""
        for group, cells in C.SPAWNS.items():
            for cx, cy in cells:
                for name, (x, y) in O.PROPS:
                    if spec(name).collider is None:
                        continue
                    x0, y0, x1, y1 = collider_box(name, x, y)
                    near = x0 - 0.5 <= cx <= x1 + 0.5 and y0 - 0.5 <= cy <= y1 + 0.5
                    self.assertFalse(near, '%s spawn (%s, %s) is within 0.5 of %s at %s' % (group, cx, cy, name, (x, y)))

    def test_placements_match_room(self):
        room_names = [n for n, _ in C.PLACEABLES_()]
        for name, _ in O.PROPS:
            self.assertIn(name, room_names)


if __name__ == '__main__':
    unittest.main()
