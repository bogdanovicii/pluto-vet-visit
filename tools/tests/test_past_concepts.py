import base64
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import gemini_art as G  # noqa: E402
import gemini_past_concepts as C  # noqa: E402

EXPECTED = {'level_overview', 'zone1_waiting_room', 'zone2_ward', 'zone3_theatre',
            'cast_vet_tech', 'cast_nurse', 'cast_vet_boss', 'cast_owner_receptionist', 'cast_patients',
            'props_waiting_room', 'props_ward', 'props_theatre', 'tiles_and_walls',
            'beat_intro', 'beat_ward_fight', 'beat_boss_intro', 'beat_victory'}


class PastConceptTests(unittest.TestCase):
    def test_prompts_are_well_formed(self):
        names = [p.name for p in C.PROMPTS]
        self.assertEqual(len(names), len(set(names)))
        for p in C.PROMPTS:
            self.assertIn(p.ratio, G.RATIOS)
            self.assertTrue(p.text.startswith(C.STYLE), p.name)   # style block first
            self.assertTrue(p.text.endswith(C.NEG), p.name)       # negative list last
            self.assertGreaterEqual(p.text.lower().count('no text'), 2, p.name)
            self.assertIn('Enter the Gungeon', p.text)
            self.assertIn('#3F9E8F', p.text)                      # palette hexes spelled out

    def test_expected_outputs_and_references(self):
        self.assertEqual({p.name[:-4] for p in C.PROMPTS}, EXPECTED)
        self.assertTrue(C.MULTI <= {p.name for p in C.PROMPTS})
        for p in C.PROMPTS:
            if 'The Vet matches the attached reference' in p.text:
                # every image with the Vet attaches a reference that shows him (boss card, or the win picture)
                self.assertIn(p.ref, (C.VET_REF, C.WIN_REF), p.name)
            if p.ref:
                self.assertTrue(os.path.exists(p.ref), p.ref)

    def test_plan_only_accepts_comma_list_and_candidates(self):
        jobs = C.plan(force=True, only='zone1_waiting_room,beat_intro.png', candidates=3)
        self.assertEqual([os.path.basename(o) for _, _, o in jobs],
                         ['zone1_waiting_room.png', 'zone1_waiting_room_c2.png', 'zone1_waiting_room_c3.png', 'beat_intro.png'])

    def test_dry_run_touches_no_network(self):
        called = []
        original, original_out = C.call_api, C.OUT_DIR
        with tempfile.TemporaryDirectory() as d:
            C.call_api, C.OUT_DIR = lambda body, model, timeout=0: called.append(body) or {}, d
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    self.assertEqual(C.main(['--dry-run']), 0)
            finally:
                C.call_api, C.OUT_DIR = original, original_out
        self.assertEqual(called, [])
        self.assertIn(C.DEFAULT_MODEL, buf.getvalue())

    def test_generate_writes_png_and_sidecar(self):
        png = base64.b64encode(b'\x89PNG fake').decode()
        seen = {}

        def fake(body, model, timeout=0):
            seen['body'] = body
            return {'modelVersion': 'model-x', 'candidates': [{'content': {'parts': [{'inlineData': {'data': png}}]}}]}
        original, original_out = C.call_api, C.OUT_DIR
        with tempfile.TemporaryDirectory() as d:
            C.call_api, C.OUT_DIR = fake, d
            try:
                p = next(p for p in C.PROMPTS if p.ref)
                with contextlib.redirect_stdout(io.StringIO()):
                    out = C.generate((p, 2, C.out_path(p, 2)), 'ignored')
            finally:
                C.call_api, C.OUT_DIR = original, original_out
            self.assertEqual(out, os.path.join(d, p.name[:-4] + '_c2.png'))
            with open(out, 'rb') as fh:
                self.assertEqual(fh.read(), b'\x89PNG fake')
            with open(out[:-4] + '.json', encoding='utf-8') as fh:
                side = json.load(fh)
        self.assertEqual(side['model'], 'model-x')
        self.assertEqual(side['candidate'], 2)
        self.assertEqual(side['prompt'], p.text)
        cfg = seen['body']['generationConfig']['imageConfig']
        self.assertEqual((cfg['aspectRatio'], cfg['imageSize']), (p.ratio, C.IMAGE_SIZE))
        self.assertIn('inlineData', seen['body']['contents'][0]['parts'][0])  # reference image attached first


if __name__ == '__main__':
    unittest.main()
