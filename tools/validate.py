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


def check_room():
    import clinic_room
    path = os.path.join(RES, 'Rooms', 'vet_clinic.newroom')
    if not os.path.exists(path):
        err('vet_clinic.newroom missing (run tools/make_art.py)')
        return
    data = json.load(open(path))
    w, h = data['roomSize']['x'], data['roomSize']['y']
    if len(data['tileInfo']) != w * h:
        err('tileInfo length %d != %d' % (len(data['tileInfo']), w * h))
    if data['category'] != 'ENTRANCE':
        err('room category must be ENTRANCE')
    if data != clinic_room.room_data():
        err('vet_clinic.newroom is stale (run tools/make_art.py)')
    cs = open(os.path.join(PROJECT, 'src', 'ClinicLayout.cs')).read()
    if cs != clinic_room.layout_cs():
        err('ClinicLayout.cs is stale (run tools/make_art.py)')
    known = {o.name for o in clinic_room.O.OBJECTS} | {clinic_room.CONTROLLER}
    unknown = sorted(set(data['placeableGUIDs']) - known)
    if unknown:
        err('room places unknown objects: %s' % unknown)
    ok('room %dx%d, %d placeables' % (w, h, len(data['placeableGUIDs'])))


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
    for name in ['PlutoVetVisit.Resources.Rooms.vet_clinic.newroom']:
        if name not in man:
            err('DLL lacks embedded resource ' + name)
    ok('DLL embeds %d PNGs' % man.count('.png'))


CHECKS = [check_thunderstore, check_room]


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
