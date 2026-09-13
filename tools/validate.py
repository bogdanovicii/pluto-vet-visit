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


def check_objects():
    import clinic_objects
    for o in clinic_objects.OBJECTS:
        p = os.path.join(RES, 'Objects', o.png + '.png')
        if not os.path.exists(p):
            err('object PNG missing: ' + p)
        elif Image.open(p).size != o.size:
            err('%s: PNG size %s != %s' % (o.png, Image.open(p).size, o.size))
    ok('%d object sprites' % len(clinic_objects.OBJECTS))


def check_boss():
    import vet_poses
    root = os.path.join(RES, 'Boss', 'vet')
    for clip, frames in vet_poses.CLIPS.items():
        d = os.path.join(root, clip)
        files = sorted(f for f in os.listdir(d)) if os.path.isdir(d) else []
        if len(files) != len(frames):
            err('%s: %d files != %d frames' % (clip, len(files), len(frames)))
        if not all(re.match(r'^vet_%s_\d{3}\.png$' % clip, f) for f in files):
            err('%s: bad frame names %s' % (clip, files))
        if any(Image.open(os.path.join(d, f)).size != vet_poses.CANVAS for f in files):
            err('%s: frame size != %s' % (clip, vet_poses.CANVAS))
    names = list(vet_poses.CLIPS)
    for a in names:
        for b in names:
            if a != b and b.startswith(a):
                err('clip folder %s is a prefix of %s (Alexandria matches by StartsWith)' % (a, b))
    if Image.open(os.path.join(RES, 'Boss', 'vet_bosscard.png')).size != (427, 240):
        err('boss card must be 427x240')
    if Image.open(os.path.join(RES, 'past_win_pic.png')).size != (115, 71):
        err('past win pic must be 115x71')
    ok('boss: %d clips, card, win pic' % len(names))


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
    for name in ['PlutoVetVisit.Resources.Rooms.vet_clinic.newroom', 'PlutoVetVisit.Resources.Objects.exam_table.png',
                 'PlutoVetVisit.Resources.Boss.vet.idle.vet_idle_001.png', 'PlutoVetVisit.Resources.Boss.vet_bosscard.png',
                 'PlutoVetVisit.Resources.past_win_pic.png']:
        if name not in man:
            err('DLL lacks embedded resource ' + name)
    ok('DLL embeds %d PNGs' % man.count('.png'))


CHECKS = [check_thunderstore, check_room, check_objects, check_boss]


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
