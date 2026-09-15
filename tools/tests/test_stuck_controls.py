"""The loadout watchdog must still self-heal a persistent 'cannot fire' state without fighting short legitimate locks."""
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

HARNESS = r'''
using System;
using PlutoVetVisit;
class Checks {
    static void Check(bool ok, string why) { if (!ok) throw new Exception(why); }
    static void Main() {
        var p = new StuckControlPolicy();
        Check(!p.Observe(0, true, false) && !p.Observe(0, true, false), "two stuck ticks are tolerated");
        Check(p.Observe(0, true, false), "third consecutive stuck tick escalates");
        Check(p.StuckTicks(0) == 0, "escalation resets the count");
        p.Observe(0, true, false); p.Observe(0, true, false);
        Check(!p.Observe(0, true, true), "an excused tick (cutscene, roll, stealth) resets instead of escalating");
        Check(!p.Observe(0, true, false) && !p.Observe(0, true, false), "count restarts after an excuse");
        p.Reset();
        p.Observe(0, true, false); p.Observe(0, true, false);
        Check(!p.Observe(0, false, false), "recovering on its own resets");
        p.Reset();
        p.Observe(1, true, false); p.Observe(1, true, false);
        Check(!p.Observe(0, true, false), "players are tracked separately");
        Check(p.Observe(1, true, false), "co-op player escalates on its own count");
        Check(!p.Observe(5, true, false), "unknown slot ignored");
    }
}'''


def controller():
    return '\n'.join(p.read_text(encoding='utf-8') for p in sorted((ROOT / 'src').glob('VetVisitController*.cs')))


class StuckControlTests(unittest.TestCase):
    def test_policy_executable(self):
        source = ROOT / 'src' / 'StuckControlPolicy.cs'
        self.assertTrue(source.exists())
        if not shutil.which('mcs') or not shutil.which('mono'):
            self.skipTest('Mono compiler/runtime required')
        with tempfile.TemporaryDirectory() as tmp:
            cs = pathlib.Path(tmp) / 'check.cs'
            exe = pathlib.Path(tmp) / 'check.exe'
            cs.write_text(HARNESS, encoding='utf-8')
            subprocess.run(['mcs', '-out:' + str(exe), str(source), str(cs)], check=True, capture_output=True)
            subprocess.run(['mono', str(exe)], check=True, capture_output=True)

    def test_watchdog_escalates_through_policy(self):
        c = controller()
        self.assertIn('stuckControls.Observe(', c)
        self.assertIn('EnsureLoadout(p, "watchdog escalation", true, true)', c)


if __name__ == '__main__':
    unittest.main()
