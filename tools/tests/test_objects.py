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
    'pluto_sharps_bin': (12, 14), 'pluto_iv_stand': (16, 40), 'pluto_treat_jar': (8, 10), 'pluto_food_bowls': (20, 8),
    'pluto_litter_box': (20, 12), 'pluto_floor_mat': (48, 24), 'pluto_paw_prints': (24, 16), 'pluto_wet_floor_sign': (12, 16),
    # v0.5
    'pluto_clinic_door': (32, 40), 'pluto_nurse_station': (96, 32),
    # v0.6
    'pluto_prep_sign': (16, 10), 'pluto_monitor_cart': (24, 40),
    'pluto_vaccine_fridge': (24, 40), 'pluto_intercom': (10, 12), 'pluto_wall_tv': (32, 20),
    'pluto_side_door': (16, 32),
    # v0.10
    'pluto_lamp_pool': (64, 24),
    'pluto_cabinet_wide': (64, 56),
    'pluto_floor_waiting': (576, 256), 'pluto_floor_ward': (576, 320), 'pluto_floor_theatre': (576, 336),
    # v0.10.1
    'pluto_wall_face': (576, 48), 'pluto_wall_face_solid': (576, 48), 'pluto_wall_shelf': (32, 24),
    'pluto_kennel_cat': (40, 48), 'pluto_kennel_dog': (40, 48), 'pluto_kennel_cone': (40, 48),
    'pluto_kennel_open_r': (52, 48), 'pluto_kennel_open_l': (52, 48),
    # v0.11
    'pluto_rug': (136, 104), 'pluto_coffee_table': (48, 24), 'pluto_carrier_open': (32, 24), 'pluto_back_cabinet': (64, 32),
    'pluto_water_cooler': (16, 32), 'pluto_notice_board': (32, 24), 'pluto_sign_waiting': (56, 12), 'pluto_sign_ward': (24, 12),
    'pluto_sign_surgery': (36, 12), 'pluto_supply_shelf': (48, 40), 'pluto_scrubs_rack': (48, 40), 'pluto_med_trolley': (24, 32),
    'pluto_stool': (12, 14), 'pluto_anaesthesia_machine': (32, 48), 'pluto_instrument_trolley': (24, 24),
    'pluto_counter_towels': (48, 32), 'pluto_counter_printer': (48, 32), 'pluto_biohazard_bin': (14, 18), 'pluto_table_mat': (144, 96),
    # v0.12.0
    'pluto_op_lamp': (80, 56), 'pluto_xray_cat': (32, 24), 'pluto_anatomy_poster': (24, 24), 'pluto_vaccine_chart': (32, 24),
    'pluto_healthy_pets': (16, 24), 'pluto_diploma': (16, 20), 'pluto_weight_chart': (16, 24), 'pluto_flea_poster': (24, 24),
    'pluto_whiteboard': (32, 24), 'pluto_pet_photos': (32, 24),
}
WALL_FACES = {'pluto_wall_face', 'pluto_wall_face_solid'}
WALL_DECOR = {'pluto_wall_tv', 'pluto_window', 'pluto_clock', 'pluto_poster', 'pluto_intercom',
              'pluto_xray_box', 'pluto_prep_sign', 'pluto_wall_shelf',
              'pluto_notice_board', 'pluto_sign_waiting', 'pluto_sign_ward', 'pluto_sign_surgery'}
WALL_ART = {'pluto_xray_cat', 'pluto_anatomy_poster', 'pluto_vaccine_chart', 'pluto_healthy_pets', 'pluto_diploma',
            'pluto_weight_chart', 'pluto_flea_poster', 'pluto_whiteboard', 'pluto_pet_photos'}
WALL_DECOR |= WALL_ART
V011_NEW = {n for n in EXPECTED_SIZES if n in (
    'pluto_rug', 'pluto_coffee_table', 'pluto_carrier_open', 'pluto_back_cabinet', 'pluto_water_cooler', 'pluto_notice_board',
    'pluto_sign_waiting', 'pluto_sign_ward', 'pluto_sign_surgery', 'pluto_supply_shelf', 'pluto_scrubs_rack', 'pluto_med_trolley',
    'pluto_stool', 'pluto_anaesthesia_machine', 'pluto_instrument_trolley', 'pluto_counter_towels', 'pluto_counter_printer',
    'pluto_biohazard_bin', 'pluto_table_mat')}
ANIMATED = {'pluto_fish_tank': 4, 'pluto_monitor_cart': 6, 'pluto_clock': 2, 'pluto_reception_desk': 2, 'pluto_iv_stand': 3,
            'pluto_anaesthesia_machine': 3}
VET = C.NAMED['Vet']
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
                                    'pluto_monitor_cart', 'pluto_vaccine_fridge', 'pluto_cabinet_wide',
                                    'pluto_coffee_table', 'pluto_carrier_open', 'pluto_back_cabinet', 'pluto_water_cooler',
                                    'pluto_supply_shelf', 'pluto_scrubs_rack', 'pluto_med_trolley', 'pluto_stool',
                                    'pluto_anaesthesia_machine', 'pluto_instrument_trolley', 'pluto_counter_towels',
                                    'pluto_counter_printer', 'pluto_biohazard_bin', 'pluto_op_lamp'} | set(KENNELS))

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
        """0.12.0: the op lamp STANDS on the exam table's base row just in front of it (the flat head at +2 drew over the Vet);
        the pool, mats and floors go under everything; the wall faces stand at -0.2."""
        hog = {o.name: o.height_off_ground for o in O.OBJECTS}
        self.assertTrue(spec('pluto_op_lamp').stand)
        self.assertTrue(0.0 < hog['pluto_op_lamp'] - hog['pluto_exam_table'] < 0.2)
        (lx, ly), = [c for n, c in O.PROPS if n == 'pluto_op_lamp']
        (tx, ty), = [c for n, c in O.PROPS if n == 'pluto_exam_table']
        self.assertEqual(ly, ty)
        self.assertLess(2 * ly - hog['pluto_op_lamp'], 2 * ty - hog['pluto_exam_table'])        # in front of the table
        for o in O.OBJECTS:
            self.assertFalse(not o.stand and o.height_off_ground > 0.5, o.name)           # nothing flat hangs over the actors
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
        g = O.DOOR_GAP_PX
        self.assertEqual(g, 17 * 16)
        for y, row in enumerate(face.rows):
            if y < 16:
                self.assertNotIn('.', row, y)                                # the lintel runs across
            else:
                self.assertEqual(row[g:g + 32], '.' * 32, y)
                self.assertNotIn('.', row[:g] + row[g + 32:], y)
        for y in range(12, 16):
            self.assertIn(face.rows[y][g + 16], 'o&%', y)                    # the frame's top bar across the lintel
        for y in range(16, 48):
            self.assertNotIn(face.rows[y][g - 4], '._$', y)                  # steel frame down both sides of the opening
            self.assertIn(face.rows[y][g - 3], '&o', y)
            self.assertIn(face.rows[y][g + 34], '&o', y)
        for row in solid.rows:
            self.assertNotIn('.', row)
        self.assertEqual(set(solid.rows[0]), {'o'})
        self.assertEqual(set(solid.rows[-1]), {'o'})

    def test_floors_cover_their_zones_edge_to_edge(self):
        floors = {name: (x, y) for name, (x, y) in O.PROPS if name.startswith('pluto_floor_') and name != 'pluto_floor_mat'}
        self.assertEqual(floors, {'pluto_floor_waiting': (0.0, 0.0), 'pluto_floor_ward': (0.0, 18.0), 'pluto_floor_theatre': (0.0, 40.0)})
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
            tile, grout = O.FLOOR_TONES[name]
            if name == 'pluto_floor_ward':                                  # the guide stripe is not a variant
                rows = [r[:O.WARD_STRIPE_PX - 4] + r[O.WARD_STRIPE_PX + 4:] for r in rows]
            text = ''.join(rows)
            self.assertNotIn('B', text)
            self.assertTrue(set(text) <= {tile, grout, '$', '%', '#'}, (name, set(text)))
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
        for frame in spec('pluto_clock').frames:
            text = ''.join(frame)
            self.assertEqual(text.count('!'), 1)
            self.assertTrue(set(text) <= {'.', 'o', '#', '_', 'K', '!', '%'})
            self.assertGreaterEqual(text.count('%'), 3)                    # the second hand

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
        for side, x_box in (('west', 0.5), ('east', 33.0)):
            units = sorted((collider_box(n, x, y), n) for n, (x, y) in placed if (x < 18) == (side == 'west'))
            self.assertEqual(len(units), 5, side)
            for (x0, y0, x1, y1), n in units:
                self.assertEqual((x0, x1 - x0, y1 - y0), (x_box, 2.5, 3.0), (side, n))
            for (a, _), (b, _) in zip(units, units[1:]):
                self.assertEqual(b[1], a[3], side)                          # stacked touching, no gaps
            self.assertGreaterEqual(units[0][0][1], 19.0, side)             # clear of the waiting room's standing face
            self.assertLessEqual(units[-1][0][3], 38.0, side)               # under the north wall
        self.assertIn(('pluto_kennel_open_r', (0.5, 22.0)), placed)
        self.assertIn(('pluto_kennel_open_l', (32.25, 25.0)), placed)
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
        self.assertEqual(doors, [(35.0, 45.5)])

    def test_removed_props_are_gone(self):
        names = {o.name for o in O.OBJECTS}
        placed = {n for n, _ in O.PROPS}
        for gone in ('pluto_surgical_lamp', 'pluto_strap_table_pad', 'pluto_floor_strip', 'pluto_floor_strip_1',
                     'pluto_kennel', 'pluto_kennel_open', 'pluto_med_shelf', 'pluto_lamp_head', 'pluto_lamp_arm'):
            self.assertNotIn(gone, names)
        self.assertFalse(hasattr(O, 'FLOOR'))
        for kept_but_unplaced in ('pluto_treat_jar', 'pluto_syringe_tray', 'pluto_cabinet', 'pluto_cone'):
            self.assertIn(kept_but_unplaced, names)
            self.assertNotIn(kept_but_unplaced, placed)
        self.assertEqual(sum(1 for n, _ in O.PROPS if n == 'pluto_chair'), 10)
        litter = [c for n, c in O.PROPS if n == 'pluto_litter_box']
        self.assertEqual(litter, [(23.5, 36.0)])                            # under the north wall, not mid-floor

    def test_theatre_toys_in_the_south_corners(self):
        for name in ('pluto_toy_mouse', 'pluto_toy_ball', 'pluto_feather_wand'):
            cells = [c for n, c in O.PROPS if n == name and c[1] >= 40]
            self.assertEqual(len(cells), 1, name)
            x, y = cells[0]
            self.assertTrue(x <= 6.0 and y <= 48.0, name)
        posts = [c for n, c in O.PROPS if n == 'pluto_scratch_post']
        self.assertEqual(len(posts), 1)
        self.assertTrue(posts[0][0] >= 26.0 and 40 <= posts[0][1] <= 48.0)     # south-east corner
        for y, row in enumerate(O.CONE):                                        # the cone now sits on the west counter
            for x, ch in enumerate(row):
                if ch != '.':
                    self.assertEqual(O.COUNTER_TOWELS[3 + y][30 + x], ch, (x, y))

    # ------------------------------------------------------------------ v0.11
    def test_v011_props_are_placed_and_outlined(self):
        self.assertGreaterEqual(len(V011_NEW), 10)
        placed = {n for n, _ in O.PROPS}
        for name in V011_NEW:
            self.assertIn(name, placed, name)
            rows = spec(name).rows
            self.assertIn('o', rows[0] + rows[-1] + ''.join(r[0] + r[-1] for r in rows), name)   # a drawn 'o' outline
        for name in ('pluto_coffee_table', 'pluto_supply_shelf', 'pluto_back_cabinet'):
            self.assertIn('\\', ''.join(spec(name).rows), name)                  # wood / cardboard ramp
        for name in ('pluto_instrument_trolley', 'pluto_anaesthesia_machine', 'pluto_med_trolley'):
            text = ''.join(spec(name).rows)
            self.assertTrue({'&', '%', '#'} <= set(text) or {'&', '%', 'K'} <= set(text), name)   # steel ramp
        self.assertIn('$', ''.join(O.SCRUBS_RACK))
        self.assertIn('~', ''.join(O.SCRUBS_RACK))

    def test_signs_spell_their_zone(self):
        for rows, text in ((O.SIGN_WAITING, 'WAITING ROOM'), (O.SIGN_WARD, 'WARD'), (O.SIGN_SURGERY, 'SURGERY')):
            ink = [''.join('#' if ch == 'W' else '.' for ch in r) for r in rows[3:8]]
            x0 = (len(rows[0]) - (4 * len(text) - 1)) // 2
            for i, c in enumerate(text):
                glyph = [r[x0 + 4 * i:x0 + 4 * i + 3] for r in ink]
                self.assertEqual(glyph, O.FONT[c], (text, c))

    def test_animated_props(self):
        animated = {o.name: o for o in O.OBJECTS if o.frames}
        self.assertEqual({n: o.frame_count for n, o in animated.items()}, ANIMATED)
        for name, o in animated.items():
            self.assertTrue(2 <= len(o.frames) <= 8, name)
            self.assertEqual(o.rows, o.frames[0], name)                          # the placed sprite is frame 1
            for frame in o.frames:
                V.R(frame)
                V.image(frame)
                self.assertEqual((len(frame[0]), len(frame)), o.size, name)
            for a, b in zip(o.frames, o.frames[1:] + o.frames[:1]):
                self.assertNotEqual(a, b, name)                                  # every frame changes something
            self.assertGreater(o.fps, 0, name)
        for o in O.OBJECTS:
            if not o.frames:
                self.assertEqual(o.frame_count, 1, o.name)

    def test_write_saves_frame_pngs(self):
        import tempfile
        from PIL import Image
        with tempfile.TemporaryDirectory() as d:
            paths = O.write(d)
            out = os.path.join(d, 'Resources', 'Objects')
            def size(path):
                with Image.open(path) as im:
                    return im.size

            for o in O.OBJECTS:
                self.assertEqual(size(os.path.join(out, o.png + '.png')), o.size, o.name)
                self.assertFalse(os.path.exists(os.path.join(out, o.png + '_f1.png')), o.name)
                for k in range(2, o.frame_count + 1):
                    p = os.path.join(out, '%s_f%d.png' % (o.png, k))
                    self.assertIn(p, paths)
                    self.assertEqual(size(p), o.size, p)
                self.assertFalse(os.path.exists(os.path.join(out, '%s_f%d.png' % (o.png, o.frame_count + 1))), o.name)

    def test_comments(self):
        commented = [o for o in O.OBJECTS if o.comment]
        self.assertTrue(12 <= len(commented) <= 30, len(commented))
        placed = {n for n, _ in O.PROPS}
        for o in commented:
            self.assertLess(len(o.comment), 60, o.name)
            self.assertTrue(all(32 <= ord(ch) < 127 for ch in o.comment), o.name)
            self.assertFalse(set(o.comment) & {'"', "'", '\\'}, o.name)
            self.assertIn(o.name, placed, o.name)
        for name in ('pluto_fish_tank', 'pluto_litter_box'):
            self.assertTrue(spec(name).comment, name)

    def test_depth_of_the_new_flat_decor(self):
        hog = {o.name: o.height_off_ground for o in O.OBJECTS}
        for name in ('pluto_rug', 'pluto_table_mat'):
            self.assertFalse(spec(name).stand, name)
            self.assertLess(-4.0, hog[name])
            self.assertLess(hog[name], hog['pluto_lamp_pool'])
            self.assertLess(hog[name], hog['pluto_floor_mat'])

    def test_zone_floor_tones_and_the_ward_stripe(self):
        self.assertEqual(set(''.join(O.FLOOR_WAITING)) & {'_', '0'}, set())
        self.assertEqual(set(''.join(O.FLOOR_THEATRE)) & {'_', '0'}, set())
        self.assertEqual(O.FLOOR_TONES['pluto_floor_ward'], ('_', '0'))
        px = O.WARD_STRIPE_PX
        self.assertEqual(px, 18 * 16)                                           # the door centre line
        for y, row in enumerate(O.FLOOR_WARD[2:], start=2):
            self.assertEqual(row[px - 4:px + 4], '~$$$$$$~', y)
        for name, variants in O.FLOOR_VARIANTS.items():
            if name == 'pluto_floor_ward':
                self.assertFalse({tx for tx, _ in variants} & {17, 18})

    def high_boxes(self):
        for name, (x, y) in O.PROPS:
            o = spec(name)
            if o.collider is not None and o.collider[0] == 'high':
                yield name, (x, y), collider_box(name, x, y)

    def collider_boxes(self):
        for name, (x, y) in O.PROPS:
            if spec(name).collider is not None:
                yield name, (x, y), collider_box(name, x, y)

    def test_open_fight_areas(self):
        """The 10 x 8 cells around the Vet and the ward's middle hold no high blocker (the table and the station excepted)."""
        areas = [((VET[0] - 5, VET[1] - 4, VET[0] + 5, VET[1] + 4), {'pluto_exam_table'}),
                 ((4.0, 20.0, 32.0, 34.0), {'pluto_nurse_station'})]
        for (ax0, ay0, ax1, ay1), allowed in areas:
            for name, cell, (x0, y0, x1, y1) in self.high_boxes():
                if name in allowed:
                    continue
                self.assertFalse(x0 < ax1 and ax0 < x1 and y0 < ay1 and ay0 < y1, '%s at %s blocks a fight area' % (name, cell))
        tx, ty = C.NAMED['Table']
        for name, cell, (x0, y0, x1, y1) in self.collider_boxes():
            if name != 'pluto_exam_table':
                self.assertFalse(x0 < tx + 2.5 and tx - 2.5 < x1 and y0 < ty + 0.5 and ty - 1.0 < y1, (name, cell))

    def test_door_gaps_clear(self):
        """Nothing with a collider within half a cell of either door gap (x 14..16), on either side of the wall."""
        gx = O.DOOR_GAP_X
        for wall in (16.0, 38.0):
            for name, cell, (x0, y0, x1, y1) in self.collider_boxes():
                if name == 'pluto_clinic_door':
                    continue
                self.assertFalse(x0 < gx + 2.5 and gx - 0.5 < x1 and y0 < wall + 3.0 and wall - 1.5 < y1,
                                 '%s at %s crowds the door at y %s' % (name, cell, wall))

    def test_waiting_room_chair_rows_are_aligned(self):
        chairs = sorted(c for n, c in O.PROPS if n == 'pluto_chair')
        rows = sorted({y for _, y in chairs})
        self.assertEqual(rows, sorted(O.CHAIR_ROWS))
        xs = [sorted(x for x, y in chairs if y == row) for row in rows]
        self.assertEqual(xs[0], xs[1])                                          # the two rows line up column for column
        self.assertEqual(len(xs[0]), 5)
        self.assertEqual({round(b - a, 6) for a, b in zip(xs[0], xs[0][1:])}, {O.CHAIR_PITCH})
        centre = (xs[0][0] + xs[0][-1] + 1.5) / 2
        (tx, ty), = [c for n, c in O.PROPS if n == 'pluto_coffee_table']
        self.assertAlmostEqual(tx + 1.5, centre)                               # the table sits centred between the rows
        self.assertTrue(rows[0] < ty < rows[1])
        (rx, ry), = [c for n, c in O.PROPS if n == 'pluto_rug']
        self.assertTrue(rx <= xs[0][0] and rx + 136 / 16.0 >= xs[0][-1] + 1.5 and ry <= rows[0] and ry + 104 / 16.0 >= rows[1] + 1.5)
        plants = sorted(x + 0.5 for n, (x, y) in O.PROPS if n == 'pluto_plant' and y < 16)
        self.assertEqual(len(plants), 2)
        self.assertAlmostEqual(plants[0] + plants[1], 36.0)                   # framing the exit, mirrored about x 18

    def assert_mirrored(self, a, b, axis, zone):
        def centre(name):
            (x, y), = [c for n, c in O.PROPS if n == name and zone[0] <= c[1] < zone[1] and (c[0] < axis) == (name == a)] or [(None, None)]
            return x + EXPECTED_SIZES[name][0] / 32.0, y
        (ax, ay), (bx, by) = centre(a), centre(b)
        self.assertAlmostEqual(ax + bx, 2 * axis, msg=(a, b))
        self.assertEqual(ay, by, (a, b))

    def test_ward_north_wall_is_mirrored(self):
        for a, b in (('pluto_supply_shelf', 'pluto_scrubs_rack'), ('pluto_sharps_bin', 'pluto_litter_box')):
            self.assert_mirrored(a, b, 18.0, (18, 38))
        ivs = sorted(x + 0.5 for n, (x, y) in O.PROPS if n == 'pluto_iv_stand' and 18 <= y < 38)
        self.assertEqual(len(ivs), 2)
        self.assertAlmostEqual(ivs[0] + ivs[1], 36.0)
        (sx, sy), = [c for n, c in O.PROPS if n == 'pluto_nurse_station']
        self.assertEqual(sx + 3.0, 18.0)                                        # the island on the centre line

    def test_theatre_table_group_is_symmetric(self):
        axis = 18.0
        (tx, ty), = [c for n, c in O.PROPS if n == 'pluto_exam_table']
        self.assertEqual(tx + 2.5, axis)
        for name in ('pluto_lamp_pool', 'pluto_table_mat'):
            (x, y), = [c for n, c in O.PROPS if n == name]
            self.assertEqual(x + EXPECTED_SIZES[name][0] / 32.0, axis, name)
        (lx, ly), = [c for n, c in O.PROPS if n == 'pluto_op_lamp']
        dish = [i for i, ch in enumerate(O.OP_LAMP[12]) if ch != '.' and i >= 40]         # the dish's widest row
        self.assertAlmostEqual(lx + (dish[0] + dish[-1] + 1) / 32.0, axis)           # the lamp dish hangs over the table centre
        trolleys = sorted(x + 0.75 for n, (x, y) in O.PROPS if n == 'pluto_instrument_trolley')
        self.assertAlmostEqual(trolleys[0] + trolleys[1], 2 * axis)
        self.assert_mirrored('pluto_anaesthesia_machine', 'pluto_monitor_cart', axis, (40, 61))
        self.assert_mirrored('pluto_iv_stand', 'pluto_cart', axis, (40, 61))
        self.assert_mirrored('pluto_counter_towels', 'pluto_counter_printer', axis, (40, 61))
        north = sorted((x, x + EXPECTED_SIZES[n][0] / 16.0) for n, (x, y) in O.PROPS if y == 58.0)
        self.assertAlmostEqual(north[0][0] + north[-1][1], 36.0)               # the north wall row spans symmetric ends
        diplomas = sorted(x + 0.5 for n, (x, y) in O.PROPS if n == 'pluto_diploma')
        self.assertEqual(len(diplomas), 3)
        self.assertAlmostEqual(diplomas[1], axis)                               # the diplomas hang centred behind the Vet

    def test_vet_stage_is_clear(self):
        """0.12.0, the clipping bug: nothing may draw over the Vet's 48x40 sprite at his spawn. Every prop sprite within a quarter cell
        of it must sort BEHIND him: a standing prop further north (base depth 2y - hog above his feet' 2*y0), a flat one under the
        actors (negative height off ground)."""
        vx0, vy0, vx1, vy1 = C.vet_sprite_rect()
        m = 0.25
        feet_z = 2 * vy0
        for name, (x, y) in O.PROPS:
            o = spec(name)
            w, h = o.size
            if not (x < vx1 + m and vx0 - m < x + w / 16.0 and y < vy1 + m and vy0 - m < y + h / 16.0):
                continue
            if o.stand:
                self.assertGreater(2 * y - o.height_off_ground, feet_z, '%s at %s draws over the Vet' % (name, (x, y)))
            else:
                self.assertLess(o.height_off_ground, 0.0, '%s at %s lies over the Vet' % (name, (x, y)))
        # and open floor around his feet: no collider within a cell of his body
        hx, hy, hw, hh = __import__('vet_poses').HITBOX
        bx0, bx1 = vx0 + hx / 16.0, vx0 + (hx + hw) / 16.0
        for name, cell, (x0, y0, x1, y1) in self.collider_boxes():
            self.assertFalse(x0 < bx1 + 1 and bx0 - 1 < x1 and y0 < vy0 + 1.5 and vy0 - 1 < y1, (name, cell))

    def test_wall_art(self):
        """0.12.0: nine hand-drawn clinic pieces, outlined, hung on the three north walls, most of them examinable."""
        placed = [(n, c) for n, c in O.PROPS if n in WALL_ART]
        self.assertEqual({n for n, _ in placed}, WALL_ART)
        zones = {wall_base(y) for n, (x, y) in placed}
        self.assertEqual(zones, set(O.WALL_BASES))                              # art on every zone's north wall
        for name in WALL_ART:
            rows = spec(name).rows
            self.assertEqual(set(rows[0]) | set(rows[-1]) - {'.'}, set(rows[0]) | set(rows[-1]) - {'.'})
            self.assertIn('o', rows[0], name)
            self.assertGreaterEqual(len(set(''.join(rows)) - {'.'}), 5, name)  # outline plus a real ramp of colours
        self.assertGreaterEqual(sum(1 for n in WALL_ART if spec(n).comment), 7)
        for name, (x, y) in placed:
            base = wall_base(y)
            if base < 61.0:
                gx = O.DOOR_GAP_X
                self.assertFalse(x < gx + 2.25 and gx - 0.25 < x + spec(name).size[0] / 16.0, (name, x))   # not over a door
        text = ''.join(O.WHITEBOARD)
        self.assertIn('!', text)
        self.assertIn('*', text)

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



class ColliderTests(unittest.TestCase):
    """0.12.1: Pluto walked into the reception counter from the south (in-game screenshot 19.44.02)."""

    @classmethod
    def setUpClass(cls):
        import clinic_colliders as K
        cls.K = K
        cls.seen = K.reachable()

    def feet_reachable(self, x, y):
        W = C.WIDTH * 16
        return bool(self.seen[int(round(y * 16)) * W + int(round(x * 16))])

    def test_standing_props_sort_like_the_player(self):
        """A standing prop with a collider stands at STAND_HOG (the player's -0.5); the zone door stays at 0 in its wall."""
        self.assertEqual(O.STAND_HOG, -0.5)
        for o in O.OBJECTS:
            if o.collider is not None and o.stand and o.name not in ('pluto_clinic_door', 'pluto_op_lamp'):
                self.assertEqual(o.height_off_ground, O.STAND_HOG, o.name)
        self.assertEqual(spec('pluto_clinic_door').height_off_ground, 0.0)
        self.assertEqual(self.K.spec_problems(), [])

    def test_the_audit_catches_the_counter_bug_class(self):
        """The 0.12.0 counter (HeightOffGround 0) ties with the player; a collider that starts above the drawing or is narrower
        than it is reported too."""
        rows = ['o' * 32] * 16
        tie = O.Obj('t_tie', 't', rows, ('high', 0, 0, 32, 8), 0.0)
        high = O.Obj('t_high', 't', rows, ('high', 0, 6, 32, 8))
        narrow = O.Obj('t_narrow', 't', rows, ('high', 8, 0, 16, 8))
        good = O.Obj('t_good', 't', rows, ('high', 0, 0, 32, 8))
        found = self.K.spec_problems([tie, high, narrow, good])
        self.assertTrue(any(l.startswith('t_tie:') and 'ties' in l for l in found), found)
        self.assertTrue(any(l.startswith('t_high:') and 'above' in l for l in found), found)
        self.assertTrue(any(l.startswith('t_narrow:') and 'outside' in l for l in found), found)
        self.assertFalse(any(l.startswith('t_good:') for l in found), found)

    def test_reception_counter_is_closed(self):
        """South of the counter Pluto is in front of it; the strip behind it (the receptionist) is out of reach from every side."""
        (dx, dy), = [c for n, c in O.PROPS if n == 'pluto_reception_desk']
        self.assertTrue(self.feet_reachable(29.0, dy - 0.25))                  # pressed against the front
        for x in (26.25, 27.75, 29.5, 31.25, 32.5):                           # the strip behind, end to end
            for y in (dy + 1.3, dy + 1.5):
                self.assertFalse(self.feet_reachable(x, y), (x, y))
        self.assertEqual(self.K.npc_spots_reachable(self.seen), [])
        (rx, ry), = [c for n, c in C.NPCS if n == 'pluto_npc_receptionist']
        for name in ('pluto_reception_desk', 'pluto_back_cabinet'):
            (px, py), = [c for n, c in O.PROPS if n == name]
            for layer, ox, oy, w, h in spec(name).colliders:
                inside = px + ox / 16.0 <= rx < px + (ox + w) / 16.0 and py + oy / 16.0 <= ry < py + (oy + h) / 16.0
                self.assertFalse(inside, (name, (ox, oy, w, h)))

    def test_no_pockets_behind_furniture(self):
        self.assertEqual(self.K.hidden_spots(self.seen), {})

    def test_extra_colliders_are_exported(self):
        cs = C.layout_cs()
        self.assertIn('public static readonly ColliderRect[] EXTRA_COLLIDERS', cs)
        for o in O.OBJECTS:
            for r in o.extra:
                self.assertIn('new ColliderRect("%s", %d, %d, %d, %d),' % ((o.name,) + r), cs)
                self.assertLessEqual(r[0] + r[2], o.size[0], o.name)
                self.assertLessEqual(r[1] + r[3], o.size[1], o.name)


if __name__ == '__main__':
    unittest.main()


class KennelClipTests(unittest.TestCase):
    def test_every_kennel_has_the_three_clips(self):
        import art_sources
        import clinic_objects as O
        kennels = [o for o in O.OBJECTS if o.png in art_sources.KENNEL_STEMS]
        self.assertEqual(sorted(set(o.png for o in kennels)), sorted(art_sources.KENNEL_STEMS))
        for o in kennels:
            self.assertEqual(list(o.clips), ['idle', 'react', 'rattle'], o.name)
            for clip, (frames, fps, loop) in o.clips.items():
                self.assertEqual(frames, art_sources.KENNEL_CLIPS[clip], (o.name, clip))
            self.assertTrue(o.clips['idle'][2] and not o.clips['react'][2] and not o.clips['rattle'][2])

    def test_layout_emits_prop_clips(self):
        import clinic_room
        cs = clinic_room.layout_cs()
        self.assertTrue('public static readonly PropClip[] PROP_CLIPS = {' in cs)
        self.assertTrue('new PropClip("pluto_kennel_dog", "react", 4, 8.0f, false),' in cs)
        self.assertTrue('public class PropClip' in cs)


class KennelArtTests(unittest.TestCase):
    """0.14.0: kennel clips change only the animal and the latch; the cage stays pixel-identical."""

    def test_clip_counts_and_canvas(self):
        import art_sources
        for stem in art_sources.KENNEL_STEMS:
            frames = O.kennel_frames(stem)
            self.assertEqual(dict((k, len(v)) for k, v in frames.items()), dict(art_sources.KENNEL_CLIPS), stem)
            size = art_sources.PIECES[stem + '_idle']['canvas']
            for clip, fs in frames.items():
                for i, f in enumerate(fs):
                    self.assertEqual((len(f[0]), len(f)), tuple(size), (stem, clip, i))

    def test_first_idle_frame_is_the_static_kennel(self):
        import art_sources
        static = dict((o.png, o.rows) for o in O.OBJECTS if o.png in art_sources.KENNEL_STEMS)
        for stem in art_sources.KENNEL_STEMS:
            self.assertEqual(list(O.kennel_frames(stem)['idle'][0]), list(static[stem]), stem)

    def test_frames_animate(self):
        import art_sources
        for stem in art_sources.KENNEL_STEMS:
            for clip, fs in O.kennel_frames(stem).items():
                self.assertGreater(len(set(tuple(f) for f in fs)), 1, (stem, clip))
