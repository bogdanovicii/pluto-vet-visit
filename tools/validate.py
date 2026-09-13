"""Static validation of the Vet Visit package. Run: python3 tools/validate.py  Exits non-zero on failure."""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
RES = os.path.join(PROJECT, 'Resources')
DLL = os.path.join(PROJECT, 'bin', 'Release', 'PlutoVetVisit.dll')
sys.path.insert(0, HERE)
from PIL import Image  # noqa: E402

errors = []


def err(msg):
    errors.append(msg)
    print('FAIL', msg)


def ok(msg):
    print(' ok ', msg)


def check_thunderstore():
    ts = os.path.join(PROJECT, 'thunderstore')
    m = json.load(open(os.path.join(ts, 'manifest.json')))
    if not re.match(r'^[A-Za-z0-9_]+$', m['name']):
        err('manifest name has invalid characters')
    if len(m['description']) > 250:
        err('manifest description > 250 chars')
    if Image.open(os.path.join(ts, 'icon.png')).size != (256, 256):
        err('thunderstore icon must be 256x256')
    if not os.path.exists(os.path.join(ts, 'README.md')):
        err('thunderstore README.md missing')
    ok('thunderstore manifest/icon/readme')


def dll_manifest():
    """Embedded resource names inside the built DLL, or None when not built / monodis missing."""
    if not os.path.exists(DLL):
        print('skip  DLL not built yet')
        return None
    try:
        return subprocess.run(['monodis', '--manifest', DLL], capture_output=True, text=True).stdout
    except FileNotFoundError:
        print('skip  monodis not available')
        return None


def check_dll(man):
    if man is None:
        return
    ok('DLL embeds %d PNGs' % man.count('.png'))


CHECKS = [check_thunderstore]


def main():
    for check in CHECKS:
        check()
    check_dll(dll_manifest())
    if errors:
        print('\n%d problem(s)' % len(errors))
        sys.exit(1)
    print('\nall checks passed')


if __name__ == '__main__':
    main()
