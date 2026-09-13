import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import gemini_art as G  # noqa: E402


class GeminiTests(unittest.TestCase):
    def test_prompts_are_well_formed(self):
        names = [p.name for p in G.PROMPTS]
        self.assertEqual(len(names), len(set(names)))
        for p in G.PROMPTS:
            self.assertTrue(p.name.endswith('.png'))
            self.assertIn(p.ratio, G.RATIOS)
            self.assertGreater(len(p.text), 80)
            self.assertIn('no text', p.text.lower())  # every prompt forbids lettering in the image

    def test_expected_outputs(self):
        self.assertEqual({p.name for p in G.PROMPTS},
                         {'vet_bosscard_raw.png', 'past_win_pic_raw.png', 'icon_raw.png', 'vet_reference_sheet.png', 'clinic_reference.png'})

    def test_load_env_sets_only_missing_names_and_never_prints_values(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, '.env')
            with open(path, 'w') as fh:
                fh.write('# comment\nVETVISIT_TEST_A="alpha"\nVETVISIT_TEST_B=beta\n\n')
            os.environ.pop('VETVISIT_TEST_A', None)
            os.environ['VETVISIT_TEST_B'] = 'kept'
            names = G.load_env(path)
            self.assertEqual(names, ['VETVISIT_TEST_A'])
            self.assertEqual(os.environ['VETVISIT_TEST_A'], 'alpha')
            self.assertEqual(os.environ['VETVISIT_TEST_B'], 'kept')

    def test_load_env_missing_file(self):
        self.assertEqual(G.load_env('/nonexistent/.env'), [])

    def test_dry_run_calls_no_cli(self):
        called = []
        original = G.run_cli
        G.run_cli = lambda args: called.append(args) or {'success': True, 'filePath': 'x'}
        try:
            self.assertEqual(G.main(['--dry-run']), 0)
        finally:
            G.run_cli = original
        self.assertEqual(called, [])

    def test_generate_writes_where_asked(self):
        with tempfile.TemporaryDirectory() as d:
            captured = {}

            def fake(args):
                captured['args'] = args
                out = args[args.index('-o') + 1]
                open(out, 'wb').close()
                return {'success': True, 'filePath': out}
            original, original_out = G.run_cli, G.OUT_DIR
            G.run_cli, G.OUT_DIR = fake, d
            try:
                p = G.PROMPTS[0]
                path = G.generate(p, force=True)
            finally:
                G.run_cli, G.OUT_DIR = original, original_out
            self.assertEqual(path, os.path.join(d, p.name))
            self.assertIn('-a', captured['args'])
            self.assertIn(p.ratio, captured['args'])


if __name__ == '__main__':
    unittest.main()
