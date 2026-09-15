"""Executable pure C# roster tests plus Unity integration wiring regressions."""
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def controller():
    return '\n'.join(p.read_text() for p in sorted((ROOT / 'src').glob('VetVisitController*.cs')))


def method(text, name):
    start = text.index(name)
    begin = text.index('{', start)
    depth = 1
    end = begin + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[begin:end]


class EncounterLifecycleTests(unittest.TestCase):
    def test_diagnostics_do_not_issue_paths(self):
        self.assertNotIn('PathfindToPosition', method(controller(), 'private string Describe('))

    def test_greeter_uses_wave_lifecycle(self):
        c = controller()
        self.assertNotIn('while (wave1Extra', c)
        self.assertIn('alive.Add(wave1Extra)', method(c, 'private IEnumerator RunWave('))

    def test_delayed_spawn_checks_victory_after_wait(self):
        c = method(controller(), 'private IEnumerator Reinforce(')
        self.assertIn('if (ending', c[c.index('yield return'):c.index('SpawnWave(')])

    def test_emergency_repair_is_explicit(self):
        c = method(controller(), 'private void EnsureLoadout(')
        self.assertIn('if (emergency)', c)
        self.assertNotIn('hiddenTicks', c)
        self.assertNotIn('overriddenTicks', c)

    def test_roster_executable(self):
        source = ROOT / 'src' / 'EncounterRoster.cs'
        self.assertTrue(source.exists(), 'EncounterRoster policy must be implemented')
        harness = r'''
using System;
using PlutoVetVisit;
class Checks {
    static void Check(bool ok, string why) { if (!ok) throw new Exception(why); }
    static void Main() {
        var r = new EncounterRoster<object>();
        var greeter = new object(); var boss = new object();
        Check(r.Track(greeter), "first registration");
        Check(!r.Track(greeter), "duplicate registration");
        Check(r.Track(boss), "boss registration");
        var copy = r.Snapshot(); copy.Clear();
        Check(r.Snapshot().Count == 2, "snapshot must not expose ownership list");
        Check(r.End(), "first ending wins");
        Check(!r.End(), "ending is idempotent");
        Check(!r.Track(new object()), "late reinforcement rejected");
        Check(r.Contains(greeter), "keep owners for projectile cleanup after ending");
        Check(!r.Track(null), "null registration rejected");
    }
}'''
        with tempfile.TemporaryDirectory() as tmp:
            cs = pathlib.Path(tmp) / 'check.cs'
            exe = pathlib.Path(tmp) / 'check.exe'
            cs.write_text(harness)
            subprocess.run(['mcs', '-out:' + str(exe), str(source), str(cs)], check=True, capture_output=True)
            subprocess.run(['mono', str(exe)], check=True, capture_output=True)
