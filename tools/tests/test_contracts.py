"""Source contracts for C# behaviour that has no C# test runner: each test pins the wiring the design needs, so a refactor
cannot silently drop it. The Steam tester confirms the behaviour in game through the named log lines."""
import os
import unittest

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src')


def src(name):
    return open(os.path.join(SRC, name), encoding='utf-8').read()


class ContractTests(unittest.TestCase):
    def has(self, needle, text, where=''):
        self.assertTrue(needle in text, 'missing in %s: %s' % (where, needle))

    def test_past_rearms_the_costume_guns(self):
        c = src('VetVisitController.cs')
        self.has('LoadoutChoice.UseAlternate(p)', c, 'VetVisitController.cs')
        self.has('foreach (int id in p.startingAlternateGunIds) GiveGunById(p, id);', c, 'VetVisitController.cs')
        self.has('LoadoutChoice.Describe(p)', c, 'VetVisitController.cs')
        self.has('p.IsUsingAlternateCostume', src('LoadoutChoice.cs'), 'LoadoutChoice.cs')
